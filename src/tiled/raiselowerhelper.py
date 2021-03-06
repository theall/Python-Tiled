##
# raiselowerhelper.py
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

from objectgroup import ObjectGroup
from changemapobjectsorder import ChangeMapObjectsOrder
from mapobjectitem import MapObjectItem
from rangeset import RangeSet
from pyqtcore import QList
from PyQt5.QtGui import (
    QPainterPath
)
from PyQt5.QtCore import (
    Qt,
    QCoreApplication
)

##
# Implements operations to raise or lower the set of selected objects.
#
# The operations don't do anything when there are multiple object groups
# active in the selection, or when the object group does not use index drawing
# order.
##
class RaiseLowerHelper():

    def __init__(self, mapScene):
        self.mSelectionRanges = RangeSet()

        self.mMapDocument = mapScene.mapDocument()
        self.mMapScene = mapScene
        # Context
        self.mObjectGroup = None
        self.mRelatedObjects = QList()

    def raise_(self):
        if (not self.initContext()):
            return
        # Iterate backwards over the ranges in order to keep the indexes valid
        size = len(self.mSelectionRanges)
        if size <= 0:# no range
            return
        firstRange = self.mSelectionRanges.begin()
        it = self.mSelectionRanges.end()
        if (it == firstRange): # no range
            return
        # For each range of objects, only the first will move
        commands = QList()
        
        lastIndex = len(self.mRelatedObjects) - 1
        for i in range(size-1, -1, -1):
            it = self.mSelectionRanges.item(i)
            value = it[1]
            # The last range may be already at the top of the related items
            if value == lastIndex:
                continue
            movingItem = self.mRelatedObjects.at(value)
            targetItem = self.mRelatedObjects.at(value + 1)
            _from = int(movingItem.zValue())
            to = int(targetItem.zValue() + 1)
            commands.append(ChangeMapObjectsOrder(self.mMapDocument, self.mObjectGroup,
                                                      _from, to, 1))
        self.push(commands, QCoreApplication.translate("Undo Commands", "Raise Object"))

    def lower(self):
        if (not self.initContext()):
            return

        # For each range of objects, only the first will move
        commands = QList()
        for it in self.mSelectionRanges:
            value = it[0]
            # The first range may be already at the bottom of the related items
            if (value == 0):
                continue
            movingItem = self.mRelatedObjects.at(value)
            targetItem = self.mRelatedObjects.at(value - 1)
            _from = int(movingItem.zValue())
            to = int(targetItem.zValue())
            commands.append(ChangeMapObjectsOrder(self.mMapDocument, self.mObjectGroup, _from, to, 1))

        self.push(commands, QCoreApplication.translate("Undo Commands", "Lower Object"))

    def raiseToTop(self):
        selectedItems = self.mMapScene.selectedObjectItems()
        objectGroup = RaiseLowerHelper.sameObjectGroup(selectedItems)
        if (not objectGroup):
            return
        if (objectGroup.drawOrder() != ObjectGroup.DrawOrder.IndexOrder):
            return
        ranges = RangeSet()
        for item in selectedItems:
            ranges.insert(int(item.zValue()))
 
        # Iterate backwards over the ranges in order to keep the indexes valid
        size = len(ranges)
        if size <= 0:# no range
            return

        commands = QList()
        to = objectGroup.objectCount()
        for i in range(size-1, -1, -1):
            it = ranges.item(i)
            first = it[0]
            last = it[1]
            count = last - first + 1
            if (last + 1 == to):
                to -= count
                continue

            _from = first
            commands.append(ChangeMapObjectsOrder(self.mMapDocument, objectGroup,
                                                      _from, to, count))
            to -= count

        self.push(commands,
             QCoreApplication.translate("Undo Commands", "Raise Object To Top"))

    def lowerToBottom(self):
        selectedItems = self.mMapScene.selectedObjectItems()
        objectGroup = RaiseLowerHelper.sameObjectGroup(selectedItems)
        if (not objectGroup):
            return
        if (objectGroup.drawOrder() != ObjectGroup.DrawOrder.IndexOrder):
            return
        ranges = RangeSet()
        for item in selectedItems:
            ranges.insert(int(item.zValue()))

        commands = QList()
        to = 0
        for it in ranges:
            first = it[0]
            _from = first
            count = it[1] - first + 1
            if (_from == to):
                to += count
                continue

            commands.append(ChangeMapObjectsOrder(self.mMapDocument, objectGroup,
                                                      _from, to, count))
            to += count

        self.push(commands,
             QCoreApplication.translate("Undo Commands", "Lower Object To Bottom"))

    def sameObjectGroup(items):
        if (items.isEmpty()):
            return None
        # All selected objects need to be in the same group
        group = items.begin().mapObject().objectGroup()
        for item in items:
            if (item.mapObject().objectGroup() != group):
                return None
        return group

    ##
    # Initializes the context in which objects are being raised or lowered. Only
    # used for single-step raising and lowering, since the context is not relevant
    # when raising to the top or lowering to the bottom.
    #
    # Returns whether the operation can be performed.
    ##
    def initContext(self):
        self.mObjectGroup = None
        self.mRelatedObjects.clear()
        self.mSelectionRanges.clear()
        selectedItems = self.mMapScene.selectedObjectItems()
        if (selectedItems.isEmpty()):
            return False
        # All selected objects need to be in the same group
        self.mObjectGroup = selectedItems.begin().mapObject().objectGroup()
        if (self.mObjectGroup.drawOrder() != ObjectGroup.DrawOrder.IndexOrder):
            return False
        shape = QPainterPath()
        for item in selectedItems:
            if (item.mapObject().objectGroup() != self.mObjectGroup):
                return False
            shape |= item.mapToScene(item.shape())

        # The list of related items are all items from the same object group
        # that share space with the selected items.
        items = self.mMapScene.items(shape, Qt.IntersectsItemShape, Qt.AscendingOrder)
        for item in items:
            if type(item) == MapObjectItem:
                if (item.mapObject().objectGroup() == self.mObjectGroup):
                    self.mRelatedObjects.append(item)

        for item in selectedItems:
            index = self.mRelatedObjects.indexOf(item)
            self.mSelectionRanges.insert(index)

        return True

    def push(self, commands, text):
        if (commands.isEmpty()):
            return
        undoStack = self.mMapDocument.undoStack()
        undoStack.beginMacro(text)
        for command in commands:
            undoStack.push(command)
        undoStack.endMacro()
