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
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
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

import IECore

import Gaffer


## Packs cross-section style ``rowTimes`` + ``valuesRowMajor`` + ``numColumns`` into one
# :class:`Gaffer.MatrixPlug` (e.g. connect :class:`CrossSectionNode` outputs here, then
# :class:`PCALoadingsNode`).
class PackMatrixNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "PackMatrix" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["panelRowTimes"] = Gaffer.Int64VectorDataPlug(
			"panelRowTimes",
			direction = Gaffer.Plug.Direction.In,
			defaultValue = IECore.Int64VectorData(),
		)
		self["panelValuesRowMajor"] = Gaffer.FloatVectorDataPlug(
			"panelValuesRowMajor",
			direction = Gaffer.Plug.Direction.In,
			defaultValue = IECore.FloatVectorData(),
		)
		self["panelNumColumns"] = Gaffer.IntPlug( "panelNumColumns", defaultValue = 0, minValue = 0 )

		self["out"] = Gaffer.MatrixPlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )
		if inputPlug.getName() in ( "panelRowTimes", "panelValuesRowMajor", "panelNumColumns" ) :
			outputs.append( self["out"]["rowTimes"] )
			outputs.append( self["out"]["valuesRowMajor"] )
			outputs.append( self["out"]["numColumns"] )

		return outputs

	def hash( self, output, context, h ) :

		if (
			output.isSame( self["out"]["rowTimes"] ) or
			output.isSame( self["out"]["valuesRowMajor"] ) or
			output.isSame( self["out"]["numColumns"] )
		) :
			self["panelRowTimes"].hash( h )
			self["panelValuesRowMajor"].hash( h )
			self["panelNumColumns"].hash( h )

	def compute( self, plug, context ) :

		out = self["out"]
		if plug.isSame( out["rowTimes"] ) :
			plug.setValue( IECore.Int64VectorData( list( self["panelRowTimes"].getValue() ) ) )
		elif plug.isSame( out["valuesRowMajor"] ) :
			plug.setValue( IECore.FloatVectorData( list( self["panelValuesRowMajor"].getValue() ) ) )
		elif plug.isSame( out["numColumns"] ) :
			plug.setValue( int( self["panelNumColumns"].getValue() ) )
		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( PackMatrixNode, typeName = "Gaffer::PackMatrixNode" )
