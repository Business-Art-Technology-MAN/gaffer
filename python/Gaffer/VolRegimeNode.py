##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import IECore

import Gaffer

from . import MarketDataTimeseries
from .MarketRegimeAlgo import last_scalar_from_series_plug


## Phase 3 volatility regime: compares **realized vol** (annualised, same units as VIX points)
# to **VIX level** at the evaluation date.
#
# Let ``r = realizedVol / max(vix, eps)`` using samples at or before
# :data:`Gaffer.MarketDataTimeseries.PCE_TIME_CONTEXT_KEY` when set.
#
# * ``r >= highRatio`` → **VOL_HIGH**
# * ``r <= lowRatio`` → **VOL_LOW**
# * otherwise → **VOL_NORMAL**
#
# Missing data or non‑positive VIX → **ANY**.
class VolRegimeNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "VolRegime" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["vixSeries"] = Gaffer.SeriesPlug()
		self["realizedVolSeries"] = Gaffer.SeriesPlug()
		self["lowRatio"] = Gaffer.FloatPlug( defaultValue = 0.85, minValue = 1e-6 )
		self["highRatio"] = Gaffer.FloatPlug( defaultValue = 1.15, minValue = 1e-6 )

		self["out"] = Gaffer.VolRegimePlug( direction = Gaffer.Plug.Direction.Out )

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
			series_affects( self["vixSeries"] )
			or series_affects( self["realizedVolSeries"] )
			or inputPlug.isSame( self["lowRatio"] )
			or inputPlug.isSame( self["highRatio"] )
		) :
			outputs.append( self["out"]["value"] )

		return outputs

	def hash( self, output, context, h ) :

		if output.isSame( self["out"]["value"] ) :
			self["vixSeries"]["times"].hash( h )
			self["vixSeries"]["values"].hash( h )
			self["realizedVolSeries"]["times"].hash( h )
			self["realizedVolSeries"]["values"].hash( h )
			self["lowRatio"].hash( h )
			self["highRatio"].hash( h )

			if context is not None :
				ct = context.get( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, None )
				if ct is not None :
					h.append( int( ct ) )

	def compute( self, plug, context ) :

		if plug.isSame( self["out"]["value"] ) :

			ct = context.get( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, None ) if context is not None else None
			vix = last_scalar_from_series_plug( self["vixSeries"], ct )
			rv = last_scalar_from_series_plug( self["realizedVolSeries"], ct )

			if vix is None or rv is None or vix <= 1e-6 :
				plug.setValue( "ANY" )
				return

			ratio = rv / vix
			low = float( self["lowRatio"].getValue() )
			high = float( self["highRatio"].getValue() )

			if ratio >= high :
				plug.setValue( "VOL_HIGH" )
			elif ratio <= low :
				plug.setValue( "VOL_LOW" )
			else :
				plug.setValue( "VOL_NORMAL" )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( VolRegimeNode, typeName = "Gaffer::VolRegimeNode" )
