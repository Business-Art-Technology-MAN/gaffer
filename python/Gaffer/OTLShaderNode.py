##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

from __future__ import annotations

import os

import IECore

import Gaffer

import Gaffer.otl as otl


_DYNAMIC = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic


def _scalar_default( p : otl.ParamDecl ) -> object :

	if p.defaultValue is not None :
		return p.defaultValue
	if p.paramType == "float" :
		return 0.0
	if p.paramType == "int" :
		return 0
	if p.paramType == "string" :
		return ""
	if p.paramType == "bool" :
		return False
	return None


def _make_param_plug( p : otl.ParamDecl ) -> Gaffer.Plug :

	dv = _scalar_default( p )
	if p.paramType == "float" :
		return Gaffer.FloatPlug(
			p.name,
			Gaffer.Plug.Direction.In,
			float( dv ),
			flags = _DYNAMIC,
		)
	if p.paramType == "int" :
		return Gaffer.IntPlug(
			p.name,
			Gaffer.Plug.Direction.In,
			int( dv ),
			flags = _DYNAMIC,
		)
	if p.paramType == "string" :
		return Gaffer.StringPlug(
			p.name,
			Gaffer.Plug.Direction.In,
			str( dv ),
			flags = _DYNAMIC,
		)
	if p.paramType == "bool" :
		return Gaffer.BoolPlug(
			p.name,
			Gaffer.Plug.Direction.In,
			bool( dv ),
			flags = _DYNAMIC,
		)
	raise otl.OTLParseError( f"Unknown OTL parameter type {p.paramType!r}" )


def _plug_scalar_value( plug : Gaffer.ValuePlug ) -> object :

	if isinstance( plug, Gaffer.FloatPlug ) :
		return float( plug.getValue() )
	if isinstance( plug, Gaffer.IntPlug ) :
		return int( plug.getValue() )
	if isinstance( plug, Gaffer.StringPlug ) :
		return str( plug.getValue() )
	if isinstance( plug, Gaffer.BoolPlug ) :
		return bool( plug.getValue() )
	raise TypeError( f"Unsupported OTL parameter plug type: {type(plug).__name__}" )


## Loads a **``.otl``** shader, exposes **parameters** as **dynamic** input plugs, and
# evaluates a full **:class:`SignalClosurePlug`** on **``out``**.
#
# Call **:meth:`reloadParameterPlugs` after changing the shader **file** if its
# **parameter list** changes. Bumping **``refreshCount``** or editing the file (mtime)
# forces re-parse of the body for **hash** / **compute** without recreating plugs.
class OTLShaderNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "OTLShader" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["shaderPath"] = Gaffer.StringPlug(
			"shaderPath",
			Gaffer.Plug.Direction.In,
			"",
		)
		self["refreshCount"] = Gaffer.IntPlug(
			"refreshCount",
			Gaffer.Plug.Direction.In,
			0,
		)
		self["layerIndex"] = Gaffer.IntPlug(
			"layerIndex",
			Gaffer.Plug.Direction.In,
			0,
		)
		self["out"] = Gaffer.SignalClosurePlug(
			direction = Gaffer.Plug.Direction.Out,
		)

		self.__otlParamNames : list = []
		self.__astCacheKey = None
		self.__cachedAst = None

		self.__plugSetConnection = self.plugSetSignal().connect(
			Gaffer.WeakMethod( self.__shaderPathOrRefreshChanged ),
			scoped = True,
		)

	def __shaderPathOrRefreshChanged( self, plug : Gaffer.Plug ) -> None :

		if plug.isSame( self["shaderPath"] ) :
			try :
				self.reloadParameterPlugs()
			except Exception :
				## Leave existing plugs if the path is incomplete during scripted load.
				pass

	def _resolvedPath( self ) -> str :

		raw = self["shaderPath"].getValue()
		rp = otl.resolve_otl_shader_path( raw )
		if rp is None :
			raise otl.OTLParseError( f"OTL shader not found: {raw!r}" )
		return rp

	def reloadParameterPlugs( self ) -> None :

		raw = self["shaderPath"].getValue()
		if not raw :
			self._clearOtlParamPlugs()
			self.__cachedAst = None
			self.__astCacheKey = None
			return

		path = self._resolvedPath()
		ast = otl.parse_otl_file( path )
		otl.check_shader( ast )

		self._clearOtlParamPlugs()
		for p in ast.params :
			self.addChild( _make_param_plug( p ) )
			self.__otlParamNames.append( p.name )

		self.__cachedAst = ast
		self.__astCacheKey = ( path, os.path.getmtime( path ), self["refreshCount"].getValue() )

	def _clearOtlParamPlugs( self ) -> None :

		for n in list( self.__otlParamNames ) :
			if n in self :
				self.removeChild( self[n] )
		self.__otlParamNames = []

	def _getAst( self ) -> otl.ShaderAST :

		path = self._resolvedPath()
		mtime = os.path.getmtime( path )
		key = ( path, mtime, self["refreshCount"].getValue() )
		if key == self.__astCacheKey and self.__cachedAst is not None :
			return self.__cachedAst
		ast = otl.parse_otl_file( path )
		otl.check_shader( ast )
		self.__cachedAst = ast
		self.__astCacheKey = key
		return ast

	def _paramValues( self, ast : otl.ShaderAST ) -> dict :

		values = {}
		for p in ast.params :
			if p.name in self :
				values[p.name] = _plug_scalar_value( self[p.name] )
			elif p.defaultValue is not None :
				values[p.name] = p.defaultValue
			else :
				values[p.name] = _scalar_default( p )
		return values

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )
		sp = self["out"]
		touched = (
			inputPlug.isSame( self["shaderPath"] )
			or inputPlug.isSame( self["refreshCount"] )
		)
		for pn in self.__otlParamNames :
			if pn in self and inputPlug.isSame( self[pn] ) :
				touched = True
				break
		if touched :
			for c in (
				"alphaWeight",
				"confidence",
				"halfLife",
				"maxImpactFrac",
				"regimeCondition",
				"sideBet",
			) :
				outputs.append( sp[c] )
		return outputs

	def hash( self, output, context, h ) :

		if output.parent() is not None and output.parent().isSame( self["out"] ) :
			self["shaderPath"].hash( h )
			self["refreshCount"].hash( h )
			try :
				mt = os.path.getmtime( self._resolvedPath() )
				h.append( IECore.StringData( str( mt ) ) )
			except Exception :
				pass
			for pn in sorted( self.__otlParamNames ) :
				if pn in self :
					self[pn].hash( h )
		else :
			Gaffer.ComputeNode.hash( self, output, context, h )

	def compute( self, plug, context ) :

		parent = plug.parent()
		if parent is not None and parent.isSame( self["out"] ) :

			ast = self._getAst()
			d = otl.eval_signal_dict( ast, self._paramValues( ast ) )
			if plug.isSame( self["out"]["alphaWeight"] ) :
				plug.setValue( float( d["alphaWeight"] ) )
			elif plug.isSame( self["out"]["confidence"] ) :
				plug.setValue( float( d["confidence"] ) )
			elif plug.isSame( self["out"]["halfLife"] ) :
				plug.setValue( float( d["halfLife"] ) )
			elif plug.isSame( self["out"]["maxImpactFrac"] ) :
				plug.setValue( float( d["maxImpactFrac"] ) )
			elif plug.isSame( self["out"]["regimeCondition"] ) :
				plug.setValue( str( d["regimeCondition"] ) )
			elif plug.isSame( self["out"]["sideBet"] ) :
				plug.setValue( bool( d["sideBet"] ) )
			else :
				Gaffer.ComputeNode.compute( self, plug, context )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( OTLShaderNode, typeName = "Gaffer::OTLShaderNode" )
