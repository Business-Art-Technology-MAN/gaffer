##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import unittest

import IECore

import Gaffer
import GafferTest


class HMMRegimeNodeTest( GafferTest.TestCase ) :

	def testMedianFallbackProducesSeries( self ) :

		n = Gaffer.HMMRegimeNode()
		n["returnsSeries"]["times"].setValue( IECore.Int64VectorData( list( range( 20 ) ) ) )
		n["returnsSeries"]["values"].setValue(
			IECore.FloatVectorData( [ 0.01 ] * 10 + [ -0.02 ] * 10 )
		)
		n["trainWindow"].setValue( 16 )
		n["minSamples"].setValue( 8 )
		n["numStates"].setValue( 2 )

		reg = n["regimeOut"]["value"].getValue()
		self.assertNotEqual( reg, "ANY" )

		times = list( n["stateProbSeries"]["times"].getValue() )
		probs = list( n["stateProbSeries"]["values"].getValue() )
		self.assertEqual( len( times ), len( probs ) )
		self.assertEqual( len( times ), 16 )

	def testTooFewSamples( self ) :

		n = Gaffer.HMMRegimeNode()
		n["returnsSeries"]["times"].setValue( IECore.Int64VectorData( [ 1, 2, 3 ] ) )
		n["returnsSeries"]["values"].setValue( IECore.FloatVectorData( [ 0.01, -0.01, 0.02 ] ) )
		n["minSamples"].setValue( 20 )

		self.assertEqual( n["regimeOut"]["value"].getValue(), "ANY" )
		self.assertEqual( len( n["stateProbSeries"]["times"].getValue() ), 0 )

	def testSerialisation( self ) :

		script = Gaffer.ScriptNode()
		script["hmm"] = Gaffer.HMMRegimeNode()
		script["hmm"]["trainWindow"].setValue( 40 )

		script2 = Gaffer.ScriptNode()
		script2.execute( script.serialise() )

		self.assertEqual( script2["hmm"]["trainWindow"].getValue(), 40 )


if __name__ == "__main__" :
	unittest.main()
