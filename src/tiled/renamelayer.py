##
# renamelayer.py
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
class RenameLayer(QUndoCommand):
    def __init__(self, mapDocument, layerIndex, name):
        super().__init__()
        
        self.mLayerIndex = layerIndex
        self.mName = name
        self.mMapDocument = mapDocument
        self.setText(QCoreApplication.translate("Undo Commands", "Rename Layer"))

    def undo(self):
        self.swapName()

    def redo(self):
        self.swapName()

    def swapName(self):
        layer = self.mMapDocument.map().layerAt(self.mLayerIndex)
        previousName = layer.name()
        self.mMapDocument.layerModel().renameLayer(self.mLayerIndex, self.mName)
        self.mName = previousName
