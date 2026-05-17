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

import IECore

import Gaffer

from .MarketMath import linear_least_squares


def _column( flat : list, numRows : int, numCols : int, col : int ) -> list :

	return [ flat[r * numCols + col] for r in range( numRows ) ]


def _submatrix_cols( flat : list, numRows : int, numCols : int, exclude : int ) -> list :
	"""Return ``numRows`` rows of length ``numCols - 1``, omitting column ``exclude``."""

	indices = [ i for i in range( numCols ) if i != exclude ]
	out = []
	for r in range( numRows ) :
		row = [ flat[r * numCols + j] for j in indices ]
		out.append( row )
	return out


## Cross-asset OLS coefficients (Avramov–He-style connectivity): column *j* regresses series *j*
# on all other series. ``lambdaMatrix`` is ``N × N`` row-major (diagonal zero).
class ConnectionMatrixNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "ConnectionMatrix" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["matrixIn"] = Gaffer.FloatVectorDataPlug(
			"matrixIn",
			defaultValue = IECore.FloatVectorData(),
		)
		self["numRows"] = Gaffer.IntPlug( defaultValue = 0, minValue = 0 )
		self["numColumns"] = Gaffer.IntPlug( defaultValue = 0, minValue = 0 )

		self["lambdaMatrix"] = Gaffer.FloatVectorDataPlug(
			"lambdaMatrix",
			direction = Gaffer.Plug.Direction.Out,
			defaultValue = IECore.FloatVectorData(),
		)

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )
		if inputPlug.isSame( self["matrixIn"] ) or inputPlug.isSame( self["numRows"] ) or inputPlug.isSame( self["numColumns"] ) :
			outputs.append( self["lambdaMatrix"] )

		return outputs

	def hash( self, output, context, h ) :

		if output.isSame( self["lambdaMatrix"] ) :
			self["matrixIn"].hash( h )
			self["numRows"].hash( h )
			self["numColumns"].hash( h )

	def compute( self, plug, context ) :

		if plug.isSame( self["lambdaMatrix"] ) :

			flat = list( self["matrixIn"].getValue() )
			T = self["numRows"].getValue()
			N = self["numColumns"].getValue()

			if T < 2 or N < 2 or T * N != len( flat ) :
				plug.setValue( IECore.FloatVectorData( [ 0.0 ] * ( N * N ) if N > 0 else [] ) )
				return

			lam = [ 0.0 ] * ( N * N )

			for j in range( N ) :
				y = _column( flat, T, N, j )
				Xrows = _submatrix_cols( flat, T, N, j )
				try :
					b = linear_least_squares( Xrows, y )
				except ValueError :
					continue
				idxMap = [ i for i in range( N ) if i != j ]
				for i, k in enumerate( idxMap ) :
					if i < len( b ) :
						lam[j * N + k] = b[i]

			plug.setValue( IECore.FloatVectorData( lam ) )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( ConnectionMatrixNode, typeName = "Gaffer::ConnectionMatrixNode" )
