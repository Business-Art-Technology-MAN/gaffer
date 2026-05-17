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
import os
import tempfile
import unittest

import IECore

import Gaffer
import GafferTest


class SeriesCsvReaderNodeTest( GafferTest.TestCase ) :

	@staticmethod
	def __floatValues( floatVectorData ) :

		return [ GafferTest.asFloat32( floatVectorData[i] ) for i in range( len( floatVectorData ) ) ]

	def testMissingFile( self ) :

		n = Gaffer.SeriesCsvReaderNode()
		n["filePath"].setValue( "" )
		self.assertEqual( len( n["out"]["times"].getValue() ), 0 )
		self.assertEqual( len( n["out"]["values"].getValue() ), 0 )

	def testReadsCsv( self ) :

		fd, path = tempfile.mkstemp( suffix = ".csv" )
		try :
			with os.fdopen( fd, "w", encoding = "utf-8" ) as f :
				f.write( "t,v\n0,100.0\n10,110.0\n20,121.0\n" )

			n = Gaffer.SeriesCsvReaderNode()
			n["filePath"].setValue( path )

			self.assertEqual( n["out"]["times"].getValue(), IECore.Int64VectorData( [ 0, 10, 20 ] ) )
			self.assertEqual(
				self.__floatValues( n["out"]["values"].getValue() ),
				[ GafferTest.asFloat32( x ) for x in ( 100.0, 110.0, 121.0 ) ],
			)
		finally :
			os.remove( path )

	def testTabDelimiter( self ) :

		fd, path = tempfile.mkstemp( suffix = ".csv" )
		try :
			with os.fdopen( fd, "w", encoding = "utf-8" ) as f :
				f.write( "a\tb\n0\t1.5\n2\t2.5\n" )

			n = Gaffer.SeriesCsvReaderNode()
			n["filePath"].setValue( path )
			n["delimiter"].setValue( "\t" )
			n["timeColumn"].setValue( 0 )
			n["valueColumn"].setValue( 1 )
			n["hasHeader"].setValue( True )

			self.assertEqual( n["out"]["times"].getValue(), IECore.Int64VectorData( [ 0, 2 ] ) )
			self.assertEqual(
				self.__floatValues( n["out"]["values"].getValue() ),
				[ GafferTest.asFloat32( x ) for x in ( 1.5, 2.5 ) ],
			)
		finally :
			os.remove( path )

	def testPipelineToRollingReturns( self ) :

		fd, path = tempfile.mkstemp( suffix = ".csv" )
		try :
			with os.fdopen( fd, "w", encoding = "utf-8" ) as f :
				f.write( "time,px\n0,100.0\n1,110.0\n2,121.0\n" )

			reader = Gaffer.SeriesCsvReaderNode()
			reader["filePath"].setValue( path )

			rr = Gaffer.RollingReturnsNode()
			rr["in"].setInput( reader["out"] )
			rr["window"].setValue( 1 )

			r1 = math.log( 110.0 / 100.0 )
			r2 = math.log( 121.0 / 110.0 )
			self.assertEqual(
				self.__floatValues( rr["out"]["values"].getValue() ),
				[ GafferTest.asFloat32( x ) for x in ( r1, r2 ) ],
			)
		finally :
			os.remove( path )

	def testSerialisation( self ) :

		fd, path = tempfile.mkstemp( suffix = ".csv" )
		try :
			with os.fdopen( fd, "w", encoding = "utf-8" ) as f :
				f.write( "x,y\n1,10\n2,20\n" )

			script = Gaffer.ScriptNode()
			script["csv"] = Gaffer.SeriesCsvReaderNode()
			script["csv"]["filePath"].setValue( path )
			script["csv"]["timeColumn"].setValue( 0 )
			script["csv"]["valueColumn"].setValue( 1 )

			timesLen = len( script["csv"]["out"]["times"].getValue() )

			script2 = Gaffer.ScriptNode()
			script2.execute( script.serialise() )

			self.assertEqual( script2["csv"]["filePath"].getValue(), path )
			self.assertEqual( len( script2["csv"]["out"]["times"].getValue() ), timesLen )
		finally :
			os.remove( path )


if __name__ == "__main__" :
	unittest.main()
