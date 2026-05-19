##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

from typing import List, Tuple

import IECore

import Gaffer

from . import MarketDataTimeseries
from .MarketRegimeAlgo import truncate_series_by_pit

try :
	import numpy as np
	from hmmlearn import hmm as _hmmlearn_hmm
	_hmmlearn_ok = True
except ImportError :
	np = None  # type: ignore
	_hmmlearn_hmm = None
	_hmmlearn_ok = False


def _median( xs : List[float] ) -> float :

	s = sorted( xs )
	n = len( s )
	if n == 0 :
		return 0.0
	mid = n // 2
	if n % 2 :
		return float( s[mid] )
	return 0.5 * float( s[mid - 1] + s[mid] )


def _classify_returns_window(
	values : List[float],
	numStates : int,
) -> Tuple[str, List[float]] :
	"""Return ``(regime_token, bull_probability_per_sample)`` for the window."""

	if len( values ) < 2 :
		return "ANY", []

	if _hmmlearn_ok :
		X = np.asarray( values, dtype = float ).reshape( -1, 1 )  # type: ignore[union-attr]
		try :
			model = _hmmlearn_hmm.GaussianHMM(
				n_components = numStates,
				covariance_type = "diag",
				n_iter = 200,
				random_state = 0,
			)
			model.fit( X )
			means = model.means_.ravel().tolist()
			order = sorted( range( numStates ), key = lambda i : means[i] )
			risk_off_s = order[0]
			risk_on_s = order[-1]
			middle = set( order[1:-1] )
			proba = model.predict_proba( X )
			bull_probs = [ float( row[risk_on_s] ) for row in proba ]
			last = int( np.argmax( proba[-1] ) )  # type: ignore[union-attr]
			if last == risk_on_s :
				regime = "RISK_ON"
			elif last == risk_off_s :
				regime = "RISK_OFF"
			elif middle :
				regime = "TRANSITION"
			else :
				regime = "TRANSITION"
			return regime, bull_probs
		except Exception :
			pass

	# Fallback: median split on returns (no hmmlearn / failed fit).
	med = _median( values )
	probs = [ 1.0 if float( v ) >= med else 0.0 for v in values ]
	regime = "RISK_ON" if float( values[-1] ) >= med else "RISK_OFF"
	return regime, probs


## Rolling **Gaussian HMM** on return observations when ``hmmlearn`` is installed; otherwise a
# lightweight **median-return** split on the same trailing window.
#
# Outputs:
#
# * ``regimeOut`` — **RISK_ON** / **RISK_OFF** / **TRANSITION** / **ANY**
# * ``stateProbSeries`` — ``times`` / ``values`` aligned to the last ``trainWindow`` returns;
#   ``values`` are posterior probabilities of the **highest-mean** state (continuous risk-on proxy).
class HMMRegimeNode( Gaffer.ComputeNode ) :

	def __init__( self, name = "HMMRegime" ) :

		Gaffer.ComputeNode.__init__( self, name )

		self["returnsSeries"] = Gaffer.SeriesPlug()
		self["numStates"] = Gaffer.IntPlug( defaultValue = 2, minValue = 2 )
		self["trainWindow"] = Gaffer.IntPlug( defaultValue = 60, minValue = 4 )
		self["minSamples"] = Gaffer.IntPlug( defaultValue = 12, minValue = 4 )

		self["regimeOut"] = Gaffer.RegimePlug( direction = Gaffer.Plug.Direction.Out )
		self["stateProbSeries"] = Gaffer.SeriesPlug( direction = Gaffer.Plug.Direction.Out )

	def affects( self, inputPlug ) :

		outputs = Gaffer.ComputeNode.affects( self, inputPlug )

		rs = self["returnsSeries"]
		if (
			inputPlug.isSame( rs )
			or ( inputPlug.parent() is not None and inputPlug.parent().isSame( rs ) )
			or inputPlug.isSame( self["numStates"] )
			or inputPlug.isSame( self["trainWindow"] )
			or inputPlug.isSame( self["minSamples"] )
		) :
			outputs.append( self["regimeOut"]["value"] )
			outputs.append( self["stateProbSeries"]["times"] )
			outputs.append( self["stateProbSeries"]["values"] )

		return outputs

	def hash( self, output, context, h ) :

		if (
			output.isSame( self["regimeOut"]["value"] )
			or output.isSame( self["stateProbSeries"]["times"] )
			or output.isSame( self["stateProbSeries"]["values"] )
		) :
			self["returnsSeries"]["times"].hash( h )
			self["returnsSeries"]["values"].hash( h )
			self["numStates"].hash( h )
			self["trainWindow"].hash( h )
			self["minSamples"].hash( h )

			if context is not None :
				ct = context.get( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, None )
				if ct is not None :
					h.append( int( ct ) )

	def compute( self, plug, context ) :

		if (
			plug.isSame( self["regimeOut"]["value"] )
			or plug.isSame( self["stateProbSeries"]["times"] )
			or plug.isSame( self["stateProbSeries"]["values"] )
		) :

			ct = context.get( MarketDataTimeseries.PCE_TIME_CONTEXT_KEY, None ) if context is not None else None

			timesFull = list( self["returnsSeries"]["times"].getValue() )
			valuesFull = list( self["returnsSeries"]["values"].getValue() )
			times, values = truncate_series_by_pit( timesFull, valuesFull, ct )

			win = self["trainWindow"].getValue()
			minS = self["minSamples"].getValue()
			numStates = self["numStates"].getValue()

			if len( values ) < minS :
				if plug.isSame( self["regimeOut"]["value"] ) :
					plug.setValue( "ANY" )
				elif plug.isSame( self["stateProbSeries"]["times"] ) :
					plug.setValue( IECore.Int64VectorData() )
				else :
					plug.setValue( IECore.FloatVectorData() )
				return

			tailT = times[-win:] if win > 0 else times
			tailV = values[-win:] if win > 0 else values

			regime, probs = _classify_returns_window( tailV, numStates )

			if plug.isSame( self["regimeOut"]["value"] ) :
				plug.setValue( regime )
			elif plug.isSame( self["stateProbSeries"]["times"] ) :
				if len( probs ) != len( tailT ) :
					plug.setValue( IECore.Int64VectorData() )
				else :
					plug.setValue( IECore.Int64VectorData( tailT ) )
			else :
				if len( probs ) != len( tailV ) :
					plug.setValue( IECore.FloatVectorData() )
				else :
					plug.setValue( IECore.FloatVectorData( probs ) )

		else :

			Gaffer.ComputeNode.compute( self, plug, context )


IECore.registerRunTimeTyped( HMMRegimeNode, typeName = "Gaffer::HMMRegimeNode" )
