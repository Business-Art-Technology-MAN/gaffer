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


## Log return series: `out[k] = log( in[k] / in[k-window] )` at `in`'s timestamps.
# Output length is `len(in) - window` (empty when the input is too short). Values must
# be strictly positive where used.
class RollingReturnsNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "RollingReturns" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["in"] = Gaffer.SeriesPlug()
		self["window"] = Gaffer.IntPlug( defaultValue = 1, minValue = 1 )

		self["out"] = Gaffer.SeriesPlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )

		if inputPlug.isSame( self["window"] ) or inputPlug.isSame( self["in"] ) :
			outputs.append( self["out"]["times"] )
			outputs.append( self["out"]["values"] )
		else :
			parent = inputPlug.parent()
			if parent and parent.isSame( self["in"] ) :
				outputs.append( self["out"]["times"] )
				outputs.append( self["out"]["values"] )

		return outputs

	def hash( self, output, context, h ) :

		if output.isSame( self["out"]["times"] ) or output.isSame( self["out"]["values"] ) :
			self["in"]["times"].hash( h )
			self["in"]["values"].hash( h )
			self["window"].hash( h )

	def compute( self, plug, context ) :

		if plug.isSame( self["out"]["times"] ) :

			timesIn = self["in"]["times"].getValue()
			valuesIn = self["in"]["values"].getValue()
			w = self["window"].getValue()
			n = min( len( timesIn ), len( valuesIn ) )
			outTimes = [ timesIn[i] for i in range( w, n ) ]
			plug.setValue( IECore.Int64VectorData( outTimes ) )

		elif plug.isSame( self["out"]["values"] ) :

			timesIn = self["in"]["times"].getValue()
			valuesIn = self["in"]["values"].getValue()
			w = self["window"].getValue()
			n = min( len( timesIn ), len( valuesIn ) )
			outVals = []
			for k in range( w, n ) :
				a = float( valuesIn[k] )
				b = float( valuesIn[k - w] )
				outVals.append( math.log( a / b ) )
			plug.setValue( IECore.FloatVectorData( outVals ) )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( RollingReturnsNode, typeName = "Gaffer::RollingReturnsNode" )
