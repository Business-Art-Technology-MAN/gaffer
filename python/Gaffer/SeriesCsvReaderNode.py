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

import csv
import os

import IECore

import Gaffer


def _normaliseFilePath( filePath ) :

	if not filePath :
		return ""
	return os.path.normpath( os.path.expanduser( os.path.expandvars( filePath.strip() ) ) )


def _readSeriesCsvRows( rows, hasHeader, timeColumn, valueColumn ) :

	times = []
	values = []
	if hasHeader and rows :
		rows = rows[1:]

	need = max( timeColumn, valueColumn ) + 1
	for row in rows :
		if len( row ) < need :
			continue
		try :
			t = int( float( row[timeColumn].strip() ) )
			v = float( row[valueColumn].strip() )
		except ValueError :
			continue
		times.append( t )
		values.append( v )

	return times, values


def _readSeriesCsvFromString( text, hasHeader, timeColumn, valueColumn, delimiter ) :

	import io

	if not ( text or "" ).strip() :
		return [], []

	delim = delimiter if delimiter else ","
	delim = delim[0]

	try :
		reader = csv.reader( io.StringIO( text ), delimiter = delim )
		rows = list( reader )
	except csv.Error :
		return [], []

	return _readSeriesCsvRows( rows, hasHeader, timeColumn, valueColumn )


def _readSeriesCsv( filePath, hasHeader, timeColumn, valueColumn, delimiter ) :

	times = []
	values = []
	path = _normaliseFilePath( filePath )
	if not path :
		return times, values

	delim = delimiter if delimiter else ","
	delim = delim[0]

	try :
		with open( path, newline = "", encoding = "utf-8" ) as f :
			reader = csv.reader( f, delimiter = delim )
			rows = list( reader )
	except OSError :
		return times, values

	return _readSeriesCsvRows( rows, hasHeader, timeColumn, valueColumn )


## Layer 1-style reader: loads two CSV columns into a :class:`SeriesPlug`.
# UTF-8, one character from `delimiter` (empty → comma). Invalid rows are skipped.
# ``filePath`` and ``delimiter`` use :py:data:`IECore.StringAlgo.Substitutions.NoSubstitutions`
# so Windows paths (``\\Users``, ``\\t`` in ``\\Temp``, etc.) are not mangled during compute.
class SeriesCsvReaderNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "SeriesCsvReader" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["filePath"] = Gaffer.StringPlug(
			defaultValue = "",
			substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions,
		)
		self["hasHeader"] = Gaffer.BoolPlug( defaultValue = True )
		self["timeColumn"] = Gaffer.IntPlug( defaultValue = 0, minValue = 0 )
		self["valueColumn"] = Gaffer.IntPlug( defaultValue = 1, minValue = 0 )
		self["delimiter"] = Gaffer.StringPlug(
			defaultValue = ",",
			substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions,
		)

		self["out"] = Gaffer.SeriesPlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )
		if inputPlug.getName() in (
			"filePath",
			"hasHeader",
			"timeColumn",
			"valueColumn",
			"delimiter",
		) :
			outputs.append( self["out"]["times"] )
			outputs.append( self["out"]["values"] )

		return outputs

	def hash( self, output, context, h ) :

		if output.isSame( self["out"]["times"] ) or output.isSame( self["out"]["values"] ) :
			self["filePath"].hash( h )
			self["hasHeader"].hash( h )
			self["timeColumn"].hash( h )
			self["valueColumn"].hash( h )
			self["delimiter"].hash( h )
			path = _normaliseFilePath( self["filePath"].getValue() )
			if path :
				try :
					h.append( os.path.getmtime( path ) )
				except OSError :
					h.append( 0 )

	def compute( self, plug, context ) :

		if plug.isSame( self["out"]["times"] ) or plug.isSame( self["out"]["values"] ) :

			times, values = _readSeriesCsv(
				self["filePath"].getValue(),
				self["hasHeader"].getValue(),
				self["timeColumn"].getValue(),
				self["valueColumn"].getValue(),
				self["delimiter"].getValue(),
			)

			if plug.isSame( self["out"]["times"] ) :
				plug.setValue( IECore.Int64VectorData( times ) )
			else :
				plug.setValue( IECore.FloatVectorData( values ) )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( SeriesCsvReaderNode, typeName = "Gaffer::SeriesCsvReaderNode" )
