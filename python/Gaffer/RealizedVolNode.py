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

import math

import IECore

import Gaffer


def _rollingSampleStdDev( valuesSegment ) :

	# `valuesSegment` length >= 2; sample stdev with ddof=1 (Bessel).
	w = len( valuesSegment )
	if w < 2 :
		return 0.0
	mean = sum( valuesSegment ) / w
	var = sum( ( x - mean ) ** 2 for x in valuesSegment ) / ( w - 1 )
	return math.sqrt( max( var, 0.0 ) )


## Annualized realized volatility from the trailing window of a **return** series.
# Uses the last `window` samples of `in.values`, sample standard deviation, times
# `annualizationFactor` (e.g. ``sqrt(252)`` for daily returns). Output is a single
# :class:`FloatPlug` (Phase 2 `ScalarPlug` not implemented yet). If there are fewer
# than `window` samples (or `window` < 2), **out** is ``0.0``.
class RealizedVolNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "RealizedVol" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["in"] = Gaffer.SeriesPlug()
		self["window"] = Gaffer.IntPlug( defaultValue = 20, minValue = 2 )
		self["annualizationFactor"] = Gaffer.FloatPlug( defaultValue = math.sqrt( 252.0 ) )

		self["out"] = Gaffer.FloatPlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )

		if (
			inputPlug.isSame( self["window"] )
			or inputPlug.isSame( self["annualizationFactor"] )
			or inputPlug.isSame( self["in"] )
		) :
			outputs.append( self["out"] )
		else :
			parent = inputPlug.parent()
			if parent and parent.isSame( self["in"] ) :
				outputs.append( self["out"] )

		return outputs

	def hash( self, output, context, h ) :

		if output.isSame( self["out"] ) :
			self["in"]["times"].hash( h )
			self["in"]["values"].hash( h )
			self["window"].hash( h )
			self["annualizationFactor"].hash( h )

	def compute( self, plug, context ) :

		if plug.isSame( self["out"] ) :

			valuesIn = self["in"]["values"].getValue()
			w = self["window"].getValue()
			n = len( valuesIn )

			if n < w or w < 2 :
				plug.setValue( 0.0 )
				return

			segment = [ float( valuesIn[i] ) for i in range( n - w, n ) ]
			ann = float( self["annualizationFactor"].getValue() )
			plug.setValue( float( _rollingSampleStdDev( segment ) * ann ) )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( RealizedVolNode, typeName = "Gaffer::RealizedVolNode" )
