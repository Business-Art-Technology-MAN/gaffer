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

from . import ArcticBackend
from . import MarketDataIO
from . import MarketDataTimeseries


def _normaliseResourcePath( path : str ) -> str :

	return MarketDataIO.normalise_resource_path( path )


def _selectSeries( times : list, values : list, lookback : int, contextTime : object ) -> tuple :

	return MarketDataIO.select_series_by_time( times, values, lookback, contextTime )


def _readParquetSeries( path : str, field : str ) -> tuple :

	return MarketDataIO.read_parquet_two_column_series( path, field )


## Phase 2 store: :class:`SeriesPlug` from **memory**, **Parquet**, or **ArcticDB** (optional ``arcticdb`` wheel).
# ``barType`` / ``adjust`` participate in hash only. Point-in-time: if :data:`MarketDataTimeseries.PCE_TIME_CONTEXT_KEY`
# is set on the current :class:`~Gaffer.Context`, rows with ``time >`` that value are dropped
# before ``lookback`` truncation.
class TimeSeriesStoreNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "TimeSeriesStore" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["instrumentId"] = Gaffer.StringPlug( defaultValue = "DUMMY", substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions )
		self["field"] = Gaffer.StringPlug( defaultValue = "close", substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions )
		self["lookback"] = Gaffer.IntPlug( defaultValue = 252, minValue = 0 )
		self["barType"] = Gaffer.StringPlug( defaultValue = "daily", substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions )
		self["adjust"] = Gaffer.BoolPlug( defaultValue = False )

		self["backend"] = Gaffer.StringPlug( defaultValue = "memory", substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions )
		self["resourcePath"] = Gaffer.StringPlug( defaultValue = "", substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions )
		self["arcticLibrary"] = Gaffer.StringPlug(
			defaultValue = "pce",
			substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions,
		)
		self["refreshCount"] = Gaffer.IntPlug( defaultValue = 0 )

		self["out"] = Gaffer.SeriesPlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )
		if inputPlug.getName() in (
			"instrumentId",
			"field",
			"lookback",
			"barType",
			"adjust",
			"backend",
			"resourcePath",
			"arcticLibrary",
			"refreshCount",
		) :
			outputs.append( self["out"]["times"] )
			outputs.append( self["out"]["values"] )

		return outputs

	def hash( self, output, context, h ) :

		if output.isSame( self["out"]["times"] ) or output.isSame( self["out"]["values"] ) :
			self["instrumentId"].hash( h )
			self["field"].hash( h )
			self["lookback"].hash( h )
			self["barType"].hash( h )
			self["adjust"].hash( h )
			self["backend"].hash( h )
			self["resourcePath"].hash( h )
			self["arcticLibrary"].hash( h )
			self["refreshCount"].hash( h )

			if context is not None :
				ct = context.get( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, None )
				if ct is not None :
					h.append( int( ct ) )

			path = _normaliseResourcePath( self["resourcePath"].getValue() )
			backend = self["backend"].getValue().strip().lower()
			if backend == "parquet" and path :
				try :
					h.append( os.path.getmtime( path ) )
				except OSError :
					h.append( 0 )

	def _sourceArrays( self ) :

		backend = self["backend"].getValue().strip().lower()
		field = self["field"].getValue()

		if backend == "memory" :
			return MarketDataTimeseries.getSeries( self["instrumentId"].getValue(), field )

		if backend == "parquet" :
			path = _normaliseResourcePath( self["resourcePath"].getValue() )
			return _readParquetSeries( path, field )

		if backend == "arcticdb" :
			uri = _normaliseResourcePath( self["resourcePath"].getValue() )
			return ArcticBackend.read_series_for_store(
				uri,
				self["arcticLibrary"].getValue().strip() or "pce",
				self["instrumentId"].getValue(),
				field,
			)

		raise ValueError( f'TimeSeriesStoreNode: unknown backend "{self["backend"].getValue()}" (expected memory, parquet, or arcticdb).' )

	def compute( self, plug, context ) :

		if plug.isSame( self["out"]["times"] ) or plug.isSame( self["out"]["values"] ) :

			times, values = self._sourceArrays()
			lookback = self["lookback"].getValue()
			ct = context.get( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, None ) if context is not None else None
			times, values = _selectSeries( list( times ), list( values ), lookback, ct )

			if plug.isSame( self["out"]["times"] ) :
				plug.setValue( IECore.Int64VectorData( times ) )
			else :
				plug.setValue( IECore.FloatVectorData( values ) )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( TimeSeriesStoreNode, typeName = "Gaffer::TimeSeriesStoreNode" )
