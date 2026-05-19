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

from . import MarketMath


def _matrix_rows( times, flat, ncols ) :

	n = len( times )
	if ncols < 1 or n < 1 :
		return None
	if len( flat ) != n * ncols :
		return None
	rows = []
	for r in range( n ) :
		rows.append( [ float( flat[r * ncols + c] ) for c in range( ncols ) ] )
	return rows


def _last_window_pca( rows, window, k ) :

	if rows is None or window < 2 or len( rows ) < window :
		return [], []
	wrows = rows[-window:]
	cov = MarketMath.panel_sample_covariance( wrows )
	if not cov :
		return [], []
	return MarketMath.pca_top_components_covariance( cov, k )


def _rolling_pc1_series( times, rows, window ) :

	if rows is None or window < 2 :
		return [], []
	n = len( rows )
	p = len( rows[0] )
	out_t = []
	out_s = []
	for end in range( window - 1, n ) :
		wrows = rows[end - window + 1 : end + 1 ]
		cov = MarketMath.panel_sample_covariance( wrows )
		if not cov :
			continue
		_evals, evecs = MarketMath.pca_top_components_covariance( cov, 1 )
		if not evecs :
			continue
		v = evecs[0]
		col_mean = [
			sum( wrows[r][j] for r in range( window ) ) / window for j in range( p )
		]
		last = rows[end]
		score = sum( ( last[j] - col_mean[j] ) * v[j] for j in range( p ) )
		out_t.append( int( times[end] ) )
		out_s.append( float( score ) )

	return out_t, out_s


## Rolling PCA on a :class:`Gaffer.MatrixPlug` panel (**T × p**).
#
# * **loadings** — :class:`VectorPlug` stacking the last-window eigenvectors (PC0, PC1, … each length **p**).
# * **varianceExplained** — :class:`VectorPlug` of ``λ_k / Σ λ`` for that same window.
# * **pc1Scores** — :class:`SeriesPlug` of the trailing-window **PC1** score on the newest row (one value per window end).
class PCALoadingsNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "PCALoadings" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["in"] = Gaffer.MatrixPlug()
		self["window"] = Gaffer.IntPlug( defaultValue = 20, minValue = 2 )
		self["numComponents"] = Gaffer.IntPlug( defaultValue = 2, minValue = 1, maxValue = 32 )

		self["loadings"] = Gaffer.VectorPlug( direction = Gaffer.Plug.Direction.Out )
		self["varianceExplained"] = Gaffer.VectorPlug( direction = Gaffer.Plug.Direction.Out )
		self["pc1Scores"] = Gaffer.SeriesPlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )
		names = ( "in", "window", "numComponents" )
		if inputPlug.getName() in names :
			outputs.append( self["loadings"]["values"] )
			outputs.append( self["varianceExplained"]["values"] )
			outputs.append( self["pc1Scores"]["times"] )
			outputs.append( self["pc1Scores"]["values"] )
		else :
			parent = inputPlug.parent()
			if parent is not None and parent.isSame( self["in"] ) :
				outputs.append( self["loadings"]["values"] )
				outputs.append( self["varianceExplained"]["values"] )
				outputs.append( self["pc1Scores"]["times"] )
				outputs.append( self["pc1Scores"]["values"] )

		return outputs

	def hash( self, output, context, h ) :

		if (
			output.isSame( self["loadings"]["values"] ) or
			output.isSame( self["varianceExplained"]["values"] ) or
			output.isSame( self["pc1Scores"]["times"] ) or
			output.isSame( self["pc1Scores"]["values"] )
		) :
			self["in"]["rowTimes"].hash( h )
			self["in"]["valuesRowMajor"].hash( h )
			self["in"]["numColumns"].hash( h )
			self["window"].hash( h )
			self["numComponents"].hash( h )

	def _panel_data( self ) :

		times = list( self["in"]["rowTimes"].getValue() )
		flat = list( self["in"]["valuesRowMajor"].getValue() )
		ncols = int( self["in"]["numColumns"].getValue() )
		k = int( self["numComponents"].getValue() )
		w = int( self["window"].getValue() )
		rows = _matrix_rows( times, flat, ncols )
		return times, flat, ncols, k, w, rows

	def compute( self, plug, context ) :

		if plug.isSame( self["loadings"]["values"] ) :
			_times, _flat, _ncols, k, w, rows = self._panel_data()
			evals, evecs = _last_window_pca( rows, w, k ) if rows else ( [], [] )
			stacked = []
			for v in evecs :
				stacked.extend( v )
			plug.setValue( IECore.FloatVectorData( stacked ) )
		elif plug.isSame( self["varianceExplained"]["values"] ) :
			_times, _flat, _ncols, k, w, rows = self._panel_data()
			evals, _evecs = _last_window_pca( rows, w, k ) if rows else ( [], [] )
			s = sum( evals ) or 1.0
			ratios = [ float( e ) / s for e in evals ]
			plug.setValue( IECore.FloatVectorData( ratios ) )
		elif plug.isSame( self["pc1Scores"]["times"] ) :
			times, _flat, ncols, _k, w, rows = self._panel_data()
			pt, _ps = _rolling_pc1_series( times, rows, w )
			plug.setValue( IECore.Int64VectorData( pt ) )
		elif plug.isSame( self["pc1Scores"]["values"] ) :
			times, _flat, ncols, _k, w, rows = self._panel_data()
			_pt, ps = _rolling_pc1_series( times, rows, w )
			plug.setValue( IECore.FloatVectorData( ps ) )
		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( PCALoadingsNode, typeName = "Gaffer::PCALoadingsNode" )
