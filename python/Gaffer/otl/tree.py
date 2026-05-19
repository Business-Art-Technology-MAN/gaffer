##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Union


@dataclass
class ParamDecl :

	name : str
	paramType : str  # float | int | string | bool
	defaultValue : Optional[object] = None


@dataclass
class ShaderAST :

	name : str
	params : List[ParamDecl]
	signalAssignments : Dict[str, "Expr"]  # field name -> expr


@dataclass
class NumberExpr :

	value : float
	isInt : bool = False


@dataclass
class StringExpr :

	value : str


@dataclass
class BoolExpr :

	value : bool


@dataclass
class NameExpr :

	name : str


@dataclass
class UnaryExpr :

	op : str  # '-'
	expr : "Expr"


@dataclass
class BinaryExpr :

	left : "Expr"
	op : str  # + - * / %
	right : "Expr"


@dataclass
class CallExpr :

	name : str
	args : List["Expr"]


Expr = Union[
	NumberExpr,
	StringExpr,
	BoolExpr,
	NameExpr,
	UnaryExpr,
	BinaryExpr,
	CallExpr,
]
