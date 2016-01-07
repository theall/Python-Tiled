##
# changetileobjectgroup.py
# Copyright 2014, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
class ChangeTileObjectGroup(QUndoCommand):
    ##
    # Creates a command that changes the ObjectGroup of the given \a tile. The
    # command takes ownership of the \a objectGroup.
    ##
    def __init__(self, mapDocument, tile, objectGroup):
        super().__init__(QCoreApplication.translate("Undo Commands", "Change Tile Collision"))
        
        self.mMapDocument = mapDocument
        self.mTile = tile
        self.mObjectGroup = objectGroup

    def __del__(self):
        del self.mObjectGroup

    def undo(self):
        self.swap()

    def redo(self):
        self.swap()

    def swap(self):
        self.mObjectGroup = self.mTile.swapObjectGroup(self.mObjectGroup)
        self.mMapDocument.emitTileObjectGroupChanged(self.mTile)
