##
# changelayer.py
# Copyright 2012-2013, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
# Used for changing layer visibility.
##
class SetLayerVisible(QUndoCommand):
    def __init__(self, mapDocument, layerIndex, visible):
        super().__init__()
        
        self.mMapDocument = mapDocument
        self.mLayerIndex = layerIndex
        self.mVisible = visible

        if (visible):
            self.setText(QCoreApplication.translate("Undo Commands", "Show Layer"))
        else:
            self.setText(QCoreApplication.translate("Undo Commands", "Hide Layer"))

    def undo(self):
        self.swap()

    def redo(self):
        self.swap()

    def swap(self):
        layer = self.mMapDocument.map().layerAt(self.mLayerIndex)
        previousVisible = layer.isVisible()
        self.mMapDocument.layerModel().setLayerVisible(self.mLayerIndex, self.mVisible)
        self.mVisible = previousVisible

##
# Used for changing layer opacity.
##
class SetLayerOpacity(QUndoCommand):
    def __init__(self, mapDocument, layerIndex, opacity):
        super().__init__()
        
        self.mMapDocument = mapDocument
        self.mLayerIndex = layerIndex
        self.mOldOpacity = self.mMapDocument.map().layerAt(layerIndex).opacity()
        self.mNewOpacity = opacity

        self.setText(QCoreApplication.translate("Undo Commands", "Change Layer Opacity"))

    def undo(self):
        self.setOpacity(self.mOldOpacity)

    def redo(self):
        self.setOpacity(self.mNewOpacity)

    def id(self):
        return UndoCommands.Cmd_ChangeLayerOpacity

    def mergeWith(self, other):
        o = other
        if (not (self.mMapDocument == o.mMapDocument and self.mLayerIndex == o.mLayerIndex)):
            return False
        self.mNewOpacity = o.mNewOpacity
        return True

    def setOpacity(self, opacity):
        self.mMapDocument.layerModel().setLayerOpacity(self.mLayerIndex, opacity)

##
# Used for changing the layer offset.
##
class SetLayerOffset(QUndoCommand):
    def __init__(self, mapDocument, layerIndex, offset):
        super().__init__()
        
        self.mMapDocument = mapDocument
        self.mLayerIndex = layerIndex
        self.mOldOffset = self.mMapDocument.map().layerAt(layerIndex).offset()
        self.mNewOffset = offset

        self.setText(QCoreApplication.translate("Undo Commands", "Change Layer Offset"))
                                        
    def undo(self):
        self.setOffset(self.mOldOffset)
        
    def redo(self):
        self.setOffset(self.mNewOffset)

    def id(self):
        return UndoCommands.Cmd_ChangeLayerOffset

    def setOffset(self, offset):
        self.mMapDocument.layerModel().setLayerOffset(self.mLayerIndex, offset)
