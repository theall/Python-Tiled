##
# editterraindialog.py
# Copyright 2012, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from Ui_editterraindialog import Ui_EditTerrainDialog
from zoomable import Zoomable
from utils import Utils
from tile import setTerrainCorner
from tilesetmodel import TilesetModel
from terrain import Terrain
from changetileterrain import ChangeTileTerrain
from addremoveterrain import AddTerrain, RemoveTerrain
from PyQt5.QtGui import (
    QKeySequence
)
from PyQt5.QtCore import (
    Qt,
    QItemSelectionModel,
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QHeaderView,
    QShortcut,
    QDialog,
    QUndoCommand
)
from pyqtcore import QString
class EditTerrainDialog(QDialog):
    def __init__(self, mapDocument, tileset, parent = None):
        super().__init__(parent)
        self.mUi = Ui_EditTerrainDialog()
        self.mMapDocument = mapDocument
        self.mInitialUndoStackIndex = self.mMapDocument.undoStack().index()
        self.mTileset = tileset

        self.mUi.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        Utils.setThemeIcon(self.mUi.redo, "edit-redo")
        Utils.setThemeIcon(self.mUi.undo, "edit-undo")
        zoomable = Zoomable(self)
        zoomable.connectToComboBox(self.mUi.zoomComboBox)
        tilesetModel = TilesetModel(self.mTileset, self.mUi.tilesetView)
        mapDocument.tileTerrainChanged.connect(tilesetModel.tilesChanged)
        self.mUi.tilesetView.setEditTerrain(True)
        self.mUi.tilesetView.setMapDocument(mapDocument)
        self.mUi.tilesetView.setZoomable(zoomable)
        self.mUi.tilesetView.setModel(tilesetModel)
        self.mTerrainModel = mapDocument.terrainModel()
        rootIndex = self.mTerrainModel.index(tileset)
        self.mUi.terrainList.setMapDocument(mapDocument)
        self.mUi.terrainList.setModel(self.mTerrainModel)
        self.mUi.terrainList.setRootIndex(rootIndex)
        terrainListHeader = self.mUi.terrainList.header()
        terrainListHeader.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        selectionModel = self.mUi.terrainList.selectionModel()
        selectionModel.currentRowChanged.connect(self.selectedTerrainChanged)
        if (self.mTerrainModel.rowCount(rootIndex) > 0):
            selectionModel.setCurrentIndex(self.mTerrainModel.index(0, 0, rootIndex),
                                            QItemSelectionModel.SelectCurrent |
                                            QItemSelectionModel.Rows)
            self.mUi.terrainList.setFocus()

        self.mUi.eraseTerrain.toggled.connect(self.eraseTerrainToggled)
        self.mUi.addTerrainTypeButton.clicked.connect(self.addTerrainType)
        self.mUi.removeTerrainTypeButton.clicked.connect(self.removeTerrainType)
        self.mUi.tilesetView.createNewTerrainSignal.connect(self.addTerrainType)
        self.mUi.tilesetView.terrainImageSelected.connect(self.setTerrainImage)
        undoStack = mapDocument.undoStack()
        undoStack.indexChanged.connect(self.updateUndoButton)
        undoStack.canRedoChanged.connect(self.mUi.redo.setEnabled)
        self.mUi.undo.clicked.connect(undoStack.undo)
        self.mUi.redo.clicked.connect(undoStack.redo)
        self.mUndoShortcut = QShortcut(QKeySequence.Undo, self)
        self.mRedoShortcut = QShortcut(QKeySequence.Redo, self)
        self.mUndoShortcut.activated.connect(undoStack.undo)
        self.mRedoShortcut.activated.connect(undoStack.redo)
        eraseShortcut = QShortcut(QKeySequence(self.tr("E")), self)
        eraseShortcut.activated.connect(self.mUi.eraseTerrain.toggle)
        self.updateUndoButton()
        Utils.restoreGeometry(self)

    def __del__(self):
        Utils.saveGeometry(self)
        del self.mUi

    def selectedTerrainChanged(self, index):
        terrainId = -1
        terrain = self.mTerrainModel.terrainAt(index)
        if terrain:
            terrainId = terrain.id()
        self.mUi.tilesetView.setTerrainId(terrainId)
        self.mUi.removeTerrainTypeButton.setEnabled(terrainId != -1)

    def eraseTerrainToggled(self, checked):
        self.mUi.tilesetView.setEraseTerrain(checked)

    def addTerrainType(self, tile = None):
        if tile:
            x = tile.id()
        else:
            x = -1
        terrain = Terrain(self.mTileset.terrainCount(), self.mTileset, QString(), x)
        terrain.setName(self.tr("New Terrain"))
        self.mMapDocument.undoStack().push(AddTerrain(self.mMapDocument, terrain))
        # Select the newly added terrain and edit its name
        index = self.mTerrainModel.index(terrain)
        selectionModel = self.mUi.terrainList.selectionModel()
        selectionModel.setCurrentIndex(index,
                                        QItemSelectionModel.ClearAndSelect |
                                        QItemSelectionModel.Rows)
        self.mUi.terrainList.edit(index)

    def removeTerrainType(self):
        currentIndex = self.mUi.terrainList.currentIndex()
        if (not currentIndex.isValid()):
            return
        terrain = self.mTerrainModel.terrainAt(currentIndex)
        removeTerrain = RemoveTerrain(self.mMapDocument, terrain)
        ##
        # Clear any references to the terrain that is about to be removed with
        # an undo command, as a way of preserving them when undoing the removal
        # of the terrain.
        ##
        changes = ChangeTileTerrain.Changes()
        for tile in terrain.tileset().tiles():
            tileTerrain = tile.terrain()
            for corner in range(4):
                if (tile.cornerTerrainId(corner) == terrain.id()):
                    tileTerrain = setTerrainCorner(tileTerrain, corner, 0xFF)

            if (tileTerrain != tile.terrain()):
                changes.insert(tile, ChangeTileTerrain.Change(tile.terrain(),
                                                               tileTerrain))

        undoStack = self.mMapDocument.undoStack()
        if (not changes.isEmpty()):
            undoStack.beginMacro(removeTerrain.text())
            undoStack.push(ChangeTileTerrain(self.mMapDocument, changes))

        self.mMapDocument.undoStack().push(removeTerrain)
        if (not changes.isEmpty()):
            undoStack.endMacro()
        ##
        # Removing a terrain usually changes the selected terrain without the
        # selection changing rows, so we can't rely on the currentRowChanged
        # signal.
        ##
        self.selectedTerrainChanged(self.mUi.terrainList.currentIndex())

    def setTerrainImage(self, tile):
        currentIndex = self.mUi.terrainList.currentIndex()
        if (not currentIndex.isValid()):
            return
        terrain = self.mTerrainModel.terrainAt(currentIndex)
        self.mMapDocument.undoStack().push(SetTerrainImage(self.mMapDocument,
                                                            terrain.tileset(),
                                                            terrain.id(),
                                                            tile.id()))

    def updateUndoButton(self):
        undoStack = self.mMapDocument.undoStack()
        canUndo = undoStack.index() > self.mInitialUndoStackIndex
        canRedo = undoStack.canRedo()
        self.mUi.undo.setEnabled(canUndo)
        self.mUi.redo.setEnabled(canRedo)
        self.mUndoShortcut.setEnabled(canUndo)
        self.mRedoShortcut.setEnabled(canRedo)

class SetTerrainImage(QUndoCommand):
    def __init__(self, mapDocument, tileset, terrainId, tileId):
        super().__init__(QCoreApplication.translate("Undo Commands", "Change Terrain Image"))

        self.mTerrainModel = mapDocument.terrainModel()
        self.mTileset = tileset
        self.mTerrainId = terrainId
        self.mOldImageTileId = tileset.terrain(terrainId).imageTileId()
        self.mNewImageTileId = tileId

    def undo(self):
        self.mTerrainModel.setTerrainImage(self.mTileset, self.mTerrainId, self.mOldImageTileId)

    def redo(self):
        self.mTerrainModel.setTerrainImage(self.mTileset, self.mTerrainId, self.mNewImageTileId)
