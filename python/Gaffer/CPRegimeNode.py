##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import IECore

import Gaffer

from . import MarketDataTimeseries
from .MarketRegimeAlgo import last_scalar_from_series_plug


## Simplified **Cochrane–Piazzesi-style** macro cue using two **yield or forward** series
# (short and long maturity) wired from Phase 2 stores or CSV nodes.
#
# ``cp_value = long − short`` using the latest observation at or before
# :data:`Gaffer.MarketDataTimeseries.PCE_TIME_CONTEXT_KEY`.
#
# Regime vs ``transitionBand`` on **cp_value**:
#
# * ``|cp_value| < transitionBand`` → **TRANSITION**
# * ``cp_value >= transitionBand`` → **RISK_ON**
# * ``cp_value <= -transitionBand`` → **RISK_OFF**
#
# Missing inputs → regime **ANY** and ``cp_value`` ``0.0``.
class CPRegimeNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "CPRegime" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["shortFwdSeries"] = Gaffer.SeriesPlug()
		self["longFwdSeries"] = Gaffer.SeriesPlug()
		self["transitionBand"] = Gaffer.FloatPlug( defaultValue = 0.25, minValue = 0.0 )

		self["regimeOut"] = Gaffer.RegimePlug( direction = Gaffer.Plug.Direction.Out )
		self["cpValue"] = Gaffer.ScalarPlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )

		def series_affects( seriesPlug ) :

			return (
				inputPlug.isSame( seriesPlug )
				or (
					inputPlug.parent() is not None
					and inputPlug.parent().isSame( seriesPlug )
				)
			)

		if (
			series_affects( self["shortFwdSeries"] )
			or series_affects( self["longFwdSeries"] )
			or inputPlug.isSame( self["transitionBand"] )
		) :
			outputs.append( self["regimeOut"]["value"] )
			outputs.append( self["cpValue"] )

		return outputs

	def hash( self, output, context, h ) :

		if output.isSame( self["regimeOut"]["value"] ) or output.isSame( self["cpValue"] ) :
			self["shortFwdSeries"]["times"].hash( h )
			self["shortFwdSeries"]["values"].hash( h )
			self["longFwdSeries"]["times"].hash( h )
			self["longFwdSeries"]["values"].hash( h )
			self["transitionBand"].hash( h )

			if context is not None :
				ct = context.get( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, None )
				if ct is not None :
					h.append( int( ct ) )

	def compute( self, plug, context ) :

		if plug.isSame( self["regimeOut"]["value"] ) or plug.isSame( self["cpValue"] ) :

			ct = context.get( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, None ) if context is not None else None
			yS = last_scalar_from_series_plug( self["shortFwdSeries"], ct )
			yL = last_scalar_from_series_plug( self["longFwdSeries"], ct )

			band = float( self["transitionBand"].getValue() )

			if yS is None or yL is None :
				if plug.isSame( self["regimeOut"]["value"] ) :
					plug.setValue( "ANY" )
				else :
					plug.setValue( 0.0 )
				return

			cp = float( yL ) - float( yS )

			if plug.isSame( self["cpValue"] ) :
				plug.setValue( cp )
				return

			if band <= 0.0 :
				if cp > 0.0 :
					plug.setValue( "RISK_ON" )
				elif cp < 0.0 :
					plug.setValue( "RISK_OFF" )
				else :
					plug.setValue( "TRANSITION" )
				return

			if abs( cp ) < band :
				plug.setValue( "TRANSITION" )
			elif cp >= band :
				plug.setValue( "RISK_ON" )
			else :
				plug.setValue( "RISK_OFF" )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( CPRegimeNode, typeName = "Gaffer::CPRegimeNode" )
