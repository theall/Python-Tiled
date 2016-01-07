##
# clipboardmanager.py
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

from tilelayer import TileLayer
from tmxmapformat import TmxMapFormat
from snaphelper import SnapHelper
from objectgroup import ObjectGroup
from map import Map
from addremovemapobject import AddMapObject
from pyqtcore import QList
from PyQt5.QtCore import (
    QMimeData,
    QObject,
    pyqtSignal,
    QPoint
)

from PyQt5.QtGui import (
    QCursor
)

from PyQt5.QtWidgets import (
    QApplication
)

TMX_MIMETYPE = "text/tmx"

class PasteMode():
    Standard = 1
    NoTileObjects = 2

##
# The clipboard manager deals with interaction with the clipboard.
##
class ClipboardManager(QObject):
    ##
    # Emitted when whether the clip has a map changed.
    ##
    hasMapChanged = pyqtSignal()
    mInstance = None

    def __init__(self):
        super().__init__()

        self.mHasMap = False
        self.mClipboard = QApplication.clipboard()
        self.mClipboard.dataChanged.connect(self.updateHasMap)
        self.updateHasMap()

    ##
    # Returns the clipboard manager instance. Creates the instance when it
    # doesn't exist yet.
    ##
    def instance():
        if (not ClipboardManager.mInstance):
            ClipboardManager.mInstance = ClipboardManager()
        return ClipboardManager.mInstance

    ##
    # Deletes the clipboard manager instance if it exists.
    ##
    def deleteInstance():
        ClipboardManager.mInstance = None

    ##
    # Returns whether the clipboard has a map.
    ##
    def hasMap(self):
        return self.mHasMap

    ##
    # Retrieves the map from the clipboard. Returns 0 when there was no map or
    # loading failed.
    ##
    def map(self):
        mimeData = self.mClipboard.mimeData()
        data = mimeData.data(TMX_MIMETYPE)
        if (data.isEmpty()):
            return None
        format = TmxMapFormat()
        return format.fromByteArray(data)
    ##
    # Sets the given map on the clipboard.
    ##
    def setMap(self, map):
        format = TmxMapFormat()
        mimeData = QMimeData()
        mimeData.setData(TMX_MIMETYPE, format.toByteArray(map))
        self.mClipboard.setMimeData(mimeData)

    ##
    # Convenience method to copy the current selection to the clipboard.
    # Deals with either tile selection or object selection.
    ##
    def copySelection(self, mapDocument):
        currentLayer = mapDocument.currentLayer()
        if (not currentLayer):
            return
        map = mapDocument.map()
        selectedArea = mapDocument.selectedArea()
        selectedObjects = mapDocument.selectedObjects()
        tileLayer = currentLayer
        copyLayer = None
        if (not selectedArea.isEmpty() and type(tileLayer)==TileLayer):
            # Copy the selected part of the layer
            copyLayer = tileLayer.copy(selectedArea.translated(-tileLayer.x(), -tileLayer.y()))
        elif (not selectedObjects.isEmpty()):
            # Create a new object group with clones of the selected objects
            objectGroup = ObjectGroup()
            for mapObject in selectedObjects:
                objectGroup.addObject(mapObject.clone())
            copyLayer = objectGroup
        else:
            return

        # Create a temporary map to write to the clipboard
        copyMap = Map(map.orientation(),
                    copyLayer.width(), copyLayer.height(),
                    map.tileWidth(), map.tileHeight())
        copyMap.setRenderOrder(map.renderOrder())
        # Resolve the set of tilesets used by this layer
        for tileset in copyLayer.usedTilesets():
            copyMap.addTileset(tileset)
        copyMap.addLayer(copyLayer)
        self.setMap(copyMap)

    ##
    # Convenience method that deals with some of the logic related to pasting
    # a group of objects.
    ##
    def pasteObjectGroup(self, objectGroup, mapDocument, view, mode = PasteMode.Standard):
        currentLayer = mapDocument.currentLayer()
        if (not currentLayer):
            return
        currentObjectGroup = currentLayer.asObjectGroup()
        if (not currentObjectGroup):
            return
        # Determine where to insert the objects
        renderer = mapDocument.renderer()
        center = objectGroup.objectsBoundingRect().center()
        # Take the mouse position if the mouse is on the view, otherwise
        # take the center of the view.
        viewPos = QPoint()
        if (view.underMouse()):
            viewPos = view.mapFromGlobal(QCursor.pos())
        else:
            viewPos = QPoint(view.width() / 2, view.height() / 2)
        scenePos = view.mapToScene(viewPos)
        insertPos = renderer.screenToPixelCoords_(scenePos) - center
        SnapHelper(renderer).snap(insertPos)
        undoStack = mapDocument.undoStack()
        pastedObjects = QList()
        pastedObjects.reserve(objectGroup.objectCount())
        undoStack.beginMacro(self.tr("Paste Objects"))
        for mapObject in objectGroup.objects():
            if (mode == PasteMode.NoTileObjects and not mapObject.cell().isEmpty()):
                continue
            objectClone = mapObject.clone()
            objectClone.setPosition(objectClone.position() + insertPos)
            pastedObjects.append(objectClone)
            undoStack.push(AddMapObject(mapDocument,
                                             currentObjectGroup,
                                             objectClone))

        undoStack.endMacro()
        mapDocument.setSelectedObjects(pastedObjects)

    def updateHasMap(self):
        data = self.mClipboard.mimeData()
        mapInClipboard = data and data.hasFormat(TMX_MIMETYPE)
        if (mapInClipboard != self.mHasMap):
            self.mHasMap = mapInClipboard
            self.hasMapChanged.emit()
