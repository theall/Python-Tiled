##
# erasetiles.py
# Copyright 2009, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
from tilepainter import TilePainter
from PyQt5.QtCore import (
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)
from undocommands import UndoCommands
class EraseTiles(QUndoCommand):
    def __init__(self, mapDocument, tileLayer, region):
        super().__init__()
        
        self.mMapDocument = mapDocument
        self.mTileLayer = tileLayer
        self.mRegion = region
        self.mMergeable = False

        self.setText(QCoreApplication.translate("Undo Commands", "Erase"))
        # Store the tiles that are to be erased
        r = self.mRegion.translated(-self.mTileLayer.x(), -self.mTileLayer.y())
        self.mErasedCells = self.mTileLayer.copy(r)

    def __del__(self):
        del self.mErasedCells

    ##
    # Sets whether this undo command can be merged with an existing command.
    ##
    def setMergeable(self, mergeable):
        self.mMergeable = mergeable

    def undo(self):
        bounds = self.mRegion.boundingRect()
        painter = TilePainter(self.mMapDocument, self.mTileLayer)
        painter.drawCells(bounds.x(), bounds.y(), self.mErasedCells)

    def redo(self):
        painter = TilePainter(self.mMapDocument, self.mTileLayer)
        painter.erase(self.mRegion)

    def id(self):
        return UndoCommands.Cmd_EraseTiles

    def mergeWith(self, other):
        o = other
        if (not (self.mMapDocument == o.mMapDocument and self.mTileLayer == o.mTileLayer and o.mMergeable)):
            return False
        combinedRegion = self.mRegion.united(o.mRegion)
        if (self.mRegion != combinedRegion):
            bounds = self.mRegion.boundingRect()
            combinedBounds = combinedRegion.boundingRect()
            # Resize the erased tiles layer when necessary
            if (bounds != combinedBounds):
                shift = bounds.topLeft() - combinedBounds.topLeft()
                self.mErasedCells.resize(combinedBounds.size(), shift)

            # Copy the newly erased tiles over
            otherBounds = o.mRegion.boundingRect()
            pos = otherBounds.topLeft() - combinedBounds.topLeft()
            self.mErasedCells.merge(pos, o.mErasedCells)
            self.mRegion = combinedRegion

        return True
