##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

from __future__ import annotations

from typing import List, Set

import IECore

import Gaffer

## Emitted via **:func:`IECore.msg`** when upstream **:class:`OTLShaderNode`** layers are
# out of order (strictly increasing **``layerIndex``** along data flow).
OTL_LAYER_VIOLATION = "OTL_LAYER_VIOLATION"


def _upstream_nodes( root : Gaffer.Node ) -> List[Gaffer.Node] :

	seen : Set[Gaffer.Node] = set()
	stack = [root]
	order : List[Gaffer.Node] = []

	while stack :
		n = stack.pop()
		if n in seen :
			continue
		seen.add( n )
		order.append( n )
		for plug in Gaffer.Plug.InputRange( n ) :
			src = plug.getInput()
			if src is not None :
				stack.append( src.node() )

	return order


def _layer_message( srcName : str, dstName : str, srcLayer : int, dstLayer : int ) -> str :

	return (
		f"OTL layer order violation: {srcName!r} (layerIndex={srcLayer}) feeds "
		f"{dstName!r} (layerIndex={dstLayer}); require src.layerIndex < dst.layerIndex."
	)


## Walk **upstream** from **``terminal_node``** and verify that every **``OTLShaderNode``**
# → **``OTLShaderNode``** connection has ``src['layerIndex'] < dst['layerIndex']``.
#
# Returns **False** if a violation was reported.
def validate_otl_shader_network( terminal_node : Gaffer.Node, emitMessages : bool = True ) -> bool :

	from Gaffer.OTLShaderNode import OTLShaderNode

	if not isinstance( terminal_node, Gaffer.Node ) :
		return True

	ok = True
	nodes = _upstream_nodes( terminal_node )
	for dst in nodes :
		if not isinstance( dst, OTLShaderNode ) :
			continue
		dstLayer = int( dst["layerIndex"].getValue() )
		for plug in Gaffer.Plug.InputRange( dst ) :
			srcP = plug.getInput()
			if srcP is None :
				continue
			src = srcP.node()
			if not isinstance( src, OTLShaderNode ) :
				continue
			srcLayer = int( src["layerIndex"].getValue() )
			if srcLayer >= dstLayer :
				ok = False
				if emitMessages :
					IECore.msg(
						IECore.MessageHandler.Level.Warning,
						OTL_LAYER_VIOLATION,
						_layer_message(
							src.getName(),
							dst.getName(),
							srcLayer,
							dstLayer,
						),
					)
	return ok


## Reserved hook for **PCE stage** scheduling (half-life–driven re-eval, etc.).
def compile_otl_network_for_pce( root_output_plug : Gaffer.Plug ) -> List[Gaffer.Node] :

	_ = root_output_plug
	return []
