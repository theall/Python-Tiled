##
# renameterrain.py
# Copyright 2012-2013, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
class RenameTerrain(QUndoCommand):
    def __init__(self, mapDocument, tileset, terrainId, newName):
        super().__init__(QCoreApplication.translate("Undo Commands", "Change Terrain Name"))
        
        self.mTerrainModel = mapDocument.terrainModel()
        self.mTileset = tileset
        self.mTerrainId = terrainId
        self.mOldName = tileset.terrain(terrainId).name()
        self.mNewName = newName

    def undo(self):
        self.mTerrainModel.setTerrainName(self.mTileset, self.mTerrainId, self.mOldName)

    def redo(self):
        self.mTerrainModel.setTerrainName(self.mTileset, self.mTerrainId, self.mNewName)
