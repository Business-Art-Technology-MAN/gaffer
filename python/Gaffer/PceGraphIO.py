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

"""
``.pce`` graph persistence:

- **PCE-USD/1** (default when OpenUSD is available, graph-only): valid USD layer (USDA on disk) with
  ``customLayerData`` holding JSON metadata and ``script.serialise()`` text.
- **PCE-USD/2** (**Phase 6**): same as /1 plus ``/Portfolio/...`` instrument prims, optional
  **subLayerPaths** (risk overlays), and timeline / delegate metadata in ``customLayerData``.
- **PCE-GRAPH/1** (legacy / no-USD builds): UTF-8 text envelope + embedded script.

:M10: USD-native format satisfies Phase 2 / Phase 6 direction that a ``.pce`` is a USD stage
layer; **PCE-USD/2** adds ``/Portfolio/...`` instrument prims, optional **sublayers** (risk
overrides), and timeline metadata (see :mod:`Gaffer.PcePortfolioStage`).
"""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any, Dict, Literal, Mapping, Optional, Sequence, Tuple

import Gaffer
from .PcePortfolioStage import (
	PcePortfolioStagePayload,
	write_portfolio_prims_to_stage,
)

## Legacy UTF-8 envelope (header line).
PCE_GRAPH_FORMAT_LINE = "PCE-GRAPH/1"
_PCE_SEPARATOR_LINE = "---\n"

## USD layer ``customLayerData["pce:format"]`` values for :func:`savePceGraphFile` / :func:`loadPceGraphFile`.
PCE_USD_FORMAT_TOKEN = "PCE-USD/1"
## Phase 6 — portfolio prims under ``/Portfolio``, optional sublayers, timeline JSON in ``customLayerData``.
PCE_USD_FORMAT_TOKEN_V2 = "PCE-USD/2"

PceGraphDiskFormat = Literal["usd", "legacy"]


def _usdRuntimeAvailable() -> bool :

	try :
		from pxr import Sdf  # noqa: F401
	except ImportError :
		return False
	return True


def usdAvailableForPce() -> bool :
	"""``True`` if OpenUSD (``pxr``) is importable so **PCE-USD/1** and **PCE-USD/2** can be read and written."""

	return _usdRuntimeAvailable()


def _effective_portfolio_payload(
	portfolio : Optional[PcePortfolioStagePayload],
	sublayerPaths : Optional[Sequence[str]],
) -> Optional[PcePortfolioStagePayload] :

	from dataclasses import replace

	has_sl = sublayerPaths is not None and len( list( sublayerPaths ) ) > 0
	if portfolio is None and not has_sl :
		return None
	base = portfolio if portfolio is not None else PcePortfolioStagePayload()
	if sublayerPaths is not None :
		return replace( base, sublayer_paths = list( sublayerPaths ) )
	return base


def _inject_pce_usd_v2_meta( cld : Any, meta : Dict[str, Any] ) -> None :

	pj = cld.get( "pce:portfolioJson" )
	if pj :
		meta["pcePortfolioStage"] = json.loads( str( pj ) )
	sp = cld.get( "pce:sublayerPathsJson" )
	if sp is not None :
		meta["pceSublayerPaths"] = json.loads( str( sp ) )
	tj = cld.get( "pce:timeLineJson" )
	if tj :
		meta["pceTimeLine"] = json.loads( str( tj ) )
	ad = cld.get( "pce:activeExecutionDelegate" )
	if ad :
		meta["pceActiveExecutionDelegate"] = str( ad )


def _saveLegacyEnvelope(
	script : Gaffer.ScriptNode,
	filePath : str,
	metadata : Optional[Mapping[str, Any]],
) -> None :

	body = script.serialise()
	metaObj : Dict[str, Any] = dict( metadata ) if metadata else {}

	path = os.path.normpath( os.path.expanduser( os.path.expandvars( filePath.strip() ) ) )
	metaLine = json.dumps( metaObj, separators = ( ",", ":" ), ensure_ascii = False )

	with open( path, "w", encoding = "utf-8", newline = "\n" ) as f :
		f.write( PCE_GRAPH_FORMAT_LINE + "\n" )
		f.write( metaLine + "\n" )
		f.write( _PCE_SEPARATOR_LINE )
		f.write( body )


def _saveUsdLayer(
	script : Gaffer.ScriptNode,
	filePath : str,
	metadata : Optional[Mapping[str, Any]],
	*,
	portfolio : Optional[PcePortfolioStagePayload] = None,
	sublayerPaths : Optional[Sequence[str]] = None,
) -> None :

	from pxr import Usd

	path = os.path.normpath( os.path.expanduser( os.path.expandvars( filePath.strip() ) ) )
	body = script.serialise()
	metaObj : Dict[str, Any] = dict( metadata ) if metadata else {}
	metaLine = json.dumps( metaObj, separators = ( ",", ":" ), ensure_ascii = False )

	eff = _effective_portfolio_payload( portfolio, sublayerPaths )
	fmtToken = PCE_USD_FORMAT_TOKEN_V2 if eff is not None else PCE_USD_FORMAT_TOKEN

	directory = os.path.dirname( path ) or os.getcwd()
	fd, tmpUsda = tempfile.mkstemp( suffix = ".usda", dir = directory, text = True )
	os.close( fd )
	try :
		stage = Usd.Stage.CreateNew( tmpUsda )
		root = stage.DefinePrim( "/PCE", "Xform" )
		stage.SetDefaultPrim( root )

		if eff is not None :
			write_portfolio_prims_to_stage( stage, eff )

		layer = stage.GetRootLayer()
		if eff is not None and eff.sublayer_paths :
			for sp in eff.sublayer_paths :
				layer.subLayerPaths.append( sp )

		layerCustom = dict( layer.customLayerData ) if layer.customLayerData else {}
		layerCustom["pce:format"] = fmtToken
		layerCustom["pce:metadataJson"] = metaLine
		layerCustom["pce:gafferSerialisedScript"] = body
		if eff is not None :
			layerCustom["pce:portfolioJson"] = json.dumps( eff.to_json_dict(), ensure_ascii = False )
			tl = {
				"timeCodesPerSecond" : eff.time_codes_per_second,
				"timeSamples" : [
					{ "frame" : ts.frame, "timeNanoseconds" : ts.time_nanoseconds }
					for ts in eff.time_samples
				],
			}
			layerCustom["pce:timeLineJson"] = json.dumps( tl, ensure_ascii = False )
			if eff.active_execution_delegate :
				layerCustom["pce:activeExecutionDelegate"] = eff.active_execution_delegate
			layerCustom["pce:sublayerPathsJson"] = json.dumps( eff.sublayer_paths, ensure_ascii = False )

		layer.customLayerData = layerCustom

		stage.Save()
		stage = None

		os.replace( tmpUsda, path )
		tmpUsda = ""

	finally :
		if tmpUsda and os.path.isfile( tmpUsda ) :
			try :
				os.remove( tmpUsda )
			except OSError :
				pass


def _loadFromUsdLayer( filePath : str ) -> Optional[Tuple[Dict[str, Any], str]] :

	from pxr import Sdf

	path = os.path.normpath( os.path.expanduser( os.path.expandvars( filePath.strip() ) ) )
	if not os.path.isfile( path ) :
		return None

	# Peek at text — ``Sdf.Layer.FindOrOpen`` throws for ``.pce`` (unknown format id from extension).
	with open( path, "r", encoding = "utf-8" ) as handle :
		firstLine = handle.readline()

	firstStripped = firstLine.lstrip( "\ufeff" ).strip()
	if firstStripped == PCE_GRAPH_FORMAT_LINE :
		return None

	layer = None
	if firstStripped.lower().startswith( "#usda" ) :
		with open( path, "r", encoding = "utf-8" ) as handle :
			usdaText = handle.read().lstrip( "\ufeff" )
		layer = Sdf.Layer.CreateAnonymous( "pce.usda" )
		layer.ImportFromString( usdaText )
	else :
		lower = path.lower()
		if not lower.endswith( ( ".usd", ".usda", ".usdc" ) ) :
			return None
		layer = Sdf.Layer.FindOrOpen( path )
		if layer is None :
			return None

	cld = layer.customLayerData
	if not cld :
		return None

	fmt = str( cld.get( "pce:format", "" ) or "" )
	if fmt not in ( PCE_USD_FORMAT_TOKEN, PCE_USD_FORMAT_TOKEN_V2 ) :
		return None

	metaLine = str( cld.get( "pce:metadataJson", "" ) or "{}" )
	body = str( cld.get( "pce:gafferSerialisedScript", "" ) or "" )
	meta : Dict[str, Any] = json.loads( metaLine ) if metaLine else {}
	if fmt == PCE_USD_FORMAT_TOKEN_V2 :
		_inject_pce_usd_v2_meta( cld, meta )
	return meta, body


def loadPceGraphFile( filePath : str ) -> Tuple[Dict[str, Any], str] :
	"""
	Load metadata and Gaffer script source. Tries **PCE-USD/1** or **PCE-USD/2** (``Sdf.Layer`` +
	``customLayerData``) first, then **PCE-GRAPH/1** text envelope.

	v2 files add ``pcePortfolioStage``, ``pceSublayerPaths``, ``pceTimeLine``, and
	``pceActiveExecutionDelegate`` keys to the returned metadata dict when present.

	:raises ValueError: file is neither a recognised PCE USD layer nor a valid legacy envelope.
	:raises json.JSONDecodeError: bad metadata in either format.
	"""

	path = os.path.normpath( os.path.expanduser( os.path.expandvars( filePath.strip() ) ) )

	if _usdRuntimeAvailable() :
		usdPayload = _loadFromUsdLayer( path )
		if usdPayload is not None :
			return usdPayload

	with open( path, "r", encoding = "utf-8" ) as f :
		magic = f.readline().rstrip( "\n\r" )
		if magic != PCE_GRAPH_FORMAT_LINE :
			raise ValueError(
				f"PceGraphIO: {path!r} is not PCE-USD/1/2 ({PCE_USD_FORMAT_TOKEN} / {PCE_USD_FORMAT_TOKEN_V2}) nor legacy {PCE_GRAPH_FORMAT_LINE!r}."
			)
		metaLine = f.readline().rstrip( "\n\r" )
		sep = f.readline()
		if sep.strip() != "---" :
			raise ValueError(
				f'PceGraphIO: expected "---" separator after metadata in {path!r}, got {sep!r}.'
			)
		body = f.read()

	metaOut : Dict[str, Any] = json.loads( metaLine ) if metaLine else {}
	return metaOut, body


def savePceGraphFile(
	script : Gaffer.ScriptNode,
	filePath : str,
	metadata : Optional[Mapping[str, Any]] = None,
	*,
	graphFormat : PceGraphDiskFormat = "usd",
	portfolio : Optional[PcePortfolioStagePayload] = None,
	sublayerPaths : Optional[Sequence[str]] = None,
) -> None :
	"""
	Write ``script.serialise()`` and JSON ``metadata`` to ``filePath``.

	:param graphFormat: ``"usd"`` when OpenUSD is available (**PCE-USD/1** by default, or **PCE-USD/2**
	  when ``portfolio`` or non-empty ``sublayerPaths`` is supplied); ``"legacy"`` forces **PCE-GRAPH/1**.
	:param portfolio: Optional :class:`~Gaffer.PcePortfolioStage.PcePortfolioStagePayload` for **Phase 6**
	  ``/Portfolio`` instrument prims + embedded JSON (implies **PCE-USD/2**).
	:param sublayerPaths: Optional USD root **subLayerPaths** (risk overlay layers). Non-empty list
	  implies **PCE-USD/2** even when ``portfolio`` is omitted.
	"""

	if graphFormat == "legacy" :
		if portfolio is not None or sublayerPaths :
			raise ValueError(
				"PceGraphIO: legacy PCE-GRAPH/1 does not support portfolio/sublayerPaths (use graphFormat='usd')."
			)
		_saveLegacyEnvelope( script, filePath, metadata )
		return

	if graphFormat != "usd" :
		raise ValueError( f'PceGraphIO: graphFormat must be "usd" or "legacy", got {graphFormat!r}.' )

	if not _usdRuntimeAvailable() :
		raise RuntimeError(
			"PceGraphIO: PCE-USD/1+ requires OpenUSD (import pxr). Use graphFormat='legacy' or install USD."
		)

	_saveUsdLayer( script, filePath, metadata, portfolio = portfolio, sublayerPaths = sublayerPaths )


def executePceGraphFile( filePath : str, script : Optional[Gaffer.ScriptNode] = None ) -> Tuple[Gaffer.ScriptNode, Dict[str, Any]] :
	"""Load file and ``execute`` into ``script`` (new :class:`~Gaffer.ScriptNode` if ``None``)."""

	meta, src = loadPceGraphFile( filePath )
	target = script if script is not None else Gaffer.ScriptNode()
	target.execute( src )
	return target, meta
