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

from . import MarketDataFactors
from . import MarketDataIO
from . import MarketDataTimeseries


## Layer 1 factor returns → :class:`Gaffer.SeriesPlug` (**memory**, **CSV**, **Parquet**,
# **httpcsv**, **fred** — FRED series id in ``factorId``, key from env).
class FactorSeriesNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "FactorSeries" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["factorId"] = Gaffer.StringPlug(
			defaultValue = "MKT_RF",
			substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions,
		)
		self["lookback"] = Gaffer.IntPlug( defaultValue = 0, minValue = 0 )

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
		self["timeColumn"] = Gaffer.IntPlug( defaultValue = 0, minValue = 0 )
		self["valueColumn"] = Gaffer.IntPlug( defaultValue = 1, minValue = 0 )
		self["delimiter"] = Gaffer.StringPlug(
			defaultValue = ",",
			substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions,
		)
		self["parquetValueColumn"] = Gaffer.StringPlug(
			defaultValue = "value",
			substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions,
		)

		self["out"] = Gaffer.SeriesPlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )
		if inputPlug.getName() in (
			"factorId",
			"lookback",
			"backend",
			"resourcePath",
			"refreshCount",
			"hasHeader",
			"timeColumn",
			"valueColumn",
			"delimiter",
			"parquetValueColumn",
		) :
			outputs.append( self["out"]["times"] )
			outputs.append( self["out"]["values"] )

		return outputs

	def hash( self, output, context, h ) :

		if output.isSame( self["out"]["times"] ) or output.isSame( self["out"]["values"] ) :
			self["factorId"].hash( h )
			self["lookback"].hash( h )
			self["backend"].hash( h )
			self["resourcePath"].hash( h )
			self["refreshCount"].hash( h )
			self["hasHeader"].hash( h )
			self["timeColumn"].hash( h )
			self["valueColumn"].hash( h )
			self["delimiter"].hash( h )
			self["parquetValueColumn"].hash( h )

			if context is not None :
				ct = context.get( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, None )
				if ct is not None :
					h.append( int( ct ) )

			path = MarketDataIO.normalise_resource_path( self["resourcePath"].getValue() )
			backend = self["backend"].getValue().strip().lower()
			if backend in ( "csv", "parquet" ) and path :
				try :
					h.append( os.path.getmtime( path ) )
				except OSError :
					h.append( 0 )

	def _source_arrays( self ) :

		backend = self["backend"].getValue().strip().lower()

		if backend == "memory" :
			return MarketDataFactors.getFactorSeries( self["factorId"].getValue() )

		if backend == "csv" :
			return MarketDataIO.read_series_csv_adapter(
				self["resourcePath"].getValue(),
				self["hasHeader"].getValue(),
				self["timeColumn"].getValue(),
				self["valueColumn"].getValue(),
				self["delimiter"].getValue(),
			)

		if backend == "parquet" :
			path = MarketDataIO.normalise_resource_path( self["resourcePath"].getValue() )
			valueCol = self["parquetValueColumn"].getValue() or "value"
			return MarketDataIO.read_parquet_two_column_series( path, valueCol )

		if backend == "httpcsv" :
			return MarketDataIO.read_series_http_csv(
				self["resourcePath"].getValue(),
				self["hasHeader"].getValue(),
				self["timeColumn"].getValue(),
				self["valueColumn"].getValue(),
				self["delimiter"].getValue(),
			)

		if backend == "fred" :
			return MarketDataIO.read_series_fred_observations( self["factorId"].getValue() )

		raise ValueError(
			f'FactorSeriesNode: unknown backend "{self["backend"].getValue()}" (expected memory, csv, parquet, httpcsv, or fred).'
		)

	def compute( self, plug, context ) :

		if plug.isSame( self["out"]["times"] ) or plug.isSame( self["out"]["values"] ) :

			times, values = self._source_arrays()
			lookback = self["lookback"].getValue()
			ct = context.get( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, None ) if context is not None else None
			times, values = MarketDataIO.select_series_by_time(
				list( times ), list( values ), lookback, ct,
			)

			if plug.isSame( self["out"]["times"] ) :
				plug.setValue( IECore.Int64VectorData( times ) )
			else :
				plug.setValue( IECore.FloatVectorData( values ) )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( FactorSeriesNode, typeName = "Gaffer::FactorSeriesNode" )
