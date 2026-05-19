##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import IECore
import unittest

import Gaffer
import Gaffer.SignalNodeAlgo as SignalNodeAlgo
import GafferTest
from Gaffer.HJBoundValidator import OTL_HJ_VIOLATION, _hj_message_text


class Phase4TrackATest( GafferTest.TestCase ) :

	def testMatVecSolve( self ) :

		a = [ [ 2.0, 0.0 ], [ 0.0, 3.0 ] ]
		b = [ 1.0, 9.0 ]
		x = SignalNodeAlgo.mat_vec_solve( a, b, 1e-9 )
		self.assertIsNotNone( x )
		self.assertAlmostEqual( x[0], 0.5, places = 5 )
		self.assertAlmostEqual( x[1], 3.0, places = 5 )

	def testAlphaHalflifePassthrough( self ) :

		n = Gaffer.AlphaHalflifeNode()
		n["halfLife"].setValue( 42.0 )
		self.assertFloat32Equal( n["out"].getValue(), 42.0 )

	def testSDFWeightNodeNonZero( self ) :

		n = Gaffer.SDFWeightNode()
		n["ffLoadings"]["values"].setValue( IECore.FloatVectorData( [ 1.0, -0.5 ] ) )
		n["factorRet"]["values"].setValue( IECore.FloatVectorData( [ 0.1, 0.05 ] ) )
		rows = [
			[ 0.01, 0.02 ],
			[ 0.02, 0.01 ],
			[ -0.01, 0.03 ],
			[ 0.03, -0.01 ],
			[ 0.0, 0.01 ],
		]
		flat = []
		for row in rows :
			flat.extend( row )
		n["connMatrix"]["rowTimes"].setValue( IECore.Int64VectorData( list( range( len( rows ) ) ) ) )
		n["connMatrix"]["valuesRowMajor"].setValue( IECore.FloatVectorData( flat ) )
		n["connMatrix"]["numColumns"].setValue( 2 )
		n["covWindow"].setValue( 5 )

		aw = n["out"]["alphaWeight"].getValue()
		cf = n["out"]["confidence"].getValue()
		self.assertTrue( cf >= 0.0 and cf <= 1.0 )
		self.assertTrue( aw >= -1.0 and aw <= 1.0 )

	def testOptionsSdfNodeVolHigh( self ) :

		n = Gaffer.OptionsSdfNode()
		n["ivSurface"]["strikes"].setValue( IECore.FloatVectorData( [ 90.0, 100.0, 110.0 ] ) )
		n["ivSurface"]["expiries"].setValue( IECore.FloatVectorData( [ 0.25, 1.0 ] ) )
		n["ivSurface"]["ivsRowMajor"].setValue(
			IECore.FloatVectorData(
				[
					0.35, 0.30,
					0.28, 0.26,
					0.26, 0.24,
				]
			)
		)
		n["volRegime"]["value"].setValue( "VOL_NORMAL" )
		a0 = n["out"]["alphaWeight"].getValue()
		n["volRegime"]["value"].setValue( "VOL_HIGH" )
		a1 = n["out"]["alphaWeight"].getValue()
		self.assertGreater( abs( a1 ), abs( a0 ) - 1e-6 )

	def testESFuturesSignalNode( self ) :

		n = Gaffer.ESFuturesSignalNode()
		n["baseSignal"]["alphaWeight"].setValue( 0.8 )
		n["baseSignal"]["confidence"].setValue( 0.9 )
		n["baseSignal"]["halfLife"].setValue( 5.0 )
		n["baseSignal"]["maxImpactFrac"].setValue( 0.05 )
		n["baseSignal"]["regimeCondition"].setValue( "es" )
		n["baseSignal"]["sideBet"].setValue( False )
		n["kyleLambda"].setValue( 1.0 )
		n["halfLifeSignal"].setValue( 30.0 )
		n["lambdaScale"].setValue( 1.0 )

		self.assertLess( n["out"]["alphaWeight"].getValue(), 0.8 )
		self.assertFloat32Equal( n["out"]["halfLife"].getValue(), 30.0 )
		self.assertEqual( n["out"]["regimeCondition"].getValue(), "es" )

	def testHJBoundValidatorWarnsAndPassesThrough( self ) :

		n = Gaffer.HJBoundValidator()
		n["signalIn"]["alphaWeight"].setValue( 2.0 )
		n["signalIn"]["confidence"].setValue( 0.6 )
		n["signalIn"]["halfLife"].setValue( 10.0 )
		n["signalIn"]["maxImpactFrac"].setValue( 0.05 )
		n["signalIn"]["regimeCondition"].setValue( "x" )
		n["signalIn"]["sideBet"].setValue( True )

		self.ignoreMessage(
			IECore.MessageHandler.Level.Warning,
			OTL_HJ_VIOLATION,
			_hj_message_text( 2.0, 0.6 ),
		)

		self.assertFloat32Equal( n["signalOut"]["alphaWeight"].getValue(), 2.0 )
		self.assertFloat32Equal( n["signalOut"]["confidence"].getValue(), 0.6 )

	def testHJBoundQuiet( self ) :

		n = Gaffer.HJBoundValidator()
		n["signalIn"]["alphaWeight"].setValue( 0.3 )
		n["signalIn"]["confidence"].setValue( 0.5 )
		self.assertFloat32Equal( n["signalOut"]["alphaWeight"].getValue(), 0.3 )


if __name__ == "__main__" :
	unittest.main()
