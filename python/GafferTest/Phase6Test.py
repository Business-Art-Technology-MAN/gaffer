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

from Gaffer.PcePortfolioStage import (
	PCE_CONTEXT_MARKET_TIME_NS,
	PceInstrumentPrim,
	PcePortfolioStagePayload,
	PceTimeSample,
	apply_market_time_to_context,
	market_time_from_context,
	open_pce_usda_stage,
	read_portfolio_payload_from_stage,
)


class Phase6Test( GafferTest.TestCase ) :

	@unittest.skipUnless( Gaffer.usdAvailableForPce(), "PCE-USD/2 needs pxr" )
	def testUsdV2PortfolioAndGraphRoundTrip( self ) :

		script = Gaffer.ScriptNode()
		script["n"] = Gaffer.ConstantSeriesNode()
		script["n"]["length"].setValue( 3 )

		payload = PcePortfolioStagePayload(
			instruments = [
				PceInstrumentPrim( symbol = "ES1!", kind = "FuturesAsset" ),
				PceInstrumentPrim( symbol = "ZN1!", kind = "BondAsset" ),
				PceInstrumentPrim( symbol = "EURUSD", kind = "FXForward", currency = "USD" ),
			],
			time_samples = [ PceTimeSample( frame = 0, time_nanoseconds = 1_700_000_000_000_000_000 ) ],
			active_execution_delegate = "PaperDelegate",
		)

		fd, path = tempfile.mkstemp( suffix = ".pce" )
		os.close( fd )
		try :
			Gaffer.savePceGraphFile(
				script,
				path,
				{ "phase" : "6" },
				graphFormat = "usd",
				portfolio = payload,
			)
			with open( path, "r", encoding = "utf-8" ) as f :
				text = f.read()
			## On-disk USDA uses ``def Xform "Portfolio"``, not a literal ``/Portfolio`` substring.
			self.assertIn( 'Xform "Portfolio"', text )
			self.assertRegex( text, r'pce:symbol\s*=\s*"ES1!"' )

			meta, body = Gaffer.loadPceGraphFile( path )
			self.assertEqual( meta.get( "phase" ), "6" )
			self.assertIn( "pcePortfolioStage", meta )
			st = open_pce_usda_stage( path )
			self.assertTrue( st )
			roundPayload = read_portfolio_payload_from_stage( st )
			syms = sorted( i.symbol for i in roundPayload.instruments )
			self.assertEqual( syms, [ "ES1!", "EURUSD", "ZN1!" ] )
			self.assertEqual( meta["pcePortfolioStage"]["activeExecutionDelegate"], "PaperDelegate" )

			restored = Gaffer.ScriptNode()
			restored.execute( body )
			self.assertEqual( restored["n"]["length"].getValue(), 3 )
		finally :
			os.remove( path )

	@unittest.skipUnless( Gaffer.usdAvailableForPce(), "PCE-USD/2 needs pxr" )
	def testUsdV2SublayerPathsRoundTrip( self ) :

		ovdir = tempfile.mkdtemp()
		try :
			ovPath = os.path.join( ovdir, "risk_override.usda" )
			with open( ovPath, "w", encoding = "utf-8", newline = "\n" ) as f :
				f.write(
					"#usda 1.0\n"
					"def Scope \"Overlay\" {\n"
					"}\n"
				)

			script = Gaffer.ScriptNode()
			script["n"] = Gaffer.Dot()

			fd, path = tempfile.mkstemp( suffix = ".pce", dir = ovdir )
			os.close( fd )
			try :
				Gaffer.savePceGraphFile(
					script,
					path,
					{},
					graphFormat = "usd",
					sublayerPaths = [ ovPath.replace( "\\", "/" ) ],
				)
				meta, _body = Gaffer.loadPceGraphFile( path )
				self.assertIn( "pceSublayerPaths", meta )
				self.assertEqual( len( meta["pceSublayerPaths"] ), 1 )
			finally :
				os.remove( path )
		finally :
			os.remove( ovPath )
			os.rmdir( ovdir )

	def testLegacyDisallowsPortfolioKwargs( self ) :

		script = Gaffer.ScriptNode()
		fd, path = tempfile.mkstemp( suffix = ".pce" )
		os.close( fd )
		try :
			with self.assertRaises( ValueError ) :
				Gaffer.savePceGraphFile(
					script,
					path,
					{},
					graphFormat = "legacy",
					portfolio = PcePortfolioStagePayload(),
				)
		finally :
			os.remove( path )

	def testMarketTimeContextVariable( self ) :

		ctx = Gaffer.Context()
		apply_market_time_to_context( ctx, 42 )
		self.assertEqual( market_time_from_context( ctx ), 42 )
		self.assertEqual( ctx[PCE_CONTEXT_MARKET_TIME_NS], 42 )

	def testExecutionDelegateRegistry( self ) :

		self.assertIn( "BacktestDelegate", Gaffer.execution_delegate_names() )
		self.assertIn( "PaperDelegate", Gaffer.execution_delegate_names() )
		d = Gaffer.create_execution_delegate( "PaperDelegate" )
		self.assertIsNotNone( d )


if __name__ == "__main__" :
	unittest.main()
