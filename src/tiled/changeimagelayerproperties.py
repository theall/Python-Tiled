##
# changeimagelayerproperties.py
# Copyright 2010, Jeff Bland <jeff@teamphobic.com>
# Copyright 2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2011, Gregory Nickonov
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
from PyQt5.QtGui import (
    QImage
)
from PyQt5.QtWidgets import (
    QUndoCommand
)

class ChangeImageLayerProperties(QUndoCommand):
    ##
    # Constructs a new 'Change Image Layer Properties' command.
    #
    # @param mapDocument   the map document of the layer's map
    # @param imageLayer    the image layer to modify
    # @param newColor      the new transparent color to apply
    # @param newPath       the new image source to apply
    ##
    def __init__(self, mapDocument, imageLayer, color, path):
        super().__init__(QCoreApplication.translate("Undo Commands", "Change Image Layer Properties"))
        
        self.mMapDocument = mapDocument
        self.mImageLayer = imageLayer
        self.mUndoColor = imageLayer.transparentColor()
        self.mRedoColor = color
        self.mUndoPath = imageLayer.imageSource()
        self.mRedoPath = path

    def undo(self):
        self.mImageLayer.setTransparentColor(self.mUndoColor)
        if self.mRedoPath == '':
            self.mImageLayer.resetImage()
        else:
            self.mImageLayer.loadFromImage(QImage(self.mUndoPath), self.mUndoPath)
        self.mMapDocument.emitImageLayerChanged(self.mImageLayer)

    def redo(self):
        self.mImageLayer.setTransparentColor(self.mRedoColor)
        if self.mRedoPath == '':
            self.mImageLayer.resetImage()
        else:
            self.mImageLayer.loadFromImage(QImage(self.mRedoPath), self.mRedoPath)
        self.mMapDocument.emitImageLayerChanged(self.mImageLayer)
