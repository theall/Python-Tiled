##
# eraser.py
# Copyright 2009-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from erasetiles import EraseTiles
from geometry import pointsOnLine
from abstracttiletool import AbstractTileTool
from PyQt5.QtGui import (
    QIcon,
    QRegion,
    QKeySequence
)
from PyQt5.QtCore import (
    Qt,
    QSize,
    QRect,
    QPoint, 
    QCoreApplication
)
##
# Implements a simple eraser tool.
##
class Eraser(AbstractTileTool):
    def __init__(self, parent = None):
        super().__init__(self.tr("Eraser"),
                           QIcon(":images/22x22/stock-tool-eraser.png"),
                           QKeySequence(self.tr("E")),
                           parent)
        self.mErasing = False

        self.mLastTilePos = QPoint()

    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('Eraser', sourceText, disambiguation, n)

    def mousePressed(self, event):
        if (not self.brushItem().isVisible()):
            return
        if (event.button() == Qt.LeftButton):
            self.mErasing = True
            self.doErase(False)

    def mouseReleased(self, event):
        if (event.button() == Qt.LeftButton):
            self.mErasing = False

    def languageChanged(self):
        self.setName(self.tr("Eraser"))
        self.setShortcut(QKeySequence(self.tr("E")))

    def tilePositionChanged(self, tilePos):
        self.brushItem().setTileRegion(QRect(tilePos, QSize(1, 1)))
        if (self.mErasing):
            self.doErase(True)

    def doErase(self, continuation):
        tileLayer = self.currentTileLayer()
        tilePos = self.tilePosition()
        eraseRegion = QRegion(tilePos.x(), tilePos.y(), 1, 1)
        if (continuation):
            for p in pointsOnLine(self.mLastTilePos, tilePos):
                eraseRegion |= QRegion(p.x(), p.y(), 1, 1)

        self.mLastTilePos = self.tilePosition()
        if (not tileLayer.bounds().intersects(eraseRegion.boundingRect())):
            return
        erase = EraseTiles(self.mapDocument(), tileLayer, eraseRegion)
        erase.setMergeable(continuation)
        self.mapDocument().undoStack().push(erase)
        self.mapDocument().emitRegionEdited(eraseRegion, tileLayer)
