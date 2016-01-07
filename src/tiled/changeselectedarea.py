##
# changeselectedarea.py
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

from PyQt5.QtGui import (
    QRegion
)
from PyQt5.QtCore import (
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)
class ChangeSelectedArea(QUndoCommand):
    ##
    # Creates an undo command that sets the selection of \a mapDocument to
    # the given \a selection.
    ##
    def __init__(self, mapDocument, selection):
        super().__init__(QCoreApplication.translate("Undo Commands", "Change Selection"))
        
        self.mMapDocument = mapDocument
        self.mSelection = QRegion(selection)

    def undo(self):
        self.swapSelection()

    def redo(self):
        self.swapSelection()

    def swapSelection(self):
        oldSelection = self.mMapDocument.selectedArea()
        self.mMapDocument.setSelectedArea(self.mSelection)
        self.mSelection = oldSelection
