# -*- coding: utf-8 -*-
##
# addremovetiles.py
# Copyright 2013, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
from PyQt5.QtCore import (
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)

from pyqtcore import QList

###
# Abstract base class for AddTiles and RemoveTiles.
##
class AddRemoveTiles(QUndoCommand):
    def __init__(self, mapDocument, tileset, index, count, tiles = QList()):
        super().__init__()
        
        self.mMapDocument = mapDocument
        self.mTileset = tileset
        self.mIndex = index
        self.mCount = count
        self.mTiles = tiles

    def __del__(self):
        del self.mTiles

    def addTiles(self):
        self.mTileset.insertTiles(self.mIndex, self.mTiles)
        self.mTiles.clear()
        self.mMapDocument.emit(self.mTileset)

    def removeTiles(self):
        self.mTiles = self.mTileset.tiles()[self.mIndex, self.mCount]
        self.mTileset.removeTiles(self.mIndex, self.mCount)
        self.mMapDocument.emit(self.mTileset)

###
# Undo command that adds tiles to a tileset.
##
class AddTiles(AddRemoveTiles):
    def __init__(self, mapDocument, tileset, tiles):
        super().__init__(mapDocument,
                         tileset,
                         tileset.tileCount(),
                         tiles.count(),
                         tiles)
        self.setText(QCoreApplication.translate("Undo Commands", "Add Tiles"))

    def undo(self):
        self.removeTiles()

    def redo(self):
        self.addTiles()

###
# Undo command that removes tiles from a tileset.
##
class RemoveTiles(AddRemoveTiles):
    def __init__(self, mapDocument, tileset, index, count):
        super(RemoveTiles, self).__init__(mapDocument, tileset, index, count)
        self.setText(QCoreApplication.translate("Undo Commands", "Remove Tiles"))

    def undo(self):
        self.addTiles()

    def redo(self):
        self.removeTiles()

