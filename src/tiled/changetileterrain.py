##
# changetileterrain.py
# Copyright 2012, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
from undocommands import UndoCommands
from pyqtcore import QMap, QList

class ChangeTileTerrain(QUndoCommand):

    class Change():
        def __init__(self, _from, to):
            self._from = _from
            self.to = to
    ##
    # Constructs an empty command that changes no terrain. When merged into
    # a previous terrain change command, it prevents that command from merging
    # with future commands.
    ##
    def __init__(self, *args):
        super().__init__()
        
        self.mChanges = QMap()
        self.mMapDocument = None
        self.mTileset = None
        self.mMergeable = False
        l = len(args)
        if l==0:
            self.initText()
        elif l==2:
            ##
            # Changes the terrain of \a tile.
            ##
            mapDocument, changes = args
            self.mMapDocument = mapDocument
            self.mTileset = changes.begin().key().tileset()
            self.mMergeable = True
            self.initText()
        elif l==3:
            ##
            # Applies the given terrain \a changes.
            ##
            mapDocument = args[0]
            tile = args[1]
            terrain = args[2]
            self.mMapDocument = mapDocument
            self.mTileset = tile.tileset()
            self.mMergeable = True
            self.initText()
            self.mChanges.insert(tile, ChangeTileTerrain.Change(tile.terrain(), terrain))

    def undo(self):
        i = self.mChanges.constBegin()
        changedTiles = QList()
        changedTiles.reserve(self.mChanges.size())
        while (i != self.mChanges.constEnd()):
            tile = i.key()
            change = i.value()
            tile.setTerrain(change._from)
            changedTiles.append(tile)
            i += 1

        self.mMapDocument.emitTileTerrainChanged(changedTiles)

    def redo(self):
        i = self.mChanges.constBegin()
        changedTiles = QList()
        changedTiles.reserve(self.mChanges.size())
        while (i != self.mChanges.constEnd()):
            tile = i.key()
            change = i.value()
            tile.setTerrain(change.to)
            changedTiles.append(tile)
            i += 1

        self.mMapDocument.emitTileTerrainChanged(changedTiles)

    def id(self):
        return UndoCommands.Cmd_ChangeTileTerrain

    def mergeWith(self, other):
        if (not self.mMergeable):
            return False
        o = other
        if (o.mMapDocument and not (self.mMapDocument == o.mMapDocument and self.mTileset == o.mTileset)):
            return False
        i = o.mChanges.constBegin()
        i_end = o.mChanges.constEnd()
        while (i != i_end):
            tile = i.key()
            change = i.value()
            tileChange = self.mChanges.find(tile)
            if (tileChange != self.mChanges.end()):
                tileChange.to = change.to
            else:
                self.mChanges.insert(tile, change)
            i += 1

        self.mMergeable = o.mMergeable
        return True

    def initText(self):
        self.setText(QCoreApplication.translate("Undo Commands", "Change Tile Terrain"))

