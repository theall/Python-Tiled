##
# tileselectionitem.py
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
    QRectF
)
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsItem, 
    QGraphicsObject
)
##
# A graphics item displaying a tile selection.
##
class TileSelectionItem(QGraphicsObject):

    ##
    # Constructs an item around the given selection model.
    ##
    def __init__(self, mapDocument):
        super().__init__()
        
        self.mBoundingRect = QRectF()
        self.mMapDocument = mapDocument

        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption)
        self.mMapDocument.selectedAreaChanged.connect(self.selectionChanged)
        self.mMapDocument.currentLayerIndexChanged.connect(self.currentLayerIndexChanged)
        self.updateBoundingRect()

    # QGraphicsItem
    def boundingRect(self):
        return self.mBoundingRect

    def paint(self, painter, option, widget = None):
        selection = self.mMapDocument.selectedArea()
        highlight = QApplication.palette().highlight().color()
        highlight.setAlpha(128)
        renderer = self.mMapDocument.renderer()
        renderer.drawTileSelection(painter, selection, highlight, option.exposedRect)

    def selectionChanged(self, newSelection, oldSelection):
        self.prepareGeometryChange()
        self.updateBoundingRect()
        # Make sure changes within the bounding rect are updated
        changedArea = newSelection.xored(oldSelection).boundingRect()
        self.update(QRectF(self.mMapDocument.renderer().boundingRect(changedArea)))

    def currentLayerIndexChanged(self):
        layer = self.mMapDocument.currentLayer()
        if layer:
            self.setPos(layer.offset())

    def updateBoundingRect(self):
        b = self.mMapDocument.selectedArea().boundingRect()
        self.mBoundingRect = QRectF(self.mMapDocument.renderer().boundingRect(b))
