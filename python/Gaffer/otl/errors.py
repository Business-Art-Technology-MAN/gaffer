##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

from __future__ import annotations

## Message / error **context** strings (align with **Phase 4** tracker nomenclature).
OTL_PARSE_ERROR = "OTL_PARSE_ERROR"
OTL_TYPE_ERROR = "OTL_TYPE_ERROR"
OTL_MISSING_INPUT = "OTL_MISSING_INPUT"


class OTLException( Exception ) :

	def __init__( self, message : str, code : str = OTL_PARSE_ERROR ) :

		Exception.__init__( self, message )
		self.code = code


class OTLParseError( OTLException ) :

	def __init__( self, message : str ) :

		OTLException.__init__( self, message, OTL_PARSE_ERROR )


class OTLTypeError_( OTLException ) :

	def __init__( self, message : str ) :

		OTLException.__init__( self, message, OTL_TYPE_ERROR )


class OTLMissingInputError( OTLException ) :

	def __init__( self, message : str ) :

		OTLException.__init__( self, message, OTL_MISSING_INPUT )
