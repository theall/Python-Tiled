##
# createobjecttool.py
# Copyright 2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from objectgroupitem import ObjectGroupItem
from objectgroup import ObjectGroup
from snaphelper import SnapHelper
from mapobjectitem import MapObjectItem
from addremovemapobject import AddMapObject
from abstractobjecttool import AbstractObjectTool
from pyqtcore import QString, QList
from PyQt5.QtCore import (
    Qt,
    QPointF, 
    QCoreApplication
)
from PyQt5.QtGui import (
    QIcon,
    QKeySequence
)
class CreationMode():
    CreateTile = 1
    CreateGeometry = 2

class CreateObjectTool(AbstractObjectTool):
    def __init__(self, mode, parent = None):
        super().__init__(QString(),
                            QIcon(":images/24x24/insert-rectangle.png"),
                            QKeySequence(self.tr("O")),
                            parent)
        self.mNewMapObjectGroup = ObjectGroup()
        self.mObjectGroupItem = ObjectGroupItem(self.mNewMapObjectGroup)
        self.mNewMapObjectItem = None
        self.mOverlayPolygonItem = None
        self.mTile = None
        self.mMode = mode
        
        self.mObjectGroupItem.setZValue(10000) # same as the BrushItem

    def __del__(self):
        #del self.mOverlayObjectGroup
        pass

    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('CreateObjectTool', sourceText, disambiguation, n)

    def activate(self, scene):
        super().activate(scene)
        scene.addItem(self.mObjectGroupItem)
    
    def deactivate(self, scene):
        if (self.mNewMapObjectItem):
            self.cancelNewMapObject()
        scene.removeItem(self.mObjectGroupItem)
        super().deactivate(scene)

    def keyPressed(self, event):
        x = event.key()
        if x==Qt.Key_Enter or x==Qt.Key_Return:
            if (self.mNewMapObjectItem):
                self.finishNewMapObject()
                return
        elif x==Qt.Key_Escape:
            if (self.mNewMapObjectItem):
                self.cancelNewMapObject()
                return

        super().keyPressed(event)

    def mouseEntered(self):
        pass
        
    def mouseMoved(self, pos, modifiers):
        super().mouseMoved(pos, modifiers)
        if (self.mNewMapObjectItem):
            offset = self.mNewMapObjectItem.mapObject().objectGroup().offset()
            self.mouseMovedWhileCreatingObject(pos-offset, modifiers)

    def mousePressed(self, event):
        if (self.mNewMapObjectItem):
            self.mousePressedWhileCreatingObject(event)
            return

        if (event.button() != Qt.LeftButton):
            super().mousePressed(event)
            return

        objectGroup = self.currentObjectGroup()
        if (not objectGroup or type(objectGroup)!=ObjectGroup or not objectGroup.isVisible()):
            return
        renderer = self.mapDocument().renderer()
        offsetPos = event.scenePos() - objectGroup.offset()
        pixelCoords = QPointF()
        ##TODO: calculate the tile offset with a polymorphic behaviour object
        # that is instantiated by the correspondend ObjectTool
        ##
        if (self.mMode == CreationMode.CreateTile):
            if (not self.mTile):
                return
            diff = QPointF(-self.mTile.width() / 2, self.mTile.height() / 2)
            pixelCoords = renderer.screenToPixelCoords_(offsetPos + diff)
        else:
            pixelCoords = renderer.screenToPixelCoords_(offsetPos)

        SnapHelper(renderer, event.modifiers()).snap(pixelCoords)
        self.startNewMapObject(pixelCoords, objectGroup)

    def mouseReleased(self, event):
        if (self.mNewMapObjectItem):
            self.mouseReleasedWhileCreatingObject(event)

    ##
    # Sets the tile that will be used when the creation mode is
    # CreateTileObjects.
    ##
    def setTile(self, tile):
        if type(tile)==list:
            tile = tile[0]
        self.mTile = tile

    def mouseMovedWhileCreatingObject(self, pos, modifiers):
        # optional override
        pass

    def mousePressedWhileCreatingObject(self, event):
        # optional override
        pass

    def mouseReleasedWhileCreatingObject(self, event):
        # optional override
        pass

    def startNewMapObject(self, pos, objectGroup):
        newMapObject = self.createNewMapObject()
        if not newMapObject:
            return
        newMapObject.setPosition(pos)
        objectGroup.addObject(newMapObject)
        self.mObjectGroupItem.setObjectGroup(objectGroup)
        
        self.mNewMapObjectItem = MapObjectItem(newMapObject, self.mapDocument(), self.mObjectGroupItem)

    def cancelNewMapObject(self):
        newMapObject = self.clearNewMapObjectItem()
        del newMapObject

    def finishNewMapObject(self):
        newMapObject = self.mNewMapObjectItem.mapObject()
        objectGroup = newMapObject.objectGroup()
        self.clearNewMapObjectItem()
        self.mapDocument().undoStack().push(AddMapObject(self.mapDocument(), objectGroup, newMapObject))
        self.mapDocument().setSelectedObjects(QList([newMapObject]))
        
    def clearNewMapObjectItem(self):
        newMapObject = self.mNewMapObjectItem.mapObject()
        objectGroup = newMapObject.objectGroup()
        objectGroup.removeObject(newMapObject)
        if self.mNewMapObjectItem:
            self.mapScene().removeItem(self.mNewMapObjectItem)
            self.mNewMapObjectItem = None
        if self.mOverlayPolygonItem:
            self.mapScene().removeItem(self.mOverlayPolygonItem)
            self.mOverlayPolygonItem = None
        return newMapObject
