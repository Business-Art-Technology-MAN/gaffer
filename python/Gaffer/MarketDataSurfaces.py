##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

"""
In-memory implied-volatility surfaces keyed by symbol (``IVSurfaceNode`` ``memory`` backend).

Payload keys mirror :func:`Gaffer.MarketDataAlgo.surfacePlugToDict`: ``asOfTime``, ``strikes``,
``expiries``, ``ivsRowMajor``.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

__registry : Dict[str, Dict[str, Any]] = {}


def register_iv_surface( symbol : str, surface : Mapping[str, Any] ) -> None :

	key = ( symbol or "" ).strip()
	if not key :
		return
	__registry[key] = dict( surface )


def get_iv_surface( symbol : str ) -> Optional[Dict[str, Any]] :

	return __registry.get( ( symbol or "" ).strip() )


def clear_all_for_tests() -> None :
	"""Test helper — clear registry."""

	__registry.clear()
