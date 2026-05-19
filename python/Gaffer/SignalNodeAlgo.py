##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

"""Numerical helpers for Phase 4 **signal** nodes (SDF projection, IV metrics)."""

from __future__ import annotations

from typing import List, Optional, Sequence, Tuple


def covariance_from_rows( rows : Sequence[Sequence[float]] ) -> Optional[List[List[float]]] :
	"""Unbiased sample covariance of **rows** (each row a factor observation); ``n >= 2`` rows."""

	n = len( rows )
	if n < 2 :
		return None
	p = len( rows[0] )
	if p < 1 :
		return None
	for r in rows :
		if len( r ) != p :
			return None

	means = [ sum( float( rows[i][j] ) for i in range( n ) ) / n for j in range( p ) ]
	cov = [ [ 0.0 for _ in range( p ) ] for _ in range( p ) ]
	den = max( n - 1, 1 )
	for i in range( n ) :
		d = [ float( rows[i][j] ) - means[j] for j in range( p ) ]
		for a in range( p ) :
			for b in range( p ) :
				cov[a][b] += d[a] * d[b]
	for a in range( p ) :
		for b in range( p ) :
			cov[a][b] /= den
	return cov


def mat_vec_solve( a : List[List[float]], b : List[float], ridge : float ) -> Optional[List[float]] :
	"""Solve ``(A + ridge I) x = b`` with partial pivoting (no external deps)."""

	p = len( b )
	if p < 1 or len( a ) != p :
		return None
	for row in a :
		if len( row ) != p :
			return None

	A = [ [ float( a[r][c] ) + ( ridge if r == c else 0.0 ) for c in range( p ) ] for r in range( p ) ]
	x = [ float( v ) for v in b ]

	for k in range( p ) :
		piv = max( range( k, p ), key = lambda r : abs( A[r][k] ) )
		if abs( A[piv][k] ) < 1e-18 :
			return None
		if piv != k :
			A[k], A[piv] = A[piv], A[k]
			x[k], x[piv] = x[piv], x[k]
		pk = A[k][k]
		for c in range( k, p ) :
			A[k][c] /= pk
		x[k] /= pk
		for r in range( k + 1, p ) :
			f = A[r][k]
			if f == 0.0 :
				continue
			for c in range( k, p ) :
				A[r][c] -= f * A[k][c]
			x[r] -= f * x[k]

	for k in range( p - 1, -1, -1 ) :
		for c in range( k + 1, p ) :
			x[k] -= A[k][c] * x[c]
		if abs( A[k][k] ) < 1e-18 :
			return None
		x[k] /= A[k][k]

	return x


def sdf_projection_alpha(
	ff_loadings : Sequence[float],
	factor_returns : Sequence[float],
	panel_rows : Sequence[Sequence[float]],
	cov_window : int,
	ridge : float,
) -> Tuple[float, float] :
	"""Avramov–He-style **linear** SDF step: ``λ = (Σ+ridge I)^{-1} μ``, ``α = L·λ``.

	Returns ``(alpha_weight, confidence)`` where confidence down-weights ill-conditioned **λ**.
	"""

	L = [ float( x ) for x in ff_loadings ]
	r = [ float( x ) for x in factor_returns ]
	if len( L ) != len( r ) or len( L ) < 1 :
		return 0.0, 0.0

	p = len( L )
	rows = [ [ float( row[j] ) for j in range( p ) ] for row in panel_rows[-cov_window:] if len( row ) == p ]
	if len( rows ) < 2 :
		return 0.0, 0.0

	cov = covariance_from_rows( rows )
	if cov is None :
		return 0.0, 0.0

	lam = mat_vec_solve( cov, r, max( float( ridge ), 1e-18 ) )
	if lam is None :
		return 0.0, 0.0

	alpha = sum( L[i] * lam[i] for i in range( p ) )
	ln = sum( x * x for x in lam ) ** 0.5
	conf = 1.0 / ( 1.0 + ln )
	alpha_scaled = alpha / ( 1.0 + ln )
	return float( max( min( alpha_scaled, 1.0 ), -1.0 ) ), float( max( min( conf, 1.0 ), 0.0 ) )


def iv_skew_alpha(
	strikes : Sequence[float],
	ivs_first_expiry : Sequence[float],
) -> float :
	"""Heuristic **skew** alpha from OTM put vs call IV (single expiry column). Clipped to ``[-1,1]``."""

	if len( strikes ) != len( ivs_first_expiry ) or len( strikes ) < 2 :
		return 0.0
	pairs = sorted( zip( strikes, ivs_first_expiry ), key = lambda z : z[0] )
	s = [ float( p[0] ) for p in pairs ]
	v = [ float( p[1] ) for p in pairs ]
	mid = 0.5 * ( s[0] + s[-1] )
	low_iv = [ v[i] for i in range( len( s ) ) if s[i] < mid ]
	high_iv = [ v[i] for i in range( len( s ) ) if s[i] > mid ]
	if not low_iv or not high_iv :
		return 0.0
	sk = sum( low_iv ) / len( low_iv ) - sum( high_iv ) / len( high_iv )
	den = sum( v ) / len( v )
	if den < 1e-9 :
		return 0.0
	a = sk / den
	return float( max( min( a, 1.0 ), -1.0 ) )
