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
#        disclaimer in the documentation and/or other materials provided
#        with the distribution.
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

import importlib.util
import os
import tempfile
import unittest

import IECore

import Gaffer
import GafferTest


def _pyarrowAvailable() :

	return importlib.util.find_spec( "pyarrow" ) is not None


class TimeSeriesStoreNodeTest( GafferTest.TestCase ) :

	def setUp( self ) :

		Gaffer.MarketDataTimeseries.clearRegistry()

	def tearDown( self ) :

		Gaffer.MarketDataTimeseries.clearRegistry()

	@staticmethod
	def __floatValues( floatVectorData ) :

		return [ GafferTest.asFloat32( floatVectorData[i] ) for i in range( len( floatVectorData ) ) ]

	def testMemoryEmpty( self ) :

		n = Gaffer.TimeSeriesStoreNode()
		n["instrumentId"].setValue( "X" )
		n["field"].setValue( "close" )

		self.assertEqual( len( n["out"]["times"].getValue() ), 0 )
		self.assertEqual( len( n["out"]["values"].getValue() ), 0 )

	def testMemoryRegistered( self ) :

		Gaffer.MarketDataTimeseries.registerSeries(
			"AAA",
			"close",
			[ 1, 2, 3 ],
			[ 10.0, 20.0, 30.0 ],
		)

		n = Gaffer.TimeSeriesStoreNode()
		n["instrumentId"].setValue( "AAA" )
		n["field"].setValue( "close" )
		n["lookback"].setValue( 0 )

		self.assertEqual( n["out"]["times"].getValue(), IECore.Int64VectorData( [ 1, 2, 3 ] ) )
		self.assertEqual(
			self.__floatValues( n["out"]["values"].getValue() ),
			[ GafferTest.asFloat32( x ) for x in ( 10.0, 20.0, 30.0 ) ],
		)

	def testLookback( self ) :

		Gaffer.MarketDataTimeseries.registerSeries(
			"LB",
			"close",
			[ 1, 2, 3, 4, 5 ],
			[ 1.0, 2.0, 3.0, 4.0, 5.0 ],
		)

		n = Gaffer.TimeSeriesStoreNode()
		n["instrumentId"].setValue( "LB" )
		n["lookback"].setValue( 3 )

		self.assertEqual( n["out"]["times"].getValue(), IECore.Int64VectorData( [ 3, 4, 5 ] ) )

	def testPceTimeContext( self ) :

		Gaffer.MarketDataTimeseries.registerSeries(
			"PIT",
			"close",
			[ 1, 2, 5, 10 ],
			[ 1.0, 1.0, 1.0, 1.0 ],
		)

		n = Gaffer.TimeSeriesStoreNode()
		n["instrumentId"].setValue( "PIT" )
		n["lookback"].setValue( 0 )

		c = Gaffer.Context()
		c[ Gaffer.MarketDataTimeseries.PCE_TIME_CONTEXT_KEY ] = 5

		with c :
			self.assertEqual( n["out"]["times"].getValue(), IECore.Int64VectorData( [ 1, 2, 5 ] ) )

	def testRefreshCountChangesHash( self ) :

		Gaffer.MarketDataTimeseries.registerSeries( "R", "close", [ 1 ], [ 1.0 ] )

		n = Gaffer.TimeSeriesStoreNode()
		n["instrumentId"].setValue( "R" )
		n["lookback"].setValue( 0 )

		h0 = n["out"]["times"].hash()
		n["refreshCount"].setValue( 1 )
		h1 = n["out"]["times"].hash()
		self.assertNotEqual( h0, h1 )

	def testArcticDbRequiresUriOrPackage( self ) :

		n = Gaffer.TimeSeriesStoreNode()
		n["backend"].setValue( "arcticdb" )
		n["resourcePath"].setValue( "" )

		with self.assertRaises( Gaffer.ProcessException ) as cm :
			n["out"]["times"].getValue()

		msg = str( cm.exception ).lower()
		self.assertTrue(
			"arcticdb" in msg or "resourcepath" in msg or "requires" in msg,
			msg,
		)

	@unittest.skipUnless( Gaffer.ArcticBackend.arcticdbAvailable(), "arcticdb / pandas not installed" )
	def testArcticDbReadsLmdb( self ) :

		import shutil

		import pandas as pd
		from arcticdb import Arctic

		d = tempfile.mkdtemp( prefix = "gaffer_arctic_" )
		try :
			uri = "lmdb://" + os.path.abspath( d ).replace( "\\", "/" )
			ac = Arctic( uri )
			ac.create_library( "pce" )
			lib = ac["pce"]
			idx = pd.date_range( "2020-01-01", periods = 3, freq = "D" )
			lib.write( "AAA", pd.DataFrame( { "close": [ 10.0, 11.0, 12.0 ] }, index = idx ) )
			# LMDB: one open per path per process — release before the store opens the same URI.
			del lib, ac

			n = Gaffer.TimeSeriesStoreNode()
			n["backend"].setValue( "arcticdb" )
			n["resourcePath"].setValue( uri )
			n["arcticLibrary"].setValue( "pce" )
			n["instrumentId"].setValue( "AAA" )
			n["field"].setValue( "close" )

			self.assertEqual( len( n["out"]["times"].getValue() ), 3 )
			self.assertEqual(
				self.__floatValues( n["out"]["values"].getValue() ),
				[ GafferTest.asFloat32( x ) for x in ( 10.0, 11.0, 12.0 ) ],
			)
		finally :
			shutil.rmtree( d, ignore_errors = True )

	@unittest.skipUnless( Gaffer.ArcticBackend.arcticdbAvailable(), "arcticdb / pandas not installed" )
	def testArcticDbWriteThenReadViaStore( self ) :

		import shutil

		import pandas as pd

		d = tempfile.mkdtemp( prefix = "gaffer_arctic_w_" )
		try :
			uri = "lmdb://" + os.path.abspath( d ).replace( "\\", "/" )
			idx = pd.date_range( "2020-01-01", periods = 3, freq = "D" )
			times = [ int( ts.value ) for ts in idx ]
			values = [ 10.0, 11.0, 12.0 ]

			Gaffer.ArcticBackend.write_series_for_store(
				uri, "pce", "ZZ", times, values, "close", createLibrary = True,
			)

			n = Gaffer.TimeSeriesStoreNode()
			n["backend"].setValue( "arcticdb" )
			n["resourcePath"].setValue( uri )
			n["arcticLibrary"].setValue( "pce" )
			n["instrumentId"].setValue( "ZZ" )
			n["field"].setValue( "close" )

			self.assertEqual( len( n["out"]["times"].getValue() ), 3 )
			self.assertEqual(
				self.__floatValues( n["out"]["values"].getValue() ),
				[ GafferTest.asFloat32( x ) for x in ( 10.0, 11.0, 12.0 ) ],
			)
		finally :
			shutil.rmtree( d, ignore_errors = True )

	@unittest.skipUnless( Gaffer.ArcticBackend.arcticdbAvailable(), "arcticdb / pandas not installed" )
	def testArcticDbAppendThenRead( self ) :

		import shutil

		import pandas as pd

		d = tempfile.mkdtemp( prefix = "gaffer_arctic_a_" )
		try :
			uri = "lmdb://" + os.path.abspath( d ).replace( "\\", "/" )
			idx0 = pd.date_range( "2020-01-01", periods = 2, freq = "D" )
			t0 = [ int( ts.value ) for ts in idx0 ]
			Gaffer.ArcticBackend.write_series_for_store(
				uri, "pce", "APP", t0, [ 1.0, 2.0 ], "close", createLibrary = True,
			)
			idx1 = pd.date_range( "2020-01-03", periods = 1, freq = "D" )
			t1 = [ int( ts.value ) for ts in idx1 ]
			Gaffer.ArcticBackend.append_series_for_store(
				uri, "pce", "APP", t1, [ 3.0 ], "close",
			)

			n = Gaffer.TimeSeriesStoreNode()
			n["backend"].setValue( "arcticdb" )
			n["resourcePath"].setValue( uri )
			n["arcticLibrary"].setValue( "pce" )
			n["instrumentId"].setValue( "APP" )
			n["field"].setValue( "close" )

			self.assertEqual( len( n["out"]["times"].getValue() ), 3 )
			self.assertEqual(
				self.__floatValues( n["out"]["values"].getValue() ),
				[ GafferTest.asFloat32( x ) for x in ( 1.0, 2.0, 3.0 ) ],
			)
		finally :
			shutil.rmtree( d, ignore_errors = True )

	@unittest.skipUnless( Gaffer.ArcticBackend.arcticdbAvailable(), "arcticdb / pandas not installed" )
	def testArcticDbListLibrariesAndSymbols( self ) :

		import shutil

		import pandas as pd

		d = tempfile.mkdtemp( prefix = "gaffer_arctic_ls_" )
		try :
			uri = "lmdb://" + os.path.abspath( d ).replace( "\\", "/" )
			self.assertEqual( Gaffer.ArcticBackend.list_libraries( uri ), [] )

			idx = pd.date_range( "2020-01-01", periods = 1, freq = "D" )
			t = [ int( ts.value ) for ts in idx ]
			Gaffer.ArcticBackend.write_series_for_store(
				uri, "pce2", "SYM_A", t, [ 42.0 ], "close", createLibrary = True,
			)
			Gaffer.ArcticBackend.write_series_for_store(
				uri, "pce2", "SYM_B", t, [ 43.0 ], "close", createLibrary = False,
			)

			self.assertEqual( Gaffer.ArcticBackend.list_libraries( uri ), [ "pce2" ] )
			self.assertEqual(
				Gaffer.ArcticBackend.list_symbols( uri, "pce2" ),
				[ "SYM_A", "SYM_B" ],
			)
		finally :
			shutil.rmtree( d, ignore_errors = True )

	def testUnknownBackend( self ) :

		n = Gaffer.TimeSeriesStoreNode()
		n["backend"].setValue( "nope" )

		with self.assertRaisesRegex( Gaffer.ProcessException, r"out\.times : [\s\S]*unknown backend.*nope" ) :
			n["out"]["times"].getValue()

	@unittest.skipUnless( _pyarrowAvailable(), "pyarrow not installed" )
	def testParquet( self ) :

		import pyarrow as pa
		import pyarrow.parquet as pq

		fd, path = tempfile.mkstemp( suffix = ".parquet" )
		os.close( fd )
		try :
			table = pa.table(
				{
					"time" : [ 100, 200, 300 ],
					"close" : [ 1.0, 2.0, 3.0 ],
				}
			)
			pq.write_table( table, path )

			n = Gaffer.TimeSeriesStoreNode()
			n["backend"].setValue( "parquet" )
			n["resourcePath"].setValue( path )
			n["field"].setValue( "close" )
			n["lookback"].setValue( 2 )

			self.assertEqual( n["out"]["times"].getValue(), IECore.Int64VectorData( [ 200, 300 ] ) )
			self.assertEqual(
				self.__floatValues( n["out"]["values"].getValue() ),
				[ GafferTest.asFloat32( x ) for x in ( 2.0, 3.0 ) ],
			)
		finally :
			os.remove( path )

	def testSerialisation( self ) :

		Gaffer.MarketDataTimeseries.registerSeries(
			"S",
			"close",
			[ 9, 8 ],
			[ 0.5, 1.5 ],
		)

		script = Gaffer.ScriptNode()
		script["s"] = Gaffer.TimeSeriesStoreNode()
		script["s"]["instrumentId"].setValue( "S" )
		script["s"]["lookback"].setValue( 1 )
		script["s"]["refreshCount"].setValue( 3 )

		times = script["s"]["out"]["times"].getValue()

		script2 = Gaffer.ScriptNode()
		script2.execute( script.serialise() )

		self.assertEqual( script2["s"]["instrumentId"].getValue(), "S" )
		self.assertEqual( script2["s"]["arcticLibrary"].getValue(), "pce" )
		self.assertEqual( script2["s"]["lookback"].getValue(), 1 )
		self.assertEqual( script2["s"]["refreshCount"].getValue(), 3 )
		self.assertEqual( script2["s"]["out"]["times"].getValue(), times )


if __name__ == "__main__" :
	unittest.main()
