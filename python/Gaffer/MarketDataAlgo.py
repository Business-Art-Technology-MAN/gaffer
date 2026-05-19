##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

"""
JSON-friendly dict interchange for Phase 1 OTL plugs (USD / layer storage helpers).

Includes :class:`SeriesPlug`, :class:`SignalClosurePlug`, :class:`WeightVectorPlug`,
:class:`MarketContextPlug`, :class:`SurfacePlug`, :class:`VectorPlug`, :class:`MatrixPlug`,
:class:`RegimePlug`, and :class:`VolRegimePlug`.

These operate on plug *values* only; use :func:`json.dumps` / :func:`json.loads` at boundaries.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping

import IECore

import Gaffer


def seriesPlugToDict( plug: Gaffer.SeriesPlug ) -> Dict[str, Any] :
	return {
		"times": list( plug.timesPlug().getValue() ),
		"values": list( plug.valuesPlug().getValue() ),
	}


def applySeriesPlugDict( plug: Gaffer.SeriesPlug, d : Mapping[str, Any] ) -> None :
	if "times" in d :
		plug.timesPlug().setValue( IECore.Int64VectorData( list( d["times"] ) ) )
	if "values" in d :
		plug.valuesPlug().setValue( IECore.FloatVectorData( list( d["values"] ) ) )


def signalClosurePlugToDict( plug: Gaffer.SignalClosurePlug ) -> Dict[str, Any] :
	return {
		"alphaWeight": plug.alphaWeightPlug().getValue(),
		"confidence": plug.confidencePlug().getValue(),
		"halfLife": plug.halfLifePlug().getValue(),
		"maxImpactFrac": plug.maxImpactFracPlug().getValue(),
		"regimeCondition": plug.regimeConditionPlug().getValue(),
		"sideBet": plug.sideBetPlug().getValue(),
	}


def applySignalClosurePlugDict( plug: Gaffer.SignalClosurePlug, d : Mapping[str, Any] ) -> None :
	if "alphaWeight" in d :
		plug.alphaWeightPlug().setValue( float( d["alphaWeight"] ) )
	if "confidence" in d :
		plug.confidencePlug().setValue( float( d["confidence"] ) )
	if "halfLife" in d :
		plug.halfLifePlug().setValue( float( d["halfLife"] ) )
	if "maxImpactFrac" in d :
		plug.maxImpactFracPlug().setValue( float( d["maxImpactFrac"] ) )
	if "regimeCondition" in d :
		plug.regimeConditionPlug().setValue( str( d["regimeCondition"] ) )
	if "sideBet" in d :
		plug.sideBetPlug().setValue( bool( d["sideBet"] ) )


def weightVectorPlugToDict( plug: Gaffer.WeightVectorPlug ) -> Dict[str, Any] :
	return {
		"instrumentIds": list( plug.instrumentIdsPlug().getValue() ),
		"targetWeights": list( plug.targetWeightsPlug().getValue() ),
		"confidences": list( plug.confidencesPlug().getValue() ),
		"halfLives": list( plug.halfLivesPlug().getValue() ),
		"grossExposure": plug.grossExposurePlug().getValue(),
		"netExposure": plug.netExposurePlug().getValue(),
		"activeRegime": plug.activeRegimePlug().getValue(),
		"evaluatedAt": plug.evaluatedAtPlug().getValue(),
	}


def applyWeightVectorPlugDict( plug: Gaffer.WeightVectorPlug, d : Mapping[str, Any] ) -> None :
	if "instrumentIds" in d :
		plug.instrumentIdsPlug().setValue( IECore.StringVectorData( list( d["instrumentIds"] ) ) )
	if "targetWeights" in d :
		plug.targetWeightsPlug().setValue( IECore.FloatVectorData( list( d["targetWeights"] ) ) )
	if "confidences" in d :
		plug.confidencesPlug().setValue( IECore.FloatVectorData( list( d["confidences"] ) ) )
	if "halfLives" in d :
		plug.halfLivesPlug().setValue( IECore.FloatVectorData( list( d["halfLives"] ) ) )
	if "grossExposure" in d :
		plug.grossExposurePlug().setValue( float( d["grossExposure"] ) )
	if "netExposure" in d :
		plug.netExposurePlug().setValue( float( d["netExposure"] ) )
	if "activeRegime" in d :
		plug.activeRegimePlug().setValue( str( d["activeRegime"] ) )
	if "evaluatedAt" in d :
		plug.evaluatedAtPlug().setValue( str( d["evaluatedAt"] ) )


def marketContextPlugToDict( plug: Gaffer.MarketContextPlug ) -> Dict[str, Any] :
	return {
		"timeNanoseconds": plug.timeNanosecondsPlug().getValue(),
		"macroRegime": plug.macroRegimePlug().getValue(),
		"vixLevel": plug.vixLevelPlug().getValue(),
		"termSpread": plug.termSpreadPlug().getValue(),
		"creditSpread": plug.creditSpreadPlug().getValue(),
	}


def applyMarketContextPlugDict( plug: Gaffer.MarketContextPlug, d : Mapping[str, Any] ) -> None :
	if "timeNanoseconds" in d :
		plug.timeNanosecondsPlug().setValue( str( d["timeNanoseconds"] ) )
	if "macroRegime" in d :
		plug.macroRegimePlug().setValue( str( d["macroRegime"] ) )
	if "vixLevel" in d :
		plug.vixLevelPlug().setValue( float( d["vixLevel"] ) )
	if "termSpread" in d :
		plug.termSpreadPlug().setValue( float( d["termSpread"] ) )
	if "creditSpread" in d :
		plug.creditSpreadPlug().setValue( float( d["creditSpread"] ) )


def surfacePlugToDict( plug: Gaffer.SurfacePlug ) -> Dict[str, Any] :
	return {
		"asOfTime": plug.asOfTimePlug().getValue(),
		"strikes": list( plug.strikesPlug().getValue() ),
		"expiries": list( plug.expiriesPlug().getValue() ),
		"ivsRowMajor": list( plug.ivsRowMajorPlug().getValue() ),
	}


def applySurfacePlugDict( plug: Gaffer.SurfacePlug, d : Mapping[str, Any] ) -> None :
	if "asOfTime" in d :
		plug.asOfTimePlug().setValue( str( d["asOfTime"] ) )
	if "strikes" in d :
		plug.strikesPlug().setValue( IECore.FloatVectorData( list( d["strikes"] ) ) )
	if "expiries" in d :
		plug.expiriesPlug().setValue( IECore.FloatVectorData( list( d["expiries"] ) ) )
	if "ivsRowMajor" in d :
		plug.ivsRowMajorPlug().setValue( IECore.FloatVectorData( list( d["ivsRowMajor"] ) ) )


def vectorPlugToDict( plug: Gaffer.VectorPlug ) -> Dict[str, Any] :
	return {
		"values": list( plug.valuesPlug().getValue() ),
	}


def applyVectorPlugDict( plug: Gaffer.VectorPlug, d : Mapping[str, Any] ) -> None :
	if "values" in d :
		plug.valuesPlug().setValue( IECore.FloatVectorData( list( d["values"] ) ) )


def matrixPlugToDict( plug: Gaffer.MatrixPlug ) -> Dict[str, Any] :
	return {
		"rowTimes": list( plug.rowTimesPlug().getValue() ),
		"valuesRowMajor": list( plug.valuesRowMajorPlug().getValue() ),
		"numColumns": plug.numColumnsPlug().getValue(),
	}


def applyMatrixPlugDict( plug: Gaffer.MatrixPlug, d : Mapping[str, Any] ) -> None :
	if "rowTimes" in d :
		plug.rowTimesPlug().setValue( IECore.Int64VectorData( list( d["rowTimes"] ) ) )
	if "valuesRowMajor" in d :
		plug.valuesRowMajorPlug().setValue( IECore.FloatVectorData( list( d["valuesRowMajor"] ) ) )
	if "numColumns" in d :
		plug.numColumnsPlug().setValue( int( d["numColumns"] ) )


def regimePlugToDict( plug: Gaffer.RegimePlug ) -> Dict[str, Any] :
	return {
		"value": plug.valuePlug().getValue(),
	}


def applyRegimePlugDict( plug: Gaffer.RegimePlug, d : Mapping[str, Any] ) -> None :
	if "value" in d :
		plug.valuePlug().setValue( str( d["value"] ) )


def volRegimePlugToDict( plug: Gaffer.VolRegimePlug ) -> Dict[str, Any] :
	return {
		"value": plug.valuePlug().getValue(),
	}


def applyVolRegimePlugDict( plug: Gaffer.VolRegimePlug, d : Mapping[str, Any] ) -> None :
	if "value" in d :
		plug.valuePlug().setValue( str( d["value"] ) )
