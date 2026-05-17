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
import unittest

import IECore

import Gaffer
import GafferTest

from Gaffer.RealizedVolNode import _rollingSampleStdDev


class RealizedVolNodeTest( GafferTest.TestCase ) :

	def testTooFewSamples( self ) :

		n = Gaffer.RealizedVolNode()
		n["in"]["times"].setValue( IECore.Int64VectorData( [ 1, 2, 3 ] ) )
		n["in"]["values"].setValue( IECore.FloatVectorData( [ 0.01, 0.02, -0.01 ] ) )
		n["window"].setValue( 5 )

		self.assertFloat32Equal( n["out"].getValue(), 0.0 )

	def testConstantReturns( self ) :

		n = Gaffer.RealizedVolNode()
		n["in"]["times"].setValue( IECore.Int64VectorData( list( range( 10 ) ) ) )
		n["in"]["values"].setValue( IECore.FloatVectorData( [ 0.05 ] * 10 ) )
		n["window"].setValue( 4 )
		n["annualizationFactor"].setValue( 1.0 )

		self.assertFloat32Equal( n["out"].getValue(), 0.0 )

	def testKnownWindow( self ) :

		n = Gaffer.RealizedVolNode()
		# Last 3 returns; sample stdev of [0.1, -0.2, 0.1]
		n["in"]["times"].setValue( IECore.Int64VectorData( [ 1, 2, 3, 4, 5 ] ) )
		n["in"]["values"].setValue(
			IECore.FloatVectorData( [ 0.0, 0.0, 0.1, -0.2, 0.1 ] )
		)
		n["window"].setValue( 3 )
		n["annualizationFactor"].setValue( 1.0 )

		seg = [ 0.1, -0.2, 0.1 ]
		w = 3
		mean = sum( seg ) / w
		var = sum( ( x - mean ) ** 2 for x in seg ) / ( w - 1 )
		expected = math.sqrt( var )

		self.assertFloat32Equal( GafferTest.asFloat32( n["out"].getValue() ), GafferTest.asFloat32( expected ) )

	def testPipeline( self ) :

		src = Gaffer.Node()
		src.addChild(
			Gaffer.SeriesPlug(
				"prices",
				Gaffer.Plug.Direction.In,
				Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic,
			)
		)
		src["prices"]["times"].setValue( IECore.Int64VectorData( list( range( 6 ) ) ) )
		src["prices"]["values"].setValue(
			IECore.FloatVectorData( [ 100.0, 110.0, 121.0, 133.1, 146.41, 161.051 ] )
		)

		rr = Gaffer.RollingReturnsNode()
		rr["in"].setInput( src["prices"] )
		rr["window"].setValue( 1 )

		rv = Gaffer.RealizedVolNode()
		rv["in"].setInput( rr["out"] )
		rv["window"].setValue( 3 )
		rv["annualizationFactor"].setValue( 1.0 )

		self.assertGreater( rv["out"].getValue(), 0.0 )

	def testStdDevHelper( self ) :

		self.assertAlmostEqual( _rollingSampleStdDev( [ 1.0, -1.0 ] ), math.sqrt( 2.0 ) )
		self.assertAlmostEqual( _rollingSampleStdDev( [ 2.0, 2.0, 2.0 ] ), 0.0 )

	def testSerialisation( self ) :

		script = Gaffer.ScriptNode()
		script["rv"] = Gaffer.RealizedVolNode()
		script["rv"]["in"]["times"].setValue( IECore.Int64VectorData( [ 1, 2, 3, 4 ] ) )
		script["rv"]["in"]["values"].setValue( IECore.FloatVectorData( [ 0.0, 0.01, -0.02, 0.03 ] ) )
		script["rv"]["window"].setValue( 3 )
		script["rv"]["annualizationFactor"].setValue( 10.0 )

		v = script["rv"]["out"].getValue()

		script2 = Gaffer.ScriptNode()
		script2.execute( script.serialise() )

		self.assertEqual( script2["rv"]["window"].getValue(), 3 )
		self.assertFloat32Equal( script2["rv"]["annualizationFactor"].getValue(), 10.0 )
		self.assertFloat32Equal( script2["rv"]["out"].getValue(), v )


if __name__ == "__main__" :
	unittest.main()
