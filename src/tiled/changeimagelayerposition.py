##
# changeimagelayerproperties.py
# Copyright 2014, Michael Aquilina
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
class ChangeImageLayerPosition(QUndoCommand):
    ##
    # Constructs a new 'Change Image Layer Position' command.
    #
    # @param mapDocument   the map document of the layer's map
    # @param imageLayer    the image layer to modify
    # @param newPos        the new positon of the image layer
    ##
    def __init__(self, mapDocument, imageLayer, newPos):
        super().__init__(QCoreApplication.translate("Undo Commands", "Change Image Layer Position"))
        
        self.mMapDocument = mapDocument
        self.mImageLayer = imageLayer
        self.mUndoPos = imageLayer.position()
        self.mRedoPos = newPos

    def undo(self):
        self.mImageLayer.setPosition(self.mUndoPos)
        self.mMapDocument.emitImageLayerChanged(self.mImageLayer)

    def redo(self):
        self.mImageLayer.setPosition(self.mRedoPos)
        self.mMapDocument.emitImageLayerChanged(self.mImageLayer)
