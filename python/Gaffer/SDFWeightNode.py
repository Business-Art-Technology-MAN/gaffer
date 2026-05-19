##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

import IECore

import Gaffer

from .SignalNodeAlgo import sdf_projection_alpha


def _matrix_panel_rows( matrixPlug : Gaffer.MatrixPlug ) -> list :

	times = list( matrixPlug["rowTimes"].getValue() )
	flat = list( matrixPlug["valuesRowMajor"].getValue() )
	nc = matrixPlug["numColumns"].getValue()
	n = len( times )
	if nc < 1 or n < 1 or len( flat ) != n * nc :
		return []
	rows = []
	for r in range( n ) :
		rows.append( [ float( flat[r * nc + c] ) for c in range( nc ) ] )
	return rows


def _vector_values( vectorPlug : Gaffer.VectorPlug ) -> list :

	return [ float( x ) for x in vectorPlug["values"].getValue() ]


## Phase 4 **Track A** — linear SDF projection (Avramov–He-style).
#
# * **ff_loadings** — factor exposures (length **F**).
# * **factor_ret** — expected factor payoffs / premia (length **F**).
# * **conn_matrix** — **T×F** factor panel (``MatrixPlug``); trailing **cov_window** rows build **Σ**.
#
# Fills **SignalClosurePlug** ``alphaWeight`` / ``confidence``; other fields come from parameters.
class SDFWeightNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "SDFWeight" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["ffLoadings"] = Gaffer.VectorPlug()
		self["connMatrix"] = Gaffer.MatrixPlug()
		self["factorRet"] = Gaffer.VectorPlug()

		self["covWindow"] = Gaffer.IntPlug( defaultValue = 60, minValue = 2 )
		self["ridge"] = Gaffer.FloatPlug( defaultValue = 1e-6, minValue = 0.0 )
		self["halfLife"] = Gaffer.FloatPlug( defaultValue = 63.0, minValue = 1e-6 )
		self["maxImpactFrac"] = Gaffer.FloatPlug( defaultValue = 0.05, minValue = 0.0 )
		self["regimeCondition"] = Gaffer.StringPlug( defaultValue = "sdf_projection" )
		self["sideBet"] = Gaffer.BoolPlug( defaultValue = False )

		self["out"] = Gaffer.SignalClosurePlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )

		def vec_dep( vp ) :
			return inputPlug.isSame( vp ) or (
				inputPlug.parent() is not None and inputPlug.parent().isSame( vp )
			)

		def mat_dep( mp ) :
			return inputPlug.isSame( mp ) or (
				inputPlug.parent() is not None and inputPlug.parent().isSame( mp )
			)

		out_children = (
			"alphaWeight",
			"confidence",
			"halfLife",
			"maxImpactFrac",
			"regimeCondition",
			"sideBet",
		)

		if (
			vec_dep( self["ffLoadings"] )
			or vec_dep( self["factorRet"] )
			or mat_dep( self["connMatrix"] )
			or inputPlug.isSame( self["covWindow"] )
			or inputPlug.isSame( self["ridge"] )
			or inputPlug.isSame( self["halfLife"] )
			or inputPlug.isSame( self["maxImpactFrac"] )
			or inputPlug.isSame( self["regimeCondition"] )
			or inputPlug.isSame( self["sideBet"] )
		) :
			for c in out_children :
				outputs.append( self["out"][c] )

		return outputs

	def hash( self, output, context, h ) :

		if output.parent() is not None and output.parent().isSame( self["out"] ) :
			self["ffLoadings"]["values"].hash( h )
			self["connMatrix"]["rowTimes"].hash( h )
			self["connMatrix"]["valuesRowMajor"].hash( h )
			self["connMatrix"]["numColumns"].hash( h )
			self["factorRet"]["values"].hash( h )
			self["covWindow"].hash( h )
			self["ridge"].hash( h )
			self["halfLife"].hash( h )
			self["maxImpactFrac"].hash( h )
			self["regimeCondition"].hash( h )
			self["sideBet"].hash( h )

	def compute( self, plug, context ) :

		parent = plug.parent()
		if parent is not None and parent.isSame( self["out"] ) :

			rows = _matrix_panel_rows( self["connMatrix"] )
			L = _vector_values( self["ffLoadings"] )
			r = _vector_values( self["factorRet"] )
			w = self["covWindow"].getValue()
			ridge = float( self["ridge"].getValue() )

			alpha, conf = sdf_projection_alpha( L, r, rows, w, ridge )

			if plug.isSame( self["out"]["alphaWeight"] ) :
				plug.setValue( alpha )
			elif plug.isSame( self["out"]["confidence"] ) :
				plug.setValue( conf )
			elif plug.isSame( self["out"]["halfLife"] ) :
				plug.setValue( float( self["halfLife"].getValue() ) )
			elif plug.isSame( self["out"]["maxImpactFrac"] ) :
				plug.setValue( float( self["maxImpactFrac"].getValue() ) )
			elif plug.isSame( self["out"]["regimeCondition"] ) :
				plug.setValue( self["regimeCondition"].getValue() )
			elif plug.isSame( self["out"]["sideBet"] ) :
				plug.setValue( self["sideBet"].getValue() )
			else :
				Gaffer.ComputeNode.compute( self, plug, context )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( SDFWeightNode, typeName = "Gaffer::SDFWeightNode" )
