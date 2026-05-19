##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

"""
**Phase 6 v0.1** — portfolio prim paths and timeline metadata for **PCE-USD/2**.

Full **usdGenSchema**-backed API types (``EquityAsset`` …) are deferred; prims use ``Scope``
and ``pce:*`` attributes so the stage round-trips without generated schemas. See
``SRD/PCE_Phase6_MilestoneTracker.md``.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Tuple

## Gaffer :class:`~Gaffer.Context` variable used for timeline / evaluation scrubbing (Phase 6).
PCE_CONTEXT_MARKET_TIME_NS = "pce:marketTimeNanoseconds"

InstrumentKind = Literal["EquityAsset", "BondAsset", "FuturesAsset", "OptionsAsset", "FXForward"]

_ASSET_FOLDER : Dict[str, str] = {
	"EquityAsset" : "Equities",
	"BondAsset" : "Rates",
	"FuturesAsset" : "Futures",
	"OptionsAsset" : "Options",
	"FXForward" : "FX",
}


def _sanitize_prim_name( symbol : str ) -> str :

	s = re.sub( r"[^A-Za-z0-9_]", "_", symbol or "" )
	if not s :
		s = "EMPTY"
	if s[0].isdigit() :
		s = "S_" + s
	return s


@dataclass
class PceTimeSample :

	## USD TimeCode frame index (integer ticks at **timeCodesPerSecond**).
	frame : int
	time_nanoseconds : int


@dataclass
class PceInstrumentPrim :

	symbol : str
	kind : InstrumentKind
	currency : str = "USD"
	## Optional venue / MIC-style id (OTL instrument context analogue).
	mic : str = ""
	extra : Dict[str, Any] = field( default_factory = dict )

	def portfolio_prim_path( self ) -> str :

		folder = _ASSET_FOLDER.get( self.kind, "Equities" )
		return f"/Portfolio/{folder}/{_sanitize_prim_name( self.symbol )}"


@dataclass
class PcePortfolioStagePayload :

	instruments : List[PceInstrumentPrim] = field( default_factory = list )
	## Stronger layers listed later (USD composition): e.g. quant base + risk override on top.
	sublayer_paths : List[str] = field( default_factory = list )
	time_samples : List[PceTimeSample] = field( default_factory = list )
	time_codes_per_second : float = 24.0
	active_execution_delegate : str = ""

	def to_json_dict( self ) -> Dict[str, Any] :

		return {
			"instruments" : [
				{
					"symbol" : i.symbol,
					"kind" : i.kind,
					"currency" : i.currency,
					"mic" : i.mic,
					"extra" : i.extra,
				}
				for i in self.instruments
			],
			"sublayerPaths" : list( self.sublayer_paths ),
			"timeSamples" : [
				{ "frame" : ts.frame, "timeNanoseconds" : ts.time_nanoseconds }
				for ts in self.time_samples
			],
			"timeCodesPerSecond" : self.time_codes_per_second,
			"activeExecutionDelegate" : self.active_execution_delegate,
		}

	@staticmethod
	def from_json_dict( d : Dict[str, Any] ) -> "PcePortfolioStagePayload" :

		instruments : List[PceInstrumentPrim] = []
		for row in d.get( "instruments", [] ) or [] :
			instruments.append(
				PceInstrumentPrim(
					symbol = str( row.get( "symbol", "" ) ),
					kind = str( row.get( "kind", "EquityAsset" ) ), # type: ignore[arg-type]
					currency = str( row.get( "currency", "USD" ) ),
					mic = str( row.get( "mic", "" ) ),
					extra = dict( row.get( "extra", {} ) or {} ),
				)
			)
		tss = [
			PceTimeSample( frame = int( x["frame"] ), time_nanoseconds = int( x["timeNanoseconds"] ) )
			for x in ( d.get( "timeSamples" ) or [] )
		]
		return PcePortfolioStagePayload(
			instruments = instruments,
			sublayer_paths = [ str( x ) for x in ( d.get( "sublayerPaths" ) or [] ) ],
			time_samples = tss,
			time_codes_per_second = float( d.get( "timeCodesPerSecond", 24.0 ) ),
			active_execution_delegate = str( d.get( "activeExecutionDelegate", "" ) ),
		)


def write_portfolio_prims_to_stage( stage : Any, payload : PcePortfolioStagePayload ) -> None :

	from pxr import Sdf

	port = stage.DefinePrim( "/Portfolio", "Xform" )
	_ = port
	for folder in sorted( set( _ASSET_FOLDER.values() ) ) :
		pp = f"/Portfolio/{folder}"
		if not stage.GetPrimAtPath( pp ) :
			stage.DefinePrim( pp, "Scope" )

	for inst in payload.instruments :
		ppath = inst.portfolio_prim_path()
		prim = stage.DefinePrim( ppath, "Scope" )
		kindAttr = prim.CreateAttribute( "pce:kind", Sdf.ValueTypeNames.Token )
		kindAttr.Set( inst.kind )
		symAttr = prim.CreateAttribute( "pce:symbol", Sdf.ValueTypeNames.String )
		symAttr.Set( inst.symbol )
		curAttr = prim.CreateAttribute( "pce:currency", Sdf.ValueTypeNames.String )
		curAttr.Set( inst.currency )
		if inst.mic :
			micAttr = prim.CreateAttribute( "pce:mic", Sdf.ValueTypeNames.String )
			micAttr.Set( inst.mic )
		if inst.extra :
			exAttr = prim.CreateAttribute( "pce:extraJson", Sdf.ValueTypeNames.String )
			exAttr.Set( json.dumps( inst.extra, ensure_ascii = False ) )


def read_portfolio_payload_from_stage( stage : Any ) -> PcePortfolioStagePayload :

	## Best-effort read of ``pce:*`` attrs; falls back to empty payload if ``/Portfolio`` missing.
	from pxr import Sdf

	instruments : List[PceInstrumentPrim] = []
	portfolio = stage.GetPrimAtPath( "/Portfolio" )
	if not portfolio :
		return PcePortfolioStagePayload()

	def visit( prim : Any ) -> None :

		if prim.GetPath() == "/Portfolio" :
			for c in prim.GetChildren() :
				visit( c )
			return
		path_s = str( prim.GetPath() )
		if not path_s.startswith( "/Portfolio/" ) :
			return
		symAttr = prim.GetAttribute( "pce:symbol" )
		if not symAttr or not symAttr.IsValid() :
			for c in prim.GetChildren() :
				visit( c )
			return
		sym = symAttr.Get()
		kind = "EquityAsset"
		ka = prim.GetAttribute( "pce:kind" )
		if ka and ka.IsValid() :
			kind = str( ka.Get() )
		cur = "USD"
		ca = prim.GetAttribute( "pce:currency" )
		if ca and ca.IsValid() :
			cur = str( ca.Get() )
		mic = ""
		ma = prim.GetAttribute( "pce:mic" )
		if ma and ma.IsValid() :
			mic = str( ma.Get() )
		ex : Dict[str, Any] = {}
		ea = prim.GetAttribute( "pce:extraJson" )
		if ea and ea.IsValid() :
			try :
				ex = json.loads( str( ea.Get() ) )
			except json.JSONDecodeError :
				ex = {}
		instruments.append(
			PceInstrumentPrim( symbol = str( sym ), kind = kind, currency = cur, mic = mic, extra = ex )
		)
		for c in prim.GetChildren() :
			visit( c )

	visit( portfolio )
	_ = Sdf
	return PcePortfolioStagePayload( instruments = instruments )


def open_pce_usda_stage( filePath : str ) -> Any :

	## ``Usd.Stage.Open`` often rejects unknown extensions; match :mod:`Gaffer.PceGraphIO` load path.
	from pxr import Sdf, Usd

	path = os.path.normpath( os.path.expanduser( os.path.expandvars( str( filePath ).strip() ) ) )
	with open( path, "r", encoding = "utf-8" ) as handle :
		usdaText = handle.read().lstrip( "\ufeff" )
	src = Sdf.Layer.CreateAnonymous( "pce.usda" )
	src.ImportFromString( usdaText )
	st = Usd.Stage.CreateInMemory()
	root = st.GetRootLayer()
	root.TransferContent( src )
	return st


def apply_market_time_to_context( context : Any, time_nanoseconds : int ) -> None :

	"""Set :data:`PCE_CONTEXT_MARKET_TIME_NS` on *context* (int ``timeNanoseconds``)."""

	context.set( PCE_CONTEXT_MARKET_TIME_NS, int( time_nanoseconds ) )


def market_time_from_context( context : Any, default_ns : int = 0 ) -> int :

	if PCE_CONTEXT_MARKET_TIME_NS not in context :
		return default_ns
	return int( context[PCE_CONTEXT_MARKET_TIME_NS] )
