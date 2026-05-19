##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import unittest

import IECore

import Gaffer
import GafferTest


class CPRegimeNodeTest( GafferTest.TestCase ) :

	def testSpreadAndRegBand( self ) :

		n = Gaffer.CPRegimeNode()
		n["shortFwdSeries"]["times"].setValue( IECore.Int64VectorData( [ 1 ] ) )
		n["shortFwdSeries"]["values"].setValue( IECore.FloatVectorData( [ 2.0 ] ) )
		n["longFwdSeries"]["times"].setValue( IECore.Int64VectorData( [ 1 ] ) )
		n["longFwdSeries"]["values"].setValue( IECore.FloatVectorData( [ 5.0 ] ) )
		n["transitionBand"].setValue( 0.5 )

		self.assertEqual( n["regimeOut"]["value"].getValue(), "RISK_ON" )
		self.assertFloat32Equal( n["cpValue"].getValue(), 3.0 )

	def testTransition( self ) :

		n = Gaffer.CPRegimeNode()
		n["shortFwdSeries"]["times"].setValue( IECore.Int64VectorData( [ 1 ] ) )
		n["shortFwdSeries"]["values"].setValue( IECore.FloatVectorData( [ 2.0 ] ) )
		n["longFwdSeries"]["times"].setValue( IECore.Int64VectorData( [ 1 ] ) )
		n["longFwdSeries"]["values"].setValue( IECore.FloatVectorData( [ 2.1 ] ) )
		n["transitionBand"].setValue( 0.5 )

		self.assertEqual( n["regimeOut"]["value"].getValue(), "TRANSITION" )

	def testSerialisation( self ) :

		script = Gaffer.ScriptNode()
		script["cp"] = Gaffer.CPRegimeNode()
		script["cp"]["transitionBand"].setValue( 0.9 )

		r = script["cp"]["regimeOut"]["value"].getValue()
		c = script["cp"]["cpValue"].getValue()

		script2 = Gaffer.ScriptNode()
		script2.execute( script.serialise() )

		self.assertFloat32Equal( script2["cp"]["transitionBand"].getValue(), 0.9 )
		self.assertEqual( script2["cp"]["regimeOut"]["value"].getValue(), r )
		self.assertFloat32Equal( script2["cp"]["cpValue"].getValue(), c )


if __name__ == "__main__" :
	unittest.main()
