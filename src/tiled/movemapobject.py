##
# movemapobject.py
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
class MoveMapObject(QUndoCommand):
    def __init__(self, *args):
        super().__init__()
        
        l = len(args)
        if l==3:
            mapDocument, mapObject, oldPos = args
            newPos = mapObject.position()
        elif l==4:
            mapDocument, mapObject, newPos, oldPos = args
        else:
            return
        self.mMapDocument = mapDocument
        self.mMapObject = mapObject
        self.mOldPos = oldPos
        self.mNewPos = newPos

        self.setText(QCoreApplication.translate("Undo Commands", "Move Object"))

    def undo(self):
        self.mMapDocument.mapObjectModel().setObjectPosition(self.mMapObject, self.mOldPos)

    def redo(self):
        self.mMapDocument.mapObjectModel().setObjectPosition(self.mMapObject, self.mNewPos)
