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

import os
import tempfile
import unittest

import IECore

import Gaffer
import GafferTest
from Gaffer import MarketDataSurfaces


class IVSurfaceNodeTest( GafferTest.TestCase ) :

	def setUp( self ) :

		MarketDataSurfaces.clear_all_for_tests()

	def tearDown( self ) :

		MarketDataSurfaces.clear_all_for_tests()

	def testMemoryBackend( self ) :

		MarketDataSurfaces.register_iv_surface(
			"SPY",
			{
				"asOfTime": "snapA",
				"strikes": [ 100.0, 110.0 ],
				"expiries": [ 0.25, 1.0 ],
				"ivsRowMajor": [ 0.2, 0.22, 0.21, 0.24 ],
			},
		)

		n = Gaffer.IVSurfaceNode()
		n["symbol"].setValue( "SPY" )
		n["backend"].setValue( "memory" )

		self.assertEqual( n["out"]["asOfTime"].getValue(), "snapA" )
		self.assertEqual(
			list( n["out"]["strikes"].getValue() ),
			[ GafferTest.asFloat32( x ) for x in ( 100.0, 110.0 ) ],
		)
		self.assertEqual(
			list( n["out"]["expiries"].getValue() ),
			[ GafferTest.asFloat32( x ) for x in ( 0.25, 1.0 ) ],
		)
		self.assertEqual(
			[ GafferTest.asFloat32( x ) for x in n["out"]["ivsRowMajor"].getValue() ],
			[ GafferTest.asFloat32( x ) for x in ( 0.2, 0.22, 0.21, 0.24 ) ],
		)

	def testMemoryDefaultAsOfTimeFallback( self ) :

		MarketDataSurfaces.register_iv_surface(
			"QQQ",
			{
				"strikes": [ 100.0 ],
				"expiries": [ 0.5 ],
				"ivsRowMajor": [ 0.3 ],
			},
		)
		n = Gaffer.IVSurfaceNode()
		n["symbol"].setValue( "QQQ" )
		n["defaultAsOfTime"].setValue( "fallbackTs" )
		n["backend"].setValue( "memory" )
		self.assertEqual( n["out"]["asOfTime"].getValue(), "fallbackTs" )

	def testMemoryMismatchClearsGrid( self ) :

		MarketDataSurfaces.register_iv_surface(
			"BAD",
			{
				"asOfTime": "x",
				"strikes": [ 100.0, 101.0 ],
				"expiries": [ 0.5 ],
				"ivsRowMajor": [ 0.1 ],
			},
		)
		n = Gaffer.IVSurfaceNode()
		n["symbol"].setValue( "BAD" )
		n["backend"].setValue( "memory" )
		self.assertEqual( n["out"]["asOfTime"].getValue(), "x" )
		self.assertEqual( len( n["out"]["strikes"].getValue() ), 0 )
		self.assertEqual( len( n["out"]["expiries"].getValue() ), 0 )
		self.assertEqual( len( n["out"]["ivsRowMajor"].getValue() ), 0 )

	def testCsvBackend( self ) :

		content = "strike,expiry,iv\n100,0.25,0.2\n100,1,0.21\n110,0.25,0.22\n110,1,0.24\n"
		fd, path = tempfile.mkstemp( suffix = ".csv", text = True )
		try :
			os.close( fd )
			with open( path, "w", encoding = "utf-8", newline = "" ) as f :
				f.write( content )

			n = Gaffer.IVSurfaceNode()
			n["backend"].setValue( "csv" )
			n["resourcePath"].setValue( path )
			n["defaultAsOfTime"].setValue( "fileSnap" )
			n["hasHeader"].setValue( True )
			n["strikeColumn"].setValue( 0 )
			n["expiryColumn"].setValue( 1 )
			n["ivColumn"].setValue( 2 )

			self.assertEqual( n["out"]["asOfTime"].getValue(), "fileSnap" )
			strikes = [ float( x ) for x in n["out"]["strikes"].getValue() ]
			expiries = [ float( x ) for x in n["out"]["expiries"].getValue() ]
			self.assertEqual( strikes, [ 100.0, 110.0 ] )
			self.assertEqual( expiries, [ 0.25, 1.0 ] )
			self.assertEqual(
				[ GafferTest.asFloat32( x ) for x in n["out"]["ivsRowMajor"].getValue() ],
				[ GafferTest.asFloat32( x ) for x in ( 0.2, 0.21, 0.22, 0.24 ) ],
			)
		finally :
			try :
				os.unlink( path )
			except OSError :
				pass

	def testSerialisation( self ) :

		MarketDataSurfaces.register_iv_surface(
			"X",
			{
				"strikes": [ 100.0 ],
				"expiries": [ 0.5 ],
				"ivsRowMajor": [ 0.19 ],
			},
		)
		script = Gaffer.ScriptNode()
		script["iv"] = Gaffer.IVSurfaceNode()
		script["iv"]["symbol"].setValue( "X" )
		script["iv"]["backend"].setValue( "memory" )

		s = script.serialise()
		script2 = Gaffer.ScriptNode()
		script2.execute( s )

		self.assertEqual( len( script2["iv"]["out"]["strikes"].getValue() ), 1 )


if __name__ == "__main__" :
	unittest.main()
