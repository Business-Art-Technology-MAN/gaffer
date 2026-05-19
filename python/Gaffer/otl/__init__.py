##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

"""
**OTL v0.1** — parse, type-check, and evaluate minimal ``.otl`` shaders (Phase 4 Track B).

See **SRD/otl/OTL_v0.1.g4** for the ANTLR-shaped spec; the shipped parser is pure Python
(:mod:`Gaffer.otl.parse`).
"""

from __future__ import annotations

import os
import pathlib
from typing import Optional

from .check import REQUIRED_SIGNAL_FIELDS, check_shader
from .errors import (
	OTL_MISSING_INPUT,
	OTL_PARSE_ERROR,
	OTL_TYPE_ERROR,
	OTLException,
	OTLMissingInputError,
	OTLParseError,
	OTLTypeError_,
)
from .evaluate import eval_expr, eval_signal_dict
from .parse import parse_otl_file, parse_otl_string
from .tree import Expr, ParamDecl, ShaderAST


def otl_package_path() -> pathlib.Path :

	return pathlib.Path( __file__ ).resolve().parent


def otl_stdlib_path() -> pathlib.Path :

	return otl_package_path() / "stdlib"


def resolve_otl_shader_path( pathStr : str, searchStdlib : bool = True ) -> Optional[str] :

	if not pathStr :
		return None
	p = pathlib.Path( os.path.expandvars( pathStr ) )
	if p.is_file() :
		return str( p.resolve() )
	if searchStdlib :
		q = otl_stdlib_path() / pathStr
		if q.is_file() :
			return str( q.resolve() )
	return None


__all__ = [
	"REQUIRED_SIGNAL_FIELDS",
	"OTL_MISSING_INPUT",
	"OTL_PARSE_ERROR",
	"OTL_TYPE_ERROR",
	"OTLException",
	"OTLMissingInputError",
	"OTLParseError",
	"OTLTypeError_",
	"ParamDecl",
	"ShaderAST",
	"Expr",
	"check_shader",
	"eval_expr",
	"eval_signal_dict",
	"parse_otl_file",
	"parse_otl_string",
	"otl_package_path",
	"otl_stdlib_path",
	"resolve_otl_shader_path",
]
