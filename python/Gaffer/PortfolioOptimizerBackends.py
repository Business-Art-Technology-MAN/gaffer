##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

"""
Portfolio construction helpers that may use **PyPortfolioOpt** when installed.

**v0.1** provides **numpy** fallbacks so Phase 5 runs without extra **pip** packages.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING :
	pass


def inverse_volatility_weights( cov : np.ndarray ) -> np.ndarray :

	## Stand-in for full **HRP** when only a covariance (or variances) is available.
	v = np.sqrt( np.maximum( np.diag( cov ), 1e-18 ) )
	iv = 1.0 / v
	return iv / np.sum( iv )


def max_sharpe_weights_long_only( mu : np.ndarray, cov : np.ndarray, *, riskFree : float = 0.0 ) -> np.ndarray :

	m = np.asarray( mu, dtype = float ).reshape( -1 )
	c = np.asarray( cov, dtype = float )
	n = m.size
	if c.shape != ( n, n ) :
		raise ValueError( "mu and cov shape mismatch" )

	try :
		from pypfopt.efficient_frontier import EfficientFrontier

		ef = EfficientFrontier( m.tolist(), c.tolist() )
		w = ef.max_sharpe( risk_free_rate = float( riskFree ) )
		ef.clean_weights()
		return np.array( [ w[i] for i in sorted( w.keys() ) ], dtype = float )
	except ImportError :
		pass

	excess = m - float( riskFree )
	inv = np.linalg.pinv( c )
	w = inv @ excess
	w = np.maximum( w, 0.0 )
	s = float( np.sum( w ) )
	if s < 1e-18 :
		return np.ones( n, dtype = float ) / max( n, 1 )
	return w / s


def equal_risk_contribution_weights( cov : np.ndarray, *, iterations : int = 50 ) -> np.ndarray :

	## Simple iterative **ERC** on covariance (no **riskfolio** requirement).
	c = np.asarray( cov, dtype = float )
	n = c.shape[0]
	if c.shape != ( n, n ) :
		raise ValueError( "cov must be square" )
	w = np.ones( n, dtype = float ) / n
	for _ in range( int( iterations ) ) :
		mrc = c @ w
		rc = w * mrc
		target = np.sum( rc ) / n
		adj = np.maximum( rc, 1e-18 )
		w = w * ( target / adj )
		w = w / np.sum( w )
	return w
