# -*- coding: utf-8 -*-
##
# addremoveterrain.py
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
####

from PyQt5.QtCore import (
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)

###
# Abstract base class for AddTerrain and RemoveTerrain.
##
class AddRemoveTerrain(QUndoCommand):
    def __init__(self, mapDocument, tileset, index, terrain):
        super().__init__(mapDocument, tileset, index, terrain)

        self.mTileset = tileset
        self.mIndex = index
        self.mTerrain = terrain

    def __del__(self):
        del self.mTerrain

    def addTerrain(self):
        self.mMapDocument.terrainModel().insertTerrain(self.mTileset, self.mIndex, self.mTerrain)
        self.mTerrain = None

    def removeTerrain(self):
        self.mTerrain = self.mMapDocument.terrainModel().takeTerrainAt(self.mTileset, self.mIndex)

###
# Adds a terrain to a map.
##
class AddTerrain(AddRemoveTerrain):
    def __init__(self, mapDocument, terrain):
        super(AddTerrain, self).__init__(mapDocument, terrain.tileset(), terrain.tileset().terrainCount(), terrain)

        self.setText(QCoreApplication.translate("Undo Commands", "Add Terrain"))

    def undo(self):
        self.removeTerrain()

    def redo(self):
        self.addTerrain()

###
# Removes a terrain from a map.
##
class RemoveTerrain(AddRemoveTerrain):
    def __init__(self, mapDocument, terrain):
        super(AddTerrain, self).__init__(mapDocument, terrain.tileset(), terrain.id(), None)

        self.setText(QCoreApplication.translate("Undo Commands", "Remove Terrain"))

    def undo(self):
        self.addTerrain()

    def redo(self):
        self.removeTerrain()

