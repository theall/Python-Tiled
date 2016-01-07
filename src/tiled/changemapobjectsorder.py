##
# changemapobjectsorder.py
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
class ChangeMapObjectsOrder(QUndoCommand):
    def __init__(self, mapDocument, objectGroup, _from, to, count):
        super().__init__()
        
        self.mMapDocument = mapDocument
        self.mObjectGroup = objectGroup
        self.mFrom = _from
        self.mTo = to
        self.mCount = count

        if (self.mTo > self.mFrom):
            self.setText(QCoreApplication.translate("Undo Commands", "Raise Object"))
        else:
            self.setText(QCoreApplication.translate("Undo Commands", "Lower Object"))

    def undo(self):
        to = self.mFrom
        _from = self.mTo
        # When reversing the operation, either the 'from' or the 'to' index will
        # need to be adapted to take into account the number of objects moved.
        if (_from > to):
            _from -= self.mCount
        else:
            to += self.mCount
        self.mMapDocument.mapObjectModel().moveObjects(self.mObjectGroup,
                                                    _from, to, self.mCount)

    def redo(self):
        self.mMapDocument.mapObjectModel().moveObjects(self.mObjectGroup,
                                                    self.mFrom, self.mTo, self.mCount)
