# -*- coding: utf-8 -*-
##
# addremovetileset.py
# Copyright 2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from tilesetmanager import TilesetManager
from PyQt5.QtCore import (
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)

###
# Abstract base class for AddTileset and RemoveTileset.
##
class AddRemoveTileset(QUndoCommand):
    def __init__(self, mapDocument, index, tileset, parent=None):
        super().__init__(parent)
        
        self.mMapDocument = mapDocument
        self.mTileset = tileset
        self.mIndex = index
        # Make sure the tileset manager keeps watching this tileset
        TilesetManager.instance().addReference(self.mTileset)

    def __del__(self):
        super(AddRemoveTileset, self).instance().removeReference(self.mTileset)

    def addTileset(self):
        self.mMapDocument.insertTileset(self.mIndex, self.mTileset)

    def removeTileset(self):
        self.mMapDocument.removeTilesetAt(self.mIndex)

###
# Adds a tileset to a map.
##
class AddTileset(AddRemoveTileset):
    def __init__(self, mapDocument, tileset, parent=None):
        super().__init__(mapDocument, mapDocument.map().tilesets().size(), tileset, parent)
        
        self.setText(QCoreApplication.translate("Undo Commands", "Add Tileset"))

    def undo(self):
        self.removeTileset()

    def redo(self):
        self.addTileset()

###
# Removes a tileset from a map.
##
class RemoveTileset(AddRemoveTileset):
    def __init__(self, mapDocument, index, tileset):
        super(RemoveTileset, self).__init__(mapDocument, index, mapDocument.map().tilesetAt(index))
        
        self.setText(QCoreApplication.translate("Undo Commands", "Remove Tileset"))

    def undo(self):
        self.addTileset()

    def redo(self):
        self.removeTileset()

