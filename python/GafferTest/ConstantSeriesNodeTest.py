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


class ConstantSeriesNodeTest( GafferTest.TestCase ) :

	@staticmethod
	def __floatVectorReadable32( floatVectorData ) :

		return [ GafferTest.asFloat32( floatVectorData[i] ) for i in range( len( floatVectorData ) ) ]

	def testCompute( self ) :

		n = Gaffer.ConstantSeriesNode()
		n["startTime"].setValue( 100 )
		n["step"].setValue( 10 )
		n["length"].setValue( 4 )
		n["constant"].setValue( 0.25 )

		self.assertEqual( n["out"]["times"].getValue(), IECore.Int64VectorData( [ 100, 110, 120, 130 ] ) )
		self.assertEqual(
			self.__floatVectorReadable32( n["out"]["values"].getValue() ),
			[ GafferTest.asFloat32( x ) for x in ( 0.25, 0.25, 0.25, 0.25 ) ],
		)

	def testEmptySeries( self ) :

		n = Gaffer.ConstantSeriesNode()
		n["length"].setValue( 0 )
		self.assertEqual( n["out"]["times"].getValue(), IECore.Int64VectorData( [] ) )
		self.assertEqual( len( n["out"]["values"].getValue() ), 0 )

	def testSerialisation( self ) :

		script = Gaffer.ScriptNode()
		script["n"] = Gaffer.ConstantSeriesNode()
		script["n"]["startTime"].setValue( 5 )
		script["n"]["step"].setValue( 2 )
		script["n"]["length"].setValue( 3 )
		script["n"]["constant"].setValue( 1.5 )

		script2 = Gaffer.ScriptNode()
		script2.execute( script.serialise() )

		self.assertEqual( script2["n"]["startTime"].getValue(), 5 )
		self.assertEqual( script2["n"]["step"].getValue(), 2 )
		self.assertEqual( script2["n"]["length"].getValue(), 3 )
		self.assertFloat32Equal( script2["n"]["constant"].getValue(), 1.5 )
		self.assertEqual( script2["n"]["out"]["times"].getValue(), IECore.Int64VectorData( [ 5, 7, 9 ] ) )
		self.assertEqual(
			self.__floatVectorReadable32( script2["n"]["out"]["values"].getValue() ),
			[ GafferTest.asFloat32( x ) for x in ( 1.5, 1.5, 1.5 ) ],
		)


if __name__ == "__main__" :
	unittest.main()
