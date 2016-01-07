##
# movetileset.py
# Copyright 2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from undocommands import UndoCommands
from PyQt5.QtCore import (
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)
##
# An undo command for moving a tileset from one place to another.
##
class MoveTileset(QUndoCommand):
    def __init__(self, mapDocument, _from, to):
        super().__init__(QCoreApplication.translate("Undo Commands", "Move Tileset"))
        
        self.mMapDocument = mapDocument
        self.mFrom = _from
        self.mTo = to

    def undo(self):
        self.mMapDocument.moveTileset(self.mTo, self.mFrom)

    def redo(self):
        self.mMapDocument.moveTileset(self.mFrom, self.mTo)

    def id(self):
        return UndoCommands.Cmd_MoveTileset

    def mergeWith(self, other):
        o = other
        if (self.mMapDocument != o.mMapDocument):
            return False
        # When moving only one step, swapping from and to is identical
        otherIsOneStep = abs(o.mFrom - o.mTo) == 1
        isOneStep = abs(self.mFrom - self.mTo) == 1
        if (self.mTo == self.mFrom):              # This command is a no-op
            self.mTo = o.mTo
            self.mFrom = o.mFrom
            return True
        elif (o.mTo == o.mFrom): # The other command is a no-op
            return True
        elif (o.mFrom == self.mTo):    # Regular transitive relation logic
            self.mTo = o.mTo
            return True
        elif (otherIsOneStep and o.mTo == self.mTo): # Consider other swapped
            self.mTo = o.mFrom
            return True
        elif (isOneStep and o.mFrom == self.mFrom):  # Consider this swapped
            self.mFrom = self.mTo
            self.mTo = o.mTo
            return True
        elif (otherIsOneStep and isOneStep and o.mTo == self.mFrom): # Swap both
            self.mFrom = self.mTo
            self.mTo = o.mFrom
            return True

        return False
