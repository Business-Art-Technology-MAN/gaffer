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
File menu helpers for **`.pce`** graphs (:mod:`Gaffer.PceGraphIO`).
"""

import os

import IECore

import Gaffer
import GafferUI


def appendDefinitions( menuDefinition : IECore.MenuDefinition, prefix : str = "/File/PCE" ) -> None :

	menuDefinition.append( prefix + "/Save Graph As...", { "command" : saveGraphAs } )
	menuDefinition.append( prefix + "/Open Graph...", { "command" : openGraph } )


def __pathAndBookmarks( scriptWindow : GafferUI.ScriptWindow ) :

	bookmarks = GafferUI.Bookmarks.acquire(
		scriptWindow,
		pathType = Gaffer.FileSystemPath,
		category = "script",
	)

	currentFileName = scriptWindow.scriptNode()["fileName"].getValue()
	if currentFileName :
		path = Gaffer.FileSystemPath( os.path.dirname( os.path.abspath( currentFileName ) ) )
	else :
		path = Gaffer.FileSystemPath( bookmarks.getDefault( scriptWindow ) )

	path.setFilter( Gaffer.FileSystemPath.createStandardFilter( [ "pce" ] ) )

	return path, bookmarks


def __graphFormat() -> str :

	return "usd" if Gaffer.usdAvailableForPce() else "legacy"


def saveGraphAs( menu : GafferUI.Menu ) -> None :

	scriptWindow = menu.ancestor( GafferUI.ScriptWindow )
	script = scriptWindow.scriptNode()
	path, bookmarks = __pathAndBookmarks( scriptWindow )

	dialogue = GafferUI.PathChooserDialogue(
		path,
		title = "Save PCE graph",
		confirmLabel = "Save",
		leaf = True,
		bookmarks = bookmarks,
	)
	chosen = dialogue.waitForPath( parentWindow = scriptWindow )

	if not chosen :
		return

	outPath = str( chosen )
	if not outPath.endswith( ".pce" ) :
		outPath += ".pce"

	meta = {
		"app" : "MarketLab",
		"sourceGafferScript" : script["fileName"].getValue() or "",
	}

	def task() -> None :

		Gaffer.savePceGraphFile( script, outPath, meta, graphFormat = __graphFormat() )

	bg = GafferUI.BackgroundTaskDialogue( "Saving PCE graph" )
	result = bg.waitForBackgroundTask( task, parentWindow = scriptWindow )

	if isinstance( result, IECore.Cancelled ) :
		return

	application = script.ancestor( Gaffer.ApplicationRoot )
	GafferUI.FileMenu.addRecentFile( application, outPath )


def openGraph( menu : GafferUI.Menu ) -> None :

	scriptWindow = menu.ancestor( GafferUI.ScriptWindow )
	script = scriptWindow.scriptNode()

	if script["unsavedChanges"].getValue() :
		confirm = GafferUI.ConfirmationDialogue(
			title = "Open PCE graph",
			message = "The current script has unsaved changes. Continue and replace it?",
			confirmLabel = "Open",
			cancelLabel = "Cancel",
		)
		if not confirm.waitForConfirmation( parentWindow = scriptWindow ) :
			return

	path, bookmarks = __pathAndBookmarks( scriptWindow )
	dialogue = GafferUI.PathChooserDialogue(
		path,
		title = "Open PCE graph",
		confirmLabel = "Open",
		valid = True,
		leaf = True,
		bookmarks = bookmarks,
	)
	chosen = dialogue.waitForPath( parentWindow = scriptWindow )

	if not chosen :
		return

	inPath = str( chosen )

	def task() -> None :

		_, body = Gaffer.loadPceGraphFile( inPath )
		with Gaffer.UndoScope( script, Gaffer.UndoScope.Disabled ) :
			script.deleteNodes()
			script["variables"].clearChildren()
		script.execute( body, continueOnError = True )
		with Gaffer.UndoScope( script, Gaffer.UndoScope.Disabled ) :
			script["fileName"].setValue( "" )
			script["unsavedChanges"].setValue( False )

	bg = GafferUI.BackgroundTaskDialogue( "Loading PCE graph" )
	result = bg.waitForBackgroundTask( task, parentWindow = scriptWindow )

	if isinstance( result, IECore.Cancelled ) :
		return

	application = script.ancestor( Gaffer.ApplicationRoot )
	GafferUI.FileMenu.addRecentFile( application, inPath )
