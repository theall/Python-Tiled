# -*- coding: utf-8 -*-
##
# addremovemapobject.py
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
from PyQt5.QtCore import (
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)

###
# Abstract base class for AddMapObject and RemoveMapObject.
##
class AddRemoveMapObject(QUndoCommand):
    def __init__(self, mapDocument, objectGroup, mapObject, ownObject, parent = None):
        super().__init__(parent)

        self.mMapDocument = mapDocument
        self.mMapObject = mapObject
        self.mObjectGroup = objectGroup
        self.mIndex = -1
        self.mOwnsObject = ownObject

    def __del__(self):
        if (self.mOwnsObject):
            self.mMapObject

    def addObject(self):
        self.mMapDocument.mapObjectModel().insertObject(self.mObjectGroup, self.mIndex, self.mMapObject)
        self.mOwnsObject = False

    def removeObject(self):
        self.mIndex = self.mMapDocument.mapObjectModel().removeObject(self.mObjectGroup, self.mMapObject)
        self.mOwnsObject = True

###
# Undo command that adds an object to a map.
##
class AddMapObject(AddRemoveMapObject):
    def __init__(self, mapDocument, objectGroup, mapObject, parent = None):
        super().__init__(mapDocument, objectGroup, mapObject, True, parent)

        self.setText(QCoreApplication.translate("Undo Commands", "Add Object"))

    def undo(self):
        self.removeObject()

    def redo(self):
        self.addObject()

###
# Undo command that removes an object from a map.
##
class RemoveMapObject(AddRemoveMapObject):
    def __init__(self, mapDocument, mapObject, parent = None):
        super().__init__(mapDocument, mapObject.objectGroup(), mapObject, False, parent)

        self.setText(QCoreApplication.translate("Undo Commands", "Remove Object"))

    def undo(self):
        self.addObject()

    def redo(self):
        self.removeObject()
