##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights
#  reserved.
#
##########################################################################

import unittest

import IECore

import Gaffer
import Gaffer.PortfolioConstrainer as PC
import GafferTest


class Phase5Test( GafferTest.TestCase ) :

	def testThreeNameAggregatorEqualWeight( self ) :

		n = Gaffer.PortfolioAggregatorNode()
		n["instrumentSignals"]["instrumentIds"].setValue(
			IECore.StringVectorData( [ "ES1!", "ZN1!", "EURUSD" ] )
		)
		sigs = n["instrumentSignals"].signalsPlug()
		sigs.resize( 3 )
		for i, ch in enumerate( list( sigs.children() ) ) :
			self.assertTrue( isinstance( ch, Gaffer.SignalClosurePlug ) )
			ch.alphaWeightPlug().setValue( float( i + 1 ) * 0.1 )
			ch.confidencePlug().setValue( 0.9 )
			ch.halfLifePlug().setValue( float( 10 + i ) )
			ch.maxImpactFracPlug().setValue( 0.05 )
			ch.regimeConditionPlug().setValue( "p5" )
			ch.sideBetPlug().setValue( False )

		n["assetVariances"]["values"].setValue( IECore.FloatVectorData( [ 0.04, 0.01, 0.09 ] ) )
		n["constructionMethod"].setValue( "equal_weight" )
		w = [ GafferTest.asFloat32( x ) for x in n["out"]["targetWeights"].getValue() ]
		self.assertEqual( len( w ), 3 )
		for x in w :
			self.assertAlmostEqual( x, 1.0 / 3.0, places = 5 )
		self.assertEqual( list( n["out"]["instrumentIds"].getValue() ), [ "ES1!", "ZN1!", "EURUSD" ] )
		h = [ GafferTest.asFloat32( x ) for x in n["out"]["halfLives"].getValue() ]
		self.assertEqual( h, [ GafferTest.asFloat32( x ) for x in ( 10.0, 11.0, 12.0 ) ] )

	def testConstructionMethodChangesWeights( self ) :

		n = Gaffer.PortfolioAggregatorNode()
		n["instrumentSignals"]["instrumentIds"].setValue(
			IECore.StringVectorData( [ "A", "B" ] )
		)
		sigs = n["instrumentSignals"].signalsPlug()
		sigs.resize( 2 )
		for ch in sigs.children() :
			ch.maxImpactFracPlug().setValue( 0.05 )
			ch.regimeConditionPlug().setValue( "x" )
			ch.sideBetPlug().setValue( False )

		children = list( sigs.children() )
		self.assertEqual( len( children ), 2 )
		ch0, ch1 = children[0], children[1]
		ch0.alphaWeightPlug().setValue( 1.0 )
		ch0.confidencePlug().setValue( 1.0 )
		ch0.halfLifePlug().setValue( 5.0 )
		ch1.alphaWeightPlug().setValue( 0.5 )
		ch1.confidencePlug().setValue( 1.0 )
		ch1.halfLifePlug().setValue( 5.0 )

		n["assetVariances"]["values"].setValue( IECore.FloatVectorData( [ 1.0, 1.0 ] ) )
		## Default **maxSingleName** (0.6) would cap alpha-proportional (~0.67, ~0.33) and emit **OTL_EXPOSURE_VIOLATION** — not under test here.
		n["maxSingleName"].setValue( 1.0 )
		n["constructionMethod"].setValue( "equal_weight" )
		wEq = list( n["out"]["targetWeights"].getValue() )
		n["constructionMethod"].setValue( "alpha_proportional" )
		wAp = list( n["out"]["targetWeights"].getValue() )
		self.assertNotEqual(
			[ GafferTest.asFloat32( x ) for x in wEq ],
			[ GafferTest.asFloat32( x ) for x in wAp ],
		)

	def testExposureMessageOnTightCap( self ) :

		n = Gaffer.PortfolioAggregatorNode()
		n["instrumentSignals"]["instrumentIds"].setValue(
			IECore.StringVectorData( [ "A", "B", "C" ] )
		)
		sigs = n["instrumentSignals"].signalsPlug()
		sigs.resize( 3 )
		for ch in sigs.children() :
			ch.alphaWeightPlug().setValue( 1.0 )
			ch.confidencePlug().setValue( 1.0 )
			ch.halfLifePlug().setValue( 1.0 )
			ch.maxImpactFracPlug().setValue( 0.05 )
			ch.regimeConditionPlug().setValue( "x" )
			ch.sideBetPlug().setValue( False )

		n["maxSingleName"].setValue( 0.25 )
		n["constructionMethod"].setValue( "equal_weight" )

		msg = (
			"Portfolio constraint adjustment active (drawdown_gate=False, single_name=True, "
			"gross=False, net=False)."
		)
		self.ignoreMessage( IECore.MessageHandler.Level.Warning, PC.OTL_EXPOSURE_VIOLATION, msg )

		_ = list( n["out"]["targetWeights"].getValue() )

	def testPortfolioInputMismatchWarning( self ) :

		n = Gaffer.PortfolioAggregatorNode()
		n["instrumentSignals"]["instrumentIds"].setValue(
			IECore.StringVectorData( [ "A", "B", "C" ] )
		)
		sigs = n["instrumentSignals"].signalsPlug()
		sigs.resize( 2 )
		for ch in sigs.children() :
			ch.alphaWeightPlug().setValue( 1.0 )
			ch.confidencePlug().setValue( 1.0 )
			ch.halfLifePlug().setValue( 1.0 )
			ch.maxImpactFracPlug().setValue( 0.05 )
			ch.regimeConditionPlug().setValue( "x" )
			ch.sideBetPlug().setValue( False )

		n["assetVariances"]["values"].setValue( IECore.FloatVectorData( [ 1.0, 1.0 ] ) )
		n["maxSingleName"].setValue( 1.0 )

		msg = (
			"PortfolioAggregator: instrumentIds length (3) differs from SignalClosurePlug count (2)."
		)
		self.ignoreMessage( IECore.MessageHandler.Level.Warning, Gaffer.OTL_PORTFOLIO_INPUT, msg )
		_ = list( n["out"]["targetWeights"].getValue() )


if __name__ == "__main__" :
	unittest.main()
