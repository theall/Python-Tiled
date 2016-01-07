##
# offsetmapdialog.py
# Copyright 2009, Jeff Bland <jeff@teamphobic.com>
# Copyright 2009, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from Ui_offsetmapdialog import Ui_OffsetMapDialog
from pyqtcore import QList
from PyQt5.QtCore import (
    Qt,
    QPoint,
    QRect
)
from PyQt5.QtWidgets import (
    QDialog
)
class OffsetMapDialog(QDialog):
    AllVisibleLayers, AllLayers, SelectedLayer = range(3)
    WholeMap, CurrentSelectionArea = range(2)
    def __init__(self, mapDocument, parent = None):
        super().__init__(parent)
        self.mUi = Ui_OffsetMapDialog()
        self.mMapDocument = mapDocument

        self.mUi.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        if (self.mMapDocument.selectedArea().isEmpty()):
            self.disableBoundsSelectionCurrentArea()
        else:
            self.mUi.boundsSelection.setCurrentIndex(1)

    def __del__(self):
        del self.mUi

    def affectedLayerIndexes(self):
        layerIndexes = QList()
        map = self.mMapDocument.map()
        x = self.layerSelection()
        if x==OffsetMapDialog.AllVisibleLayers:
            for i in range(map.layerCount()):
                if (map.layerAt(i).isVisible()):
                    layerIndexes.append(i)
        elif x==OffsetMapDialog.AllLayers:
            for i in range(map.layerCount()):
                layerIndexes.append(i)
        elif x==OffsetMapDialog.SelectedLayer:
            layerIndexes.append(self.mMapDocument.currentLayerIndex())

        return layerIndexes

    def affectedBoundingRect(self):
        boundingRect = QRect()
        x = self.boundsSelection()
        if x==OffsetMapDialog.WholeMap:
            boundingRect = QRect(QPoint(0, 0), self.mMapDocument.map().size())
        elif x==OffsetMapDialog.CurrentSelectionArea:
            selection = self.mMapDocument.selectedArea()
            boundingRect = selection.boundingRect()

        return boundingRect

    def offset(self):
        return QPoint(self.mUi.xOffset.value(), self.mUi.yOffset.value())

    def wrapX(self):
        return self.mUi.wrapX.isChecked()

    def wrapY(self):
        return self.mUi.wrapY.isChecked()

    def layerSelection(self):
        x = self.mUi.layerSelection.currentIndex()
        if x==0:
            return OffsetMapDialog.AllVisibleLayers
        elif x==1:
            return OffsetMapDialog.AllLayers
        return OffsetMapDialog.SelectedLayer
        
    def boundsSelection(self):
        if (self.mUi.boundsSelection.currentIndex() == 0):
            return OffsetMapDialog.WholeMap
        return OffsetMapDialog.CurrentSelectionArea

    def disableBoundsSelectionCurrentArea(self):
        self.mUi.boundsSelection.setEnabled(False)
        self.mUi.boundsSelection.setCurrentIndex(0)

