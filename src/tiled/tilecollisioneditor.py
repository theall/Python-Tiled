##
# tilecollisioneditor.py
# Copyright 2013, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
from toolmanager import ToolManager
from tilelayer import TileLayer, Cell
from objectselectiontool import ObjectSelectionTool
from objectgroup import ObjectGroup
from mapview import MapView, MapViewMode
from mapscene import MapScene
from map import Map
from object import Object
from createpolylineobjecttool import CreatePolylineObjectTool
from createpolygonobjecttool import CreatePolygonObjectTool
from createellipseobjecttool import CreateEllipseObjectTool
from createrectangleobjecttool import CreateRectangleObjectTool
from clipboardmanager import ClipboardManager
from changetileobjectgroup import ChangeTileObjectGroup
from editpolygontool import EditPolygonTool
from addremovemapobject import RemoveMapObject
from mapdocument import MapDocument
from pyqtcore import QString
from PyQt5.QtGui import (
    QKeySequence
)
from PyQt5.QtCore import (
    Qt,
    QEvent,
    pyqtSignal
)
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QToolBar,
    QShortcut,
    QComboBox,
    QMainWindow
)

class Operation():
    Cut = 1
    Delete = 2

class TileCollisionEditor(QMainWindow):
    closed = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)
        self.mTile = None
        self.mMapDocument = None
        self.mMapScene = MapScene(self)
        self.mMapView = MapView(self, MapViewMode.NoStaticContents)
        self.mToolManager = ToolManager(self)
        self.mApplyingChanges = False
        self.mSynchronizing = False

        self.setObjectName("TileCollisionEditor")
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setSpacing(0)
        layout.setContentsMargins(5, 5, 5, 5)
        self.mMapView.setScene(self.mMapScene)
        self.mMapView.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.mMapView.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        rectangleObjectsTool = CreateRectangleObjectTool(self)
        ellipseObjectsTool = CreateEllipseObjectTool(self)
        polygonObjectsTool = CreatePolygonObjectTool(self)
        polylineObjectsTool = CreatePolylineObjectTool(self)
        toolBar = QToolBar(self)
        toolBar.setMovable(False)
        toolBar.setFloatable(False)
        toolBar.setContextMenuPolicy(Qt.ActionsContextMenu)
        self.mToolManager = ToolManager(self)
        toolBar.addAction(self.mToolManager.registerTool(ObjectSelectionTool(self)))
        toolBar.addAction(self.mToolManager.registerTool(EditPolygonTool(self)))
        toolBar.addAction(self.mToolManager.registerTool(rectangleObjectsTool))
        toolBar.addAction(self.mToolManager.registerTool(ellipseObjectsTool))
        toolBar.addAction(self.mToolManager.registerTool(polygonObjectsTool))
        toolBar.addAction(self.mToolManager.registerTool(polylineObjectsTool))
        self.setCentralWidget(self.mMapView)
        self.addToolBar(toolBar)
        self.mMapScene.setSelectedTool(self.mToolManager.selectedTool())
        self.mToolManager.selectedToolChanged.connect(self.setSelectedTool)
        zoomComboBox = QComboBox()
        self.statusBar().addPermanentWidget(zoomComboBox)
        zoomable = self.mMapView.zoomable()
        zoomable.connectToComboBox(zoomComboBox)
        undoShortcut = QShortcut(QKeySequence.Undo, self)
        redoShortcut = QShortcut(QKeySequence.Redo, self)
        cutShortcut = QShortcut(QKeySequence.Cut, self)
        copyShortcut = QShortcut(QKeySequence.Copy, self)
        pasteShortcut = QShortcut(QKeySequence.Paste, self)
        deleteShortcut = QShortcut(QKeySequence.Delete, self)
        deleteShortcut2 = QShortcut(QKeySequence.Back, self)
        undoShortcut.activated.connect(self.undo)
        redoShortcut.activated.connect(self.redo)
        cutShortcut.activated.connect(self.cut)
        copyShortcut.activated.connect(self.copy)
        pasteShortcut.activated.connect(self.paste)
        deleteShortcut.activated.connect(self.delete_)
        deleteShortcut2.activated.connect(self.delete_)
        self.retranslateUi()
        self.resize(300, 300)
        Utils.restoreGeometry(self)

    def __del__(self):
        self.setTile(None)

    def setMapDocument(self, mapDocument):
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
        self.mMapDocument = mapDocument
        if (self.mMapDocument):
            self.mMapDocument.tileObjectGroupChanged.connect(self.tileObjectGroupChanged)
            self.mMapDocument.tilesetFileNameChanged.connect(self.tilesetFileNameChanged)
            self.mMapDocument.currentObjectChanged.connect(self.currentObjectChanged)

    def writeSettings(self):
        Utils.saveGeometry(self)

    def setTile(self, tile):
        if type(tile)==list:
            tile = tile[0]
        if (self.mTile == tile):
            return
        self.mTile = tile
        self.mMapScene.disableSelectedTool()
        previousDocument = self.mMapScene.mapDocument()
        if (tile):
            self.mMapView.setEnabled(not self.mTile.tileset().isExternal())
            map = Map(Map.Orientation.Orthogonal, 1, 1, tile.width(), tile.height())
            map.addTileset(tile.sharedTileset())
            tileLayer = TileLayer(QString(), 0, 0, 1, 1)
            tileLayer.setCell(0, 0, Cell(tile))
            map.addLayer(tileLayer)
            objectGroup = None
            if (tile.objectGroup()):
                objectGroup = tile.objectGroup().clone()
            else:
                objectGroup = ObjectGroup()
            objectGroup.setDrawOrder(ObjectGroup.DrawOrder.IndexOrder)
            map.addLayer(objectGroup)
            mapDocument = MapDocument(map)
            self.mMapScene.setMapDocument(mapDocument)
            self.mToolManager.setMapDocument(mapDocument)
            mapDocument.setCurrentLayerIndex(1)
            self.mMapScene.enableSelectedTool()
            mapDocument.undoStack().indexChanged.connect(self.applyChanges)
        else:
            self.mMapView.setEnabled(False)
            self.mMapScene.setMapDocument(None)
            self.mToolManager.setMapDocument(None)

        if (previousDocument):
            previousDocument.undoStack().disconnect()
            del previousDocument

    def closeEvent(self, event):
        super().closeEvent(event)
        if (event.isAccepted()):
            self.closed.emit()

    def changeEvent(self, e):
        super().changeEvent(e)
        x = e.type()
        if x==QEvent.LanguageChange:
            self.retranslateUi()
        else:
            pass

    def setSelectedTool(self, tool):
        if type(tool)==list:
            tool = tool[0]
        self.mMapScene.disableSelectedTool()
        self.mMapScene.setSelectedTool(tool)
        self.mMapScene.enableSelectedTool()

    def applyChanges(self):
        if (self.mSynchronizing):
            return
        dummyDocument = self.mMapScene.mapDocument()
        objectGroup = dummyDocument.map().layerAt(1)
        clonedGroup = objectGroup.clone()
        undoStack = self.mMapDocument.undoStack()
        self.mApplyingChanges = True
        undoStack.push(ChangeTileObjectGroup(self.mMapDocument, self.mTile, clonedGroup))
        self.mApplyingChanges = False

    def tileObjectGroupChanged(self, tile):
        if (self.mTile != tile):
            return
        if (self.mApplyingChanges):
            return
        self.mSynchronizing = True
        dummyDocument = self.mMapScene.mapDocument()
        layerModel = dummyDocument.layerModel()
        dummyDocument.undoStack().clear()
        layerModel.takeLayerAt(1).close()
        objectGroup = None
        if (tile.objectGroup()):
            objectGroup = tile.objectGroup().clone()
        else:
            objectGroup = ObjectGroup()
        objectGroup.setDrawOrder(ObjectGroup.DrawOrder.IndexOrder)
        layerModel.insertLayer(1, objectGroup)
        dummyDocument.setCurrentLayerIndex(1)
        self.mSynchronizing = False

    def currentObjectChanged(self, object):
        if type(object)==list and len(object)>0:
            object = object[0]
        # If a tile object is selected, edit the collision shapes for that tile
        if object and object.typeId() == Object.MapObjectType:
            cell = object.cell()
            if cell.tile:
                self.setTile(cell.tile)
                
    def tilesetFileNameChanged(self, tileset):
        if (self.mTile and self.mTile.tileset() == tileset):
            self.mMapView.setEnabled(not tileset.isExternal())

    def undo(self):
        if (self.mMapDocument):
            self.mMapDocument.undoStack().undo()

    def redo(self):
        if (self.mMapDocument):
            self.mMapDocument.undoStack().redo()

    def cut(self):
        if (not self.mTile):
            return
        self.copy()
        self.delete_(Operation.Cut)

    def copy(self):
        if (not self.mTile):
            return
        dummyDocument = self.mMapScene.mapDocument()
        ClipboardManager.instance().copySelection(dummyDocument)

    def paste(self):
        if (not self.mTile):
            return
        clipboardManager = ClipboardManager.instance()
        map = clipboardManager.map()
        if (not map):
            return

        # We can currently only handle maps with a single layer
        if (map.layerCount() != 1):
            return
        layer = map.layerAt(0)
        objectGroup = layer.asObjectGroup()
        if objectGroup:
            dummyDocument = self.mMapScene.mapDocument()
            clipboardManager.pasteObjectGroup(objectGroup,
                                               dummyDocument, self.mMapView,
                                               ClipboardManager.NoTileObjects)

    def delete_(self, operation = Operation.Delete):
        if (not self.mTile):
            return
        dummyDocument = self.mMapScene.mapDocument()
        selectedObjects = dummyDocument.selectedObjects()
        if (selectedObjects.isEmpty()):
            return
        undoStack = dummyDocument.undoStack()
        if Operation.Delete:
            _x = self.tr("Delete")
        else:
            _x = self.tr("Cut")
        undoStack.beginMacro(operation == _x)
        for mapObject in selectedObjects:
            undoStack.push(RemoveMapObject(dummyDocument, mapObject))
        undoStack.endMacro()

    def retranslateUi(self):
        self.setWindowTitle(self.tr("Tile Collision Editor"))
