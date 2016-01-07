# -*- coding: utf-8 -*-
##
# addremovelayer.py
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

from PyQt5.QtWidgets import (
    QUndoCommand
)
from PyQt5.QtCore import (
    QCoreApplication
)
###
# Abstract base class for AddLayer and RemoveLayer.
##
class AddRemoveLayer(QUndoCommand):
    def __init__(self, mapDocument, index, layer):
        super().__init__()
        
        self.mMapDocument = mapDocument
        self.mLayer = layer
        self.mIndex = index

    def __del__(self):
        self.mLayer

    def addLayer(self):
        currentLayer = self.mMapDocument.currentLayerIndex()
        self.mMapDocument.layerModel().insertLayer(self.mIndex, self.mLayer)
        self.mLayer = None
        # Insertion below or at the current layer increases current layer index
        if (self.mIndex <= currentLayer):
            self.mMapDocument.setCurrentLayerIndex(currentLayer + 1)

    def removeLayer(self):
        currentLayer = self.mMapDocument.currentLayerIndex()
        self.mLayer = self.mMapDocument.layerModel().takeLayerAt(self.mIndex)
        # Removal below the current layer decreases the current layer index
        if (self.mIndex < currentLayer):
            self.mMapDocument.setCurrentLayerIndex(currentLayer - 1)

###
# Undo command that adds a layer to a map.
##
class AddLayer(AddRemoveLayer):
    ###
    # Creates an undo command that adds the \a layer at \a index.
    ##
    def __init__(self, mapDocument, index, layer):
        super().__init__(mapDocument, index, layer)
        
        self.setText(QCoreApplication.translate("Undo Commands", "Add Layer"))

    def undo(self):
        self.removeLayer()

    def redo(self):
        self.addLayer()

###
# Undo command that removes a layer from a map.
##
class RemoveLayer(AddRemoveLayer):
    ###
    # Creates an undo command that removes the layer at \a index.
    ##
    def __init__(self, mapDocument, index):
        super().__init__(mapDocument, index, None)
        self.setText(QCoreApplication.translate("Undo Commands", "Remove Layer"))

    def undo(self):
        self.addLayer()

    def redo(self):
        self.removeLayer()
