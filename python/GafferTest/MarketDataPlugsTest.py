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
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
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

import json
import unittest

import IECore

import Gaffer
import Gaffer.MarketDataAlgo as MarketDataAlgo
import GafferTest

class MarketDataPlugsTest( GafferTest.TestCase ) :

	@staticmethod
	def __floatVectorReadable32( floatVectorData ) :

		# Python bindings expose vector data as a sequence (no C++ `.readable()`).
		return [ GafferTest.asFloat32( floatVectorData[i] ) for i in range( len( floatVectorData ) ) ]

	def testSeriesPlug( self ) :

		p = Gaffer.SeriesPlug()
		self.assertEqual( p.getName(), "SeriesPlug" )
		p.timesPlug().setValue( IECore.Int64VectorData( [ 1, 2, 3 ] ) )
		p.valuesPlug().setValue( IECore.FloatVectorData( [ 0.5, 1.0, 1.5 ] ) )
		self.assertEqual( p.timesPlug().getValue(), IECore.Int64VectorData( [ 1, 2, 3 ] ) )
		self.assertEqual(
			self.__floatVectorReadable32( p.valuesPlug().getValue() ),
			[ GafferTest.asFloat32( x ) for x in ( 0.5, 1.0, 1.5 ) ],
		)

		o = p.createCounterpart( "sOut", Gaffer.Plug.Direction.Out )
		self.assertEqual( o.getName(), "sOut" )
		self.assertEqual( o.direction(), Gaffer.Plug.Direction.Out )
		self.assertTrue( isinstance( o, Gaffer.SeriesPlug ) )

	def testSignalClosurePlug( self ) :

		p = Gaffer.SignalClosurePlug()
		p.alphaWeightPlug().setValue( 0.25 )
		p.confidencePlug().setValue( 0.9 )
		p.halfLifePlug().setValue( 12.0 )
		p.maxImpactFracPlug().setValue( 0.05 )
		p.regimeConditionPlug().setValue( "riskOn" )
		p.sideBetPlug().setValue( True )

		self.assertFloat32Equal( p.alphaWeightPlug().getValue(), 0.25 )
		self.assertFloat32Equal( p.confidencePlug().getValue(), 0.9 )
		self.assertFloat32Equal( p.halfLifePlug().getValue(), 12.0 )
		self.assertFloat32Equal( p.maxImpactFracPlug().getValue(), 0.05 )
		self.assertEqual( p.regimeConditionPlug().getValue(), "riskOn" )
		self.assertEqual( p.sideBetPlug().getValue(), True )

	def testWeightVectorPlug( self ) :

		p = Gaffer.WeightVectorPlug()
		p.instrumentIdsPlug().setValue( IECore.StringVectorData( [ "SPY", "TLT" ] ) )
		p.targetWeightsPlug().setValue( IECore.FloatVectorData( [ 0.6, 0.4 ] ) )
		p.confidencesPlug().setValue( IECore.FloatVectorData( [ 0.8, 0.7 ] ) )
		p.grossExposurePlug().setValue( 1.0 )
		p.netExposurePlug().setValue( 0.2 )
		p.activeRegimePlug().setValue( "carry" )
		p.evaluatedAtPlug().setValue( "1700000000" )

		self.assertEqual(
			p.instrumentIdsPlug().getValue(),
			IECore.StringVectorData( [ "SPY", "TLT" ] ),
		)
		self.assertEqual(
			self.__floatVectorReadable32( p.targetWeightsPlug().getValue() ),
			[ GafferTest.asFloat32( x ) for x in ( 0.6, 0.4 ) ],
		)
		self.assertEqual(
			self.__floatVectorReadable32( p.confidencesPlug().getValue() ),
			[ GafferTest.asFloat32( x ) for x in ( 0.8, 0.7 ) ],
		)
		self.assertFloat32Equal( p.grossExposurePlug().getValue(), 1.0 )
		self.assertFloat32Equal( p.netExposurePlug().getValue(), 0.2 )
		self.assertEqual( p.activeRegimePlug().getValue(), "carry" )
		self.assertEqual( p.evaluatedAtPlug().getValue(), "1700000000" )

	def testMarketContextPlug( self ) :

		p = Gaffer.MarketContextPlug()
		p.timeNanosecondsPlug().setValue( "1700000000123" )
		p.macroRegimePlug().setValue( "late_cycle" )
		p.vixLevelPlug().setValue( 18.5 )
		p.termSpreadPlug().setValue( 0.5 )
		p.creditSpreadPlug().setValue( 1.2 )

		self.assertEqual( p.timeNanosecondsPlug().getValue(), "1700000000123" )
		self.assertEqual( p.macroRegimePlug().getValue(), "late_cycle" )
		self.assertFloat32Equal( p.vixLevelPlug().getValue(), 18.5 )
		self.assertFloat32Equal( p.termSpreadPlug().getValue(), 0.5 )
		self.assertFloat32Equal( p.creditSpreadPlug().getValue(), 1.2 )

	def testIncompatibleCompoundInput( self ) :

		series = Gaffer.SeriesPlug()
		sig = Gaffer.SignalClosurePlug()
		weights = Gaffer.WeightVectorPlug()
		ctx = Gaffer.MarketContextPlug()
		self.assertFalse( series.acceptsInput( sig ) )
		self.assertFalse( sig.acceptsInput( series ) )
		self.assertFalse( series.acceptsInput( weights ) )
		self.assertFalse( weights.acceptsInput( series ) )
		self.assertFalse( series.acceptsInput( ctx ) )
		self.assertFalse( ctx.acceptsInput( series ) )

	def testRunTimeTyped( self ) :

		for plugType in (
			Gaffer.SeriesPlug,
			Gaffer.SignalClosurePlug,
			Gaffer.WeightVectorPlug,
			Gaffer.MarketContextPlug,
		) :
			p = plugType()
			self.assertNotEqual( p.typeId(), Gaffer.ValuePlug.staticTypeId() )
			self.assertTrue( p.isInstanceOf( Gaffer.ValuePlug.staticTypeId() ) )

	def testCompoundNoduleMetadata( self ) :

		for plugFactory, childName in (
			( Gaffer.SeriesPlug, "times" ),
			( Gaffer.SignalClosurePlug, "alphaWeight" ),
			( Gaffer.WeightVectorPlug, "instrumentIds" ),
			( Gaffer.MarketContextPlug, "timeNanoseconds" ),
		) :
			p = plugFactory()
			self.assertEqual( Gaffer.Metadata.value( p, "nodule:type" ), "GafferUI::CompoundNodule" )
			self.assertEqual( Gaffer.Metadata.value( p[childName], "nodule:type" ), "GafferUI::StandardNodule" )

	def testJsonDictInterchange( self ) :

		series = Gaffer.SeriesPlug()
		series.timesPlug().setValue( IECore.Int64VectorData( [ 1, 2 ] ) )
		series.valuesPlug().setValue( IECore.FloatVectorData( [ 0.1, 0.2 ] ) )
		seriesCopy = Gaffer.SeriesPlug()
		d = MarketDataAlgo.seriesPlugToDict( series )
		self.assertEqual( json.loads( json.dumps( d ) ), d )
		MarketDataAlgo.applySeriesPlugDict( seriesCopy, d )
		self.assertEqual( seriesCopy.timesPlug().getValue(), series.timesPlug().getValue() )
		self.assertEqual(
			self.__floatVectorReadable32( seriesCopy.valuesPlug().getValue() ),
			self.__floatVectorReadable32( series.valuesPlug().getValue() ),
		)

		sig = Gaffer.SignalClosurePlug()
		sig.alphaWeightPlug().setValue( 0.3 )
		sig.regimeConditionPlug().setValue( "abc" )
		sigCopy = Gaffer.SignalClosurePlug()
		sd = MarketDataAlgo.signalClosurePlugToDict( sig )
		self.assertEqual( json.loads( json.dumps( sd ) ), sd )
		MarketDataAlgo.applySignalClosurePlugDict( sigCopy, sd )
		self.assertFloat32Equal( sigCopy.alphaWeightPlug().getValue(), 0.3 )
		self.assertEqual( sigCopy.regimeConditionPlug().getValue(), "abc" )

		w = Gaffer.WeightVectorPlug()
		w.instrumentIdsPlug().setValue( IECore.StringVectorData( [ "X", "Y" ] ) )
		w.targetWeightsPlug().setValue( IECore.FloatVectorData( [ 0.2, 0.8 ] ) )
		w.confidencesPlug().setValue( IECore.FloatVectorData( [ 0.9, 0.8 ] ) )
		w.grossExposurePlug().setValue( 1.0 )
		w.netExposurePlug().setValue( 0.0 )
		w.activeRegimePlug().setValue( "foo" )
		w.evaluatedAtPlug().setValue( "ts1" )
		wCopy = Gaffer.WeightVectorPlug()
		wd = MarketDataAlgo.weightVectorPlugToDict( w )
		self.assertEqual( json.loads( json.dumps( wd ) ), wd )
		MarketDataAlgo.applyWeightVectorPlugDict( wCopy, wd )
		self.assertEqual( wCopy.instrumentIdsPlug().getValue(), w.instrumentIdsPlug().getValue() )
		self.assertEqual(
			self.__floatVectorReadable32( wCopy.targetWeightsPlug().getValue() ),
			self.__floatVectorReadable32( w.targetWeightsPlug().getValue() ),
		)
		self.assertEqual(
			self.__floatVectorReadable32( wCopy.confidencesPlug().getValue() ),
			self.__floatVectorReadable32( w.confidencesPlug().getValue() ),
		)
		self.assertFloat32Equal( wCopy.grossExposurePlug().getValue(), w.grossExposurePlug().getValue() )
		self.assertFloat32Equal( wCopy.netExposurePlug().getValue(), w.netExposurePlug().getValue() )
		self.assertEqual( wCopy.activeRegimePlug().getValue(), w.activeRegimePlug().getValue() )
		self.assertEqual( wCopy.evaluatedAtPlug().getValue(), w.evaluatedAtPlug().getValue() )

		mc = Gaffer.MarketContextPlug()
		mc.timeNanosecondsPlug().setValue( "t0" )
		mc.macroRegimePlug().setValue( "r0" )
		mc.vixLevelPlug().setValue( 11.0 )
		mc.termSpreadPlug().setValue( 0.12 )
		mc.creditSpreadPlug().setValue( 3.4 )
		mcCopy = Gaffer.MarketContextPlug()
		md = MarketDataAlgo.marketContextPlugToDict( mc )
		self.assertEqual( json.loads( json.dumps( md ) ), md )
		MarketDataAlgo.applyMarketContextPlugDict( mcCopy, md )
		self.assertEqual( mcCopy.timeNanosecondsPlug().getValue(), mc.timeNanosecondsPlug().getValue() )
		self.assertEqual( mcCopy.macroRegimePlug().getValue(), mc.macroRegimePlug().getValue() )
		self.assertFloat32Equal( mcCopy.vixLevelPlug().getValue(), mc.vixLevelPlug().getValue() )
		self.assertFloat32Equal( mcCopy.termSpreadPlug().getValue(), mc.termSpreadPlug().getValue() )
		self.assertFloat32Equal( mcCopy.creditSpreadPlug().getValue(), mc.creditSpreadPlug().getValue() )

	def testDynamicSerialisation( self ) :

		dynamic = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic

		s = Gaffer.ScriptNode()
		s["n"] = Gaffer.Node()
		s["n"]["series"] = Gaffer.SeriesPlug( flags = dynamic )
		s["n"]["series"].timesPlug().setValue( IECore.Int64VectorData( [ 10, 20 ] ) )
		s["n"]["series"].valuesPlug().setValue( IECore.FloatVectorData( [ 1.0, 2.0 ] ) )
		s["n"]["sig"] = Gaffer.SignalClosurePlug( flags = dynamic )
		s["n"]["sig"].alphaWeightPlug().setValue( 0.1 )
		s["n"]["sig"].regimeConditionPlug().setValue( "test" )
		s["n"]["weights"] = Gaffer.WeightVectorPlug( flags = dynamic )
		s["n"]["weights"].instrumentIdsPlug().setValue( IECore.StringVectorData( [ "A", "B" ] ) )
		s["n"]["weights"].targetWeightsPlug().setValue( IECore.FloatVectorData( [ 0.5, 0.5 ] ) )
		s["n"]["weights"].grossExposurePlug().setValue( 1.0 )
		s["n"]["mc"] = Gaffer.MarketContextPlug( flags = dynamic )
		s["n"]["mc"].timeNanosecondsPlug().setValue( "99" )
		s["n"]["mc"].macroRegimePlug().setValue( "mid" )
		s["n"]["mc"].vixLevelPlug().setValue( 22.0 )
		s["n"]["mc"].termSpreadPlug().setValue( 0.4 )
		s["n"]["mc"].creditSpreadPlug().setValue( 1.1 )

		ss = s.serialise()
		s2 = Gaffer.ScriptNode()
		s2.execute( ss )

		self.assertEqual( s2["n"]["series"].timesPlug().getValue(), IECore.Int64VectorData( [ 10, 20 ] ) )
		self.assertEqual(
			self.__floatVectorReadable32( s2["n"]["series"].valuesPlug().getValue() ),
			[ GafferTest.asFloat32( x ) for x in ( 1.0, 2.0 ) ],
		)
		self.assertFloat32Equal( s2["n"]["sig"].alphaWeightPlug().getValue(), 0.1 )
		self.assertEqual( s2["n"]["sig"].regimeConditionPlug().getValue(), "test" )
		self.assertEqual(
			s2["n"]["weights"].instrumentIdsPlug().getValue(),
			IECore.StringVectorData( [ "A", "B" ] ),
		)
		self.assertEqual(
			self.__floatVectorReadable32( s2["n"]["weights"].targetWeightsPlug().getValue() ),
			[ GafferTest.asFloat32( x ) for x in ( 0.5, 0.5 ) ],
		)
		self.assertFloat32Equal( s2["n"]["weights"].grossExposurePlug().getValue(), 1.0 )
		self.assertEqual( s2["n"]["mc"].timeNanosecondsPlug().getValue(), "99" )
		self.assertEqual( s2["n"]["mc"].macroRegimePlug().getValue(), "mid" )
		self.assertFloat32Equal( s2["n"]["mc"].vixLevelPlug().getValue(), 22.0 )
		self.assertFloat32Equal( s2["n"]["mc"].termSpreadPlug().getValue(), 0.4 )
		self.assertFloat32Equal( s2["n"]["mc"].creditSpreadPlug().getValue(), 1.1 )

if __name__ == "__main__":
	unittest.main()
