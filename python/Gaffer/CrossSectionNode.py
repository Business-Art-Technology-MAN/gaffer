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
from . import MarketDataPanel
from . import MarketDataTimeseries


## Layer 1 cross-sectional returns as row-major **T × N** panel (``matrix`` plug type from the OTL
# plan is represented as ``rowTimes`` + ``valuesRowMajor`` + ``numColumns``).
class CrossSectionNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "CrossSection" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["panelKey"] = Gaffer.StringPlug(
			defaultValue = "",
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
		self["delimiter"] = Gaffer.StringPlug(
			defaultValue = ",",
			substitutions = IECore.StringAlgo.Substitutions.NoSubstitutions,
		)

		self["rowTimes"] = Gaffer.Int64VectorDataPlug(
			"rowTimes",
			direction = Gaffer.Plug.Direction.Out,
			defaultValue = IECore.Int64VectorData(),
		)
		self["valuesRowMajor"] = Gaffer.FloatVectorDataPlug(
			"valuesRowMajor",
			direction = Gaffer.Plug.Direction.Out,
			defaultValue = IECore.FloatVectorData(),
		)
		self["numColumns"] = Gaffer.IntPlug(
			"numColumns",
			direction = Gaffer.Plug.Direction.Out,
			defaultValue = 0,
		)

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )
		if inputPlug.getName() in (
			"panelKey",
			"lookback",
			"backend",
			"resourcePath",
			"refreshCount",
			"hasHeader",
			"delimiter",
		) :
			outputs.append( self["rowTimes"] )
			outputs.append( self["valuesRowMajor"] )
			outputs.append( self["numColumns"] )

		return outputs

	def hash( self, output, context, h ) :

		if (
			output.isSame( self["rowTimes"] ) or
			output.isSame( self["valuesRowMajor"] ) or
			output.isSame( self["numColumns"] )
		) :
			self["panelKey"].hash( h )
			self["lookback"].hash( h )
			self["backend"].hash( h )
			self["resourcePath"].hash( h )
			self["refreshCount"].hash( h )
			self["hasHeader"].hash( h )
			self["delimiter"].hash( h )

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

	def _source_panel( self ) -> tuple :

		backend = self["backend"].getValue().strip().lower()

		if backend == "memory" :
			return MarketDataPanel.getPanel( self["panelKey"].getValue() )

		if backend == "csv" :
			return MarketDataIO.read_wide_csv_panel(
				self["resourcePath"].getValue(),
				self["hasHeader"].getValue(),
				self["delimiter"].getValue(),
			)

		if backend == "parquet" :
			path = MarketDataIO.normalise_resource_path( self["resourcePath"].getValue() )
			return MarketDataIO.read_wide_parquet_panel( path )

		raise ValueError(
			f'CrossSectionNode: unknown backend "{self["backend"].getValue()}" (expected memory, csv, or parquet).'
		)

	def compute( self, plug, context ) :

		if (
			plug.isSame( self["rowTimes"] ) or
			plug.isSame( self["valuesRowMajor"] ) or
			plug.isSame( self["numColumns"] )
		) :

			times, nCols, flat = self._source_panel()
			if nCols < 1 :
				if plug.isSame( self["rowTimes"] ) :
					plug.setValue( IECore.Int64VectorData() )
				elif plug.isSame( self["valuesRowMajor"] ) :
					plug.setValue( IECore.FloatVectorData() )
				else :
					plug.setValue( 0 )
				return

			lookback = self["lookback"].getValue()
			ct = context.get( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, None ) if context is not None else None
			times2, nCols2, flat2 = MarketDataIO.select_panel_by_time(
				list( times ), list( flat ), nCols, lookback, ct,
			)

			if plug.isSame( self["rowTimes"] ) :
				plug.setValue( IECore.Int64VectorData( times2 ) )
			elif plug.isSame( self["valuesRowMajor"] ) :
				plug.setValue( IECore.FloatVectorData( flat2 ) )
			else :
				plug.setValue( int( nCols2 ) )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( CrossSectionNode, typeName = "Gaffer::CrossSectionNode" )
