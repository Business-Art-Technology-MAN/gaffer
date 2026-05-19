##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import IECore

import Gaffer

## Context string for **Hansen–Jagannathan**-style bound messages (Phase 4).
OTL_HJ_VIOLATION = "OTL_HJ_VIOLATION"


def _hj_message_text( alpha : float, confidence : float ) -> str :

	return (
		f"HJ bound violated: |alpha_weight|*confidence = {abs(alpha)*confidence:.6g} > 1.0"
	)


## Phase 4 **Track A** — pass-through **``SignalClosurePlug``** with **HJ bound** checking.
#
# If ``|alpha_weight| * confidence > 1.0``, emits **:data:`OTL_HJ_VIOLATION`** via
# ``IECore.msg`` (**Warning**); values are still copied to **signalOut** unchanged.
class HJBoundValidator( Gaffer.ComputeNode ) :

	def __init__( self, name = "HJBoundValidator" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["signalIn"] = Gaffer.SignalClosurePlug()
		self["signalOut"] = Gaffer.SignalClosurePlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )
		sp = self["signalIn"]
		if inputPlug.isSame( sp ) or (
			inputPlug.parent() is not None and inputPlug.parent().isSame( sp )
		) :
			for c in (
				"alphaWeight",
				"confidence",
				"halfLife",
				"maxImpactFrac",
				"regimeCondition",
				"sideBet",
			) :
				outputs.append( self["signalOut"][c] )
		return outputs

	def hash( self, output, context, h ) :

		if output.parent() is not None and output.parent().isSame( self["signalOut"] ) :
			self["signalIn"]["alphaWeight"].hash( h )
			self["signalIn"]["confidence"].hash( h )
			self["signalIn"]["halfLife"].hash( h )
			self["signalIn"]["maxImpactFrac"].hash( h )
			self["signalIn"]["regimeCondition"].hash( h )
			self["signalIn"]["sideBet"].hash( h )

	def compute( self, plug, context ) :

		parent = plug.parent()
		if parent is not None and parent.isSame( self["signalOut"] ) :

			alpha = float( self["signalIn"]["alphaWeight"].getValue() )
			conf = float( self["signalIn"]["confidence"].getValue() )

			if plug.isSame( self["signalOut"]["alphaWeight"] ) :
				if abs( alpha ) * conf > 1.0 :
					IECore.msg(
						IECore.MessageHandler.Level.Warning,
						OTL_HJ_VIOLATION,
						_hj_message_text( alpha, conf ),
					)
				plug.setValue( alpha )
			elif plug.isSame( self["signalOut"]["confidence"] ) :
				plug.setValue( conf )
			elif plug.isSame( self["signalOut"]["halfLife"] ) :
				plug.setValue( float( self["signalIn"]["halfLife"].getValue() ) )
			elif plug.isSame( self["signalOut"]["maxImpactFrac"] ) :
				plug.setValue( float( self["signalIn"]["maxImpactFrac"].getValue() ) )
			elif plug.isSame( self["signalOut"]["regimeCondition"] ) :
				plug.setValue( self["signalIn"]["regimeCondition"].getValue() )
			elif plug.isSame( self["signalOut"]["sideBet"] ) :
				plug.setValue( self["signalIn"]["sideBet"].getValue() )
			else :
				Gaffer.ComputeNode.compute( self, plug, context )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( HJBoundValidator, typeName = "Gaffer::HJBoundValidator" )
