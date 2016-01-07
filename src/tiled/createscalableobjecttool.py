##
# createscalableobjecttool.py
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
from createobjecttool import CreateObjectTool, CreationMode
from PyQt5.QtCore import (
    Qt,
    QPointF,
    QSizeF
)
class CreateScalableObjectTool(CreateObjectTool):
    def __init__(self, parent):
        super().__init__(CreationMode.CreateGeometry, parent)

    def mouseMovedWhileCreatingObject(self, pos, modifiers):
        renderer = self.mapDocument().renderer()
        pixelCoords = renderer.screenToPixelCoords_(pos)
        # Update the size of the new map object
        objectPos = self.mNewMapObjectItem.mapObject().position()
        newSize = QPointF(max(0.0, pixelCoords.x() - objectPos.x()),
                        max(0.0, pixelCoords.y() - objectPos.y()))
        # Holding shift creates circle or square
        if (modifiers & Qt.ShiftModifier):
            m = max(newSize.x(), newSize.y())
            newSize.setX(m)
            newSize.setY(m)

        SnapHelper(renderer, modifiers).snap(newSize)
        self.mNewMapObjectItem.resizeObject(QSizeF(newSize.x(), newSize.y()))

    def mousePressedWhileCreatingObject(self, event):
        if (event.button() == Qt.RightButton):
            self.cancelNewMapObject()

    def mouseReleasedWhileCreatingObject(self, event):
        if (event.button() == Qt.LeftButton):
            self.finishNewMapObject()
