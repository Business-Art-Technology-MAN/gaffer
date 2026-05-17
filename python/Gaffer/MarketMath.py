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

from typing import List, Sequence


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
