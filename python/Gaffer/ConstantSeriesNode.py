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

import IECore

import Gaffer


## Generates a `SeriesPlug` with evenly spaced int64 `times` and a float `values`
# vector filled with a constant (Phase 2a milestone 1 — no external store).
class ConstantSeriesNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "ConstantSeries" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["startTime"] = Gaffer.IntPlug( defaultValue = 0 )
		self["step"] = Gaffer.IntPlug( defaultValue = 1 )
		self["length"] = Gaffer.IntPlug( defaultValue = 3, minValue = 0 )
		self["constant"] = Gaffer.FloatPlug( defaultValue = 1.0 )

		self["out"] = Gaffer.SeriesPlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )
		if inputPlug.isSame( self["startTime"] ) or inputPlug.isSame( self["step"] ) or inputPlug.isSame( self["length"] ) or inputPlug.isSame( self["constant"] ) :
			outputs.append( self["out"]["times"] )
			outputs.append( self["out"]["values"] )

		return outputs

	def hash( self, output, context, h ) :

		if output.isSame( self["out"]["times"] ) or output.isSame( self["out"]["values"] ) :
			self["startTime"].hash( h )
			self["step"].hash( h )
			self["length"].hash( h )
			self["constant"].hash( h )

	def compute( self, plug, context ) :

		if plug.isSame( self["out"]["times"] ) :
			start = self["startTime"].getValue()
			step = self["step"].getValue()
			n = self["length"].getValue()
			times = [ start + i * step for i in range( n ) ]
			plug.setValue( IECore.Int64VectorData( times ) )
		elif plug.isSame( self["out"]["values"] ) :
			n = self["length"].getValue()
			v = float( self["constant"].getValue() )
			plug.setValue( IECore.FloatVectorData( [ v ] * n ) )
		else :
			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( ConstantSeriesNode, typeName = "Gaffer::ConstantSeriesNode" )
