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

"""
In-process time series registry for :class:`TimeSeriesStoreNode` **memory** backend
and tests. Production stores (ArcticDB, etc.) will bypass this module.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Sequence, Tuple, Union

__registry : Dict[ Tuple[str, str], Tuple[ List[int], List[float] ] ] = {}

## Context key for point-in-time evaluation (nanoseconds since epoch, or any sortable int bar id).
PCE_TIME_CONTEXT_KEY = "marketlab:pceTime"


def registerSeries( instrumentId : str, field : str, times : Sequence[Union[int, float]], values : Sequence[Union[int, float]] ) -> None :

	__registry[ ( str( instrumentId ), str( field ) ) ] = (
		[ int( t ) for t in times ],
		[ float( v ) for v in values ],
	)


def registeredSeriesView() -> Mapping[Tuple[str, str], Tuple[List[int], List[float]]] :

	return __registry


def getSeries( instrumentId : str, field : str ) -> Tuple[List[int], List[float]] :

	return __registry.get( ( str( instrumentId ), str( field ) ), ( [], [] ) )


def clearRegistry() -> None :

	__registry.clear()
