##
# layermodel.py
# Copyright 2008-2009, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from renamelayer import RenameLayer
from layer import Layer
from changelayer import SetLayerVisible, SetLayerOpacity
from PyQt5.QtCore import (
    Qt,
    QVariant,
    pyqtSignal,
    QModelIndex,
    QAbstractListModel
)
from PyQt5.QtGui import (
    QIcon
)
##
# A model wrapping the layers of a map. Used to display the layers in a view.
# The model also allows modification of the layer stack while keeping the
# layer views up to date.
##
class LayerModel(QAbstractListModel):
    layerAdded = pyqtSignal(int)
    layerAboutToBeRemoved = pyqtSignal(int)
    layerRemoved = pyqtSignal(int)
    layerAboutToBeRenamed = pyqtSignal(int)
    layerRenamed = pyqtSignal(int)
    layerChanged = pyqtSignal(int)
    
    ##
    # The OpacityRole allows querying and changing the layer opacity.
    ##
    class UserRoles():
        OpacityRole = Qt.UserRole
        
    ##
    # Constructor.
    ##
    def __init__(self, parent):
        super().__init__(parent)

        self.mMapDocument = None
        self.mMap = None
        self.mTileLayerIcon = QIcon(":/images/16x16/layer-tile.png")
        self.mObjectGroupIcon = QIcon(":/images/16x16/layer-object.png")
        self.mImageLayerIcon = QIcon(":/images/16x16/layer-image.png")

    ##
    # Returns the number of rows.
    ##
    def rowCount(self, parent):
        if parent.isValid():
            return 0
        else:
            if self.mMap:
                return self.mMap.layerCount()
            else:
                return 0

    ##
    # Returns the data stored under the given <i>role</i> for the item
    # referred to by the <i>index</i>.
    ##
    def data(self, index, role = Qt.DisplayRole):
        layerIndex = self.toLayerIndex(index)
        if (layerIndex < 0):
            return QVariant()
        layer = self.mMap.layerAt(layerIndex)
        x = role
        if x==Qt.DisplayRole or x==Qt.EditRole:
            return layer.name()
        elif x==Qt.DecorationRole:
            x = layer.layerType()
            if x==Layer.TileLayerType:
                return self.mTileLayerIcon
            elif x==Layer.ObjectGroupType:
                return self.mObjectGroupIcon
            elif x==Layer.ImageLayerType:
                return self.mImageLayerIcon
        elif x==Qt.CheckStateRole:
            if layer.isVisible():
                return Qt.Checked
            else:
                return Qt.Unchecked
        elif x==LayerModel.UserRoles.OpacityRole:
            return layer.opacity()
        else:
            return QVariant()

    ##
    # Allows for changing the name, visibility and opacity of a layer.
    ##
    def setData(self, index, value, role):
        layerIndex = self.toLayerIndex(index)
        if (layerIndex < 0):
            return False
        layer = self.mMap.layerAt(layerIndex)
        if (role == Qt.CheckStateRole):
            c = value
            visible = (c == Qt.Checked)
            if (visible != layer.isVisible()):
                command = SetLayerVisible(self.mMapDocument, layerIndex, visible)
                self.mMapDocument.undoStack().push(command)

            return True
        elif (role == LayerModel.UserRoles.OpacityRole):
            try:
                opacity = float(value)
                ok = True
            except:
                ok = False
            if (ok):
                if (layer.opacity() != opacity):
                    command = SetLayerOpacity(self.mMapDocument,
                                                                layerIndex,
                                                                opacity)
                    self.mMapDocument.undoStack().push(command)

                return True
        elif (role == Qt.EditRole):
            newName = value
            if (layer.name() != newName):
                rename = RenameLayer(self.mMapDocument, layerIndex,
                                                      newName)
                self.mMapDocument.undoStack().push(rename)

            return True

        return False

    ##
    # Makes sure the items are checkable and names editable.
    ##
    def flags(self, index):
        rc = super().flags(index)
        if (index.column() == 0):
            rc |= Qt.ItemIsUserCheckable | Qt.ItemIsEditable
        return rc

    ##
    # Returns the headers for the table.
    ##
    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if (role == Qt.DisplayRole and orientation == Qt.Horizontal):
            x = section
            if x==0: return self.tr("Layer")

        return QVariant()

    ##
    # Returns the layer index associated with a given model index.
    # \sa layerIndexToRow
    ##
    def toLayerIndex(self, index):
        if (index.isValid()):
            return self.mMap.layerCount() - index.row() - 1
        else:
            return -1

    ##
    # Returns the row associated with the given layer index.
    # \sa toLayerIndex
    ##
    def layerIndexToRow(self, layerIndex):
        return self.mMap.layerCount() - layerIndex - 1

    ##
    # Returns the map document associated with this model.
    ##
    def mapDocument(self):
        return self.mMapDocument

    ##
    # Sets the map document associated with this model.
    ##
    def setMapDocument(self, mapDocument):
        if (self.mMapDocument == mapDocument):
            return
        self.beginResetModel()
        self.mMapDocument = mapDocument
        self.mMap = self.mMapDocument.map()
        self.endResetModel()

    ##
    # Adds a layer to this model's map, inserting it at the given index.
    ##
    def insertLayer(self, index, layer):
        row = self.layerIndexToRow(index) + 1
        self.beginInsertRows(QModelIndex(), row, row)
        self.mMap.insertLayer(index, layer)
        self.endInsertRows()
        self.layerAdded.emit(index)

    ##
    # Removes the layer at the given index from this model's map and 
    # returns it. The caller becomes responsible for the lifetime of this
    # layer.
    ##
    def takeLayerAt(self, index):
        self.layerAboutToBeRemoved.emit(index)
        row = self.layerIndexToRow(index)
        self.beginRemoveRows(QModelIndex(), row, row)
        layer = self.mMap.takeLayerAt(index)
        self.endRemoveRows()
        self.layerRemoved.emit(index)
        return layer

    ##
    # Sets whether the layer at the given index is visible.
    ##
    def setLayerVisible(self, layerIndex, visible):
        modelIndex = self.index(self.layerIndexToRow(layerIndex), 0)
        layer = self.mMap.layerAt(layerIndex)
        
        if layer.isVisible() == visible:
            return
            
        layer.setVisible(visible)
        self.dataChanged.emit(modelIndex, modelIndex)
        self.layerChanged.emit(layerIndex)

    ##
    # Sets the opacity of the layer at the given index.
    ##
    def setLayerOpacity(self, layerIndex, opacity):
        layer = self.mMap.layerAt(layerIndex)
        
        if layer.opacity() == opacity:
            return
            
        layer.setOpacity(opacity)
        self.layerChanged.emit(layerIndex)

    ##
    # Sets the offset of the layer at the given index.
    ##
    def setLayerOffset(self, layerIndex, offset):
        layer = self.mMap.layerAt(layerIndex)
        if layer.offset() == offset:
            return

        layer.setOffset(offset)
        self.layerChanged.emit(layerIndex)
    
    ##
    # Renames the layer at the given index.
    ##
    def renameLayer(self, layerIndex, name):
        self.layerAboutToBeRenamed.emit(layerIndex)
        modelIndex = self.index(self.layerIndexToRow(layerIndex), 0)
        layer = self.mMap.layerAt(layerIndex)
        if layer.name() == name:
            return

        self.layerAboutToBeRenamed.emit(layerIndex)
        
        layer.setName(name)
        self.layerRenamed.emit(layerIndex)
        self.dataChanged.emit(modelIndex, modelIndex)
        self.layerChanged.emit(layerIndex)

    ##
    # Show or hide all other layers except the layer at the given index.
    # If any other layer is visible then all layers will be hidden, otherwise
    # the layers will be shown.
    ##
    def toggleOtherLayers(self, layerIndex):
        if (self.mMap.layerCount() <= 1): # No other layers
            return
        visibility = True
        for i in range(self.mMap.layerCount()):
            if (i == layerIndex):
                continue
            layer = self.mMap.layerAt(i)
            if (layer.isVisible()):
                visibility = False
                break

        undoStack = self.mMapDocument.undoStack()
        if (visibility):
            undoStack.beginMacro(self.tr("Show Other Layers"))
        else:
            undoStack.beginMacro(self.tr("Hide Other Layers"))
        for i in range(self.mMap.layerCount()):
            if (i == layerIndex):
                continue
            if (visibility != self.mMap.layerAt(i).isVisible()):
                undoStack.push(SetLayerVisible(self.mMapDocument, i, visibility))

        undoStack.endMacro()
