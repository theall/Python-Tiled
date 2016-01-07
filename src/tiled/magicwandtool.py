##
# magicwandtool.py
# Copyright 2009-2010, Jeff Bland <jeff@teamphobic.com>
# Copyright 2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2011, Stefan Beller, stefanbeller@googlemail.com
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
from tilepainter import TilePainter
from abstracttiletool import AbstractTileTool
from PyQt5.QtCore import (
    Qt, 
    QCoreApplication
)
from PyQt5.QtGui import (
    QIcon,
    QRegion,
    QKeySequence
)
##
# Implements a tool that selects a region of connected similar tiles on the layer.
##
class MagicWandTool(AbstractTileTool):

    def __init__(self, parent = None):
        super().__init__(self.tr("Magic Wand"),
                           QIcon(":images/22x22/stock-tool-fuzzy-select-22.png"),
                           QKeySequence(self.tr("W")),
                           parent)

        self.mSelectedRegion = QRegion()

    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('MagicWandTool', sourceText, disambiguation, n)

    def mousePressed(self, event):
        if (event.button() != Qt.LeftButton):
            return
        modifiers = event.modifiers()
        document = self.mapDocument()
        selection = document.selectedArea()
        if (modifiers == Qt.ShiftModifier):
            selection += self.mSelectedRegion
        elif (modifiers == Qt.ControlModifier):
            selection -= self.mSelectedRegion
        elif (modifiers == (Qt.ControlModifier | Qt.ShiftModifier)):
            selection &= self.mSelectedRegion
        else:
            selection = self.mSelectedRegion
        if (selection != document.selectedArea()):
            cmd = ChangeSelectedArea(document, selection)
            document.undoStack().push(cmd)

    def mouseReleased(self, event):
        pass

    def languageChanged(self):
        self.setName(self.tr("Magic Wand"))
        self.setShortcut(QKeySequence(self.tr("W")))

    def tilePositionChanged(self, tilePos):
        # Make sure that a tile layer is selected
        tileLayer = self.currentTileLayer()
        if (not tileLayer):
            return
        regionComputer = TilePainter(self.mapDocument(), tileLayer)
        self.mSelectedRegion = regionComputer.computeFillRegion(tilePos)
        self.brushItem().setTileRegion(self.mSelectedRegion)
