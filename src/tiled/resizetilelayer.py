##
# resizetilelayer.py
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

from PyQt5.QtCore import (
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)
##
# Undo command that resizes a map layer.
##
class ResizeTileLayer(QUndoCommand):

    ##
    # Creates an undo command that resizes the \a layer to \a size,
    # shifting the tiles by \a offset.
    ##
    def __init__(self, mapDocument, layer, size, offset):
        super().__init__(QCoreApplication.translate("Undo Commands", "Resize Layer"))
        
        self.mMapDocument = mapDocument
        self.mIndex = mapDocument.map().layers().indexOf(layer)
        self.mOriginalLayer = None

        # Create the resized layer (once)
        self.mResizedLayer = layer.clone()
        self.mResizedLayer.resize(size, offset)

    def __del__(self):
        del self.mOriginalLayer
        del self.mResizedLayer

    def undo(self):
        self.mResizedLayer = self.swapLayer(self.mOriginalLayer)
        self.mOriginalLayer = None

    def redo(self):
        self.mOriginalLayer = self.swapLayer(self.mResizedLayer)
        self.mResizedLayer = None

    def swapLayer(self, layer):
        currentIndex = self.mMapDocument.currentLayerIndex()
        layerModel = self.mMapDocument.layerModel()
        replaced = layerModel.takeLayerAt(self.mIndex)
        layerModel.insertLayer(self.mIndex, layer)
        if (self.mIndex == currentIndex):
            self.mMapDocument.setCurrentLayerIndex(self.mIndex)
        return replaced

