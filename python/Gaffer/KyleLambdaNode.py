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
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
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

import IECore

import Gaffer

from . import MarketMath


## Rolling Kyle-λ **proxy** from aligned return + dollar-volume :class:`SeriesPlug` inputs.
# See :func:`~Gaffer.MarketMath.rolling_kyle_lambda_proxy`. Output is a :class:`ScalarPlug`.
class KyleLambdaNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "KyleLambda" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["returns"] = Gaffer.SeriesPlug()
		self["dollarVolume"] = Gaffer.SeriesPlug()
		self["window"] = Gaffer.IntPlug( defaultValue = 20, minValue = 3 )

		self["out"] = Gaffer.ScalarPlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )

		if inputPlug.isSame( self["window"] ) :
			outputs.append( self["out"] )
		else :
			for seriesName in ( "returns", "dollarVolume" ) :
				s = self[seriesName]
				if inputPlug.isSame( s ) :
					outputs.append( self["out"] )
				else :
					parent = inputPlug.parent()
					if parent and parent.isSame( s ) :
						outputs.append( self["out"] )

		return outputs

	def hash( self, output, context, h ) :

		if output.isSame( self["out"] ) :
			self["returns"]["times"].hash( h )
			self["returns"]["values"].hash( h )
			self["dollarVolume"]["times"].hash( h )
			self["dollarVolume"]["values"].hash( h )
			self["window"].hash( h )

	def compute( self, plug, context ) :

		if plug.isSame( self["out"] ) :

			rt = list( self["returns"]["times"].getValue() )
			rv = list( self["returns"]["values"].getValue() )
			vt = list( self["dollarVolume"]["times"].getValue() )
			vv = list( self["dollarVolume"]["values"].getValue() )
			w = self["window"].getValue()

			lam = MarketMath.rolling_kyle_lambda_proxy( rt, rv, vt, vv, w )
			plug.setValue( lam )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( KyleLambdaNode, typeName = "Gaffer::KyleLambdaNode" )
