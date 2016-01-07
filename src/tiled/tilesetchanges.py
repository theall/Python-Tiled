##
# tilesetchanges.py
# Copyright 2011, Maus
# Copyright 2011-2013, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
#
# This file is part of Tiled.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
##
from undocommands import UndoCommands
from PyQt5.QtCore import (
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)
class RenameTileset(QUndoCommand):
    def __init__(self, mapDocument, tileset, newName):
        super().__init__(QCoreApplication.translate("Undo Commands", "Change Tileset Name"))
        
        self.mMapDocument = mapDocument
        self.mTileset = tileset
        self.mOldName = tileset.name()
        self.mNewName = newName

    def undo(self):
        self.mMapDocument.setTilesetName(self.mTileset, self.mOldName)

    def redo(self):
        self.mMapDocument.setTilesetName(self.mTileset, self.mNewName)

class ChangeTilesetTileOffset(QUndoCommand):

    def __init__(self, mapDocument, tileset, tileOffset):
        super().__init__(QCoreApplication.translate("Undo Commands", "Change Drawing Offset"))
        
        self.mMapDocument = mapDocument
        self.mTileset = tileset
        self.mOldTileOffset = tileset.tileOffset()
        self.mNewTileOffset = tileOffset

    def undo(self):
        self.mMapDocument.setTilesetTileOffset(self.mTileset, self.mOldTileOffset)

    def redo(self):
        self.mMapDocument.setTilesetTileOffset(self.mTileset, self.mNewTileOffset)

    def id(self):
        return UndoCommands.Cmd_ChangeTilesetTileOffset

    def mergeWith(self, other):
        o = other
        if (not (self.mMapDocument == o.mMapDocument and self.mTileset == o.mTileset)):
            return False
        self.mNewTileOffset = o.mNewTileOffset
        return True
