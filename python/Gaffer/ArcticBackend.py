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

"""ArcticDB path for :class:`TimeSeriesStoreNode` and helpers (N4: write / append / catalog). Requires PyPI ``arcticdb`` (+ ``pandas``)."""

from __future__ import annotations

import os
import warnings

from typing import List, Tuple


def arcticdbAvailable() -> bool :

	try :
		import arcticdb  # noqa: F401
		import pandas  # noqa: F401
	except ImportError :
		return False
	return True


def _arcticAndPandas() -> Tuple[object, object] :

	try :
		from arcticdb import Arctic
		import pandas as pd
	except ImportError as e :
		raise RuntimeError(
			"ArcticBackend: requires PyPI packages `arcticdb` and `pandas`."
		) from e

	return Arctic, pd


def _normaliseUri( arcticUri : str ) -> str :

	uri = ( arcticUri or "" ).strip()
	if not uri :
		raise RuntimeError(
			"ArcticBackend: requires a non-empty arcticUri (Arctic URI / storage id)."
		)

	uri = os.path.expanduser( os.path.expandvars( uri ) )

	# Real URIs must not go through os.path.normpath — on Windows it corrupts e.g.
	# ``lmdb://C:/Users/...`` into ``lmdb:\C:\Users\...``, which ArcticDB rejects.
	if "://" in uri :
		return uri

	# Repair already-mangled LMDB paths (e.g. after normpath) for Windows.
	if uri.lower().startswith( "lmdb:" ) :
		_unused, _sep, rest = uri.partition( ":" )
		rest = rest.lstrip( "\\/" )
		return "lmdb://" + rest.replace( "\\", "/" )

	return os.path.normpath( uri )


def _resolveLibrary( ac : object, libraryName : str, *, createIfMissing : bool = False ) -> object :

	name = libraryName.strip() or "pce"
	if createIfMissing :
		libs = ac.list_libraries()
		if name not in libs :
			ac.create_library( name )

	try :
		return ac.get_library( name )
	except Exception : # noqa: BLE001
		try :
			return ac[name]
		except Exception as e2 :
			raise RuntimeError(
				f"ArcticBackend: library {name!r} not available: {e2}"
			) from e2


def list_libraries( arcticUri : str ) -> List[str] :

	"""List Arctic library names at ``arcticUri`` (sorted)."""

	Arctic, _pd = _arcticAndPandas()
	ac = Arctic( _normaliseUri( arcticUri ) )
	return sorted( ac.list_libraries() )


def list_symbols( arcticUri : str, libraryName : str ) -> List[str] :

	"""
	List symbol names in ``libraryName`` (sorted). The library must exist.
	"""

	Arctic, _pd = _arcticAndPandas()
	ac = Arctic( _normaliseUri( arcticUri ) )
	lib = _resolveLibrary( ac, libraryName, createIfMissing = False )
	return sorted( lib.list_symbols() )


def _timesAndValuesToDataFrame( pd : object, times : List[int], values : List[float], valueColumn : str ) -> object :

	if len( times ) != len( values ) :
		raise RuntimeError(
			f"ArcticBackend: times and values length mismatch ({len( times )} vs {len( values )})."
		)

	col = valueColumn if valueColumn else "value"
	if not times :
		# Empty frame with typed index/column for schema-stable append workflows
		idx = pd.DatetimeIndex( [] )
		return pd.DataFrame( { col : [] }, index = idx )

	# Heuristic: very large ints → nanosecond UTC wall time (matches read path for DatetimeIndex).
	if times[0] > 10 ** 15 :
		idx = pd.to_datetime( times, unit = "ns" )
	else :
		idx = pd.Index( times, dtype = "int64" )

	return pd.DataFrame( { col : values }, index = idx )


def write_series_for_store(
	arcticUri : str,
	libraryName : str,
	symbol : str,
	times : List[int],
	values : List[float],
	valueColumn : str,
	*,
	createLibrary : bool = True,
) -> None :

	"""
	``library.write(symbol, df)`` — replaces the symbol’s data with ``(times, values)``.

	:param createLibrary: if true (default), create ``libraryName`` when missing.
	:param valueColumn: dataframe column name (should match ``TimeSeriesStoreNode.field`` when round-tripping reads).
	"""

	if not str( symbol ).strip() :
		raise RuntimeError( "ArcticBackend: write requires a non-empty symbol." )

	Arctic, pd = _arcticAndPandas()
	ac = Arctic( _normaliseUri( arcticUri ) )
	lib = _resolveLibrary( ac, libraryName, createIfMissing = createLibrary )
	df = _timesAndValuesToDataFrame( pd, times, values, valueColumn )
	lib.write( symbol, df )


def append_series_for_store(
	arcticUri : str,
	libraryName : str,
	symbol : str,
	times : List[int],
	values : List[float],
	valueColumn : str,
) -> None :

	"""
	``library.append(symbol, df)`` — appends rows; **symbol must exist** and new rows must continue the index per the ArcticDB rules.
	"""

	if not symbol.strip() :
		raise RuntimeError( "ArcticBackend: append requires a non-empty symbol." )

	Arctic, pd = _arcticAndPandas()
	ac = Arctic( _normaliseUri( arcticUri ) )
	lib = _resolveLibrary( ac, libraryName, createIfMissing = False )
	df = _timesAndValuesToDataFrame( pd, times, values, valueColumn )
	lib.append( symbol, df )


def read_series_for_store(
	arcticUri : str,
	libraryName : str,
	symbol : str,
	valueColumn : str,
) -> Tuple[List[int], List[float]] :
	"""
	Read a single series from ArcticDB: returns ``(times, values)``.

	- **Times**: ``DatetimeIndex`` → int64 nanoseconds since Unix epoch; integer index → int bar ids.
	- **Values**: column ``valueColumn`` if present, else ``"value"``, else first numeric column.
	"""

	Arctic, pd = _arcticAndPandas()
	ac = Arctic( _normaliseUri( arcticUri ) )
	lib = _resolveLibrary( ac, libraryName, createIfMissing = False )

	try :
		# ArcticDB builds DataFrames via pandas internals that emit DeprecationWarning on
		# recent pandas; Gaffer's compute treats warnings as errors.
		with warnings.catch_warnings() :
			warnings.simplefilter( "ignore", DeprecationWarning )
			item = lib.read( symbol )
	except Exception as e :
		raise RuntimeError(
			f'TimeSeriesStoreNode: ArcticDB read failed for symbol {symbol!r}: {e}'
		) from e

	df = item.data
	if df is None or len( df ) == 0 :
		return [], []

	colName = valueColumn if valueColumn in df.columns else None
	if colName is None and "value" in df.columns :
		colName = "value"
	if colName is None :
		num = df.select_dtypes( include = ( "number", ) ).columns
		if len( num ) :
			colName = str( num[0] )
	if colName is None :
		raise RuntimeError(
			f"TimeSeriesStoreNode: no numeric column for ArcticDB symbol {symbol!r} (field {valueColumn!r})."
		)

	idx = df.index
	if isinstance( idx, pd.DatetimeIndex ) :
		asi8 = getattr( idx, "asi8", None )
		if asi8 is not None :
			times = [ int( x ) for x in asi8 ]
		else :
			times = [ int( pd.Timestamp( ts ).value ) for ts in idx ]
	elif hasattr( idx, "dtype" ) and str( idx.dtype ).startswith( "int" ) :
		times = [ int( x ) for x in idx.tolist() ]
	else :
		times = list( range( len( df ) ) )

	values = [ float( x ) for x in df[colName].tolist() ]
	n = min( len( times ), len( values ) )
	return times[:n], values[:n]
