##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import unittest

import IECore

import Gaffer
import Gaffer.otl as otl
import GafferTest

from Gaffer.OTLShadingSystem import OTL_LAYER_VIOLATION, validate_otl_shader_network


class Phase4TrackBTest( GafferTest.TestCase ) :

	def testParseStdlibMomentum( self ) :

		path = str( otl.otl_stdlib_path() / "momentum.otl" )
		ast = otl.parse_otl_file( path )
		self.assertEqual( ast.name, "momentum" )
		otl.check_shader( ast )

	def testMissingInputRejected( self ) :

		src = """
		shader bad(float a = 1.0) {
		  signal(
		    alphaWeight = notThere,
		    confidence = 1.0,
		    halfLife = 21.0,
		    maxImpactFrac = 0.05,
		    regimeCondition = "x",
		    sideBet = false
		  );
		}
		"""
		ast = otl.parse_otl_string( src )
		with self.assertRaises( otl.OTLMissingInputError ) :
			otl.check_shader( ast )

	def testInvalidSignalFields( self ) :

		src = """
		shader bad(float a = 1.0) {
		  signal(
		    alphaWeight = 0.0,
		    confidence = 1.0,
		    halfLife = 21.0,
		    maxImpactFrac = 0.05,
		    regimeCondition = "x",
		    sideBet = false,
		    extraField = 1.0
		  );
		}
		"""
		ast = otl.parse_otl_string( src )
		with self.assertRaises( otl.OTLTypeError_ ) :
			otl.check_shader( ast )

	def testOTLShaderNodeStdlibCompute( self ) :

		n = Gaffer.OTLShaderNode()
		n["shaderPath"].setValue( "momentum.otl" )
		n.reloadParameterPlugs()
		n["scale"].setValue( 2.0 )
		self.assertFloat32Equal( n["out"]["alphaWeight"].getValue(), 0.2 )
		self.assertEqual( n["out"]["regimeCondition"].getValue(), "momentum" )

	def testOTLShaderNodeRefreshCount( self ) :

		n = Gaffer.OTLShaderNode()
		n["shaderPath"].setValue( "momentum.otl" )
		n.reloadParameterPlugs()
		n["scale"].setValue( 1.0 )
		_ = n["out"]["alphaWeight"].getValue()
		n["refreshCount"].setValue( 1 )
		self.assertFloat32Equal( n["out"]["alphaWeight"].getValue(), 0.1 )

	def testLayerViolationMessage( self ) :

		a = Gaffer.OTLShaderNode( "upstream" )
		b = Gaffer.OTLShaderNode( "downstream" )
		a["shaderPath"].setValue( "momentum.otl" )
		b["shaderPath"].setValue( "momentum.otl" )
		a.reloadParameterPlugs()
		b.reloadParameterPlugs()
		a["layerIndex"].setValue( 1 )
		b["layerIndex"].setValue( 0 )
		b["scale"].setInput( a["out"]["alphaWeight"] )

		msg = (
			"OTL layer order violation: 'upstream' (layerIndex=1) feeds "
			"'downstream' (layerIndex=0); require src.layerIndex < dst.layerIndex."
		)
		self.ignoreMessage( IECore.MessageHandler.Level.Warning, OTL_LAYER_VIOLATION, msg )

		self.assertFalse( validate_otl_shader_network( b, emitMessages = True ) )

	def testLayerOrderOk( self ) :

		a = Gaffer.OTLShaderNode( "upstream" )
		b = Gaffer.OTLShaderNode( "downstream" )
		a["shaderPath"].setValue( "momentum.otl" )
		b["shaderPath"].setValue( "momentum.otl" )
		a.reloadParameterPlugs()
		b.reloadParameterPlugs()
		a["layerIndex"].setValue( 0 )
		b["layerIndex"].setValue( 1 )
		b["scale"].setInput( a["out"]["alphaWeight"] )
		self.assertTrue( validate_otl_shader_network( b, emitMessages = True ) )


if __name__ == "__main__" :
	unittest.main()
