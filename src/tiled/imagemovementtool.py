##
# imagemovementtool.py
# Copyright 2014, Mattia Basaglia
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
from changeimagelayerposition import ChangeImageLayerPosition
from abstractimagetool import AbstractImageTool
from PyQt5.QtCore import (
    QPoint,
    QPointF, 
    QCoreApplication
)
from PyQt5.QtGui import (
    QIcon, 
    QKeySequence
)

class ImageMovementTool(AbstractImageTool):
    def __init__(self, parent = None):
        super().__init__(self.tr("Move Images"),
                       QIcon(":images/24x24/move-image-layer.png"),
                       QKeySequence(self.tr("M")),
                       parent)

        self.mLayerStart = QPoint()
        self.mMousePressed = False
        self.mMouseStart = QPointF()

    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('MapReader', sourceText, disambiguation, n)

    def activate(self, scene):
        super().activate(scene)

    def deactivate(self, scene):
        super().deactivate(scene)

    def mouseEntered(self):
        pass

    def mouseMoved(self, pos, modifiers):
        super().mouseMoved(pos, modifiers)
        if (not self.mMousePressed):
            return
        layer = self.currentImageLayer()
        if (not layer):
            return
        newPosition = self.mLayerStart + (pos - self.mMouseStart)
        SnapHelper(self.mapDocument().renderer(), modifiers).snap(newPosition)
        layer.setPosition(newPosition.toPoint())
        self.mapDocument().emitImageLayerChanged(layer)

    def mousePressed(self, event):
        self.mMousePressed = True
        self.mMouseStart = event.scenePos()
        layer = self.currentImageLayer()
        if layer:
            self.mLayerStart = layer.position()

    def mouseReleased(self, event):
        self.mMousePressed = False
        layer = self.currentImageLayer()
        if layer:
            layerFinish = layer.position()
            layer.setPosition(self.mLayerStart)
            self.mapDocument().undoStack().push(ChangeImageLayerPosition(self.mapDocument(), self.currentImageLayer(), layerFinish))

    def languageChanged(self):
        self.setName(self.tr("Move Images"))
        self.setShortcut(QKeySequence(self.tr("M")))
