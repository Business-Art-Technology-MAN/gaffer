##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#      * Redistributions of source code must retain the above
#      copyright notice, this list of conditions and the following
#      disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided with
#      the distribution.
#
#      * Neither the name of John Haddon nor the names of
#      any other contributors to this software may be used to endorse or
#      promote products derived from this software without specific prior
#      written permission.
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

from typing import List, Optional, Tuple

import IECore

import Gaffer
from . import MarketDataTimeseries


def _last_sample_at_or_before(
	times : List[int],
	values : List[float],
	contextTime : Optional[object],
) -> Optional[float] :
	"""Latest observation with ``time <= contextTime``; if ``contextTime`` is None, last row overall."""

	pairs = sorted( zip( times, values ), key = lambda z : z[0] )
	if contextTime is not None :
		tlim = int( contextTime )
		pairs = [ p for p in pairs if p[0] <= tlim ]
	if not pairs :
		return None
	return float( pairs[-1][1] )


## Phase 3 macro regime from three **level** series (e.g. VIX, term spread, credit spread).
# Uses the latest sample at or before :data:`Gaffer.MarketDataTimeseries.PCE_TIME_CONTEXT_KEY`
# when set; otherwise the final sample in each series.
#
# Threshold semantics:
#
# * **vixThreshold** — stress if ``VIX >= threshold``.
# * **creditThreshold** — stress if ``credit_spread >= threshold``.
# * **termThreshold** — stress if ``term_spread <= threshold`` (flat/inverted curve proxy).
#
# If any series has no usable sample at the evaluation time, output is **ANY**. Otherwise let
# ``n`` be the count of stress flags among the three indicators:
#
# * ``n >= 2`` → **RISK_OFF**
# * ``n == 1`` → **TRANSITION**
# * ``n == 0`` → **RISK_ON**
class ThresholdRegimeNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "ThresholdRegime" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["vixSeries"] = Gaffer.SeriesPlug()
		self["termSpreadSeries"] = Gaffer.SeriesPlug()
		self["creditSpreadSeries"] = Gaffer.SeriesPlug()

		self["vixThreshold"] = Gaffer.FloatPlug( defaultValue = 25.0 )
		self["creditThreshold"] = Gaffer.FloatPlug( defaultValue = 5.0 )
		self["termThreshold"] = Gaffer.FloatPlug( defaultValue = 0.0 )

		self["out"] = Gaffer.RegimePlug( direction = Gaffer.Plug.Direction.Out )

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
			or series_affects( self["termSpreadSeries"] )
			or series_affects( self["creditSpreadSeries"] )
			or inputPlug.isSame( self["vixThreshold"] )
			or inputPlug.isSame( self["creditThreshold"] )
			or inputPlug.isSame( self["termThreshold"] )
		) :
			outputs.append( self["out"]["value"] )

		return outputs

	def hash( self, output, context, h ) :

		if output.isSame( self["out"]["value"] ) :
			for series in (
				self["vixSeries"],
				self["termSpreadSeries"],
				self["creditSpreadSeries"],
			) :
				series["times"].hash( h )
				series["values"].hash( h )
			self["vixThreshold"].hash( h )
			self["creditThreshold"].hash( h )
			self["termThreshold"].hash( h )

			if context is not None :
				ct = context.get( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, None )
				if ct is not None :
					h.append( int( ct ) )

	def compute( self, plug, context ) :

		if plug.isSame( self["out"]["value"] ) :

			ct = context.get( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, None ) if context is not None else None

			def pit_scalar( seriesPlug ) -> Optional[float] :

				times = list( seriesPlug["times"].getValue() )
				values = list( seriesPlug["values"].getValue() )
				if len( times ) != len( values ) or not times :
					return None
				return _last_sample_at_or_before( times, values, ct )

			vix = pit_scalar( self["vixSeries"] )
			term = pit_scalar( self["termSpreadSeries"] )
			credit = pit_scalar( self["creditSpreadSeries"] )

			if vix is None or term is None or credit is None :
				plug.setValue( "ANY" )
				return

			vixT = float( self["vixThreshold"].getValue() )
			creditT = float( self["creditThreshold"].getValue() )
			termT = float( self["termThreshold"].getValue() )

			flags = 0
			if vix >= vixT :
				flags += 1
			if credit >= creditT :
				flags += 1
			if term <= termT :
				flags += 1

			if flags >= 2 :
				plug.setValue( "RISK_OFF" )
			elif flags == 1 :
				plug.setValue( "TRANSITION" )
			else :
				plug.setValue( "RISK_ON" )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( ThresholdRegimeNode, typeName = "Gaffer::ThresholdRegimeNode" )
