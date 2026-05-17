##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import os
import tempfile
import unittest

import Gaffer
import GafferTest


class PceGraphIOTest( GafferTest.TestCase ) :

	@unittest.skipUnless( Gaffer.usdAvailableForPce(), "PCE-USD/1 needs pxr" )
	def testUsdNativeRoundTrip( self ) :

		script = Gaffer.ScriptNode()
		script["n"] = Gaffer.ConstantSeriesNode()
		script["n"]["length"].setValue( 4 )
		script["n"]["constant"].setValue( 2.5 )

		fd, path = tempfile.mkstemp( suffix = ".pce" )
		os.close( fd )
		try :
			Gaffer.savePceGraphFile( script, path, { "unit" : "PceGraphIOTest" }, graphFormat = "usd" )
			with open( path, "r", encoding = "utf-8" ) as f :
				head = f.read( 32 ).lower()
			self.assertTrue( head.startswith( "#usda" ), "expected USDA header in default USD save" )

			meta, body = Gaffer.loadPceGraphFile( path )
			self.assertEqual( meta.get( "unit" ), "PceGraphIOTest" )
			self.assertIn( "ConstantSeriesNode", body )

			restored = Gaffer.ScriptNode()
			restored.execute( body )
			self.assertEqual( restored["n"]["length"].getValue(), 4 )
			self.assertEqual( restored["n"]["constant"].getValue(), 2.5 )
		finally :
			os.remove( path )

	def testLegacyEnvelopeRoundTrip( self ) :

		script = Gaffer.ScriptNode()
		script["n"] = Gaffer.ConstantSeriesNode()
		script["n"]["length"].setValue( 4 )
		script["n"]["constant"].setValue( 2.5 )

		fd, path = tempfile.mkstemp( suffix = ".pce" )
		os.close( fd )
		try :
			Gaffer.savePceGraphFile( script, path, { "unit" : "PceGraphLegacy" }, graphFormat = "legacy" )
			meta, body = Gaffer.loadPceGraphFile( path )
			self.assertEqual( meta.get( "unit" ), "PceGraphLegacy" )
			self.assertIn( "ConstantSeriesNode", body )

			restored = Gaffer.ScriptNode()
			restored.execute( body )
			self.assertEqual( restored["n"]["length"].getValue(), 4 )
			self.assertEqual( restored["n"]["constant"].getValue(), 2.5 )
		finally :
			os.remove( path )

	def testExecutePceGraphFile( self ) :

		script = Gaffer.ScriptNode()
		script["n"] = Gaffer.ConstantSeriesNode()
		script["n"]["startTime"].setValue( 10 )

		fmt = "usd" if Gaffer.usdAvailableForPce() else "legacy"

		fd, path = tempfile.mkstemp( suffix = ".pce" )
		os.close( fd )
		try :
			Gaffer.savePceGraphFile( script, path, {}, graphFormat = fmt )
			other, meta = Gaffer.executePceGraphFile( path )
			self.assertEqual( meta, {} )
			self.assertEqual( other["n"]["startTime"].getValue(), 10 )
		finally :
			os.remove( path )

	def testRejectWrongMagic( self ) :

		fd, path = tempfile.mkstemp( suffix = ".pce" )
		os.close( fd )
		try :
			with open( path, "w", encoding = "utf-8" ) as f :
				f.write( "NOT-PCE\n{}\n---\n" )
			with self.assertRaises( ValueError ) :
				Gaffer.loadPceGraphFile( path )
		finally :
			os.remove( path )


if __name__ == "__main__" :
	unittest.main()
