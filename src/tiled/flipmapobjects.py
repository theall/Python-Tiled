##
# flipmapobjects.py
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

from PyQt5.QtCore import (
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)
class FlipMapObjects(QUndoCommand):
    def __init__(self, mapDocument, mapObjects, flipDirection):
        super().__init__()
        
        self.mMapDocument = mapDocument
        self.mMapObjects = mapObjects
        self.mFlipDirection = flipDirection

        self.setText(QCoreApplication.translate("Undo Commands", "Flip %n Object(s)", '', mapObjects.size()))

    def undo(self):
        self.flip()

    def redo(self):
        self.flip()

    def flip(self):
        # TODO: Flip them properly as a group
        for object in self.mMapObjects:
            object.flip(self.mFlipDirection)
        self.mMapDocument.mapObjectModel().emitObjectsChanged(self.mMapObjects)

