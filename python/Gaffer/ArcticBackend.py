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

"""Optional ArcticDB read path for :class:`TimeSeriesStoreNode`. Requires PyPI ``arcticdb`` (+ ``pandas``)."""

from __future__ import annotations

from typing import List, Tuple


def arcticdbAvailable() -> bool :

	try :
		import arcticdb  # noqa: F401
		import pandas  # noqa: F401
	except ImportError :
		return False
	return True


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

	try :
		from arcticdb import Arctic
	except ImportError as e :
		raise RuntimeError(
			"TimeSeriesStoreNode: arcticdb backend requires PyPI packages `arcticdb` and `pandas`."
		) from e

	import pandas as pd

	uri = arcticUri.strip()
	if not uri :
		raise RuntimeError(
			"TimeSeriesStoreNode: arcticdb backend requires a non-empty resourcePath (Arctic URI)."
		)

	ac = Arctic( uri )
	try :
		lib = ac.get_library( libraryName )
	except Exception : # noqa: BLE001
		try :
			lib = ac[libraryName]
		except Exception as e2 :
			raise RuntimeError(
				f"TimeSeriesStoreNode: ArcticDB library {libraryName!r} not available at {uri!r}: {e2}"
			) from e2

	try :
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
		# Fallback: positional bar indices
		times = list( range( len( df ) ) )

	values = [ float( x ) for x in df[colName].tolist() ]
	n = min( len( times ), len( values ) )
	return times[:n], values[:n]
