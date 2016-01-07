##
# mapdocumentactionhandler.py
# Copyright 2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2011, Stefan Beller <stefanbeller@googlemail.com
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
import math
from layer import Layer
from documentmanager import DocumentManager
from changeselectedarea import ChangeSelectedArea
from pyqtcore import QString
from PyQt5.QtCore import (
    QRect,
    QObject,
    pyqtSignal
)
from PyQt5.QtGui import (
    QIcon,
    QKeySequence,
    QCursor,
    QRegion
)
from PyQt5.QtWidgets import (
    QApplication,
    QAction
)
##
# The map document action handler deals with most basic actions that can be
# performed on a MapDocument.
##
class MapDocumentActionHandler(QObject):
    mInstance = None
    mapDocumentChanged = pyqtSignal(list)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.mMapDocument = None

        MapDocumentActionHandler.mInstance = self
        self.mActionSelectAll = QAction(self)
        self.mActionSelectAll.setShortcuts(QKeySequence.SelectAll)
        self.mActionSelectNone = QAction(self)
        self.mActionSelectNone.setShortcut(self.tr("Ctrl+Shift+A"))
        self.mActionCropToSelection = QAction(self)
        self.mActionAddTileLayer = QAction(self)
        self.mActionAddObjectGroup = QAction(self)
        self.mActionAddImageLayer = QAction(self)
        self.mActionDuplicateLayer = QAction(self)
        self.mActionDuplicateLayer.setShortcut(self.tr("Ctrl+Shift+D"))
        self.mActionDuplicateLayer.setIcon(QIcon(":/images/16x16/stock-duplicate-16.png"))
        self.mActionMergeLayerDown = QAction(self)
        self.mActionRemoveLayer = QAction(self)
        self.mActionRemoveLayer.setIcon(QIcon(":/images/16x16/edit-delete.png"))
        self.mActionSelectPreviousLayer = QAction(self)
        self.mActionSelectPreviousLayer.setShortcut(self.tr("Ctrl+PgUp"))
        self.mActionSelectNextLayer = QAction(self)
        self.mActionSelectNextLayer.setShortcut(self.tr("Ctrl+PgDown"))
        self.mActionMoveLayerUp = QAction(self)
        self.mActionMoveLayerUp.setShortcut(self.tr("Ctrl+Shift+Up"))
        self.mActionMoveLayerUp.setIcon(
                QIcon(":/images/16x16/go-up.png"))
        self.mActionMoveLayerDown = QAction(self)
        self.mActionMoveLayerDown.setShortcut(self.tr("Ctrl+Shift+Down"))
        self.mActionMoveLayerDown.setIcon(
                QIcon(":/images/16x16/go-down.png"))
        self.mActionToggleOtherLayers = QAction(self)
        self.mActionToggleOtherLayers.setShortcut(self.tr("Ctrl+Shift+H"))
        self.mActionToggleOtherLayers.setIcon(
                QIcon(":/images/16x16/show_hide_others.png"))
        self.mActionLayerProperties = QAction(self)
        self.mActionLayerProperties.setIcon(
                QIcon(":images/16x16/document-properties.png"))
        self.mActionDuplicateObjects = QAction(self)
        self.mActionDuplicateObjects.setIcon(QIcon(":/images/16x16/stock-duplicate-16.png"))
        self.mActionRemoveObjects = QAction(self)
        self.mActionRemoveObjects.setIcon(QIcon(":/images/16x16/edit-delete.png"))
        Utils.setThemeIcon(self.mActionRemoveLayer, "edit-delete")
        Utils.setThemeIcon(self.mActionMoveLayerUp, "go-up")
        Utils.setThemeIcon(self.mActionMoveLayerDown, "go-down")
        Utils.setThemeIcon(self.mActionLayerProperties, "document-properties")
        Utils.setThemeIcon(self.mActionRemoveObjects, "edit-delete")
        self.mActionSelectAll.triggered.connect(self.selectAll)
        self.mActionSelectNone.triggered.connect(self.selectNone)
        self.mActionCropToSelection.triggered.connect(self.cropToSelection)
        self.mActionAddTileLayer.triggered.connect(self.addTileLayer)
        self.mActionAddObjectGroup.triggered.connect(self.addObjectGroup)
        self.mActionAddImageLayer.triggered.connect(self.addImageLayer)
        self.mActionDuplicateLayer.triggered.connect(self.duplicateLayer)
        self.mActionMergeLayerDown.triggered.connect(self.mergeLayerDown)
        self.mActionSelectPreviousLayer.triggered.connect(self.selectPreviousLayer)
        self.mActionSelectNextLayer.triggered.connect(self.selectNextLayer)
        self.mActionRemoveLayer.triggered.connect(self.removeLayer)
        self.mActionMoveLayerUp.triggered.connect(self.moveLayerUp)
        self.mActionMoveLayerDown.triggered.connect(self.moveLayerDown)
        self.mActionToggleOtherLayers.triggered.connect(self.toggleOtherLayers)
        self.mActionLayerProperties.triggered.connect(self.layerProperties)
        self.mActionDuplicateObjects.triggered.connect(self.duplicateObjects)
        self.mActionRemoveObjects.triggered.connect(self.removeObjects)
        self.updateActions()
        self.retranslateUi()

    def __del__(self):
        MapDocumentActionHandler.mInstance = None

    def instance():
        return MapDocumentActionHandler.mInstance

    def retranslateUi(self):
        self.mActionSelectAll.setText(self.tr("Select All"))
        self.mActionSelectNone.setText(self.tr("Select None"))
        self.mActionCropToSelection.setText(self.tr("Crop to Selection"))
        self.mActionAddTileLayer.setText(self.tr("Add Tile Layer"))
        self.mActionAddObjectGroup.setText(self.tr("Add Object Layer"))
        self.mActionAddImageLayer.setText(self.tr("Add Image Layer"))
        self.mActionDuplicateLayer.setText(self.tr("Duplicate Layer"))
        self.mActionMergeLayerDown.setText(self.tr("Merge Layer Down"))
        self.mActionRemoveLayer.setText(self.tr("Remove Layer"))
        self.mActionSelectPreviousLayer.setText(self.tr("Select Previous Layer"))
        self.mActionSelectNextLayer.setText(self.tr("Select Next Layer"))
        self.mActionMoveLayerUp.setText(self.tr("Raise Layer"))
        self.mActionMoveLayerDown.setText(self.tr("Lower Layer"))
        self.mActionToggleOtherLayers.setText(self.tr("Show/Hide all Other Layers"))
        self.mActionLayerProperties.setText(self.tr("Layer Properties..."))

    def setMapDocument(self, mapDocument):
        if (self.mMapDocument == mapDocument):
            return
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
        self.mMapDocument = mapDocument
        self.updateActions()
        if (self.mMapDocument):
            mapDocument.layerRemoved.connect(self.updateActions)
            mapDocument.currentLayerIndexChanged.connect(self.updateActions)
            mapDocument.selectedAreaChanged.connect(self.updateActions)
            mapDocument.selectedObjectsChanged.connect(self.updateActions)

        self.mapDocumentChanged.emit([self.mMapDocument])

    def mapDocument(self):
        return self.mMapDocument

    def actionSelectAll(self):
        return self.mActionSelectAll

    def actionSelectNone(self):
        return self.mActionSelectNone

    def actionCropToSelection(self):
        return self.mActionCropToSelection

    def actionAddTileLayer(self):
        return self.mActionAddTileLayer

    def actionAddObjectGroup(self):
        return self.mActionAddObjectGroup

    def actionAddImageLayer(self):
        return self.mActionAddImageLayer

    def actionDuplicateLayer(self):
        return self.mActionDuplicateLayer

    def actionMergeLayerDown(self):
        return self.mActionMergeLayerDown

    def actionRemoveLayer(self):
        return self.mActionRemoveLayer

    def actionSelectPreviousLayer(self):
        return self.mActionSelectPreviousLayer

    def actionSelectNextLayer(self):
        return self.mActionSelectNextLayer

    def actionMoveLayerUp(self):
        return self.mActionMoveLayerUp

    def actionMoveLayerDown(self):
        return self.mActionMoveLayerDown

    def actionToggleOtherLayers(self):
        return self.mActionToggleOtherLayers

    def actionLayerProperties(self):
        return self.mActionLayerProperties

    def actionDuplicateObjects(self):
        return self.mActionDuplicateObjects

    def actionRemoveObjects(self):
        return self.mActionRemoveObjects

    def selectAll(self):
        if (not self.mMapDocument):
            return
        layer = self.mMapDocument.currentLayer()
        if (not layer):
            return
        tileLayer = layer.asTileLayer()
        if tileLayer:
            all = QRect(tileLayer.x(), tileLayer.y(),
                      tileLayer.width(), tileLayer.height())
            if (self.mMapDocument.selectedArea() == all):
                return
            command = ChangeSelectedArea(self.mMapDocument, all)
            self.mMapDocument.undoStack().push(command)
        else:
            objectGroup = layer.asObjectGroup()
            if objectGroup:
                self.mMapDocument.setSelectedObjects(objectGroup.objects())

    def selectNone(self):
        if (not self.mMapDocument):
            return
        if (self.mMapDocument.selectedArea().isEmpty()):
            return
        command = ChangeSelectedArea(self.mMapDocument, QRegion())
        self.mMapDocument.undoStack().push(command)

    def copyPosition(self):
        view = DocumentManager.instance().currentMapView()
        if (not view):
            return
        globalPos = QCursor.pos()
        viewportPos = view.viewport().mapFromGlobal(globalPos)
        scenePos = view.mapToScene(viewportPos)
        renderer = self.mapDocument().renderer()
        tilePos = renderer.screenToTileCoords_(scenePos)
        x = math.floor(tilePos.x())
        y = math.floor(tilePos.y())
        QApplication.clipboard().setText(str(x) + ", " + str(y))

    def cropToSelection(self):
        if (not self.mMapDocument):
            return
        bounds = self.mMapDocument.selectedArea().boundingRect()
        if (bounds.isNull()):
            return
        self.mMapDocument.resizeMap(bounds.size(), -bounds.topLeft())

    def addTileLayer(self):
        if (self.mMapDocument):
            self.mMapDocument.addLayer(Layer.TileLayerType)

    def addObjectGroup(self):
        if (self.mMapDocument):
            self.mMapDocument.addLayer(Layer.ObjectGroupType)

    def addImageLayer(self):
         if (self.mMapDocument):
             self.mMapDocument.addLayer(Layer.ImageLayerType)

    def duplicateLayer(self):
        if (self.mMapDocument):
            self.mMapDocument.duplicateLayer()

    def mergeLayerDown(self):
        if (self.mMapDocument):
            self.mMapDocument.mergeLayerDown()

    def selectPreviousLayer(self):
        if (self.mMapDocument):
            currentLayer = self.mMapDocument.currentLayerIndex()
            if (currentLayer < self.mMapDocument.map().layerCount() - 1):
                self.mMapDocument.setCurrentLayerIndex(currentLayer + 1)

    def selectNextLayer(self):
        if (self.mMapDocument):
            currentLayer = self.mMapDocument.currentLayerIndex()
            if (currentLayer > 0):
                self.mMapDocument.setCurrentLayerIndex(currentLayer - 1)

    def moveLayerUp(self):
        if (self.mMapDocument):
            self.mMapDocument.moveLayerUp(self.mMapDocument.currentLayerIndex())

    def moveLayerDown(self):
        if (self.mMapDocument):
            self.mMapDocument.moveLayerDown(self.mMapDocument.currentLayerIndex())

    def removeLayer(self):
        if (self.mMapDocument):
            self.mMapDocument.removeLayer(self.mMapDocument.currentLayerIndex())

    def toggleOtherLayers(self):
        if (self.mMapDocument):
            self.mMapDocument.toggleOtherLayers(self.mMapDocument.currentLayerIndex())

    def layerProperties(self):
        if (self.mMapDocument):
            self.mMapDocument.setCurrentObject(self.mMapDocument.currentLayer())
            self.mMapDocument.emitEditCurrentObject()

    def duplicateObjects(self):
        if (self.mMapDocument):
            self.mMapDocument.duplicateObjects(self.mMapDocument.selectedObjects())

    def removeObjects(self):
        if (self.mMapDocument):
            self.mMapDocument.removeObjects(self.mMapDocument.selectedObjects())

    def moveObjectsToGroup(self, objectGroup):
        if (self.mMapDocument):
            self.mMapDocument.moveObjectsToGroup(self.mMapDocument.selectedObjects(), objectGroup)

    def updateActions(self):
        map = None
        currentLayerIndex = -1
        selection = QRegion()
        selectedObjectsCount = 0
        canMergeDown = False
        if (self.mMapDocument):
            map = self.mMapDocument.map()
            currentLayerIndex = self.mMapDocument.currentLayerIndex()
            selection = self.mMapDocument.selectedArea()
            selectedObjectsCount = self.mMapDocument.selectedObjects().count()
            if (currentLayerIndex > 0):
                upper = map.layerAt(currentLayerIndex)
                lower = map.layerAt(currentLayerIndex - 1)
                canMergeDown = lower.canMergeWith(upper)

        self.mActionSelectAll.setEnabled(bool(map))
        self.mActionSelectNone.setEnabled(not selection.isEmpty())
        self.mActionCropToSelection.setEnabled(not selection.isEmpty())
        self.mActionAddTileLayer.setEnabled(bool(map))
        self.mActionAddObjectGroup.setEnabled(bool(map))
        self.mActionAddImageLayer.setEnabled(bool(map))
        if map:
            _x = map.layerCount()
        else:
            _x = 0
        layerCount = _x
        hasPreviousLayer = currentLayerIndex >= 0 and currentLayerIndex < layerCount - 1
        hasNextLayer = currentLayerIndex > 0
        self.mActionDuplicateLayer.setEnabled(currentLayerIndex >= 0)
        self.mActionMergeLayerDown.setEnabled(canMergeDown)
        self.mActionSelectPreviousLayer.setEnabled(hasPreviousLayer)
        self.mActionSelectNextLayer.setEnabled(hasNextLayer)
        self.mActionMoveLayerUp.setEnabled(hasPreviousLayer)
        self.mActionMoveLayerDown.setEnabled(hasNextLayer)
        self.mActionToggleOtherLayers.setEnabled(layerCount > 1)
        self.mActionRemoveLayer.setEnabled(currentLayerIndex >= 0)
        self.mActionLayerProperties.setEnabled(currentLayerIndex >= 0)
        self.mActionDuplicateObjects.setEnabled(selectedObjectsCount > 0)
        self.mActionRemoveObjects.setEnabled(selectedObjectsCount > 0)
        duplicateText = QString()
        removeText = QString()
        if (selectedObjectsCount > 0):
            duplicateText = self.tr("Duplicate %n Object(s)", "", selectedObjectsCount)
            removeText = self.tr("Remove %n Object(s)", "", selectedObjectsCount)
        else:
            duplicateText = self.tr("Duplicate Objects")
            removeText = self.tr("Remove Objects")

        self.mActionDuplicateObjects.setText(duplicateText)
        self.mActionRemoveObjects.setText(removeText)
