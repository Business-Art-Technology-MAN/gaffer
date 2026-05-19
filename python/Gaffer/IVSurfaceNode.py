##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided
#        with the distribution.
#
#      * Neither the name of John Haddon nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import os

import IECore

import Gaffer

from . import MarketDataIO
from . import MarketDataSurfaces


def _coerce_surface_arrays(
	defaultAsOf : str,
	strikesIn,
	expiriesIn,
	ivsIn,
	payloadAsOf : str = "",
) -> tuple :
	"""Return ``(asOfTime, strikes, expiries, ivsRowMajor)`` or empty axes if lengths mismatch."""

	as_of = str( payloadAsOf ).strip() if payloadAsOf else ""
	if not as_of :
		as_of = str( defaultAsOf or "" )

	try :
		strikes = [ float( x ) for x in ( strikesIn or [] ) ]
		expiries = [ float( x ) for x in ( expiriesIn or [] ) ]
		ivs = [ float( x ) for x in ( ivsIn or [] ) ]
	except ( TypeError, ValueError ) :
		return as_of, [], [], []

	if not strikes or not expiries :
		return as_of, [], [], []
	if len( strikes ) * len( expiries ) != len( ivs ) :
		return as_of, [], [], []
	return as_of, strikes, expiries, ivs


## Layer 1 options IV **surface** as :class:`Gaffer.SurfacePlug` — **memory** registry or long CSV
# (columns ``strike``, ``expiry``, ``iv`` via ``strikeColumn`` / ``expiryColumn`` / ``ivColumn``).
# The output ``asOfTime`` string defaults to the node's ``defaultAsOfTime`` unless a **memory**
# payload supplies non-empty ``asOfTime``.
class IVSurfaceNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "IVSurface" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["symbol"] = Gaffer.StringPlug(
			defaultValue = "SPY",
			substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions,
		)
		self["defaultAsOfTime"] = Gaffer.StringPlug(
			defaultValue = "",
			substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions,
		)

		self["backend"] = Gaffer.StringPlug(
			defaultValue = "memory",
			substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions,
		)
		self["resourcePath"] = Gaffer.StringPlug(
			defaultValue = "",
			substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions,
		)
		self["refreshCount"] = Gaffer.IntPlug( defaultValue = 0 )

		self["hasHeader"] = Gaffer.BoolPlug( defaultValue = True )
		self["strikeColumn"] = Gaffer.IntPlug( defaultValue = 0, minValue = 0 )
		self["expiryColumn"] = Gaffer.IntPlug( defaultValue = 1, minValue = 0 )
		self["ivColumn"] = Gaffer.IntPlug( defaultValue = 2, minValue = 0 )
		self["delimiter"] = Gaffer.StringPlug(
			defaultValue = ",",
			substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions,
		)

		self["out"] = Gaffer.SurfacePlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )
		if inputPlug.getName() in (
			"symbol",
			"defaultAsOfTime",
			"backend",
			"resourcePath",
			"refreshCount",
			"hasHeader",
			"strikeColumn",
			"expiryColumn",
			"ivColumn",
			"delimiter",
		) :
			outputs.append( self["out"]["asOfTime"] )
			outputs.append( self["out"]["strikes"] )
			outputs.append( self["out"]["expiries"] )
			outputs.append( self["out"]["ivsRowMajor"] )

		return outputs

	def hash( self, output, context, h ) :

		if (
			output.isSame( self["out"]["asOfTime"] ) or
			output.isSame( self["out"]["strikes"] ) or
			output.isSame( self["out"]["expiries"] ) or
			output.isSame( self["out"]["ivsRowMajor"] )
		) :
			self["symbol"].hash( h )
			self["defaultAsOfTime"].hash( h )
			self["backend"].hash( h )
			self["resourcePath"].hash( h )
			self["refreshCount"].hash( h )
			self["hasHeader"].hash( h )
			self["strikeColumn"].hash( h )
			self["expiryColumn"].hash( h )
			self["ivColumn"].hash( h )
			self["delimiter"].hash( h )

			path = MarketDataIO.normalise_resource_path( self["resourcePath"].getValue() )
			backend = self["backend"].getValue().strip().lower()
			if backend == "csv" and path :
				try :
					h.append( os.path.getmtime( path ) )
				except OSError :
					h.append( 0 )

	def _surface_payload( self ) :

		backend = self["backend"].getValue().strip().lower()
		defaultT = self["defaultAsOfTime"].getValue()

		if backend == "memory" :
			raw = MarketDataSurfaces.get_iv_surface( self["symbol"].getValue() )
			if not raw :
				return defaultT, [], [], []
			pAs = raw.get( "asOfTime", "" )
			return _coerce_surface_arrays(
				defaultT,
				raw.get( "strikes" ),
				raw.get( "expiries" ),
				raw.get( "ivsRowMajor" ),
				payloadAsOf = pAs,
			)

		if backend == "csv" :
			sk, ex, iv = MarketDataIO.read_iv_surface_long_csv(
				self["resourcePath"].getValue(),
				self["hasHeader"].getValue(),
				self["strikeColumn"].getValue(),
				self["expiryColumn"].getValue(),
				self["ivColumn"].getValue(),
				self["delimiter"].getValue(),
			)
			return _coerce_surface_arrays( defaultT, sk, ex, iv, payloadAsOf = "" )

		raise ValueError(
			f'IVSurfaceNode: unknown backend "{self["backend"].getValue()}" (expected memory or csv).'
		)

	def compute( self, plug, context ) :

		out = self["out"]
		if plug.isSame( out["asOfTime"] ) :
			tStr, strikes, expiries, ivs = self._surface_payload()
			plug.setValue( tStr )
		elif plug.isSame( out["strikes"] ) :
			_st, strikes, _ex, _iv = self._surface_payload()
			plug.setValue( IECore.FloatVectorData( strikes ) )
		elif plug.isSame( out["expiries"] ) :
			_st, _sk, expiries, _iv = self._surface_payload()
			plug.setValue( IECore.FloatVectorData( expiries ) )
		elif plug.isSame( out["ivsRowMajor"] ) :
			_st, _sk, _ex, ivs = self._surface_payload()
			plug.setValue( IECore.FloatVectorData( ivs ) )
		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( IVSurfaceNode, typeName = "Gaffer::IVSurfaceNode" )
