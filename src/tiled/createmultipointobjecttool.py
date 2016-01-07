##
# createmultipointobjecttool.py
# Copyright 2014, Martin Ziel
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
from snaphelper import SnapHelper
from objectgroup import ObjectGroup
from mapobjectitem import MapObjectItem
from mapobject import MapObject
from createobjecttool import CreateObjectTool, CreationMode
from PyQt5.QtGui import (
    QPolygonF
)
from PyQt5.QtCore import (
    Qt,
    QPointF
)
from PyQt5.QtWidgets import (
    QApplication
)
class CreateMultipointObjectTool(CreateObjectTool):
    def __init__(self, parent):
        super().__init__(CreationMode.CreateGeometry, parent)

        self.mOverlayPolygonObject = MapObject()
        self.mOverlayObjectGroup = ObjectGroup()
        self.mOverlayObjectGroup.addObject(self.mOverlayPolygonObject)
        highlight = QApplication.palette().highlight().color()
        self.mOverlayObjectGroup.setColor(highlight)

    def startNewMapObject(self, pos, objectGroup):
        super().startNewMapObject(pos, objectGroup)
        newMapObject = self.mNewMapObjectItem.mapObject()
        polygon = QPolygonF()
        polygon.append(QPointF())
        newMapObject.setPolygon(polygon)
        polygon.append(QPointF()) # The last point is connected to the mouse
        self.mOverlayPolygonObject.setPolygon(polygon)
        self.mOverlayPolygonObject.setShape(newMapObject.shape())
        self.mOverlayPolygonObject.setPosition(pos)
        self.mOverlayPolygonItem = MapObjectItem(self.mOverlayPolygonObject, self.mapDocument(), self.mObjectGroupItem)

    def languageChanged(self):
        pass

    def mouseMovedWhileCreatingObject(self, pos, modifiers):
        renderer = self.mapDocument().renderer()
        pixelCoords = renderer.screenToPixelCoords_(pos)
        SnapHelper(renderer, modifiers).snap(pixelCoords)
        pixelCoords -= self.mNewMapObjectItem.mapObject().position()
        polygon = self.mOverlayPolygonObject.polygon()
        polygon[-1] = pixelCoords
        self.mOverlayPolygonItem.setPolygon(polygon)

    def mousePressedWhileCreatingObject(self, event):
        if (event.button() == Qt.RightButton):
            self.finishNewMapObject()
        elif (event.button() == Qt.LeftButton):
            current = self.mNewMapObjectItem.mapObject().polygon()
            next = self.mOverlayPolygonObject.polygon()
            # If the last position is still the same, ignore the click
            if (next.last() == current.last()):
                return
            # Assign current overlay polygon to the new object
            self.mNewMapObjectItem.setPolygon(next)
            # Add a new editable point to the overlay
            next.append(next.last())
            self.mOverlayPolygonItem.setPolygon(next)
