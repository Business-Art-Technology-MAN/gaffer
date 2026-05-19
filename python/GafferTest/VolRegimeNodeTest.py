##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import unittest

import IECore

import Gaffer
import GafferTest


class VolRegimeNodeTest( GafferTest.TestCase ) :

	def testVolHigh( self ) :

		n = Gaffer.VolRegimeNode()
		n["vixSeries"]["times"].setValue( IECore.Int64VectorData( [ 1 ] ) )
		n["vixSeries"]["values"].setValue( IECore.FloatVectorData( [ 20.0 ] ) )
		n["realizedVolSeries"]["times"].setValue( IECore.Int64VectorData( [ 1 ] ) )
		n["realizedVolSeries"]["values"].setValue( IECore.FloatVectorData( [ 25.0 ] ) )
		n["lowRatio"].setValue( 0.85 )
		n["highRatio"].setValue( 1.15 )

		self.assertEqual( n["out"]["value"].getValue(), "VOL_HIGH" )

	def testVolLow( self ) :

		n = Gaffer.VolRegimeNode()
		n["vixSeries"]["times"].setValue( IECore.Int64VectorData( [ 1 ] ) )
		n["vixSeries"]["values"].setValue( IECore.FloatVectorData( [ 20.0 ] ) )
		n["realizedVolSeries"]["times"].setValue( IECore.Int64VectorData( [ 1 ] ) )
		n["realizedVolSeries"]["values"].setValue( IECore.FloatVectorData( [ 15.0 ] ) )
		n["lowRatio"].setValue( 0.85 )
		n["highRatio"].setValue( 1.15 )

		self.assertEqual( n["out"]["value"].getValue(), "VOL_LOW" )

	def testAnyMissing( self ) :

		n = Gaffer.VolRegimeNode()
		n["vixSeries"]["times"].setValue( IECore.Int64VectorData( [] ) )
		n["vixSeries"]["values"].setValue( IECore.FloatVectorData( [] ) )
		n["realizedVolSeries"]["times"].setValue( IECore.Int64VectorData( [ 1 ] ) )
		n["realizedVolSeries"]["values"].setValue( IECore.FloatVectorData( [ 15.0 ] ) )

		self.assertEqual( n["out"]["value"].getValue(), "ANY" )

	def testSerialisation( self ) :

		script = Gaffer.ScriptNode()
		script["v"] = Gaffer.VolRegimeNode()
		script["v"]["highRatio"].setValue( 1.4 )

		v = script["v"]["out"]["value"].getValue()

		script2 = Gaffer.ScriptNode()
		script2.execute( script.serialise() )

		self.assertFloat32Equal( script2["v"]["highRatio"].getValue(), 1.4 )
		self.assertEqual( script2["v"]["out"]["value"].getValue(), v )


if __name__ == "__main__" :
	unittest.main()
