##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import math
import os
import tempfile
import unittest

import IECore

import Gaffer
import GafferTest


class MarketVarNodeTest( GafferTest.TestCase ) :

	def setUp( self ) :

		Gaffer.MarketDataMacro.clearRegistry()

	def tearDown( self ) :

		Gaffer.MarketDataMacro.clearRegistry()

	def testMemory( self ) :

		Gaffer.MarketDataMacro.registerMacroSeries( "VIX", [ 1, 2, 3 ], [ 10.0, 11.0, 12.0 ] )
		n = Gaffer.MarketVarNode()
		n["variableName"].setValue( "VIX" )
		n["lookback"].setValue( 2 )

		self.assertEqual( n["out"]["times"].getValue(), IECore.Int64VectorData( [ 2, 3 ] ) )
		self.assertEqual(
			[ round( n["out"]["values"].getValue()[i], 5 ) for i in range( 2 ) ],
			[ 11.0, 12.0 ],
		)

	def testUnknownBackend( self ) :

		n = Gaffer.MarketVarNode()
		n["backend"].setValue( "nope" )
		with self.assertRaisesRegex( Gaffer.ProcessException, r"unknown backend.*nope" ) :
			n["out"]["times"].getValue()


class FactorSeriesNodeTest( GafferTest.TestCase ) :

	def setUp( self ) :

		Gaffer.MarketDataFactors.clearRegistry()

	def tearDown( self ) :

		Gaffer.MarketDataFactors.clearRegistry()

	def testMemory( self ) :

		Gaffer.MarketDataFactors.registerFactorSeries( "MKT_RF", [ 5, 6 ], [ 0.01, -0.02 ] )
		n = Gaffer.FactorSeriesNode()
		n["factorId"].setValue( "MKT_RF" )
		self.assertEqual( n["out"]["times"].getValue(), IECore.Int64VectorData( [ 5, 6 ] ) )


class CrossSectionNodeTest( GafferTest.TestCase ) :

	def setUp( self ) :

		Gaffer.MarketDataPanel.clearRegistry()

	def tearDown( self ) :

		Gaffer.MarketDataPanel.clearRegistry()

	def testMemory( self ) :

		Gaffer.MarketDataPanel.registerPanel(
			"U1",
			[ 1, 2 ],
			2,
			[ 1.0, 2.0, 3.0, 4.0 ],
		)
		n = Gaffer.CrossSectionNode()
		n["panelKey"].setValue( "U1" )

		self.assertEqual( n["numColumns"].getValue(), 2 )
		self.assertEqual( n["rowTimes"].getValue(), IECore.Int64VectorData( [ 1, 2 ] ) )
		self.assertEqual(
			[ GafferTest.asFloat32( n["valuesRowMajor"].getValue()[i] ) for i in range( 4 ) ],
			[ GafferTest.asFloat32( x ) for x in ( 1.0, 2.0, 3.0, 4.0 ) ],
		)

	def testWideCsv( self ) :

		fd, path = tempfile.mkstemp( suffix = ".csv" )
		os.close( fd )
		try :
			with open( path, "w", encoding = "utf-8" ) as f :
				f.write( "t,a,b\n0,1,2\n10,3,4\n" )

			n = Gaffer.CrossSectionNode()
			n["backend"].setValue( "csv" )
			n["resourcePath"].setValue( path )

			self.assertEqual( n["numColumns"].getValue(), 2 )
			self.assertEqual( n["rowTimes"].getValue(), IECore.Int64VectorData( [ 0, 10 ] ) )
		finally :
			os.remove( path )


class FamaFrenchLoadingsNodeTest( GafferTest.TestCase ) :

	def testRollingCoefficients( self ) :

		times = list( range( 20 ) )
		# ``hml`` must not be collinear with ``mkt`` (both linear in *i* breaks OLS identification).
		mkt = [ 0.01 * ( i + 1 ) for i in times ]
		smb = [ ( -1 ) ** i * 0.005 for i in times ]
		hml = [ 0.01 * math.sin( 0.35 * i ) for i in times ]
		asset = [ 1.0 + 0.5 * mkt[i] + 0.25 * smb[i] + 0.1 * hml[i] for i in times ]

		node = Gaffer.FamaFrenchLoadingsNode()
		for nm, tdata, vdata in (
			( "asset", times, asset ),
			( "mkt", times, mkt ),
			( "smb", times, smb ),
			( "hml", times, hml ),
		) :
			node[nm]["times"].setValue( IECore.Int64VectorData( tdata ) )
			node[nm]["values"].setValue( IECore.FloatVectorData( vdata ) )

		node["window"].setValue( 10 )
		bm = list( node["betaMkt"]["values"].getValue() )
		self.assertEqual( len( bm ), 11 )
		self.assertLess( abs( bm[-1] - 0.5 ), 0.05 )


class ConnectionMatrixNodeTest( GafferTest.TestCase ) :

	def testTwoByTwo( self ) :

		c = Gaffer.ConnectionMatrixNode()
		# rows: (1,2), (1,0) -> col0 [1,1], col1 [2,0]; predict col0 from col1: y=[1,1], X=[[2],[0]]
		c["matrixIn"].setValue( IECore.FloatVectorData( [ 1.0, 2.0, 1.0, 0.0 ] ) )
		c["numRows"].setValue( 2 )
		c["numColumns"].setValue( 2 )
		lam = list( c["lambdaMatrix"].getValue() )
		self.assertEqual( len( lam ), 4 )


class Phase2PipelineScriptTest( GafferTest.TestCase ) :

	def setUp( self ) :

		Gaffer.MarketDataTimeseries.clearRegistry()

	def tearDown( self ) :

		Gaffer.MarketDataTimeseries.clearRegistry()

	def testStoreRollingVolSerialise( self ) :

		Gaffer.MarketDataTimeseries.registerSeries( "ZZ", "close", [ 0, 1, 2 ], [ 10.0, 11.0, 12.0 ] )

		script = Gaffer.ScriptNode()
		script["store"] = Gaffer.TimeSeriesStoreNode()
		script["store"]["instrumentId"].setValue( "ZZ" )
		script["store"]["field"].setValue( "close" )
		script["store"]["lookback"].setValue( 3 )

		script["rr"] = Gaffer.RollingReturnsNode()
		script["rr"]["in"].setInput( script["store"]["out"] )
		script["rr"]["window"].setValue( 1 )

		script["rv"] = Gaffer.RealizedVolNode()
		script["rv"]["in"].setInput( script["rr"]["out"] )
		script["rv"]["window"].setValue( 2 )

		vol = script["rv"]["out"].getValue()

		script2 = Gaffer.ScriptNode()
		script2.execute( script.serialise() )
		self.assertAlmostEqual( script2["rv"]["out"].getValue(), vol, places = 5 )


if __name__ == "__main__" :
	unittest.main()
