##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

"""Phase 2 exit story tests.

The ``gaffer test`` / ``MarketLab.cmd test`` loader resolves ``GafferTest.Phase2ExitCriterionTest`` to the **test class** (re-exported in ``GafferTest.__init__``), not the submodule. Use **three** dotted segments (or two for the whole class)—**not** four with the class name repeated::

	MarketLab.cmd test GafferTest.Phase2ExitCriterionTest
	MarketLab.cmd test GafferTest.Phase2ExitCriterionTest.testCsvToRollingReturnsToRealizedVolAndPceRoundTrip
"""

import os
import tempfile
import unittest

import Gaffer
import GafferTest


## Phase 2 exit criterion from the OTL plan: Layer 1 **data** → :class:`RollingReturnsNode`
# → :class:`RealizedVolNode`, with results inspectable and graph restored from **`.pce`**.
class Phase2ExitCriterionTest( GafferTest.TestCase ) :

	def testCsvToRollingReturnsToRealizedVolAndPceRoundTrip( self ) :

		csvLines = [ "time,close" ] + [ f"{i},{100.0 * ( 1.01 ** i ):.8f}" for i in range( 40 ) ]
		fd, csvPath = tempfile.mkstemp( suffix = ".csv", text = True )
		try :
			os.write( fd, ( "\n".join( csvLines ) + "\n" ).encode( "utf-8" ) )
		finally :
			os.close( fd )

		fd, pcePath = tempfile.mkstemp( suffix = ".pce", text = True )
		os.close( fd )

		try :
			script = Gaffer.ScriptNode()
			script["csv"] = Gaffer.SeriesCsvReaderNode()
			script["csv"]["filePath"].setValue( csvPath )
			script["csv"]["hasHeader"].setValue( True )
			script["csv"]["timeColumn"].setValue( 0 )
			script["csv"]["valueColumn"].setValue( 1 )

			script["rr"] = Gaffer.RollingReturnsNode()
			script["rr"]["in"].setInput( script["csv"]["out"] )
			script["rr"]["window"].setValue( 1 )

			script["rv"] = Gaffer.RealizedVolNode()
			script["rv"]["in"].setInput( script["rr"]["out"] )
			script["rv"]["window"].setValue( 5 )
			script["rv"]["annualizationFactor"].setValue( 1.0 )

			volBefore = script["rv"]["out"].getValue()
			self.assertGreater( volBefore, 0.0 )

			fmt = "usd" if Gaffer.usdAvailableForPce() else "legacy"
			Gaffer.savePceGraphFile(
				script,
				pcePath,
				{ "test" : "Phase2ExitCriterion" },
				graphFormat = fmt,
			)

			loaded = Gaffer.ScriptNode()
			loaded.execute( Gaffer.loadPceGraphFile( pcePath )[1] )
			self.assertAlmostEqual( loaded["rv"]["out"].getValue(), volBefore, places = 5 )
		finally :
			for p in ( csvPath, pcePath ) :
				try :
					os.remove( p )
				except OSError :
					pass


if __name__ == "__main__" :
	unittest.main()
