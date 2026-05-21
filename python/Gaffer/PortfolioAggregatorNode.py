##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

from __future__ import annotations

from typing import List, Tuple

import IECore
import numpy as np

import Gaffer

from . import PortfolioOptimizerBackends as POpt
from .PortfolioConstrainer import (
	apply_min_confidence,
	cap_single_name,
	drawdown_gate_apply,
	enforce_gross_exposure,
	enforce_net_exposure,
	emit_exposure_violation,
)

## **IECore.msg** context when **`instrumentSignals`** layout is inconsistent (polish / PB-M2).
OTL_PORTFOLIO_INPUT = "OTL_PORTFOLIO_INPUT"


def _gather_signals( arrayPlug : Gaffer.ArraySignalPlug ) -> Tuple[List[str], List[float], List[float], List[float]] :

	ids = list( arrayPlug.instrumentIdsPlug().getValue() )
	sigRoot = arrayPlug.signalsPlug()

	alphas : List[float] = []
	confs : List[float] = []
	halfs : List[float] = []
	useIds : List[str] = []

	children = list( sigRoot.children() )
	for idx, el in enumerate( children ) :
		if not isinstance( el, Gaffer.SignalClosurePlug ) :
			continue
		alphas.append( float( el.alphaWeightPlug().getValue() ) )
		confs.append( float( el.confidencePlug().getValue() ) )
		halfs.append( float( el.halfLifePlug().getValue() ) )
		if idx < len( ids ) :
			useIds.append( str( ids[idx] ) )
		else :
			useIds.append( "inst{}".format( idx ) )

	return useIds, alphas, confs, halfs


def _emit_portfolio_input_warnings( arrayPlug : Gaffer.ArraySignalPlug, n_signals : int ) -> None :

	n_ids = len( list( arrayPlug.instrumentIdsPlug().getValue() ) )
	sigRoot = arrayPlug.signalsPlug()
	skipped = 0
	for el in sigRoot.children() :
		if not isinstance( el, Gaffer.SignalClosurePlug ) :
			skipped += 1
	if skipped > 0 :
		IECore.msg(
			IECore.MessageHandler.Level.Warning,
			OTL_PORTFOLIO_INPUT,
			"PortfolioAggregator: {} signal array slot(s) are not SignalClosurePlug; "
			"instrumentIds may not align with weights.".format( skipped ),
		)
	if n_ids > 0 and n_signals == 0 :
		IECore.msg(
			IECore.MessageHandler.Level.Warning,
			OTL_PORTFOLIO_INPUT,
			"PortfolioAggregator: instrumentIds length ({}) but no SignalClosurePlug inputs.".format( n_ids ),
		)
	elif n_signals > 0 and n_ids == 0 :
		IECore.msg(
			IECore.MessageHandler.Level.Warning,
			OTL_PORTFOLIO_INPUT,
			"PortfolioAggregator: {} SignalClosurePlug(s) but instrumentIds is empty.".format( n_signals ),
		)
	elif n_signals > 0 and n_ids != n_signals :
		IECore.msg(
			IECore.MessageHandler.Level.Warning,
			OTL_PORTFOLIO_INPUT,
			"PortfolioAggregator: instrumentIds length ({}) differs from SignalClosurePlug count ({}).".format(
				n_ids, n_signals
			),
		)


def _variances_from_plug( vp : Gaffer.VectorPlug, n : int ) -> np.ndarray :

	vals = list( vp.valuesPlug().getValue() )
	if len( vals ) < n :
		vals = list( vals ) + [ 1.0 ] * ( n - len( vals ) )
	v = np.array( [ float( vals[i] ) for i in range( n ) ], dtype = float )
	return np.maximum( v, 1e-18 )


## Phase 5 **Layer 5** — aggregate **ArraySignalPlug** into **WeightVectorPlug**.
class PortfolioAggregatorNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "PortfolioAggregator" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["instrumentSignals"] = Gaffer.ArraySignalPlug()
		self["assetVariances"] = Gaffer.VectorPlug()
		self["constructionMethod"] = Gaffer.StringPlug( defaultValue = "equal_weight" )
		self["maxGrossExposure"] = Gaffer.FloatPlug( defaultValue = 1.0, minValue = 0.0 )
		self["maxNetExposure"] = Gaffer.FloatPlug( defaultValue = 1.0, minValue = 0.0 )
		self["maxSingleName"] = Gaffer.FloatPlug( defaultValue = 0.6, minValue = 0.0 )
		self["minConfidence"] = Gaffer.FloatPlug( defaultValue = 0.0, minValue = 0.0, maxValue = 1.0 )
		self["drawdownLevel"] = Gaffer.FloatPlug( defaultValue = 0.0 )
		self["drawdownGate"] = Gaffer.FloatPlug( defaultValue = 1.0 )
		self["riskFreeRate"] = Gaffer.FloatPlug( defaultValue = 0.0 )
		self["activeRegimeFallback"] = Gaffer.StringPlug( defaultValue = "portfolio_aggregator" )
		self["out"] = Gaffer.WeightVectorPlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )

		outW = self["out"]
		if inputPlug.isSame( self["instrumentSignals"] ) or self["instrumentSignals"].isAncestorOf( inputPlug ) :
			for c in (
				"instrumentIds",
				"targetWeights",
				"confidences",
				"halfLives",
				"grossExposure",
				"netExposure",
				"activeRegime",
				"evaluatedAt",
			) :
				outputs.append( outW[c] )
			return outputs

		def vec_dep( vp : Gaffer.VectorPlug ) -> bool :

			return inputPlug.isSame( vp ) or (
				inputPlug.parent() is not None and inputPlug.parent().isSame( vp )
			)

		if (
			vec_dep( self["assetVariances"] )
			or inputPlug.isSame( self["constructionMethod"] )
			or inputPlug.isSame( self["maxGrossExposure"] )
			or inputPlug.isSame( self["maxNetExposure"] )
			or inputPlug.isSame( self["maxSingleName"] )
			or inputPlug.isSame( self["minConfidence"] )
			or inputPlug.isSame( self["drawdownLevel"] )
			or inputPlug.isSame( self["drawdownGate"] )
			or inputPlug.isSame( self["riskFreeRate"] )
			or inputPlug.isSame( self["activeRegimeFallback"] )
		) :
			for c in (
				"instrumentIds",
				"targetWeights",
				"confidences",
				"halfLives",
				"grossExposure",
				"netExposure",
				"activeRegime",
				"evaluatedAt",
			) :
				outputs.append( outW[c] )

		return outputs

	def hash( self, output, context, h ) :

		if output.parent() is not None and output.parent().isSame( self["out"] ) :
			self["instrumentSignals"]["instrumentIds"].hash( h )
			sigRoot = self["instrumentSignals"].signalsPlug()
			for ch in sigRoot.children() :
				if isinstance( ch, Gaffer.SignalClosurePlug ) :
					for nm in (
						"alphaWeight",
						"confidence",
						"halfLife",
						"maxImpactFrac",
						"regimeCondition",
						"sideBet",
					) :
						ch[nm].hash( h )
			self["assetVariances"].valuesPlug().hash( h )
			self["constructionMethod"].hash( h )
			self["maxGrossExposure"].hash( h )
			self["maxNetExposure"].hash( h )
			self["maxSingleName"].hash( h )
			self["minConfidence"].hash( h )
			self["drawdownLevel"].hash( h )
			self["drawdownGate"].hash( h )
			self["riskFreeRate"].hash( h )
			self["activeRegimeFallback"].hash( h )
		else :
			Gaffer.ComputeNode.hash( self, output, context, h )

	def compute( self, plug, context ) :

		parent = plug.parent()
		if parent is None or not parent.isSame( self["out"] ) :
			Gaffer.ComputeNode.compute( self, plug, context )
			return

		ids, alphas, confs, halfs = _gather_signals( self["instrumentSignals"] )
		n = len( alphas )

		if plug.isSame( self["out"]["targetWeights"] ) :
			_emit_portfolio_input_warnings( self["instrumentSignals"], n )

		emptyIds = IECore.StringVectorData()
		emptyF = IECore.FloatVectorData()

		if n == 0 :
			if plug.isSame( self["out"]["instrumentIds"] ) :
				plug.setValue( emptyIds )
			elif plug.isSame( self["out"]["targetWeights"] ) :
				plug.setValue( emptyF )
			elif plug.isSame( self["out"]["confidences"] ) :
				plug.setValue( emptyF )
			elif plug.isSame( self["out"]["halfLives"] ) :
				plug.setValue( emptyF )
			elif plug.isSame( self["out"]["grossExposure"] ) :
				plug.setValue( 0.0 )
			elif plug.isSame( self["out"]["netExposure"] ) :
				plug.setValue( 0.0 )
			elif plug.isSame( self["out"]["activeRegime"] ) :
				plug.setValue( self["activeRegimeFallback"].getValue() )
			elif plug.isSame( self["out"]["evaluatedAt"] ) :
				plug.setValue( "" )
			else :
				Gaffer.ComputeNode.compute( self, plug, context )
			return

		method = self["constructionMethod"].getValue().lower().strip().replace( "-", "_" )
		vars_ = _variances_from_plug( self["assetVariances"], n )
		cov = np.diag( vars_ )
		mu = np.array( alphas, dtype = float )

		if method in ( "equal_weight", "equal" ) :
			w = np.ones( n, dtype = float ) / n
		elif method in ( "alpha_proportional", "alpha", "signal" ) :
			raw = np.array( [ max( alphas[i] * confs[i], 0.0 ) for i in range( n ) ], dtype = float )
			s = float( np.sum( raw ) )
			w = ( raw / s ) if s >= 1e-18 else ( np.ones( n, dtype = float ) / n )
		elif method in ( "hrp", "inverse_vol", "inv_vol" ) :
			w = POpt.inverse_volatility_weights( cov )
		elif method in ( "max_sharpe", "tangency" ) :
			w = POpt.max_sharpe_weights_long_only( mu, cov, riskFree = self["riskFreeRate"].getValue() )
		elif method in ( "risk_parity", "erc", "equal_risk" ) :
			w = POpt.equal_risk_contribution_weights( cov )
		else :
			w = np.ones( n, dtype = float ) / n

		wList = [ float( x ) for x in w ]
		wList, _ = apply_min_confidence( wList, confs, self["minConfidence"].getValue() )
		wList, ddVi = drawdown_gate_apply(
			wList,
			drawdown = self["drawdownLevel"].getValue(),
			gate = self["drawdownGate"].getValue(),
		)
		wList, capVi = cap_single_name( wList, self["maxSingleName"].getValue() )
		wList, grVi = enforce_gross_exposure( wList, self["maxGrossExposure"].getValue() )
		wList, neVi = enforce_net_exposure( wList, self["maxNetExposure"].getValue() )

		if ddVi or capVi or grVi or neVi :
			emit_exposure_violation(
				"Portfolio constraint adjustment active "
				+ "(drawdown_gate=" + str( ddVi )
				+ ", single_name=" + str( capVi )
				+ ", gross=" + str( grVi )
				+ ", net=" + str( neVi )
				+ ")."
			)

		gross = float( sum( abs( x ) for x in wList ) )
		net = float( sum( wList ) )

		if plug.isSame( self["out"]["instrumentIds"] ) :
			plug.setValue( IECore.StringVectorData( ids ) )
		elif plug.isSame( self["out"]["targetWeights"] ) :
			plug.setValue( IECore.FloatVectorData( wList ) )
		elif plug.isSame( self["out"]["confidences"] ) :
			plug.setValue( IECore.FloatVectorData( [ float( c ) for c in confs ] ) )
		elif plug.isSame( self["out"]["halfLives"] ) :
			plug.setValue( IECore.FloatVectorData( [ float( h ) for h in halfs ] ) )
		elif plug.isSame( self["out"]["grossExposure"] ) :
			plug.setValue( gross )
		elif plug.isSame( self["out"]["netExposure"] ) :
			plug.setValue( net )
		elif plug.isSame( self["out"]["activeRegime"] ) :
			plug.setValue( self["activeRegimeFallback"].getValue() )
		elif plug.isSame( self["out"]["evaluatedAt"] ) :
			plug.setValue( "" )
		else :
			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( PortfolioAggregatorNode, typeName = "Gaffer::PortfolioAggregatorNode" )
