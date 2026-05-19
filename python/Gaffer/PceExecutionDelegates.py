##########################################################################
#
#  Copyright (c) 2026, MarketLab / PCE fork. All rights reserved.
#
##########################################################################

"""
**Phase 6 v0.1** — named execution-delegate hooks (Hydra-style) for a PCE USD stage.

This module only registers **names** and **call** stubs. Phase 8 backtest/paper/live
implementations fill in :meth:`PceExecutionDelegate.evaluate`.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Tuple, Type


class PceExecutionDelegate :
	"""Abstract base for ``BacktestDelegate`` / ``PaperDelegate`` / ``LiveDelegate`` (Phase 8)."""

	name : str = "abstract"

	def evaluate( self, stage : Any, context : Any ) -> Any :
		raise NotImplementedError


_registry : Dict[str, Type[PceExecutionDelegate]] = {}


def register_execution_delegate( name : str, cls : Type[PceExecutionDelegate] ) -> None :

	_registry[str( name ).strip() ] = cls


def deregister_execution_delegate( name : str ) -> None :

	_registry.pop( str( name ).strip(), None )


def execution_delegate_names() -> Tuple[str, ...] :

	return tuple( sorted( _registry.keys() ) )


def create_execution_delegate( name : str ) -> Optional[PceExecutionDelegate] :

	cls = _registry.get( str( name ).strip() )
	if cls is None :
		return None
	return cls()


## Phase 6 placeholder registrations (replace in Phase 8).

class _BacktestStub( PceExecutionDelegate ) :
	name = "BacktestDelegate"

	def evaluate( self, stage : Any, context : Any ) -> Any :
		return None


class _PaperStub( PceExecutionDelegate ) :
	name = "PaperDelegate"

	def evaluate( self, stage : Any, context : Any ) -> Any :
		return None


class _LiveStub( PceExecutionDelegate ) :
	name = "LiveDelegate"

	def evaluate( self, stage : Any, context : Any ) -> Any :
		return None


def _install_default_stubs() -> None :

	for c in ( _BacktestStub, _PaperStub, _LiveStub ) :
		register_execution_delegate( c.name, c )


_install_default_stubs()
