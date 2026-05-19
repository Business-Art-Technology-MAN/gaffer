##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

from __future__ import annotations

from typing import Set

from .errors import OTLMissingInputError, OTLTypeError_
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


REQUIRED_SIGNAL_FIELDS = frozenset( {
	"alphaWeight",
	"confidence",
	"halfLife",
	"maxImpactFrac",
	"regimeCondition",
	"sideBet",
} )


_FIELD_TYPES = {
	"alphaWeight": "float",
	"confidence": "float",
	"halfLife": "float",
	"maxImpactFrac": "float",
	"regimeCondition": "string",
	"sideBet": "bool",
}

_BUILTIN_FUNCS = frozenset( { "min", "max", "abs", "clamp" } )


def _expr_names_and_calls( e : Expr, names : Set[str], calls : Set[str] ) -> None :

	if isinstance( e, NameExpr ) :
		names.add( e.name )
	elif isinstance( e, CallExpr ) :
		calls.add( e.name )
		for a in e.args :
			_expr_names_and_calls( a, names, calls )
	elif isinstance( e, UnaryExpr ) :
		_expr_names_and_calls( e.expr, names, calls )
	elif isinstance( e, BinaryExpr ) :
		_expr_names_and_calls( e.left, names, calls )
		_expr_names_and_calls( e.right, names, calls )


def _literal_kind( e : Expr ) -> str :

	if isinstance( e, NumberExpr ) :
		return "int" if e.isInt else "float"
	if isinstance( e, StringExpr ) :
		return "string"
	if isinstance( e, BoolExpr ) :
		return "bool"
	return ""


def check_shader( ast : ShaderAST ) -> None :

	pnames = [ p.name for p in ast.params ]
	if len( pnames ) != len( set( pnames ) ) :
		raise OTLTypeError_( "Duplicate OTL shader parameter name" )

	got = set( ast.signalAssignments.keys() )
	if got != REQUIRED_SIGNAL_FIELDS :
		missing = REQUIRED_SIGNAL_FIELDS - got
		extra = got - REQUIRED_SIGNAL_FIELDS
		msg = []
		if missing :
			msg.append( "missing fields: " + ", ".join( sorted( missing ) ) )
		if extra :
			msg.append( "unknown fields: " + ", ".join( sorted( extra ) ) )
		raise OTLTypeError_( "Invalid signal() block: " + "; ".join( msg ) )

	paramSet = set( pnames )
	for field, expr in ast.signalAssignments.items() :
		want = _FIELD_TYPES[field]
		lk = _literal_kind( expr )
		if lk and lk != want and not ( want == "float" and lk == "int" ) :
			raise OTLTypeError_(
				f"Field {field!r} expects type {want!r}, got literal of type {lk!r}"
			)

		idNames : Set[str] = set()
		callNames : Set[str] = set()
		_expr_names_and_calls( expr, idNames, callNames )

		unknownCalls = callNames - _BUILTIN_FUNCS
		if unknownCalls :
			raise OTLMissingInputError(
				"Unknown OTL call(s): " + ", ".join( sorted( unknownCalls ) )
			)

		bad = idNames - paramSet
		if bad :
			raise OTLMissingInputError(
				"OTL_MISSING_INPUT: undefined name(s) "
				+ ", ".join( sorted( bad ) )
				+ " (allowed: shader parameters and builtins only in v0.1)"
			)
