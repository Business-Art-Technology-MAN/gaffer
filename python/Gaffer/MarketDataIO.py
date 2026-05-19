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
from typing import Dict, List, Optional, Tuple, cast

from .SeriesCsvReaderNode import _readSeriesCsv


def normalise_resource_path( path : str ) -> str :

	if not path :
		return ""
	return os.path.normpath( os.path.expanduser( os.path.expandvars( path.strip() ) ) )


def normalise_live_url( url : str ) -> str :
	"""Expand env/user only — do not :func:`os.path.normpath` (breaks ``https://`` URLs)."""

	return os.path.expanduser( os.path.expandvars( ( url or "" ).strip() ) )


def read_series_http_csv(
	url : str,
	hasHeader : bool,
	timeColumn : int,
	valueColumn : int,
	delimiter : str,
	*,
	timeout : float = 60.0,
) -> Tuple[List[int], List[float]] :
	"""Fetch a UTF-8 CSV over HTTP(S) and parse two columns like :func:`read_series_csv_adapter`."""

	from urllib.parse import urlparse
	from urllib.request import Request, urlopen

	from .SeriesCsvReaderNode import _readSeriesCsvFromString

	u = normalise_live_url( url )
	if not u :
		return [], []

	scheme = ( urlparse( u ).scheme or "" ).lower()
	if scheme not in ( "http", "https" ) :
		raise RuntimeError(
			f'MarketDataIO: httpcsv resourcePath must be an http(s) URL, got {u!r}.'
		)

	req = Request( u, headers = { "User-Agent": "Gaffer-MarketLab/N5" } )
	try :
		with urlopen( req, timeout = timeout ) as resp :
			raw = resp.read()
	except Exception as e :
		raise RuntimeError( f"MarketDataIO: HTTP CSV fetch failed for {u!r}: {e}" ) from e

	try :
		text = raw.decode( "utf-8" )
	except UnicodeDecodeError :
		text = raw.decode( "utf-8", errors = "replace" )

	return _readSeriesCsvFromString( text, hasHeader, timeColumn, valueColumn, delimiter )


def fred_api_key_from_environ() -> str :

	return (
		os.environ.get( "PCE_FRED_API_KEY" )
		or os.environ.get( "FRED_API_KEY" )
		or ""
	).strip()


def read_series_fred_observations(
	seriesId : str,
	*,
	apiKey : Optional[str] = None,
	timeout : float = 60.0,
) -> Tuple[List[int], List[float]] :
	"""
	FRED ``series/observations`` JSON → ``(times, values)`` with **YYYYMMDD** int timestamps.
	API key from ``apiKey`` or ``PCE_FRED_API_KEY`` / ``FRED_API_KEY`` (never store the key in graph files).
	"""

	import json
	from urllib.parse import urlencode
	from urllib.request import Request, urlopen

	key = apiKey if apiKey is not None else fred_api_key_from_environ()
	if not key :
		raise RuntimeError(
			"MarketDataIO: FRED requires PCE_FRED_API_KEY or FRED_API_KEY in the environment."
		)

	sid = ( seriesId or "" ).strip()
	if not sid :
		return [], []

	base = "https://api.stlouisfed.org/fred/series/observations"
	query = urlencode(
		{
			"series_id" : sid,
			"api_key" : key,
			"file_type" : "json",
		}
	)
	url = f"{base}?{query}"

	req = Request( url, headers = { "User-Agent": "Gaffer-MarketLab/N5" } )
	try :
		with urlopen( req, timeout = timeout ) as resp :
			payload = json.loads( resp.read().decode( "utf-8" ) )
	except Exception as e :
		raise RuntimeError( f"MarketDataIO: FRED request failed for {sid!r}: {e}" ) from e

	obs = payload.get( "observations" ) or []
	times : List[int] = []
	values : List[float] = []
	for row in obs :
		ds = ( row.get( "date" ) or "" ).strip()
		vraw = row.get( "value" )
		if not ds or vraw in ( None, ".", "" ) :
			continue
		try :
			parts = ds.split( "-" )
			if len( parts ) != 3 :
				continue
			t = int( parts[0] ) * 10000 + int( parts[1] ) * 100 + int( parts[2] )
			v = float( vraw )
		except ( ValueError, TypeError ) :
			continue
		times.append( t )
		values.append( v )

	return times, values


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


def long_iv_rows_to_grid(
	rows : List[List[str]],
	hasHeader : bool,
	strikeColumn : int,
	expiryColumn : int,
	ivColumn : int,
) -> Tuple[List[float], List[float], List[float]] :
	"""
	Long-format CSV rows ``strike, expiry, iv`` → sorted axes and **strike-major**
	``ivsRowMajor`` ( IV at ``strikes[i]``, ``expiries[j]`` has index ``i * len(expiries) + j`` ).
	Missing \`(strike, expiry)\` pairs become **NaN** in the flat array.
	"""

	if hasHeader and rows :
		rows = rows[1:]

	need = max( strikeColumn, expiryColumn, ivColumn ) + 1
	points : List[Tuple[float, float, float]] = []
	for row in rows :
		if len( row ) < need :
			continue
		try :
			k = float( row[strikeColumn].strip() )
			tau = float( row[expiryColumn].strip() )
			iv = float( row[ivColumn].strip() )
		except ValueError :
			continue
		points.append( ( k, tau, iv ) )

	if not points :
		return [], [], []

	lut : Dict[Tuple[float, float], float] = {}
	for k, tau, iv in points :
		lut[( k, tau )] = iv

	strikes = sorted( { p[0] for p in points } )
	expiries = sorted( { p[1] for p in points } )
	ivs : List[float] = []
	for k in strikes :
		for tau in expiries :
			ivs.append( float( lut.get( ( k, tau ), float( "nan" ) ) ) )

	return strikes, expiries, ivs


def read_iv_surface_long_csv(
	filePath : str,
	hasHeader : bool,
	strikeColumn : int,
	expiryColumn : int,
	ivColumn : int,
	delimiter : str,
) -> Tuple[List[float], List[float], List[float]] :
	"""UTF-8 CSV on disk; empty path or missing file → three empty lists."""

	path = normalise_resource_path( filePath )
	if not path :
		return [], [], []

	delim = delimiter if delimiter else ","
	delim = delim[0]

	try :
		with open( path, newline = "", encoding = "utf-8" ) as f :
			reader = csv.reader( f, delimiter = delim )
			rows = cast( List[List[str]], list( reader ) )
	except OSError :
		return [], [], []

	return long_iv_rows_to_grid( rows, hasHeader, strikeColumn, expiryColumn, ivColumn )


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
