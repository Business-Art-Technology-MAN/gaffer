##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided
#        with the distribution.
#
#      * Neither the name of John Haddon nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

from __future__ import annotations

import csv
import os
from typing import List, Tuple

from .SeriesCsvReaderNode import _readSeriesCsv


def normalise_resource_path( path : str ) -> str :

	if not path :
		return ""
	return os.path.normpath( os.path.expanduser( os.path.expandvars( path.strip() ) ) )


def read_parquet_two_column_series( path : str, field : str ) -> Tuple[List[int], List[float]] :
	"""Parquet with ``time`` and a numeric value column (``field`` or ``value``)."""

	try :
		import pyarrow.parquet as pq
	except ImportError as e :
		raise RuntimeError( "read_parquet_two_column_series: pyarrow is required." ) from e

	if not os.path.isfile( path ) :
		return [], []

	table = pq.read_table( path )
	names = table.column_names
	if "time" not in names :
		raise RuntimeError( 'read_parquet_two_column_series: parquet must contain a "time" column.' )
	valueColumn = field if field in names else ( "value" if "value" in names else None )
	if valueColumn is None :
		raise RuntimeError( f'read_parquet_two_column_series: no column "{field}" or "value".' )

	tcol = table.column( "time" )
	vcol = table.column( valueColumn )
	times = [ int( x ) for x in tcol.to_pylist() ]
	values = [ float( x ) for x in vcol.to_pylist() ]
	return times, values


def read_wide_csv_panel(
	filePath : str,
	hasHeader : bool,
	delimiter : str,
) -> Tuple[List[int], int, List[float]] :
	"""
	First column: time (int). Remaining columns: numeric panel values, row-major
	``(time_0, col0..colN-1), (time_1, …)``.
	"""

	times : List[int] = []
	values : List[float] = []
	path = normalise_resource_path( filePath )
	if not path :
		return [], 0, []

	delim = delimiter if delimiter else ","
	delim = delim[0]

	try :
		with open( path, newline = "", encoding = "utf-8" ) as f :
			reader = csv.reader( f, delimiter = delim )
			rows = list( reader )
	except OSError :
		return [], 0, []

	if hasHeader and rows :
		rows = rows[1:]

	if not rows :
		return [], 0, []

	nColsData = len( rows[0] ) - 1
	if nColsData < 1 :
		return [], 0, []

	for row in rows :
		if len( row ) < len( rows[0] ) :
			continue
		try :
			t = int( float( row[0].strip() ) )
		except ValueError :
			continue
		rowVals = []
		ok = True
		for c in range( 1, len( row ) ) :
			try :
				rowVals.append( float( row[c].strip() ) )
			except ValueError :
				ok = False
				break
		if not ok or len( rowVals ) != nColsData :
			continue
		times.append( t )
		values.extend( rowVals )

	if not times :
		return [], 0, []

	return times, nColsData, values


def read_wide_parquet_panel( path : str ) -> Tuple[List[int], int, List[float]] :

	try :
		import pyarrow.parquet as pq
	except ImportError as e :
		raise RuntimeError( "read_wide_parquet_panel: pyarrow is required." ) from e

	if not os.path.isfile( path ) :
		return [], 0, []

	table = pq.read_table( path )
	names = table.column_names
	if "time" not in names :
		raise RuntimeError( 'read_wide_parquet_panel: parquet must contain a "time" column.' )

	valueNames = sorted( n for n in names if n != "time" )
	if not valueNames :
		return [], 0, []

	tcol = table.column( "time" )
	times = [ int( x ) for x in tcol.to_pylist() ]
	nRows = len( times )
	colsData = [ table.column( name ).to_pylist() for name in valueNames ]
	nCols = len( colsData )
	values = []
	for r in range( nRows ) :
		for c in range( nCols ) :
			values.append( float( colsData[c][r] ) )

	return times, nCols, values


def read_series_csv_adapter(
	filePath : str,
	hasHeader : bool,
	timeColumn : int,
	valueColumn : int,
	delimiter : str,
) -> Tuple[List[int], List[float]] :

	return _readSeriesCsv( filePath, hasHeader, timeColumn, valueColumn, delimiter )


def select_series_by_time(
	times : List[int],
	values : List[float],
	lookback : int,
	contextTime : object,
) -> Tuple[List[int], List[float]] :
	"""Sort by time, optional point-in-time cap, then ``lookback`` tail."""

	pairs = sorted( zip( times, values ), key = lambda z : z[0] )
	if contextTime is not None :
		tlim = int( contextTime )
		pairs = [ p for p in pairs if p[0] <= tlim ]
	if lookback > 0 and len( pairs ) > lookback :
		pairs = pairs[-lookback:]
	if not pairs :
		return [], []
	t2, v2 = zip( *pairs )
	return list( t2 ), list( v2 )


def select_panel_by_time(
	times : List[int],
	valuesRowMajor : List[float],
	numColumns : int,
	lookback : int,
	contextTime : object,
) -> Tuple[List[int], int, List[float]] :
	"""Same semantics as :func:`select_series_by_time`, preserving row-major blocks."""

	if numColumns < 1 :
		return [], 0, []

	nVec = len( valuesRowMajor )
	if nVec != len( times ) * numColumns :
		return [], numColumns, []

	pairs = []
	for i, t in enumerate( times ) :
		base = i * numColumns
		row = valuesRowMajor[base:base + numColumns]
		pairs.append( ( t, row ) )

	pairs.sort( key = lambda z : z[0] )
	if contextTime is not None :
		tlim = int( contextTime )
		pairs = [ p for p in pairs if p[0] <= tlim ]
	if lookback > 0 and len( pairs ) > lookback :
		pairs = pairs[-lookback:]

	if not pairs :
		return [], numColumns, []

	outTimes = []
	outFlat = []
	for t, row in pairs :
		outTimes.append( t )
		outFlat.extend( row )

	return outTimes, numColumns, outFlat
