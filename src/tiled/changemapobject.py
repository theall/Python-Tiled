##
# changemapobject.py
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

class ChangeMapObject(QUndoCommand):
    ##
    # Creates an undo command that sets the given \a object's \a name and
    # \a type.
    ##
    def __init__(self, mapDocument, mapObject, name, type):
        super().__init__(QCoreApplication.translate("Undo Commands", "Change Object"))
        self.mMapDocument = mapDocument
        self.mMapObject = mapObject
        self.mName = name
        self.mType = type

    def undo(self):
        self.swap()

    def redo(self):
        self.swap()

    def swap(self):
        name = self.mMapObject.name()
        type = self.mMapObject.type()
        self.mMapDocument.mapObjectModel().setObjectName(self.mMapObject, self.mName)
        self.mMapDocument.mapObjectModel().setObjectType(self.mMapObject, self.mType)
        self.mName = name
        self.mType = type

##
# Used for changing object visibility.
##
class SetMapObjectVisible(QUndoCommand):

    def __init__(self, mapDocument, mapObject, visible):
        super().__init__()
        
        self.mMapObjectModel = mapDocument.mapObjectModel()
        self.mMapObject = mapObject
        self.mOldVisible = mapObject.isVisible()
        self.mNewVisible = visible

        if (visible):
            self.setText(QCoreApplication.translate("Undo Commands", "Show Object"))
        else:
            self.setText(QCoreApplication.translate("Undo Commands", "Hide Object"))

    def undo(self):
        self.mMapObjectModel.setObjectVisible(self.mMapObject, self.mOldVisible)

    def redo(self):
        self.mMapObjectModel.setObjectVisible(self.mMapObject, self.mNewVisible)
