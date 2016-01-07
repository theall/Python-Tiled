##
# tileselectiontool.py
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

from changeselectedarea import ChangeSelectedArea
from abstracttiletool import AbstractTileTool, TilePositionMethod
from PyQt5.QtCore import (
    Qt,
    QRect,
    QSize,
    QPoint, 
    QCoreApplication
)
from PyQt5.QtGui import (
    QIcon,
    QRegion,
    QKeySequence
)
class SelectionMode():
    Replace = 1
    Add = 2
    Subtract = 3
    Intersect = 4

class TileSelectionTool(AbstractTileTool):

    def __init__(self, parent = None):
        super().__init__(self.tr("Rectangular Select"),
                           QIcon(":images/22x22/stock-tool-rect-select.png"),
                           QKeySequence(self.tr("R")),
                           parent)
        self.mSelectionMode = SelectionMode.Replace
        self.mSelecting = False

        self.setTilePositionMethod(TilePositionMethod.BetweenTiles)

        self.mSelectionStart = QPoint()

    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('TileSelectionTool', sourceText, disambiguation, n)

    def mousePressed(self, event):
        button = event.button()
        modifiers = event.modifiers()
        if (button == Qt.LeftButton):
            if (modifiers == Qt.ControlModifier):
                self.mSelectionMode = SelectionMode.Subtract
            elif (modifiers == Qt.ShiftModifier):
                self.mSelectionMode = SelectionMode.Add
            elif (modifiers == (Qt.ControlModifier | Qt.ShiftModifier)):
                self.mSelectionMode = SelectionMode.Intersect
            else:
                self.mSelectionMode = SelectionMode.Replace

            self.mSelecting = True
            self.mSelectionStart = self.tilePosition()
            self.brushItem().setTileRegion(QRegion())

    def mouseReleased(self, event):
        if (event.button() == Qt.LeftButton):
            self.mSelecting = False
            document = self.mapDocument()
            selection = document.selectedArea()
            area = self.selectedArea()
            x = self.mSelectionMode
            if x==SelectionMode.Replace:
                selection = area
            elif x==SelectionMode.Add:
                selection += area
            elif x==SelectionMode.Subtract:
                selection = selection.xored(QRegion(area))
            elif x==SelectionMode.Intersect:
                selection &= area

            if (selection != document.selectedArea()):
                cmd = ChangeSelectedArea(document, selection)
                document.undoStack().push(cmd)

            self.brushItem().setTileRegion(QRegion())
            self.updateStatusInfo()

    def languageChanged(self):
        self.setName(self.tr("Rectangular Select"))
        self.setShortcut(QKeySequence(self.tr("R")))

    def tilePositionChanged(self, tilePos):
        if (self.mSelecting):
            self.brushItem().setTileRegion(self.selectedArea())

    def updateStatusInfo(self):
        if (not self.isBrushVisible() or not self.mSelecting):
            super().updateStatusInfo()
            return

        pos = self.tilePosition()
        area = self.selectedArea()
        self.setStatusInfo(self.tr("%d, %d - Rectangle: (%d x %d)"%((pos.x()), pos.y(), area.width(), area.height())))

    def selectedArea(self):
        tilePos = self.tilePosition()
        pos = QPoint(min(tilePos.x(), self.mSelectionStart.x()), min(tilePos.y(), self.mSelectionStart.y()))
        size = QSize(abs(tilePos.x() - self.mSelectionStart.x()), abs(tilePos.y() - self.mSelectionStart.y()))
        return QRect(pos, size)
