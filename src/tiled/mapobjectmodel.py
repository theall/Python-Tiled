##
# mapobjectmodel.py
# Copyright 2012, Tim Baker
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

from renamelayer import RenameLayer
from objectgroup import ObjectGroup
from mapobject import MapObject
from layermodel import LayerModel
from changemapobject import SetMapObjectVisible, ChangeMapObject
from pyqtcore import QList, QMap
from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QModelIndex,
    QVariant,
    QAbstractItemModel
)

GROUPS_IN_DISPLAY_ORDER = 0

class UserRoles():
    OpacityRole = Qt.UserRole

class ObjectOrGroup():
    def __init__(self, arg):
        tp = type(arg)
        if tp==ObjectGroup:
            self.mGroup = arg
            self.mObject = None
        elif tp==MapObject:
            self.mGroup = None
            self.mObject = arg

##
# Provides a tree view on the objects present on a map. Also has member
# functions to modify objects that emit the appropriate signals to allow
# the UI to update.
##
class MapObjectModel(QAbstractItemModel):
    objectsAdded = pyqtSignal(QList)
    objectsChanged = pyqtSignal(QList)
    objectsRemoved = pyqtSignal(QList)

    def __init__(self, parent):
        super().__init__(parent)

        self.mObjectGroups = QList()
        self.mObjects = QMap()
        self.mGroups = QMap()
        self.mMapDocument = None
        self.mMap = None
        self.mObject = None
        self.mObjectGroupIcon = ":/images/16x16/layer-object.png"

    def index(self, *args):
        l = len(args)
        if l>0:
            tp = type(args[0])
            if tp==int:
                if l==2:
                    args = (args[0], args[1], QModelIndex())
                row, column, parent = args
                if (not parent.isValid()):
                    if (row < self.mObjectGroups.count()):
                        return self.createIndex(row, column, self.mGroups[self.mObjectGroups.at(row)])
                    return QModelIndex()

                og = self.toObjectGroup(parent)
                # happens when deleting the last item in a parent
                if (row >= og.objectCount()):
                    return QModelIndex()
                # Paranoia: sometimes "fake" objects are in use (see createobjecttool)
                if (not self.mObjects.contains(og.objects().at(row))):
                    return QModelIndex()
                return self.createIndex(row, column, self.mObjects[og.objects()[row]])
            elif tp==ObjectGroup:
                og = args[0]
                row = self.mObjectGroups.indexOf(og)
                return self.createIndex(row, 0, self.mGroups[og])
            elif tp==MapObject:
                if l==1:
                    args = (args[0],0)
                o, column = args
                row = o.objectGroup().objects().indexOf(o)
                return self.createIndex(row, column, self.mObjects[o])

    def parent(self, index):
        mapObject = self.toMapObject(index)
        if mapObject:
            return self.index(mapObject.objectGroup())
        return QModelIndex()

    def rowCount(self, parent = QModelIndex()):
        if (not self.mMapDocument):
            return 0
        if (not parent.isValid()):
            return self.mObjectGroups.size()
        og = self.toObjectGroup(parent)
        if og:
            return og.objectCount()
        return 0

    def columnCount(self, parent = QModelIndex()):
        return 2 # MapObject name|type

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if (role == Qt.DisplayRole and orientation == Qt.Horizontal):
            x = section
            if x==0:
                return self.tr("Name")
            elif x==1:
                return self.tr("Type")

        return QVariant()

    def setData(self, index, value, role):
        mapObject = self.toMapObject(index)
        if mapObject:
            x = role
            if x==Qt.CheckStateRole:
                c = value
                visible = (c == Qt.Checked)
                if (visible != mapObject.isVisible()):
                    command = SetMapObjectVisible(self.mMapDocument, mapObject, visible)
                    self.mMapDocument.undoStack().push(command)
                return True
            elif x==Qt.EditRole:
                s = value
                if (index.column() == 0 and s != mapObject.name()):
                    undo = self.mMapDocument.undoStack()
                    undo.beginMacro(self.tr("Change Object Name"))
                    undo.push(ChangeMapObject(self.mMapDocument, mapObject, s, mapObject.type()))
                    undo.endMacro()

                if (index.column() == 1 and s != mapObject.type()):
                    undo = self.mMapDocument.undoStack()
                    undo.beginMacro(self.tr("Change Object Type"))
                    undo.push(ChangeMapObject(self.mMapDocument, mapObject, mapObject.name(), s))
                    undo.endMacro()

                return True

            return False

        objectGroup = self.toObjectGroup(index)
        if objectGroup:
            x = role
            if x==Qt.CheckStateRole:
                layerModel = self.mMapDocument.layerModel()
                layerIndex = self.mMap.layers().indexOf(objectGroup)
                row = layerModel.layerIndexToRow(layerIndex)
                layerModel.setData(layerModel.index(row), value, role)
                return True
            elif x==Qt.EditRole:
                newName = value
                if (objectGroup.name() != newName):
                    layerIndex = self.mMap.layers().indexOf(objectGroup)
                    rename = RenameLayer(self.mMapDocument, layerIndex,
                                                          newName)
                    self.mMapDocument.undoStack().push(rename)

                return True

            return False

        return False

    def data(self, index, role = Qt.DisplayRole):
        mapObject = self.toMapObject(index)
        if mapObject:
            x = role
            if x==Qt.DisplayRole or x==Qt.EditRole:
                if index.column():
                    _x = mapObject.type()
                else:
                    _x = mapObject.name()
                return _x
            elif x==Qt.DecorationRole:
                return QVariant() # no icon . maybe the color?
            elif x==Qt.CheckStateRole:
                if (index.column() > 0):
                    return QVariant()
                if mapObject.isVisible():
                    _x = Qt.Checked
                else:
                    _x = Qt.Unchecked
                return _x
            elif x==LayerModel.UserRoles.OpacityRole:
                return 1.0
            else:
                return QVariant()

        objectGroup = self.toObjectGroup(index)
        if objectGroup:
            x = role
            if x==Qt.DisplayRole or x==Qt.EditRole:
                if index.column():
                    _x = QVariant()
                else:
                    _x = objectGroup.name()
                return _x
            elif x==Qt.DecorationRole:
                if index.column():
                    _x = QVariant()
                else:
                    _x = self.mObjectGroupIcon
                return _x
            elif x==Qt.CheckStateRole:
                if (index.column() > 0):
                    return QVariant()
                if objectGroup.isVisible():
                    _x = Qt.Checked
                else:
                    _x = Qt.Unchecked
                return _x
            elif x==LayerModel.UserRoles.OpacityRole:
                return objectGroup.opacity()
            else:
                return QVariant()

        return QVariant()

    def flags(self, index):
        rc = super().flags(index)
        if (index.column() == 0):
            rc |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        elif (index.parent().isValid()):
            rc |= Qt.ItemIsEditable # MapObject type
        return rc

    def toObjectGroup(self, index):
        if (not index.isValid()):
            return None
        oog = index.internalPointer()
        if oog:
            return oog.mGroup

    def toMapObject(self, index):
        if (not index.isValid()):
            return None
        oog = index.internalPointer()
        if oog:
            return oog.mObject

    def toLayer(self, index):
        if (not index.isValid()):
            return None
        oog = index.internalPointer()
        if oog:
            if oog.mGroup:
                _x = oog.mGroup
            else:
                _x = oog.mObject.objectGroup()
            return _x

    def setMapDocument(self, mapDocument):
        if (self.mMapDocument == mapDocument):
            return
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
        self.beginResetModel()
        self.mMapDocument = mapDocument
        self.mMap = None
        self.mObjectGroups.clear()
        self.mGroups.clear()
        self.mGroups.clear()
        self.mObjects.clear()
        self.mObjects.clear()
        if (self.mMapDocument):
            self.mMap = self.mMapDocument.map()
            self.mMapDocument.layerAdded.connect(self.layerAdded)
            self.mMapDocument.layerChanged.connect(self.layerChanged)
            self.mMapDocument.layerAboutToBeRemoved.connect(self.layerAboutToBeRemoved)
            for og in self.mMap.objectGroups():
                if GROUPS_IN_DISPLAY_ORDER:
                    self.mObjectGroups.prepend(og)
                else:
                    self.mObjectGroups.append(og)
                self.mGroups.insert(og, ObjectOrGroup(og))
                for o in og.objects():
                    self.mObjects.insert(o, ObjectOrGroup(o))

        self.endResetModel()

    def insertObject(self, og, index, o):
        if (index >= 0):
            _x = index
        else:
            _x = og.objectCount()
        row = _x
        self.beginInsertRows(self.index(og), row, row)
        og.insertObject(row, o)
        self.mObjects.insert(o, ObjectOrGroup(o))
        self.endInsertRows()
        self.objectsAdded.emit(QList([o]))

    def removeObject(self, og, o):
        objects = QList()
        objects.append(o)
        row = og.objects().indexOf(o)
        self.beginRemoveRows(self.index(og), row, row)
        og.removeObjectAt(row)
        self.mObjects.remove(o)
        self.endRemoveRows()
        self.objectsRemoved.emit(objects)
        return row

    def moveObjects(self, og, _from, to, count):
        parent = self.index(og)
        if (not self.beginMoveRows(parent, _from, _from + count - 1, parent, to)):
            return

        og.moveObjects(_from, to, count)
        self.endMoveRows()

    # ObjectGroup color changed
    # FIXME: layerChanged should let the scene know that objects need redrawing
    def emitObjectsChanged(self, objects):
        if objects.isEmpty():
            return
        self.objectsChanged.emit(objects)

    def setObjectName(self, o, name):
        if o.name() == name:
            return
        o.setName(name)
        index = self.index(o)
        self.dataChanged.emit(index, index)
        self.objectsChanged.emit(QList([o]))

    def setObjectType(self, o, type):
        if o.type() == type:
            return
        o.setType(type)
        index = self.index(o, 1)
        self.dataChanged.emit(index, index)
        self.objectsChanged.emit(QList([o]))

    def setObjectPolygon(self, o, polygon):
        if o.polygon() == polygon:
            return
        o.setPolygon(polygon)
        self.objectsChanged.emit(QList([o]))

    def setObjectPosition(self, o, pos):
        if o.position() == pos:
            return
        o.setPosition(pos)
        self.objectsChanged.emit(QList([o]))

    def setObjectSize(self, o, size):
        if o.size() == size:
            return
        o.setSize(size)
        self.objectsChanged.emit(QList([o]))

    def setObjectRotation(self, o, rotation):
        if o.rotation() == rotation:
            return
        o.setRotation(rotation)
        self.objectsChanged.emit(QList([o]))

    def setObjectVisible(self, o, visible):
        if o.isVisible() == visible:
            return
        o.setVisible(visible)
        index = self.index(o)
        self.dataChanged.emit(index, index)
        self.objectsChanged.emit(QList([o]))

    def layerAdded(self, index):
        layer = self.mMap.layerAt(index)
        og = layer.asObjectGroup()
        if og:
            if (not self.mGroups.contains(og)):
                prev = None
                for index in range(index - 1, -1, -1):
                    prev = self.mMap.layerAt(index).asObjectGroup()
                    if prev:
                        break
                if GROUPS_IN_DISPLAY_ORDER:
                    if prev:
                        _x = self.mObjectGroups.indexOf(prev)
                    else:
                        _x = self.mObjectGroups.count()
                    index = _x
                else:
                    if prev:
                        index = self.mObjectGroups.indexOf(prev) + 1
                    else:
                        index = 0

                self.mObjectGroups.insert(index, og)
                row = self.mObjectGroups.indexOf(og)
                self.beginInsertRows(QModelIndex(), row, row)
                self.mGroups.insert(og, ObjectOrGroup(og))
                for o in og.objects():
                    if (not self.mObjects.contains(o)):
                        self.mObjects.insert(o, ObjectOrGroup(o))

                self.endInsertRows()

    def layerChanged(self, index):
        layer = self.mMap.layerAt(index)
        og = layer.asObjectGroup()
        if og:
            index = self.index(og)
            self.dataChanged.emit(index, index)

    def layerAboutToBeRemoved(self, index):
        layer = self.mMap.layerAt(index)
        og = layer.asObjectGroup()
        if og:
            row = self.mObjectGroups.indexOf(og)
            self.beginRemoveRows(QModelIndex(), row, row)
            self.mObjectGroups.removeAt(row)
            self.mGroups.remove(og)
            for o in og.objects():
                self.mObjects.remove(og)
            self.endRemoveRows()

