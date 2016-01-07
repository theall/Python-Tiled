##
# resizemap.py
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
    QCoreApplication,
    QSize
)
from PyQt5.QtWidgets import (
    QUndoCommand
)
##
# Undo command that resizes a map. This command does not touch any of the
# map layers. See ResizeLayer if you want that.
##
class ResizeMap(QUndoCommand):
    def __init__(self, mapDocument, size):
        super().__init__(QCoreApplication.translate("Undo Commands", "Resize Map"))
        
        self.mMapDocument = mapDocument
        self.mSize = QSize(size)

    def undo(self):
        self.swapSize()

    def redo(self):
        self.swapSize()

    def swapSize(self):
        map = self.mMapDocument.map()
        oldSize = QSize(map.width(), map.height())
        map.setWidth(self.mSize.width())
        map.setHeight(self.mSize.height())
        self.mSize = oldSize
        self.mMapDocument.emitMapChanged()
