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


class RollingReturnsNodeTest( GafferTest.TestCase ) :

	@staticmethod
	def __floatVectorReadable32( floatVectorData ) :

		return [ GafferTest.asFloat32( floatVectorData[i] ) for i in range( len( floatVectorData ) ) ]

	def testWindow1( self ) :

		n = Gaffer.RollingReturnsNode()
		n["in"]["times"].setValue( IECore.Int64VectorData( [ 10, 20, 30, 40 ] ) )
		n["in"]["values"].setValue( IECore.FloatVectorData( [ 100.0, 110.0, 121.0, 133.1 ] ) )
		n["window"].setValue( 1 )

		self.assertEqual( n["out"]["times"].getValue(), IECore.Int64VectorData( [ 20, 30, 40 ] ) )

		# Expectations must use the same float round-trip as `RollingReturnsNode.compute` (vector storage).
		v = n["in"]["values"].getValue()
		expected = [ math.log( float( v[k] ) / float( v[k - 1] ) ) for k in range( 1, len( v ) ) ]
		out = n["out"]["values"].getValue()
		self.assertEqual( len( out ), 3 )
		for i in range( 3 ) :
			self.assertFloat32Equal( GafferTest.asFloat32( out[i] ), GafferTest.asFloat32( expected[i] ) )

	def testWindow2( self ) :

		n = Gaffer.RollingReturnsNode()
		n["in"]["times"].setValue( IECore.Int64VectorData( [ 1, 2, 3, 4 ] ) )
		n["in"]["values"].setValue( IECore.FloatVectorData( [ 1.0, 2.0, 4.0, 8.0 ] ) )
		n["window"].setValue( 2 )

		self.assertEqual( n["out"]["times"].getValue(), IECore.Int64VectorData( [ 3, 4 ] ) )
		r = math.log( 4.0 / 1.0 )
		self.assertFloat32Equal( GafferTest.asFloat32( n["out"]["values"].getValue()[0] ), GafferTest.asFloat32( r ) )
		self.assertFloat32Equal( GafferTest.asFloat32( n["out"]["values"].getValue()[1] ), GafferTest.asFloat32( r ) )

	def testTooShort( self ) :

		n = Gaffer.RollingReturnsNode()
		n["in"]["times"].setValue( IECore.Int64VectorData( [ 1, 2 ] ) )
		n["in"]["values"].setValue( IECore.FloatVectorData( [ 1.0, 2.0 ] ) )
		n["window"].setValue( 2 )

		self.assertEqual( len( n["out"]["times"].getValue() ), 0 )
		self.assertEqual( len( n["out"]["values"].getValue() ), 0 )

	def testWireFromConstantSeries( self ) :

		c = Gaffer.ConstantSeriesNode()
		c["startTime"].setValue( 0 )
		c["step"].setValue( 1 )
		c["length"].setValue( 4 )
		c["constant"].setValue( 100.0 )

		r = Gaffer.RollingReturnsNode()
		r["in"].setInput( c["out"] )
		r["window"].setValue( 1 )

		self.assertEqual( r["out"]["times"].getValue(), IECore.Int64VectorData( [ 1, 2, 3 ] ) )
		for i in range( 3 ) :
			self.assertFloat32Equal( GafferTest.asFloat32( r["out"]["values"].getValue()[i] ), GafferTest.asFloat32( 0.0 ) )

	def testSerialisation( self ) :

		script = Gaffer.ScriptNode()
		script["c"] = Gaffer.ConstantSeriesNode()
		script["c"]["length"].setValue( 5 )
		script["c"]["constant"].setValue( 2.0 )
		script["c"]["startTime"].setValue( 100 )
		script["r"] = Gaffer.RollingReturnsNode()
		script["r"]["in"].setInput( script["c"]["out"] )
		script["r"]["window"].setValue( 2 )

		script2 = Gaffer.ScriptNode()
		script2.execute( script.serialise() )

		self.assertEqual( script2["r"]["window"].getValue(), 2 )
		self.assertEqual( script2["r"]["out"]["times"].getValue(), IECore.Int64VectorData( [ 102, 103, 104 ] ) )
		z = GafferTest.asFloat32( math.log( 2.0 / 2.0 ) )
		for i in range( 3 ) :
			self.assertFloat32Equal( GafferTest.asFloat32( script2["r"]["out"]["values"].getValue()[i] ), z )


if __name__ == "__main__" :
	unittest.main()
