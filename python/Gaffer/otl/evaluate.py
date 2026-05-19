##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

from __future__ import annotations

from typing import Any, Dict, Mapping

from .errors import OTLTypeError_
from .tree import (
	BinaryExpr,
	BoolExpr,
	CallExpr,
	Expr,
	NameExpr,
	NumberExpr,
	ShaderAST,
	StringExpr,
	UnaryExpr,
)

_SIGNAL_CLOSURE_KEYS = (
	"alphaWeight",
	"confidence",
	"halfLife",
	"maxImpactFrac",
	"regimeCondition",
	"sideBet",
)


def _builtin_min( *a : float ) -> float :

	return float( min( a ) )


def _builtin_max( *a : float ) -> float :

	return float( max( a ) )


def _builtin_abs( x : float ) -> float :

	return float( abs( x ) )


def _builtin_clamp( x : float, lo : float, hi : float ) -> float :

	return float( min( hi, max( lo, x ) ) )


_BUILTINS : Dict[str, Any] = {
	"min": _builtin_min,
	"max": _builtin_max,
	"abs": _builtin_abs,
	"clamp": _builtin_clamp,
}


def eval_expr( expr : Expr, env : Mapping[str, Any] ) -> Any :

	if isinstance( expr, NumberExpr ) :
		return int( expr.value ) if expr.isInt else float( expr.value )
	if isinstance( expr, StringExpr ) :
		return expr.value
	if isinstance( expr, BoolExpr ) :
		return bool( expr.value )
	if isinstance( expr, NameExpr ) :
		if expr.name not in env :
			raise OTLTypeError_( f"Name {expr.name!r} not bound at evaluation time" )
		return env[expr.name]
	if isinstance( expr, UnaryExpr ) :
		if expr.op != "-" :
			raise OTLTypeError_( f"Unsupported unary {expr.op!r}" )
		v = eval_expr( expr.expr, env )
		return -float( v )
	if isinstance( expr, BinaryExpr ) :
		l = eval_expr( expr.left, env )
		r = eval_expr( expr.right, env )
		lf = float( l )
		rf = float( r )
		if expr.op == "+" :
			return lf + rf
		if expr.op == "-" :
			return lf - rf
		if expr.op == "*" :
			return lf * rf
		if expr.op == "/" :
			return lf / rf
		if expr.op == "%" :
			return lf % rf
		raise OTLTypeError_( f"Unsupported binary operator {expr.op!r}" )
	if isinstance( expr, CallExpr ) :
		fn = _BUILTINS.get( expr.name )
		if fn is None :
			raise OTLTypeError_( f"Unsupported call {expr.name!r}" )
		args = [ eval_expr( a, env ) for a in expr.args ]
		return fn( *args )

	raise OTLTypeError_( f"Unsupported expression {type(expr).__name__}" )


def eval_signal_dict( ast : ShaderAST, paramValues : Mapping[str, Any] ) -> Dict[str, Any] :

	env : Dict[str, Any] = dict( paramValues )
	for p in ast.params :
		if p.name not in env and p.defaultValue is not None :
			env[p.name] = p.defaultValue
	out : Dict[str, Any] = {}
	for field in _SIGNAL_CLOSURE_KEYS :
		raw = eval_expr( ast.signalAssignments[field], env )
		if field == "alphaWeight" :
			out[field] = float( raw )
		elif field == "confidence" :
			out[field] = float( raw )
		elif field == "halfLife" :
			out[field] = float( raw )
		elif field == "maxImpactFrac" :
			out[field] = float( raw )
		elif field == "regimeCondition" :
			out[field] = str( raw )
		elif field == "sideBet" :
			out[field] = bool( raw )
	return out
