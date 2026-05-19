##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import IECore

import Gaffer

from .SignalNodeAlgo import iv_skew_alpha


def _surface_first_expiry_ivs( surf : Gaffer.SurfacePlug ) -> tuple :

	strikes = [ float( x ) for x in surf["strikes"].getValue() ]
	expiries = [ float( x ) for x in surf["expiries"].getValue() ]
	ivs = [ float( x ) for x in surf["ivsRowMajor"].getValue() ]
	ns = len( strikes )
	ne = len( expiries )
	if ns < 1 or ne < 1 or len( ivs ) != ns * ne :
		return [], []
	col0 = [ ivs[i * ne] for i in range( ns ) ]
	return strikes, col0


## Phase 4 **Track A** — options **SDF tilt** from an IV **``SurfacePlug``** and **``VolRegimePlug``**.
#
# Uses a simple **skew** measure (OTM put vs call IV on the **first** expiry). When **vol_regime**
# is **VOL_HIGH**, applies **``uShapeGain``** (U-shape emphasis) with clipping to ``[-1, 1]``.
class OptionsSdfNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "OptionsSdf" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["ivSurface"] = Gaffer.SurfacePlug()
		self["volRegime"] = Gaffer.VolRegimePlug()

		self["uShapeGain"] = Gaffer.FloatPlug( defaultValue = 1.15, minValue = 1.0 )
		self["baseConfidence"] = Gaffer.FloatPlug( defaultValue = 0.75, minValue = 1e-6 )
		self["halfLife"] = Gaffer.FloatPlug( defaultValue = 10.0, minValue = 1e-6 )
		self["maxImpactFrac"] = Gaffer.FloatPlug( defaultValue = 0.05, minValue = 0.0 )
		self["sideBet"] = Gaffer.BoolPlug( defaultValue = False )

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

		def surf_dep() :
			s = self["ivSurface"]
			return inputPlug.isSame( s ) or (
				inputPlug.parent() is not None and inputPlug.parent().isSame( s )
			)

		def vol_dep() :
			v = self["volRegime"]
			return inputPlug.isSame( v ) or (
				inputPlug.parent() is not None and inputPlug.parent().isSame( v )
			)

		if (
			surf_dep()
			or vol_dep()
			or inputPlug.isSame( self["uShapeGain"] )
			or inputPlug.isSame( self["baseConfidence"] )
			or inputPlug.isSame( self["halfLife"] )
			or inputPlug.isSame( self["maxImpactFrac"] )
			or inputPlug.isSame( self["sideBet"] )
		) :
			for c in outc :
				outputs.append( self["out"][c] )

		return outputs

	def hash( self, output, context, h ) :

		if output.parent() is not None and output.parent().isSame( self["out"] ) :
			self["ivSurface"]["asOfTime"].hash( h )
			self["ivSurface"]["strikes"].hash( h )
			self["ivSurface"]["expiries"].hash( h )
			self["ivSurface"]["ivsRowMajor"].hash( h )
			self["volRegime"]["value"].hash( h )
			self["uShapeGain"].hash( h )
			self["baseConfidence"].hash( h )
			self["halfLife"].hash( h )
			self["maxImpactFrac"].hash( h )
			self["sideBet"].hash( h )

	def compute( self, plug, context ) :

		parent = plug.parent()
		if parent is not None and parent.isSame( self["out"] ) :

			strikes, col0 = _surface_first_expiry_ivs( self["ivSurface"] )
			reg = self["volRegime"]["value"].getValue()
			alpha = iv_skew_alpha( strikes, col0 ) if strikes and col0 else 0.0

			if reg == "VOL_HIGH" :
				alpha *= float( self["uShapeGain"].getValue() )
				alpha = max( min( alpha, 1.0 ), -1.0 )

			if plug.isSame( self["out"]["alphaWeight"] ) :
				plug.setValue( float( alpha ) )
			elif plug.isSame( self["out"]["confidence"] ) :
				plug.setValue( float( self["baseConfidence"].getValue() ) )
			elif plug.isSame( self["out"]["halfLife"] ) :
				plug.setValue( float( self["halfLife"].getValue() ) )
			elif plug.isSame( self["out"]["maxImpactFrac"] ) :
				plug.setValue( float( self["maxImpactFrac"].getValue() ) )
			elif plug.isSame( self["out"]["regimeCondition"] ) :
				plug.setValue( str( reg ) )
			elif plug.isSame( self["out"]["sideBet"] ) :
				plug.setValue( self["sideBet"].getValue() )
			else :
				Gaffer.ComputeNode.compute( self, plug, context )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( OptionsSdfNode, typeName = "Gaffer::OptionsSdfNode" )
