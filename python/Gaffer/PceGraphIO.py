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

- **PCE-USD/1** (default when OpenUSD is available): valid USD layer (USDA on disk) with
  ``customLayerData`` holding JSON metadata and ``script.serialise()`` text.
- **PCE-GRAPH/1** (legacy / no-USD builds): UTF-8 text envelope + embedded script.

:M10: USD-native format satisfies the Phase 2 / Phase 6 direction that a ``.pce`` is a USD stage
layer; portfolio prims can be added beside ``/PCE`` in later milestones.
"""

from __future__ import annotations

import json
import os
import tempfile
from typing import Any, Dict, Literal, Mapping, Optional, Tuple

import Gaffer

## Legacy UTF-8 envelope (header line).
PCE_GRAPH_FORMAT_LINE = "PCE-GRAPH/1"
_PCE_SEPARATOR_LINE = "---\n"

## USD layer ``customLayerData["pce:format"]`` value for :func:`savePceGraphFile` / :func:`loadPceGraphFile`.
PCE_USD_FORMAT_TOKEN = "PCE-USD/1"

PceGraphDiskFormat = Literal["usd", "legacy"]


def _usdRuntimeAvailable() -> bool :

	try :
		from pxr import Sdf  # noqa: F401
	except ImportError :
		return False
	return True


def usdAvailableForPce() -> bool :
	"""``True`` if OpenUSD (``pxr``) is importable so **PCE-USD/1** can be read and written."""

	return _usdRuntimeAvailable()


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
) -> None :

	from pxr import Usd

	path = os.path.normpath( os.path.expanduser( os.path.expandvars( filePath.strip() ) ) )
	body = script.serialise()
	metaObj : Dict[str, Any] = dict( metadata ) if metadata else {}
	metaLine = json.dumps( metaObj, separators = ( ",", ":" ), ensure_ascii = False )

	# USD decides file format from extension; ``.pce`` is unknown — export via temp ``.usda`` then replace.
	directory = os.path.dirname( path ) or os.getcwd()
	fd, tmpUsda = tempfile.mkstemp( suffix = ".usda", dir = directory, text = True )
	os.close( fd )
	try :
		stage = Usd.Stage.CreateNew( tmpUsda )
		root = stage.DefinePrim( "/PCE", "Xform" )
		stage.SetDefaultPrim( root )

		layer = stage.GetRootLayer()
		layerCustom = dict( layer.customLayerData ) if layer.customLayerData else {}
		layerCustom["pce:format"] = PCE_USD_FORMAT_TOKEN
		layerCustom["pce:metadataJson"] = metaLine
		layerCustom["pce:gafferSerialisedScript"] = body
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
	if fmt != PCE_USD_FORMAT_TOKEN :
		return None

	metaLine = str( cld.get( "pce:metadataJson", "" ) or "{}" )
	body = str( cld.get( "pce:gafferSerialisedScript", "" ) or "" )
	meta : Dict[str, Any] = json.loads( metaLine ) if metaLine else {}
	return meta, body


def loadPceGraphFile( filePath : str ) -> Tuple[Dict[str, Any], str] :
	"""
	Load metadata and Gaffer script source. Tries **PCE-USD/1** (``Sdf.Layer`` + ``customLayerData``)
	first, then **PCE-GRAPH/1** text envelope.

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
				f"PceGraphIO: {path!r} is not PCE-USD/1 ({PCE_USD_FORMAT_TOKEN}) nor legacy {PCE_GRAPH_FORMAT_LINE!r}."
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
) -> None :
	"""
	Write ``script.serialise()`` and JSON ``metadata`` to ``filePath``.

	:param graphFormat: ``"usd"`` (**PCE-USD/1**) when OpenUSD is available; ``"legacy"`` forces the
	  **PCE-GRAPH/1** text envelope. If ``"usd"`` is requested but ``pxr`` cannot be imported,
	  raises **RuntimeError** (install / enable USD, or pass ``graphFormat=\"legacy\"``).
	"""

	if graphFormat == "legacy" :
		_saveLegacyEnvelope( script, filePath, metadata )
		return

	if graphFormat != "usd" :
		raise ValueError( f'PceGraphIO: graphFormat must be "usd" or "legacy", got {graphFormat!r}.' )

	if not _usdRuntimeAvailable() :
		raise RuntimeError(
			"PceGraphIO: PCE-USD/1 requires OpenUSD (import pxr). Use graphFormat='legacy' or install USD."
		)

	_saveUsdLayer( script, filePath, metadata )


def executePceGraphFile( filePath : str, script : Optional[Gaffer.ScriptNode] = None ) -> Tuple[Gaffer.ScriptNode, Dict[str, Any]] :
	"""Load file and ``execute`` into ``script`` (new :class:`~Gaffer.ScriptNode` if ``None``)."""

	meta, src = loadPceGraphFile( filePath )
	target = script if script is not None else Gaffer.ScriptNode()
	target.execute( src )
	return target, meta
