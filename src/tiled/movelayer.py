##
# movelayer.py
# Copyright 2008-2009, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
##
# A command that moves a map layer up or down in the layer stack.
##
class MoveLayer(QUndoCommand):
    Up, Down = range(2)
    ##
    # Constructor.
    #
    # @param mapDocument the map document that's being changed
    # @param index       the index of the layer to move
    # @param direction   the direction in which to move the layer
    ##
    def __init__(self, mapDocument, index, direction):
        super().__init__()
        
        self.mDirection = direction
        self.mIndex = index
        self.mMapDocument = mapDocument
        if direction == MoveLayer.Down:
            self.setText(QCoreApplication.translate("Undo Commands", "Lower Layer"))
        else:
            self.setText(QCoreApplication.translate("Undo Commands", "Raise Layer"))

    def undo(self):
        self.moveLayer()

    def redo(self):
        self.moveLayer()

    def moveLayer(self):
        currentIndex = self.mMapDocument.currentLayerIndex()
        selectedBefore = (self.mIndex == currentIndex)
        prevIndex = self.mIndex
        layerModel = self.mMapDocument.layerModel()
        layer = layerModel.takeLayerAt(self.mIndex)
        # Change the direction and index to swap undo/redo
        if self.mDirection == MoveLayer.Down:
            self.mIndex -= 1
        else:
            self.mIndex += 1

        if self.mDirection == MoveLayer.Down:
            self.mDirection = MoveLayer.Up
        else:
            self.mDirection = MoveLayer.Down
        selectedAfter = (self.mIndex == currentIndex)
        layerModel.insertLayer(self.mIndex, layer)
        # Set the layer that is now supposed to be selected
        if selectedBefore:
            x = self.mIndex
        else:
            if selectedAfter:
                x = prevIndex
            else:
                x = currentIndex
        self.mMapDocument.setCurrentLayerIndex(x)
