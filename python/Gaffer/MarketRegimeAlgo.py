##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

"""Shared helpers for Phase 3 regime :class:`Gaffer.ComputeNode` implementations."""

from __future__ import annotations

from typing import List, Optional, Tuple

import Gaffer


def truncate_series_by_pit(
	times : List[int],
	values : List[float],
	contextTime : Optional[object],
) -> Tuple[List[int], List[float]] :
	"""Return ``(times, values)`` sorted by time, optionally capped by ``contextTime``."""

	if len( times ) != len( values ) :
		return [], []

	pairs = sorted( zip( times, values ), key = lambda z : z[0] )
	if contextTime is not None :
		tlim = int( contextTime )
		pairs = [ p for p in pairs if p[0] <= tlim ]
	if not pairs :
		return [], []
	t2, v2 = zip( *pairs )
	return list( t2 ), list( v2 )


def last_scalar_from_series_plug(
	seriesPlug : Gaffer.SeriesPlug,
	contextTime : Optional[object],
) -> Optional[float] :

	times = list( seriesPlug["times"].getValue() )
	values = list( seriesPlug["values"].getValue() )
	t2, v2 = truncate_series_by_pit( times, values, contextTime )
	if not t2 :
		return None
	return float( v2[-1] )
