##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#      * Redistributions of source code must retain the above
#      copyright notice, this list of conditions and the following
#      disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided with
#      the distribution.
#
#      * Neither the name of John Haddon nor the names of
#      any other contributors to this software may be used to endorse or
#      promote products derived from this software without specific prior
#      written permission.
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

import unittest

import IECore

import Gaffer
import Gaffer.MarketDataTimeseries as MarketDataTimeseries
import GafferTest


class ThresholdRegimeNodeTest( GafferTest.TestCase ) :

	def __set_series( self, seriesPlug, times, values ) :

		seriesPlug["times"].setValue( IECore.Int64VectorData( times ) )
		seriesPlug["values"].setValue( IECore.FloatVectorData( values ) )

	def testRiskOn( self ) :

		n = Gaffer.ThresholdRegimeNode()
		self.__set_series( n["vixSeries"], [ 1 ], [ 15.0 ] )
		self.__set_series( n["termSpreadSeries"], [ 1 ], [ 1.0 ] )
		self.__set_series( n["creditSpreadSeries"], [ 1 ], [ 1.0 ] )
		n["vixThreshold"].setValue( 25.0 )
		n["creditThreshold"].setValue( 5.0 )
		n["termThreshold"].setValue( 0.0 )

		self.assertEqual( n["out"]["value"].getValue(), "RISK_ON" )

	def testRiskOffTwoFlags( self ) :

		n = Gaffer.ThresholdRegimeNode()
		self.__set_series( n["vixSeries"], [ 1 ], [ 30.0 ] )
		self.__set_series( n["termSpreadSeries"], [ 1 ], [ -0.5 ] )
		self.__set_series( n["creditSpreadSeries"], [ 1 ], [ 1.0 ] )
		n["vixThreshold"].setValue( 25.0 )
		n["creditThreshold"].setValue( 5.0 )
		n["termThreshold"].setValue( 0.0 )

		self.assertEqual( n["out"]["value"].getValue(), "RISK_OFF" )

	def testTransitionOneFlag( self ) :

		n = Gaffer.ThresholdRegimeNode()
		self.__set_series( n["vixSeries"], [ 1 ], [ 30.0 ] )
		self.__set_series( n["termSpreadSeries"], [ 1 ], [ 1.0 ] )
		self.__set_series( n["creditSpreadSeries"], [ 1 ], [ 1.0 ] )
		n["vixThreshold"].setValue( 25.0 )
		n["creditThreshold"].setValue( 5.0 )
		n["termThreshold"].setValue( 0.0 )

		self.assertEqual( n["out"]["value"].getValue(), "TRANSITION" )

	def testAnyMissingSeries( self ) :

		n = Gaffer.ThresholdRegimeNode()
		self.__set_series( n["vixSeries"], [], [] )
		self.__set_series( n["termSpreadSeries"], [ 1 ], [ 1.0 ] )
		self.__set_series( n["creditSpreadSeries"], [ 1 ], [ 1.0 ] )

		self.assertEqual( n["out"]["value"].getValue(), "ANY" )

	def testPointInTime( self ) :

		n = Gaffer.ThresholdRegimeNode()
		self.__set_series( n["vixSeries"], [ 10, 20 ], [ 15.0, 35.0 ] )
		self.__set_series( n["termSpreadSeries"], [ 10, 20 ], [ 1.0, 1.0 ] )
		self.__set_series( n["creditSpreadSeries"], [ 10, 20 ], [ 1.0, 1.0 ] )
		n["vixThreshold"].setValue( 25.0 )
		n["creditThreshold"].setValue( 5.0 )
		n["termThreshold"].setValue( 0.0 )

		with Gaffer.Context() as c :
			c.set( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, 15 )
			self.assertEqual( n["out"]["value"].getValue(), "RISK_ON" )

		with Gaffer.Context() as c :
			c.set( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, 25 )
			self.assertEqual( n["out"]["value"].getValue(), "TRANSITION" )

	def testSerialisation( self ) :

		script = Gaffer.ScriptNode()
		script["tr"] = Gaffer.ThresholdRegimeNode()
		self.__set_series( script["tr"]["vixSeries"], [ 1 ], [ 10.0 ] )
		self.__set_series( script["tr"]["termSpreadSeries"], [ 1 ], [ 1.0 ] )
		self.__set_series( script["tr"]["creditSpreadSeries"], [ 1 ], [ 1.0 ] )
		script["tr"]["vixThreshold"].setValue( 40.0 )

		v = script["tr"]["out"]["value"].getValue()

		script2 = Gaffer.ScriptNode()
		script2.execute( script.serialise() )

		self.assertFloat32Equal( script2["tr"]["vixThreshold"].getValue(), 40.0 )
		self.assertEqual( script2["tr"]["out"]["value"].getValue(), v )


if __name__ == "__main__" :
	unittest.main()
