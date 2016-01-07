##
# terraindock.py
# Copyright 2008-2012, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2009, Edward Hutchins
# Copyright 2012, Stefan Beller, stefanbeller@googlemail.com
# Copyright 2012, Manu Evans
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

from terrainview import TerrainView
from terrain import Terrain
from PyQt5.QtCore import (
    QSortFilterProxyModel,
    QEvent,
    pyqtSignal
)
from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QDockWidget
)
##
# The dock widget that displays the terrains. Also keeps track of the
# currently selected terrain.
##
class TerrainDock(QDockWidget):
    ##
    # Emitted when the current tile changed.
    ##
    currentTerrainChanged = pyqtSignal(Terrain)

    ##
    # Constructor.
    ##
    def __init__(self, parent = None):
        super().__init__(parent)
        self.mMapDocument = None
        self.mTerrainView = TerrainView()
        self.mCurrentTerrain = None
        self.mProxyModel = TerrainFilterModel(self)
        self.setObjectName("TerrainDock")
        self.mTerrainView.setModel(self.mProxyModel)
        self.mTerrainView.selectionModel().currentRowChanged.connect(self.currentRowChanged)
        self.mTerrainView.pressed.connect(self.indexPressed)
        self.mProxyModel.rowsInserted.connect(self.expandRows)
        w = QWidget(self)
        horizontal = QHBoxLayout(w)
        horizontal.setSpacing(5)
        horizontal.setContentsMargins(5, 5, 5, 5)
        horizontal.addWidget(self.mTerrainView)
        self.setWidget(w)
        self.retranslateUi()

    def __del__(self):
        pass

    ##
    # Sets the map for which the tilesets should be displayed.
    ##
    def setMapDocument(self, mapDocument):
        if (self.mMapDocument == mapDocument):
            return
        # Clear all connections to the previous document
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
        self.mMapDocument = mapDocument
        if (self.mMapDocument):
            self.mTerrainView.setMapDocument(self.mMapDocument)
            self.mProxyModel.setSourceModel(self.mMapDocument.terrainModel())
            self.mTerrainView.expandAll()
        else:
            self.mProxyModel.setSourceModel(None)

    ##
    # Returns the currently selected tile.
    ##
    def currentTerrain(self):
        return self.mCurrentTerrain

    def changeEvent(self, e):
        super().changeEvent(e)
        x = e.type()
        if x==QEvent.LanguageChange:
            self.retranslateUi()
        else:
            pass

    def currentRowChanged(self, index):
        terrain = self.mTerrainView.terrainAt(index)
        if terrain:
            self.setCurrentTerrain(terrain)

    def indexPressed(self, index):
        terrain = self.mTerrainView.terrainAt(index)
        if terrain:
            self.mMapDocument.setCurrentObject(terrain)

    def expandRows(self, parent, first, last):
        # If it has a valid parent, then it's not a tileset
        if (parent.isValid()):
            return
        # Make sure any newly appearing tileset rows are expanded
        for row in range(first, last+1):
            self.mTerrainView.expand(self.mProxyModel.index(row, 0, parent))

    def setCurrentTerrain(self, terrain):
        if (self.mCurrentTerrain == terrain):
            return
        self.mCurrentTerrain = terrain
        if (terrain):
            self.mMapDocument.setCurrentObject(terrain)
        self.currentTerrainChanged.emit(self.mCurrentTerrain)

    def retranslateUi(self):
        self.setWindowTitle(self.tr("Terrains"))

##
# Filter model that filters out tilesets that have no terrains from the
# TerrainModel.
##
class TerrainFilterModel(QSortFilterProxyModel):

    def __init__(self, parent):
        super().__init__(parent)

    def filterAcceptsRow(self, sourceRow, sourceParent):
        if (sourceParent.isValid()):
            return True
        model = self.sourceModel()
        index = model.index(sourceRow, 0, sourceParent)
        return index.isValid() and model.hasChildren(index)

