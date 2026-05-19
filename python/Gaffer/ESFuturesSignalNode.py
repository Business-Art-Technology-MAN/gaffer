##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import IECore

import Gaffer


## Reference **ES futures** Layer 4 node: merges a base **``SignalClosurePlug``** (e.g. from
# :class:`SDFWeightNode` or :class:`OptionsSdfNode`) with **Kyle λ** and a **half-life** scalar
# (typically from :class:`AlphaHalflifeNode`).
#
# * ``alpha_weight`` is down-weighted as ``|λ|`` grows (liquidity / impact guardrail).
# * ``confidence`` is the **minimum** of the incoming confidence and a λ-based cap.
class ESFuturesSignalNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "ESFuturesSignal" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["baseSignal"] = Gaffer.SignalClosurePlug()
		self["kyleLambda"] = Gaffer.ScalarPlug()
		self["halfLifeSignal"] = Gaffer.ScalarPlug()
		self["lambdaScale"] = Gaffer.FloatPlug( defaultValue = 1.0, minValue = 0.0 )

		self["out"] = Gaffer.SignalClosurePlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )
		outc = (
			"alphaWeight",
			"confidence",
			"halfLife",
			"maxImpactFrac",
			"regimeCondition",
			"sideBet",
		)

		def sig_dep( sp ) :
			return inputPlug.isSame( sp ) or (
				inputPlug.parent() is not None and inputPlug.parent().isSame( sp )
			)

		if (
			sig_dep( self["baseSignal"] )
			or inputPlug.isSame( self["kyleLambda"] )
			or inputPlug.isSame( self["halfLifeSignal"] )
			or inputPlug.isSame( self["lambdaScale"] )
		) :
			for c in outc :
				outputs.append( self["out"][c] )

		return outputs

	def hash( self, output, context, h ) :

		if output.parent() is not None and output.parent().isSame( self["out"] ) :
			self["baseSignal"]["alphaWeight"].hash( h )
			self["baseSignal"]["confidence"].hash( h )
			self["baseSignal"]["halfLife"].hash( h )
			self["baseSignal"]["maxImpactFrac"].hash( h )
			self["baseSignal"]["regimeCondition"].hash( h )
			self["baseSignal"]["sideBet"].hash( h )
			self["kyleLambda"].hash( h )
			self["halfLifeSignal"].hash( h )
			self["lambdaScale"].hash( h )

	def compute( self, plug, context ) :

		parent = plug.parent()
		if parent is not None and parent.isSame( self["out"] ) :

			aw0 = float( self["baseSignal"]["alphaWeight"].getValue() )
			c0 = float( self["baseSignal"]["confidence"].getValue() )
			mif = float( self["baseSignal"]["maxImpactFrac"].getValue() )
			reg = self["baseSignal"]["regimeCondition"].getValue()
			sb = self["baseSignal"]["sideBet"].getValue()

			lam = float( self["kyleLambda"].getValue() )
			ls = float( self["lambdaScale"].getValue() )
			lamEff = abs( lam ) * ls
			aw = aw0 / ( 1.0 + lamEff )
			conf = min( c0, 1.0 / ( 1.0 + lamEff ) )

			hl = float( self["halfLifeSignal"].getValue() )

			if plug.isSame( self["out"]["alphaWeight"] ) :
				plug.setValue( aw )
			elif plug.isSame( self["out"]["confidence"] ) :
				plug.setValue( conf )
			elif plug.isSame( self["out"]["halfLife"] ) :
				plug.setValue( hl )
			elif plug.isSame( self["out"]["maxImpactFrac"] ) :
				plug.setValue( mif )
			elif plug.isSame( self["out"]["regimeCondition"] ) :
				plug.setValue( reg )
			elif plug.isSame( self["out"]["sideBet"] ) :
				plug.setValue( sb )
			else :
				Gaffer.ComputeNode.compute( self, plug, context )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( ESFuturesSignalNode, typeName = "Gaffer::ESFuturesSignalNode" )
