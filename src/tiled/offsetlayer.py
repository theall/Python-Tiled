##
# offsetlayer.py
# Copyright 2009, Jeff Bland <jeff@teamphobic.com>
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

from layer import Layer
from PyQt5.QtCore import (
    QPointF,
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)
##
# Undo command that offsets a map layer.
##
class OffsetLayer(QUndoCommand):

    ##
    # Creates an undo command that offsets the layer at \a index by \a offset,
    # within \a bounds, and can optionally wrap on the x or y axis.
    ##
    def __init__(self, mapDocument, index, offset, bounds, wrapX, wrapY):
        super().__init__(QCoreApplication.translate("Undo Commands", "Offset Layer"))
        
        self.mMapDocument = mapDocument
        self.mIndex = index
        self.mOriginalLayer = None

        # Create the offset layer (once)
        layer = self.mMapDocument.map().layerAt(self.mIndex)
        self.mOffsetLayer = layer.clone()
        x = self.mOffsetLayer.layerType()
        if x==Layer.TileLayerType:
            self.mOffsetLayer.offsetTiles(offset, bounds, wrapX, wrapY)
        elif x==Layer.ObjectGroupType:
            # Object groups need offset and bounds converted to pixel units
            renderer = mapDocument.renderer()
            origin = renderer.tileToPixelCoords_(QPointF())
            pixelOffset = renderer.tileToPixelCoords_(offset) - origin
            pixelBounds = renderer.tileToPixelCoords_(bounds)
            self.mOffsetLayer.offsetObjects(pixelOffset, pixelBounds, wrapX, wrapY)
        elif x==Layer.ImageLayerType:
            # Nothing done for the image layer at the moment
            pass

    def __del__(self):
        del self.mOriginalLayer
        del self.mOffsetLayer

    def undo(self):
        self.mOffsetLayer = self.swapLayer(self.mOriginalLayer)
        self.mOriginalLayer = None

    def redo(self):
        self.mOriginalLayer = self.swapLayer(self.mOffsetLayer)
        self.mOffsetLayer = None

    def swapLayer(self, layer):
        currentIndex = self.mMapDocument.currentLayerIndex()
        layerModel = self.mMapDocument.layerModel()
        replaced = layerModel.takeLayerAt(self.mIndex)
        layerModel.insertLayer(self.mIndex, layer)
        if (self.mIndex == currentIndex):
            self.mMapDocument.setCurrentLayerIndex(self.mIndex)
        return replaced

