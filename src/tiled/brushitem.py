##
# brushitem.py
# Copyright 2008-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2010 Stefan Beller, stefanbeller@googlemail.com
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

from PyQt5.QtWidgets import (
    QGraphicsItem,
    QApplication
)
from PyQt5.QtGui import (
    QRegion,
    QColor
)
from PyQt5.QtCore import (
    QRectF,
    QPoint
)
##
# This brush item is used to represent a brush in a map scene before it is
# used.
##
class BrushItem(QGraphicsItem):
    ##
    # Constructor.
    ##
    def __init__(self):
        super().__init__()

        self.mMapDocument = None
        self.mBoundingRect = QRectF()
        self.mRegion = QRegion()
        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption)
        
    ##
    # Sets the map document this brush is operating on.
    ##
    def setMapDocument(self, mapDocument):
        if (self.mMapDocument == mapDocument):
            return
        self.mMapDocument = mapDocument
        # The tiles in the stamp may no longer be valid
        self.clear()

    ##
    # Clears the tile layer and region set on this item.
    ##
    def clear(self):
        self.setTileLayer(None)
        
    ##
    # Sets a tile layer representing this brush. When no tile layer is set,
    # the brush only draws the selection color.
    #
    # The BrushItem does not take ownership over the tile layer, but makes a
    # personal copy of the tile layer.
    ##
    def setTileLayer(self, tileLayer):
        self.mTileLayer = tileLayer
        if (tileLayer):
            self.mRegion = tileLayer.region()
        else:
            self.mRegion = QRegion()

        self.updateBoundingRect()
        self.update()

    ##
    # Returns the current tile layer.
    ##
    def tileLayer(self):
        return self.mTileLayer

    ##
    # Changes the position of the tile layer, if one is set.
    ##
    def setTileLayerPosition(self, pos):
        if (not self.mTileLayer):
            return
        oldPosition = QPoint(self.mTileLayer.x(), self.mTileLayer.y())
        if (oldPosition == pos):
            return

        self.mRegion.translate(pos - oldPosition)
        self.mTileLayer.setX(pos.x())
        self.mTileLayer.setY(pos.y())
        self.updateBoundingRect()

    ##
    # Sets the region of tiles that this brush item occupies.
    ##
    def setTileRegion(self, region):
        if type(region)!=QRegion:
            region = QRegion(region)
        if (self.mRegion == region):
            return
        self.mRegion = region
        self.updateBoundingRect()

    ##
    # Sets the layer offset used by the currently active layer.
    ##
    def setLayerOffset(self, offset):
        self.setPos(offset)
        
    ##
    # Returns the region of the current tile layer or the region that was set
    # using setTileRegion.
    ##
    def tileRegion(self):
        return self.mRegion

    # QGraphicsItem
    def boundingRect(self):
        return self.mBoundingRect

    def paint(self, painter, option, widget = None):
        insideMapHighlight = QApplication.palette().highlight().color()
        insideMapHighlight.setAlpha(64)
        outsideMapHighlight = QColor(255, 0, 0, 64)
        mapWidth = self.mMapDocument.map().width()
        mapHeight = self.mMapDocument.map().height()
        mapRegion = QRegion(0, 0, mapWidth, mapHeight)
        insideMapRegion = self.mRegion.intersected(mapRegion)
        outsideMapRegion = self.mRegion.subtracted(mapRegion)
        renderer = self.mMapDocument.renderer()
        if (self.mTileLayer):
            opacity = painter.opacity()
            painter.setOpacity(0.75)
            renderer.drawTileLayer(painter, self.mTileLayer, option.exposedRect)
            painter.setOpacity(opacity)
        renderer.drawTileSelection(painter, insideMapRegion, insideMapHighlight, option.exposedRect)
        renderer.drawTileSelection(painter, outsideMapRegion, outsideMapHighlight, option.exposedRect)

    def updateBoundingRect(self):
        self.prepareGeometryChange()
        if (not self.mMapDocument):
            self.mBoundingRect = QRectF()
            return

        bounds = self.mRegion.boundingRect()
        self.mBoundingRect = QRectF(self.mMapDocument.renderer().boundingRect(bounds))
        # Adjust for amount of pixels tiles extend at the top and to the right
        if (self.mTileLayer):
            map = self.mMapDocument.map()
            drawMargins = self.mTileLayer.drawMargins()
            drawMargins.setTop(drawMargins.top() - map.tileHeight())
            drawMargins.setRight(drawMargins.right() - map.tileWidth())
            # Since we're also drawing a tile selection, we should not apply
            # negative margins
            self.mBoundingRect.adjust(min(0, -drawMargins.left()),
                                 min(0, -drawMargins.top()),
                                 max(0, drawMargins.right()),
                                 max(0, drawMargins.bottom()))
