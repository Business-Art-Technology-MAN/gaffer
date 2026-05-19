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

import unittest

import IECore

import Gaffer
import GafferTest
from Gaffer import MarketMath


class KyleLambdaNodeTest( GafferTest.TestCase ) :

	def testTooFewAlignedBars( self ) :

		n = Gaffer.KyleLambdaNode()
		n["returns"]["times"].setValue( IECore.Int64VectorData( [ 1, 2 ] ) )
		n["returns"]["values"].setValue( IECore.FloatVectorData( [ 0.0, 0.01 ] ) )
		n["dollarVolume"]["times"].setValue( IECore.Int64VectorData( [ 1, 2 ] ) )
		n["dollarVolume"]["values"].setValue( IECore.FloatVectorData( [ 1.0, 1.0 ] ) )
		n["window"].setValue( 5 )

		self.assertFloat32Equal( n["out"].getValue(), 0.0 )

	def testWindowPlugMinimumClamps( self ) :

		# ``window`` has ``minValue == 3`` (below that the math returns 0.0 but the plug
		# rejects sub-minimum values, matching other market nodes).
		n = Gaffer.KyleLambdaNode()
		n["window"].setValue( 2 )
		self.assertEqual( n["window"].getValue(), 3 )

	def testMatchesMarketMath( self ) :

		rt = [ 0, 1, 2, 3 ]
		rv = [ 0.0, 0.1, -0.05, 0.02 ]
		vt = [ 0, 1, 2, 3 ]
		vv = [ 1.0, 1.0, 1.0, 1.0 ]
		w = 3

		n = Gaffer.KyleLambdaNode()
		n["returns"]["times"].setValue( IECore.Int64VectorData( rt ) )
		n["returns"]["values"].setValue( IECore.FloatVectorData( rv ) )
		n["dollarVolume"]["times"].setValue( IECore.Int64VectorData( vt ) )
		n["dollarVolume"]["values"].setValue( IECore.FloatVectorData( vv ) )
		n["window"].setValue( w )

		# Use the same float round-trip as ``compute`` (``FloatVectorData`` is float32).
		rt2 = list( n["returns"]["times"].getValue() )
		rv2 = list( n["returns"]["values"].getValue() )
		vt2 = list( n["dollarVolume"]["times"].getValue() )
		vv2 = list( n["dollarVolume"]["values"].getValue() )
		expected = MarketMath.rolling_kyle_lambda_proxy( rt2, rv2, vt2, vv2, w )

		self.assertFloat32Equal( n["out"].getValue(), expected )

	def testSerialisation( self ) :

		script = Gaffer.ScriptNode()
		script["kl"] = Gaffer.KyleLambdaNode()
		script["kl"]["returns"]["times"].setValue( IECore.Int64VectorData( [ 0, 1, 2, 3 ] ) )
		script["kl"]["returns"]["values"].setValue(
			IECore.FloatVectorData( [ 0.0, 0.1, -0.05, 0.02 ] )
		)
		script["kl"]["dollarVolume"]["times"].setValue( IECore.Int64VectorData( [ 0, 1, 2, 3 ] ) )
		script["kl"]["dollarVolume"]["values"].setValue( IECore.FloatVectorData( [ 1.0 ] * 4 ) )
		script["kl"]["window"].setValue( 3 )

		v = script["kl"]["out"].getValue()

		script2 = Gaffer.ScriptNode()
		script2.execute( script.serialise() )

		self.assertEqual( script2["kl"]["window"].getValue(), 3 )
		self.assertFloat32Equal( script2["kl"]["out"].getValue(), v )


if __name__ == "__main__" :
	unittest.main()
