##
# createtileobjecttool.py
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
from utils import Utils
from tilelayer import Cell
from snaphelper import SnapHelper
from mapobject import MapObject
from createobjecttool import CreateObjectTool, CreationMode
from PyQt5.QtCore import (
    Qt,
    QPointF
)
from PyQt5.QtGui import (
    QIcon,
    QKeySequence
)
class CreateTileObjectTool(CreateObjectTool):
    def __init__(self, parent):
        super().__init__(CreationMode.CreateTile, parent)

        self.setIcon(QIcon(":images/24x24/insert-image.png"))
        Utils.setThemeIcon(self, "insert-image")
        self.languageChanged()

    def languageChanged(self):
        self.setName(self.tr("Insert Tile"))
        self.setShortcut(QKeySequence(self.tr("T")))

    def mouseMovedWhileCreatingObject(self, pos, modifiers):
        renderer = self.mapDocument().renderer()
        imgSize = self.mNewMapObjectItem.mapObject().cell().tile.size()
        diff = QPointF(-imgSize.width() / 2, imgSize.height() / 2)
        pixelCoords = renderer.screenToPixelCoords_(pos + diff)
        SnapHelper(renderer, modifiers).snap(pixelCoords)
        self.mNewMapObjectItem.mapObject().setPosition(pixelCoords)
        self.mNewMapObjectItem.syncWithMapObject()
        self.mNewMapObjectItem.setZValue(10000) # sync may change it
        self.mNewMapObjectItem.setOpacity(0.75)

    def mousePressedWhileCreatingObject(self, event):
        if (event.button() == Qt.RightButton):
            self.cancelNewMapObject()

    def mouseReleasedWhileCreatingObject(self, event):
        if (event.button() == Qt.LeftButton):
            self.finishNewMapObject()

    def startNewMapObject(self, pos, objectGroup):
        super().startNewMapObject(pos, objectGroup)
        if (self.mNewMapObjectItem):
            self.mNewMapObjectItem.setOpacity(0.75)

    def createNewMapObject(self):
        if (not self.mTile):
            return None
        newMapObject = MapObject()
        newMapObject.setShape(MapObject.Rectangle)
        newMapObject.setCell(Cell(self.mTile))
        newMapObject.setSize(self.mTile.size())
        return newMapObject
