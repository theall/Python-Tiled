##
# selectsametiletool.py
# Copyright 2015, Mamed Ibrahimov <ibramlab@gmail.com>
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

from abstracttiletool import AbstractTileTool
from changeselectedarea import ChangeSelectedArea
from PyQt5.QtCore import (
    Qt, 
    QCoreApplication
)
from PyQt5.QtGui import (
    QKeySequence,
    QIcon,
    QRegion
)

##
# Implements a tool that selects a region with all similar tiles on the layer.
##
class SelectSameTileTool(AbstractTileTool):
    def __init__(self, parent = None):
        super().__init__(self.tr("Select Same Tile"),
                           QIcon(":images/22x22/stock-tool-by-color-select.png"),
                           QKeySequence(self.tr("S")),
                           parent)

        self.mSelectedRegion = QRegion()

    def __del__(self):
        pass
        
    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('SelectSameTileTool', sourceText, disambiguation, n)

    def trUtf8(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('SelectSameTileTool', sourceText, disambiguation, n)
        
    def mousePressed(self, event):
        if (event.button() != Qt.LeftButton):
            return
        modifiers = event.modifiers()
        document = self.mapDocument()
        selection = document.selectedArea()
        if (modifiers == Qt.ShiftModifier):
            selection += self.mSelectedRegion
        elif modifiers == Qt.ControlModifier:
            selection -= self.mSelectedRegion
        elif modifiers == (Qt.ControlModifier | Qt.ShiftModifier):
            selection &= self.mSelectedRegion
        else:
            selection = self.mSelectedRegion
        if (selection != document.selectedArea()):
            cmd = ChangeSelectedArea(document, selection)
            document.undoStack().push(cmd)

    def mouseReleased(self, event):
        pass
        
    def languageChanged(self):
        self.setName(self.tr("Select Same Tile"))
        self.setShortcut(QKeySequence(self.tr("S")))

    def tilePositionChanged(self, tilePos):
        # Make sure that a tile layer is selected and contains current tile pos.
        tileLayer = self.currentTileLayer ()
        if (not tileLayer):
            return
        resultRegion = QRegion()
        if (tileLayer.contains(tilePos)):
            matchCell = tileLayer.cellAt(tilePos)
            resultRegion = tileLayer.region(lambda cell:cell == matchCell)
        
        self.mSelectedRegion = resultRegion
        self.brushItem().setTileRegion(self.mSelectedRegion)



