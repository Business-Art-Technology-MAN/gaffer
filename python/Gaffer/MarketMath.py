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
Tiny linear least squares (normal equations + Gaussian elimination).
Avoids an optional ``numpy`` dependency in MarketLab unit tests / minimal installs.
"""

from __future__ import annotations

import math
from typing import Dict, List, Sequence


def linear_least_squares( X : Sequence[Sequence[float]], y : Sequence[float] ) -> List[float] :
	"""Return ``beta`` minimising ``sum_k (y_k - sum_i X_ki beta_i)^2``."""

	if not X :
		return []
	p = len( X[0] )
	if p == 0 :
		return []
	for row in X :
		if len( row ) != p :
			raise ValueError( "linear_least_squares: ragged X rows." )
	n = len( X )
	if len( y ) != n :
		raise ValueError( "linear_least_squares: y length must match X row count." )

	XtX = [ [ 0.0 ] * p for _ in range( p ) ]
	Xty = [ 0.0 ] * p

	for k in range( n ) :
		row = X[k]
		yk = float( y[k] )
		for i in range( p ) :
			Xty[i] += row[i] * yk
			for j in range( p ) :
				XtX[i][j] += row[i] * row[j]

	return _gaussian_solve( XtX, Xty )


def _gaussian_solve( A : List[List[float]], b : List[float] ) -> List[float] :

	n = len( A )
	M = [ row[:] + [b[i]] for i, row in enumerate( A ) ]

	for col in range( n ) :

		pivot = col
		best = abs( M[pivot][col] )
		for r in range( col + 1, n ) :
			v = abs( M[r][col] )
			if v > best :
				best = v
				pivot = r

		if best < 1e-18 :
			raise ValueError( "linear_least_squares: singular / ill-conditioned system." )

		if pivot != col :
			M[col], M[pivot] = M[pivot], M[col]

		d = M[col][col]
		for j in range( col, n + 1 ) :
			M[col][j] /= d

		for r in range( n ) :
			if r == col :
				continue
			f = M[r][col]
			if f == 0.0 :
				continue
			for j in range( col, n + 1 ) :
				M[r][j] -= f * M[col][j]

	return [ M[i][n] for i in range( n ) ]


def rolling_kyle_lambda_proxy(
	retTimes : Sequence[int],
	retValues : Sequence[float],
	volTimes : Sequence[int],
	volValues : Sequence[float],
	window : int,
) -> float :
	"""
	Rolling **proxy** for Kyle's λ: last ``window`` bars of OLS ``r ~ 1 + s`` where
	``s_i = sign(r_{i-1}) · log(1 + dollar_volume_i)`` on **time-aligned** bars.

	Intended for ``KyleLambdaNode``. Returns ``0.0`` when
	the sample is too short or the normal equations are singular.
	"""

	if window < 3 :
		return 0.0

	vmap : Dict[int, float] = {}
	for t, v in zip( volTimes, volValues ) :
		vmap[int( t )] = float( v )

	aligned = []
	for t, r in zip( retTimes, retValues ) :
		t = int( t )
		if t in vmap :
			aligned.append( ( t, float( r ), vmap[t] ) )

	if len( aligned ) < window + 1 :
		return 0.0

	aligned.sort( key = lambda z : z[0] )

	xs = []
	ys = []
	for i in range( 1, len( aligned ) ) :
		rPrev = aligned[i - 1][1]
		rI = aligned[i][1]
		vI = aligned[i][2]
		sgn = 1.0 if rPrev >= 0.0 else -1.0
		sI = sgn * math.log1p( max( vI, 0.0 ) )
		xs.append( sI )
		ys.append( rI )

	if len( xs ) < window :
		return 0.0

	xs = xs[-window:]
	ys = ys[-window:]
	X = [ [ 1.0, x ] for x in xs ]

	try :
		beta = linear_least_squares( X, ys )
		return float( beta[1] )
	except ValueError :
		return 0.0


def _symmetric_matvec( C : List[List[float]], v : List[float] ) -> List[float] :

	p = len( v )
	return [ sum( C[i][j] * v[j] for j in range( p ) ) for i in range( p ) ]


def _symmetric_deflate( C : List[List[float]], lam : float, v : List[float] ) -> List[List[float]] :

	p = len( v )
	return [ [ C[i][j] - lam * v[i] * v[j] for j in range( p ) ] for i in range( p ) ]


def _top_eigenpair_power(
	C : List[List[float]],
	max_iter : int = 200,
	tol : float = 1e-9,
) -> tuple :
	"""Dominant eigenpair of symmetric ``C`` (power iteration)."""

	p = len( C )
	if p < 1 :
		return 0.0, []
	# Pick an axis-aligned start so we are not orthogonal to the top eigenspace: the uniform
	# vector ``[1,…,1]/√p`` can lie in the null space (e.g. covariance ``[[a,-a],[-a,a]]``).
	v = None
	for j in range( p ) :
		unitJ = [ 1.0 if i == j else 0.0 for i in range( p ) ]
		w0 = _symmetric_matvec( C, unitJ )
		n0 = math.sqrt( sum( x * x for x in w0 ) )
		if n0 >= 1e-18 :
			v = [ x / n0 for x in w0 ]
			break
	if v is None :
		return 0.0, [ 0.0 ] * p
	lam = 0.0
	for _ in range( max_iter ) :
		w = _symmetric_matvec( C, v )
		norm = math.sqrt( sum( x * x for x in w ) )
		if norm < 1e-18 :
			return 0.0, [ 0.0 ] * p
		w = [ x / norm for x in w ]
		if max( abs( w[i] - v[i] ) for i in range( p ) ) < tol :
			v = w
			mv = _symmetric_matvec( C, v )
			lam = sum( v[i] * mv[i] for i in range( p ) )
			return lam, v
		v = w
	mv = _symmetric_matvec( C, v )
	lam = sum( v[i] * mv[i] for i in range( p ) )
	return lam, v


def pca_top_components_covariance(
	cov : List[List[float]],
	num_components : int,
) -> tuple :
	"""
	Symmetric PSD ``cov`` (**p×p**). Returns ``(eigenvalues, eigenvectors)`` with
	``eigenvalues[k]`` descending (clamped ``>= 0``) and unit **eigenvectors[k]** (length **p**).
	Power iteration + symmetric deflation.
	"""

	p = len( cov )
	if p == 0 or num_components < 1 :
		return [], []
	k = min( num_components, p )
	C = [ row[:] for row in cov ]
	evals : List[float] = []
	evecs : List[List[float]] = []
	for _i in range( k ) :
		lam, v = _top_eigenpair_power( C )
		lam = max( float( lam ), 0.0 )
		evals.append( lam )
		evecs.append( v )
		if lam > 1e-18 :
			C = _symmetric_deflate( C, lam, v )
		else :
			break
	return evals, evecs


def panel_sample_covariance( rows : List[List[float]] ) -> List[List[float]] :
	"""``rows`` is **n×p** (demeaned manually before call **not** required — we demean here)."""

	n = len( rows )
	if n < 2 :
		return []
	p = len( rows[0] )
	if p < 1 :
		return []
	for row in rows :
		if len( row ) != p :
			return []
	mean = [ sum( float( rows[r][j] ) for r in range( n ) ) / n for j in range( p ) ]
	Xc = [ [ float( rows[r][j] ) - mean[j] for j in range( p ) ] for r in range( n ) ]
	div = float( n - 1 )
	cov = [ [ 0.0 ] * p for _ in range( p ) ]
	for i in range( p ) :
		for j in range( p ) :
			cov[i][j] = sum( Xc[r][i] * Xc[r][j] for r in range( n ) ) / div
	return cov
