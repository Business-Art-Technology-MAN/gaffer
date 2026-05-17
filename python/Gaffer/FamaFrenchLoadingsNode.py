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


def _aligned_four( assetT, assetV, mktT, mktV, smbT, smbV, hmlT, hmlV ) :

	ma = { t : float( v ) for t, v in zip( assetT, assetV ) }
	mm = { t : float( v ) for t, v in zip( mktT, mktV ) }
	ms = { t : float( v ) for t, v in zip( smbT, smbV ) }
	mh = { t : float( v ) for t, v in zip( hmlT, hmlV ) }
	common = sorted( set( ma.keys() ) & set( mm.keys() ) & set( ms.keys() ) & set( mh.keys() ) )
	y = [ ma[t] for t in common ]
	Xm = [ mm[t] for t in common ]
	Xs = [ ms[t] for t in common ]
	Xh = [ mh[t] for t in common ]
	return common, y, Xm, Xs, Xh


def _rolling_betas( times, y, xm, xs, xh, window ) :

	if window < 2 or len( times ) < window :
		return [], [], [], []

	outT = []
	bm = []
	bs = []
	bh = []
	for end in range( window - 1, len( times ) ) :
		start = end - window + 1
		Xrows = []
		yw = []
		for i in range( start, end + 1 ) :
			Xrows.append( [ 1.0, xm[i], xs[i], xh[i] ] )
			yw.append( y[i] )
		try :
			b = linear_least_squares( Xrows, yw )
		except ValueError :
			continue
		if len( b ) < 4 :
			continue
		outT.append( times[end] )
		bm.append( b[1] )
		bs.append( b[2] )
		bh.append( b[3] )

	return outT, bm, bs, bh


## Rolling OLS factor loadings; three :class:`Gaffer.SeriesPlug` outputs **without** a dedicated ``VectorPlug``
# (betas are time series aligned to the end of each estimation window).
class FamaFrenchLoadingsNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "FamaFrenchLoadings" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["asset"] = Gaffer.SeriesPlug()
		self["mkt"] = Gaffer.SeriesPlug()
		self["smb"] = Gaffer.SeriesPlug()
		self["hml"] = Gaffer.SeriesPlug()
		self["window"] = Gaffer.IntPlug( defaultValue = 60, minValue = 2 )

		self["betaMkt"] = Gaffer.SeriesPlug( direction = Gaffer.Plug.Direction.Out )
		self["betaSmb"] = Gaffer.SeriesPlug( direction = Gaffer.Plug.Direction.Out )
		self["betaHml"] = Gaffer.SeriesPlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )
		names = (
			"asset",
			"mkt",
			"smb",
			"hml",
			"window",
		)
		if inputPlug.getName() in names :
			for outName in ( "betaMkt", "betaSmb", "betaHml" ) :
				outputs.append( self[outName]["times"] )
				outputs.append( self[outName]["values"] )
		else :
			parent = inputPlug.parent()
			if parent is not None :
				for seriesName in ( "asset", "mkt", "smb", "hml" ) :
					if parent.isSame( self[seriesName] ) :
						for outName in ( "betaMkt", "betaSmb", "betaHml" ) :
							outputs.append( self[outName]["times"] )
							outputs.append( self[outName]["values"] )
						break

		return outputs

	def hash( self, output, context, h ) :

		for seriesName in ( "asset", "mkt", "smb", "hml" ) :
			self[seriesName]["times"].hash( h )
			self[seriesName]["values"].hash( h )

		self["window"].hash( h )

	def compute( self, plug, context ) :

		targetSeries = None
		valueSlot = None
		for outName, slot in (
			( "betaMkt", 0 ),
			( "betaSmb", 1 ),
			( "betaHml", 2 ),
		) :
			for leaf in ( "times", "values" ) :
				if plug.isSame( self[outName][leaf] ) :
					targetSeries = outName
					valueSlot = slot
					break
			if targetSeries is not None :
				break

		if targetSeries is None :
			Gaffer.ComputeNode.compute( self, plug, context )
			return

		common, y, xm, xs, xh = _aligned_four(
			self["asset"]["times"].getValue(),
			self["asset"]["values"].getValue(),
			self["mkt"]["times"].getValue(),
			self["mkt"]["values"].getValue(),
			self["smb"]["times"].getValue(),
			self["smb"]["values"].getValue(),
			self["hml"]["times"].getValue(),
			self["hml"]["values"].getValue(),
		)

		tBeta, bm, bs, bh = _rolling_betas(
			common, y, xm, xs, xh, self["window"].getValue(),
		)

		if not tBeta :
			if plug.isSame( self[targetSeries]["times"] ) :
				plug.setValue( IECore.Int64VectorData() )
			elif plug.isSame( self[targetSeries]["values"] ) :
				plug.setValue( IECore.FloatVectorData() )
			else :
				Gaffer.ComputeNode.compute( self, plug, context )
			return

		blocks = ( bm, bs, bh )

		if plug.isSame( self[targetSeries]["times"] ) :
			plug.setValue( IECore.Int64VectorData( tBeta ) )
		elif plug.isSame( self[targetSeries]["values"] ) :
			plug.setValue( IECore.FloatVectorData( blocks[valueSlot] ) )
		else :
			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( FamaFrenchLoadingsNode, typeName = "Gaffer::FamaFrenchLoadingsNode" )
