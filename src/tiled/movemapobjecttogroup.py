##
# movemapobjecttogroup.py
# Copyright 2010, Jeff Bland <jeff@teamphobic.com>
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
class MoveMapObjectToGroup(QUndoCommand):
    def __init__(self, mapDocument, mapObject, objectGroup):
        super().__init__()
        
        self.mMapDocument = mapDocument
        self.mMapObject = mapObject
        self.mOldObjectGroup = mapObject.objectGroup()
        self.mNewObjectGroup = objectGroup

        self.setText(QCoreApplication.translate("Undo Commands", "Move Object to Layer"))

        self.mMapObject = None
        self.mMapDocument = None
        self.mOldObjectGroup = None
        self.mNewObjectGroup = None

    def undo(self):
        self.mMapDocument.mapObjectModel().removeObject(self.mNewObjectGroup, self.mMapObject)
        self.mMapDocument.mapObjectModel().insertObject(self.mOldObjectGroup, -1, self.mMapObject)

    def redo(self):
        self.mMapDocument.mapObjectModel().removeObject(self.mOldObjectGroup, self.mMapObject)
        self.mMapDocument.mapObjectModel().insertObject(self.mNewObjectGroup, -1, self.mMapObject)
