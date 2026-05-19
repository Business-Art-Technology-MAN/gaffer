##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

from __future__ import annotations

from typing import Dict, List, Optional

from .errors import OTLParseError
from .tree import (
	BinaryExpr,
	BoolExpr,
	CallExpr,
	Expr,
	NameExpr,
	NumberExpr,
	ParamDecl,
	ShaderAST,
	StringExpr,
	UnaryExpr,
)


class _Token :

	__slots__ = ( "kind", "value", "pos" )

	def __init__( self, kind : str, value : object, pos : int ) :

		self.kind = kind
		self.value = value
		self.pos = pos


class _Lexer :

	_keywords = {
		"shader": "SHADER",
		"signal": "SIGNAL",
		"float": "TYPE",
		"int": "TYPE",
		"string": "TYPE",
		"bool": "TYPE",
		"true": "TRUE",
		"false": "FALSE",
	}

	def __init__( self, text : str ) :

		self.text = text
		self.i = 0
		self.n = len( text )

	def _error( self, msg : str ) -> None :

		raise OTLParseError( f"{msg} (at char {self.i})" )

	def peek( self ) -> Optional[str] :

		if self.i >= self.n :
			return None
		return self.text[self.i]

	def _skip_ws_and_comments( self ) -> None :

		while self.i < self.n :
			c = self.text[self.i]
			if c in " \t\r\n" :
				self.i += 1
				continue
			if c == "/" and self.i + 1 < self.n and self.text[self.i + 1] == "/" :
				self.i += 2
				while self.i < self.n and self.text[self.i] not in "\r\n" :
					self.i += 1
				continue
			if c == "/" and self.i + 1 < self.n and self.text[self.i + 1] == "*" :
				self.i += 2
				while self.i + 1 < self.n and not ( self.text[self.i] == "*" and self.text[self.i + 1] == "/" ) :
					self.i += 1
				if self.i + 1 >= self.n :
					self._error( "Unterminated block comment" )
				self.i += 2
				continue
			break

	def _read_string( self, start : int ) -> str :

		self.i += 1
		chars : List[str] = []
		while self.i < self.n :
			c = self.text[self.i]
			if c == '"' :
				self.i += 1
				return "".join( chars )
			if c == "\\" :
				self.i += 1
				if self.i >= self.n :
					self._error( "Unterminated string escape" )
				ec = self.text[self.i]
				self.i += 1
				chars.append( { "n": "\n", "t": "\t", "r": "\r", '"' : '"', "\\" : "\\" }.get( ec, ec ) )
				continue
			chars.append( c )
			self.i += 1
		self._error( "Unterminated string literal" )

	def next_token( self ) -> _Token :

		self._skip_ws_and_comments()
		if self.i >= self.n :
			return _Token( "EOF", "", self.i )
		start = self.i
		c = self.text[self.i]

		if c == '"' :
			s = self._read_string( start )
			return _Token( "STRING", s, start )

		if c in "(),;{}=*+-/%" :
			self.i += 1
			return _Token( c, c, start )

		if c.isdigit() :
			j = self.i + 1
			while j < self.n and self.text[j].isdigit() :
				j += 1
			isFloat = False
			if j < self.n and self.text[j] == "." :
				isFloat = True
				j += 1
				while j < self.n and self.text[j].isdigit() :
					j += 1
			if j < self.n and self.text[j] in "eE" :
				isFloat = True
				j += 1
				if j < self.n and self.text[j] in "+-" :
					j += 1
				while j < self.n and self.text[j].isdigit() :
					j += 1
			raw = self.text[self.i:j]
			self.i = j
			if isFloat :
				return _Token( "FLOAT", float( raw ), start )
			return _Token( "INT", int( raw ), start )

		if c.isalpha() or c == "_" :
			j = self.i + 1
			while j < self.n and ( self.text[j].isalnum() or self.text[j] == "_" ) :
				j += 1
			name = self.text[self.i:j]
			self.i = j
			kw = self._keywords.get( name )
			if kw == "TYPE" :
				return _Token( "TYPE", name, start )
			if kw == "SHADER" :
				return _Token( "SHADER", name, start )
			if kw == "SIGNAL" :
				return _Token( "SIGNAL", name, start )
			if kw == "TRUE" :
				return _Token( "BOOL", True, start )
			if kw == "FALSE" :
				return _Token( "BOOL", False, start )
			return _Token( "IDENT", name, start )

		self._error( f"Unexpected character {c!r}" )


class _Parser :

	def __init__( self, text : str ) :

		self.lex = _Lexer( text )
		self.tok = self.lex.next_token()

	def _eat( self, kind : str ) -> _Token :

		if self.tok.kind != kind :
			raise OTLParseError(
				f"Expected {kind!r}, got {self.tok.kind!r} at {self.tok.pos}"
			)
		cur = self.tok
		self.tok = self.lex.next_token()
		return cur

	def _match( self, kind : str ) -> bool :

		if self.tok.kind == kind :
			self.tok = self.lex.next_token()
			return True
		return False

	def parse( self ) -> ShaderAST :

		self._eat( "SHADER" )
		nameTok = self._eat( "IDENT" )
		self._eat( "(" )
		params = self._param_list()
		self._eat( ")" )
		self._eat( "{" )
		assignments = self._body()
		self._eat( "}" )
		if self.tok.kind != "EOF" :
			raise OTLParseError( f"Unexpected token after shader: {self.tok.kind} at {self.tok.pos}" )
		return ShaderAST( name=nameTok.value, params=params, signalAssignments=assignments )

	def _param_list( self ) -> List[ParamDecl] :

		if self.tok.kind == ")" :
			return []
		params = [ self._param() ]
		while self._match( "," ) :
			params.append( self._param() )
		return params

	def _param( self ) -> ParamDecl :

		pt = self._eat( "TYPE" )
		nm = self._eat( "IDENT" )
		default : Optional[object] = None
		if self._match( "=" ) :
			expr = self._expr()
			default = _default_from_literal( expr )
		return ParamDecl( name=nm.value, paramType=pt.value, defaultValue=default )

	def _body( self ) -> Dict[str, Expr] :

		self._eat( "SIGNAL" )
		self._eat( "(" )
		args : Dict[str, Expr] = {}
		if self.tok.kind != ")" :
			self._signal_args( args )
		self._eat( ")" )
		self._eat( ";" )
		return args

	def _signal_args( self, out : Dict[str, Expr] ) -> None :

		while True :
			field = self._eat( "IDENT" )
			fn = str( field.value )
			if fn in out :
				raise OTLParseError( f"Duplicate signal field {fn!r}" )
			self._eat( "=" )
			out[fn] = self._expr()
			if not self._match( "," ) :
				break

	def _expr( self ) -> Expr :

		return self._expr_add()

	def _expr_add( self ) -> Expr :

		e = self._expr_mul()
		while self.tok.kind in "+-" :
			op = self.tok.kind
			self.tok = self.lex.next_token()
			r = self._expr_mul()
			e = BinaryExpr( left=e, op=op, right=r )
		return e

	def _expr_mul( self ) -> Expr :

		e = self._expr_unary()
		while self.tok.kind in "*/%" :
			op = self.tok.kind
			self.tok = self.lex.next_token()
			r = self._expr_unary()
			e = BinaryExpr( left=e, op=op, right=r )
		return e

	def _expr_unary( self ) -> Expr :

		if self.tok.kind == "-" :
			self.tok = self.lex.next_token()
			return UnaryExpr( op="-", expr=self._expr_unary() )
		return self._expr_primary()

	def _expr_primary( self ) -> Expr :

		t = self.tok
		if t.kind == "INT" :
			self.tok = self.lex.next_token()
			return NumberExpr( value=float( t.value ), isInt=True )
		if t.kind == "FLOAT" :
			self.tok = self.lex.next_token()
			return NumberExpr( value=float( t.value ), isInt=False )
		if t.kind == "STRING" :
			self.tok = self.lex.next_token()
			return StringExpr( value=str( t.value ) )
		if t.kind == "BOOL" :
			self.tok = self.lex.next_token()
			return BoolExpr( value=bool( t.value ) )
		if t.kind == "IDENT" :
			name = str( t.value )
			self.tok = self.lex.next_token()
			if self._match( "(" ) :
				args : List[Expr] = []
				if self.tok.kind != ")" :
					while True :
						args.append( self._expr() )
						if not self._match( "," ) :
							break
				self._eat( ")" )
				return CallExpr( name=name, args=args )
			return NameExpr( name=name )
		if self._match( "(" ) :
			e = self._expr()
			self._eat( ")" )
			return e
		raise OTLParseError( f"Unexpected token in expression: {self.tok.kind} at {self.tok.pos}" )


def _default_from_literal( expr : Expr ) -> object :

	if isinstance( expr, NumberExpr ) :
		return int( expr.value ) if expr.isInt else float( expr.value )
	if isinstance( expr, StringExpr ) :
		return expr.value
	if isinstance( expr, BoolExpr ) :
		return expr.value
	raise OTLParseError(
		"Shader parameter default must be a literal (not a complex expression) in OTL v0.1"
	)


def parse_otl_string( source : str ) -> ShaderAST :

	return _Parser( source ).parse()


def parse_otl_file( path : str ) -> ShaderAST :

	with open( path, "r", encoding="utf-8" ) as f :
		return parse_otl_string( f.read() )
