# -*- coding: utf-8 -*-
##
# abstractobjecttool.py
# Copyright 2011, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

import math

from mapobjectitem import MapObjectItem
from objectgroup import ObjectGroup
from libtiled.tiled import FlipDirection
from abstracttool import AbstractTool
from raiselowerhelper import RaiseLowerHelper
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMenu
from PyQt5.QtGui import QIcon, QKeySequence
from utils import Utils

###
# A convenient base class for tools that work on object layers. Implements
# the standard context menu.
##
class AbstractObjectTool(AbstractTool):
    ###
    # Constructs an abstract object tool with the given \a name and \a icon.
    ##
    def __init__(self, name, icon, shortcut, parent = None):
        super().__init__(name, icon, shortcut, parent)
        
        self.mMapScene = None

    def activate(self, scene):
        self.mMapScene = scene

    def deactivate(self, scene):
        self.mMapScene = None

    def keyPressed(self, event):
        ek = event.key()
        if ek == Qt.Key_PageUp:
            self.throw()
            self.throw()
            return
        elif ek == Qt.Key_PageDown:
            self.lower()
            return
        elif ek == Qt.Key_Home:
            self.raiseToTop()
            return
        elif ek == Qt.Key_End:
            self.lowerToBottom()
            return

    def mouseLeft(self):
        self.setStatusInfo('')

    def mouseMoved(self, pos, modifiers):
        # Take into account the offset of the current layer
        offsetPos = pos
        layer = self.currentObjectGroup()
        if layer:
            offsetPos -= layer.offset()
            
        tilePosF = self.mapDocument().renderer().screenToTileCoords_(offsetPos)
        x = math.floor(tilePosF.x())
        y = math.floor(tilePosF.y())
        self.setStatusInfo(("%d, %d"%(x, y)))

    def mousePressed(self, event):
        if (event.button() == Qt.RightButton):
            self.showContextMenu(self.topMostObjectItemAt(event.scenePos()), event.screenPos())

    ###
    # Overridden to only enable this tool when the currently selected layer is
    # an object group.
    ##
    def updateEnabledState(self):
        self.setEnabled(self.currentObjectGroup() != None)

    def mapScene(self):
        return self.mMapScene

    def currentObjectGroup(self):
        if (not self.mapDocument()):
            return None
        currentLayer = self.mapDocument().currentLayer()
        if type(currentLayer)==ObjectGroup:
            return currentLayer
        return None

    def topMostObjectItemAt(self, pos):
        for item in self.mMapScene.items(pos):
            if type(item) == MapObjectItem:
                return item
        return None

    def duplicateObjects(self):
        self.mapDocument().duplicateObjects(self.mapDocument().selectedObjects())

    def removeObjects(self):
        self.mapDocument().removeObjects(self.mapDocument().selectedObjects())

    def flipHorizontally(self):
        self.mapDocument().flipSelectedObjects(FlipDirection.FlipHorizontally)

    def flipVertically(self):
        self.mapDocument().flipSelectedObjects(FlipDirection.FlipVertically)

    def raise_(self):
        RaiseLowerHelper(self.mMapScene).raise_()

    def lower(self):
        RaiseLowerHelper(self.mMapScene).lower()

    def raiseToTop(self):
        RaiseLowerHelper(self.mMapScene).raiseToTop()

    def lowerToBottom(self):
        RaiseLowerHelper(self.mMapScene).lowerToBottom()

    def showContextMenu(self, clickedObjectItem, screenPos):
        selection = self.mMapScene.selectedObjectItems()
        if (clickedObjectItem and not selection.contains(clickedObjectItem)):
            selection.clear()
            selection.insert(clickedObjectItem)
            self.mMapScene.setSelectedObjectItems(selection)
        if selection.isEmpty():
            return

        selectedObjects = self.mapDocument().selectedObjects()
        objectGroups = self.mapDocument().map().objectGroups()

        menu = QMenu()
        duplicateAction = menu.addAction(self.tr("Duplicate %n Object(s)", "", selection.size()), self.duplicateObjects)
        removeAction = menu.addAction(self.tr("Remove %n Object(s)", "", selection.size()), self.removeObjects)

        duplicateAction.setIcon(QIcon("/images/16x16/stock-duplicate-16.png"))
        removeAction.setIcon(QIcon("/images/16x16/edit-delete.png"))

        menu.addSeparator()
        menu.addAction(self.tr("Flip Horizontally"), self.flipHorizontally, QKeySequence(self.tr("X")))
        menu.addAction(self.tr("Flip Vertically"), self.flipVertically, QKeySequence(self.tr("Y")))

        objectGroup = RaiseLowerHelper.sameObjectGroup(selection)
        if (objectGroup and objectGroup.drawOrder() == ObjectGroup.DrawOrder.IndexOrder):
            menu.addSeparator()
            menu.addAction(self.tr("Raise Object"), self.raise_, QKeySequence(self.tr("PgUp")))
            menu.addAction(self.tr("Lower Object"), self.lower, QKeySequence(self.tr("PgDown")))
            menu.addAction(self.tr("Raise Object to Top"), self.raiseToTop, QKeySequence(self.tr("Home")))
            menu.addAction(self.tr("Lower Object to Bottom"), self.lowerToBottom, QKeySequence(self.tr("End")))

        if (objectGroups.size() > 1):
            menu.addSeparator()
            moveToLayerMenu = menu.addMenu(self.tr("Move %n Object(s) to Layer", "", selectedObjects.size()))
            for objectGroup in objectGroups:
                action = moveToLayerMenu.addAction(objectGroup.name())
                action.setData(objectGroup)

        menu.addSeparator()
        propIcon = QIcon("images/16x16/document-properties.png")
        propertiesAction = menu.addAction(propIcon, self.tr("Object &Properties..."))
        # TODO Implement editing of properties for multiple objects
        propertiesAction.setEnabled(selectedObjects.size() == 1)

        Utils.setThemeIcon(removeAction, "edit-delete")
        Utils.setThemeIcon(propertiesAction, "document-properties")

        action = menu.exec(screenPos)
        if not action:
            return

        if action == propertiesAction:
            mapObject = selectedObjects.first()
            self.mapDocument().setCurrentObject(mapObject)
            self.mapDocument().emitEditCurrentObject()
            return
        
        objectGroup = action.data()
        if type(objectGroup) == ObjectGroup:
            self.mapDocument().moveObjectsToGroup(self.mapDocument().selectedObjects(), objectGroup)
