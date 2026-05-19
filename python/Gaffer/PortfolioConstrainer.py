##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

from __future__ import annotations

from typing import List, Sequence, Tuple

import IECore

## **IECore.msg** context when portfolio / exposure limits are hit (Phase 5).
OTL_EXPOSURE_VIOLATION = "OTL_EXPOSURE_VIOLATION"


def _abs_gross( w : Sequence[float] ) -> float :

	return sum( abs( float( x ) ) for x in w )


def cap_single_name( weights : Sequence[float], max_abs : float ) -> Tuple[List[float], bool] :

	mx = float( max_abs )
	if mx <= 0.0 :
		return [ 0.0 for _ in weights ], False

	out = [ float( x ) for x in weights ]
	viol = False
	for i, x in enumerate( out ) :
		if abs( x ) > mx :
			viol = True
			out[i] = mx * ( 1.0 if x >= 0.0 else -1.0 )
	return out, viol


def enforce_gross_exposure( weights : Sequence[float], max_gross : float ) -> Tuple[List[float], bool] :

	mg = float( max_gross )
	if mg <= 0.0 :
		return [ 0.0 for _ in weights ], False

	g = _abs_gross( weights )
	if g <= mg + 1e-12 :
		return [ float( x ) for x in weights ], False

	s = mg / g
	return [ float( x ) * s for x in weights ], True


def enforce_net_exposure( weights : Sequence[float], max_abs_net : float ) -> Tuple[List[float], bool] :

	mn = float( max_abs_net )
	if mn < 0.0 :
		return [ float( x ) for x in weights ], False

	s = sum( float( x ) for x in weights )
	if abs( s ) <= mn + 1e-12 :
		return [ float( x ) for x in weights ], False

	## Scale toward **dollar-neutral** so **|sum(w)| == max_abs_net** when possible.
	excess = abs( s ) - mn
	sign = 1.0 if s > 0.0 else -1.0
	## Distribute reduction proportionally to signed mass (simple v0.1 heuristic).
	n = len( weights )
	if n == 0 :
		return [], False

	w = [ float( x ) for x in weights ]
	target = sign * mn
	## Single scaling factor on all weights toward **target** net from **s**.
	if abs( s ) < 1e-18 :
		return w, False

	scale = target / s
	w2 = [ x * scale for x in w ]
	return w2, True


def apply_min_confidence( weights : Sequence[float], confidences : Sequence[float], min_c : float ) -> Tuple[List[float], bool] :

	mc = float( min_c )
	out = [ float( x ) for x in weights ]
	viol = False
	for i in range( len( out ) ) :
		cf = float( confidences[i] ) if i < len( confidences ) else 0.0
		if cf < mc :
			if abs( out[i] ) > 1e-18 :
				viol = True
			out[i] = 0.0
	return out, viol


def drawdown_gate_apply( weights : Sequence[float], *, drawdown : float, gate : float ) -> Tuple[List[float], bool] :

	## If **drawdown** exceeds **gate**, zero weights (v0.1 policy).
	dd = float( drawdown )
	g = float( gate )
	if g <= 0.0 or dd <= g :
		return [ float( x ) for x in weights ], False
	return [ 0.0 for _ in weights ], True


def emit_exposure_violation( message : str ) -> None :

	IECore.msg(
		IECore.MessageHandler.Level.Warning,
		OTL_EXPOSURE_VIOLATION,
		message,
	)
