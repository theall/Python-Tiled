##
# imagelayeritem.py
# Copyright 2008-2009, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2011, Gregory Nickonov
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
    QRectF
)
from PyQt5.QtWidgets import (
    QGraphicsItem
)
##
# A graphics item displaying an image layer in a QGraphicsView.
##
class ImageLayerItem(QGraphicsItem):

    ##
    # Constructor.
    #
    # @param layer       the image layer to be displayed
    # @param mapDocument the map document owning the map of this layer
    ##
    def __init__(self, layer, mapDocument):
        super().__init__()
        
        self.mBoundingRect = QRectF()
        self.mLayer = layer
        self.mMapDocument = mapDocument

        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption)
        self.syncWithImageLayer()
        self.setOpacity(self.mLayer.opacity())

        

    ##
    # Updates the size and position of this item. Should be called when the
    # size of either the image layer or its associated map have changed.
    #
    # Calling this function when the size of the map changes is necessary
    # because in certain map orientations this affects the layer position
    # (when using the IsometricRenderer for example).
    ##
    def syncWithImageLayer(self):
        self.prepareGeometryChange()
        self.mBoundingRect = QRectF(self.mMapDocument.renderer().boundingRect_(self.mLayer))

    # QGraphicsItem
    def boundingRect(self):
        return self.mBoundingRect

    def paint(self, painter, option, widget = None):
        # TODO: Display a border around the layer when selected
        renderer = self.mMapDocument.renderer()
        renderer.drawImageLayer(painter, self.mLayer, option.exposedRect)
