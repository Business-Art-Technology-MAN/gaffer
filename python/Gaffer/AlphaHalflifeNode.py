##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import IECore

import Gaffer


## Phase 4 support node: publishes **signal half-life** (bars or days) as a :class:`Gaffer.ScalarPlug`
# for wiring into :class:`ESFuturesSignalNode` / :class:`SignalClosurePlug` pipelines.
#
# v1 is a typed **constant**; later extensions may ingest series or estimator nodes.
class AlphaHalflifeNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "AlphaHalflife" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["halfLife"] = Gaffer.FloatPlug( defaultValue = 21.0, minValue = 1e-6 )
		self["out"] = Gaffer.ScalarPlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )
		if inputPlug.isSame( self["halfLife"] ) :
			outputs.append( self["out"] )
		return outputs

	def hash( self, output, context, h ) :

		if output.isSame( self["out"] ) :
			self["halfLife"].hash( h )

	def compute( self, plug, context ) :

		if plug.isSame( self["out"] ) :
			plug.setValue( float( self["halfLife"].getValue() ) )
		else :
			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( AlphaHalflifeNode, typeName = "Gaffer::AlphaHalflifeNode" )
