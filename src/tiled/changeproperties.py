##
# changeproperties.py
# Copyright 2008-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from pyqtcore import QString, QVector, QList
from PyQt5.QtCore import (
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)
class ObjectProperty():
    def __init__(self):
        self.previousValue = QString()
        self.existed = False

class ChangeProperties(QUndoCommand):
    ##
    # Constructs a new 'Change Properties' command.
    #
    # @param mapDocument  the map document of the object's map
    # @param kind         the kind of properties (Map, Layer, Object, etc.)
    # @param object       the object of which the properties should be changed
    # @param newProperties the new properties that should be applied
    ##
    def __init__(self, mapDocument, kind, object, newProperties):
        self.mMapDocument = mapDocument
        self.mObject = object
        self.mNewProperties = newProperties

        self.setText(QCoreApplication.translate("Undo Commands", "Change %s Properties"%kind))

    def undo(self):
        self.swapProperties()

    def redo(self):
        self.swapProperties()

    def swapProperties(self):
        oldProperties = self.mObject.properties()
        self.mMapDocument.setProperties(self.mObject, self.mNewProperties)
        self.mNewProperties = oldProperties

class SetProperty(QUndoCommand):
    ##
    # Constructs a new 'Set Property' command.
    #
    # @param mapDocument  the map document of the object's map
    # @param objects      the objects of which the property should be changed
    # @param name         the name of the property to be changed
    # @param value        the new value of the property
    ##
    def __init__(self, mapDocument, objects, name, value, parent = None):
        super().__init__(parent)

        self.mProperties = QVector()
        self.mMapDocument = mapDocument
        self.mObjects = objects
        self.mName = name
        self.mValue = value

        for obj in self.mObjects:
            prop = ObjectProperty()
            prop.existed = obj.hasProperty(self.mName)
            prop.previousValue = obj.property(self.mName)
            self.mProperties.append(prop)

        if (self.mObjects.size() > 1 or self.mObjects[0].hasProperty(self.mName)):
            self.setText(QCoreApplication.translate("Undo Commands", "Set Property"))
        else:
            self.setText(QCoreApplication.translate("Undo Commands", "Add Property"))

    def undo(self):
        for i in range(self.mObjects.size()):
            if (self.mProperties[i].existed):
                self.mMapDocument.setProperty(self.mObjects[i], self.mName, self.mProperties[i].previousValue)
            else:
                self.mMapDocument.removeProperty(self.mObjects[i], self.mName)

    def redo(self):
        for obj in self.mObjects:
            self.mMapDocument.setProperty(obj, self.mName, self.mValue)

class RemoveProperty(QUndoCommand):

    ##
    # Constructs a new 'Remove Property' command.
    #
    # @param mapDocument  the map document of the object's map
    # @param objects      the objects from which the property should be removed
    # @param name         the name of the property to be removed
    ##
    def __init__(self, mapDocument, objects, name, parent = None):
        super().__init__(parent)
        
        self.mMapDocument = mapDocument
        self.mObjects = objects
        self.mName = name

        for obj in self.mObjects:
            self.mPreviousValues.append(obj.property(self.mName))
        self.setText(QCoreApplication.translate("Undo Commands", "Remove Property"))

    def undo(self):
        for i in range(self.mObjects.size()):
            self.mMapDocument.setProperty(self.mObjects[i], self.mName, self.mPreviousValues[i])

    def redo(self):
        for obj in self.mObjects:
            self.mMapDocument.removeProperty(obj, self.mName)

class RenameProperty(QUndoCommand):
    ##
    # Constructs a new 'Rename Property' command.
    #
    # @param mapDocument  the map document of the object's map
    # @param object       the object of which the property should be renamed
    # @param oldName      the old name of the property
    # @param newName      the new name of the property
    ##
    def __init__(self, mapDocument, objects, oldName, newName):
        super().__init__()
        
        self.setText(QCoreApplication.translate("Undo Commands", "Rename Property"))
        # Remove the old name from all objects
        objects = RemoveProperty(mapDocument, objects, oldName, self)
        # Different objects may have different values for the same property,
        # or may not have a value at all.
        for object in objects:
            if (not object.hasProperty(oldName)):
                continue
            objects = QList()
            objects.append(object)
            value = object.property(oldName)
            objects = SetProperty(mapDocument, objects, newName, value, self)
