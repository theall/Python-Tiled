##
# terrainmodel.py
# Copyright 2008-2012, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2009, Edward Hutchins
# Copyright 2012, Manu Evans
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

from terrain import Terrain
from containerhelpers import indexOf
from renameterrain import RenameTerrain
from tileset import Tileset
from PyQt5.QtCore import (
    Qt,
    QSize,
    QVariant,
    pyqtSignal,
    QModelIndex,
    QAbstractItemModel
)
from PyQt5.QtWidgets import (
    QApplication
)

##
# A model providing a tree view on the terrain types available on a map.
##
class TerrainModel(QAbstractItemModel):
    terrainAdded = pyqtSignal(Tileset, int)
    terrainRemoved = pyqtSignal(Terrain)
    ##
    # Emitted when either the name or the image of a terrain changed.
    ##
    terrainChanged = pyqtSignal(Tileset, int)

    class UserRoles():
        TerrainRole = Qt.UserRole

    ##
    # Constructor.
    #
    # @param mapDocument the map to manage terrains for
    ##
    def __init__(self, mapDocument, parent):
        super().__init__(parent)
        self.mMapDocument = mapDocument

        mapDocument.tilesetAboutToBeAdded.connect(self.tilesetAboutToBeAdded)
        mapDocument.tilesetAdded.connect(self.tilesetAdded)
        mapDocument.tilesetAboutToBeRemoved.connect(self.tilesetAboutToBeRemoved)
        mapDocument.tilesetRemoved.connect(self.tilesetRemoved)
        mapDocument.tilesetNameChanged.connect(self.tilesetNameChanged)

    def __del__(self):
        pass

    def index(self, *args):
        l = len(args)
        if l==2 or l==3:
            if l==3:
                row, column, parent = args
            elif l==2:
                row, column = args
                parent = QModelIndex()

            if (not self.hasIndex(row, column, parent)):
                return QModelIndex()
            if (not parent.isValid()):
                return self.createIndex(row, column)
            else:
                tileset = self.tilesetAt(parent)
                if tileset:
                    return self.createIndex(row, column, tileset)
            return QModelIndex()
        elif l==1:
            tp = type(args[0])
            if tp==Tileset:
                tileset = args[0]
                row = indexOf(self.mMapDocument.map().tilesets(), tileset)
                return self.createIndex(row, 0)
            elif tp==Terrain:
                terrain = args[0]
                tileset = terrain.tileset()
                row = tileset.terrains().indexOf(terrain)
                return self.createIndex(row, 0, tileset)

    def parent(self, child):
        terrain = self.terrainAt(child)
        if terrain:
            return self.index(terrain.tileset())
        return QModelIndex()

    ##
    # Returns the number of rows. For the root, this is the number of tilesets
    # with terrain types defined. Otherwise it is the number of terrain types
    # in a certain tileset.
    ##
    def rowCount(self, parent = QModelIndex()):
        if (not parent.isValid()):
            return self.mMapDocument.map().tilesetCount()
        else:
            tileset = self.tilesetAt(parent)
            if tileset:
                return tileset.terrainCount()
        return 0

    ##
    # Returns the number of columns.
    ##
    def columnCount(self, parent = QModelIndex()):
        return 1

    ##
    # Returns the data stored under the given <i>role</i> for the item
    # referred to by the <i>index</i>.
    ##
    def data(self, index, role = Qt.DisplayRole):
        terrain = self.terrainAt(index)
        if terrain:
            x = role
            if x==Qt.DisplayRole or x==Qt.EditRole:
                return terrain.name()
            elif x==Qt.DecorationRole:
                imageTile = terrain.imageTile()
                if imageTile:
                    return imageTile.image()
            elif x==TerrainModel.UserRoles.TerrainRole:
                return QVariant(terrain)
        else:
            tileset = self.tilesetAt(index)
            if tileset:
                x = role
                if x==Qt.DisplayRole:
                    return tileset.name()
                elif x==Qt.SizeHintRole:
                    return QSize(1, 32)
                elif x==Qt.FontRole:
                    font = QApplication.font()
                    font.setBold(True)
                    return font
                elif x==Qt.BackgroundRole:
                    bg = QApplication.palette().alternateBase().color()
                    return bg#.darker(103)

        return QVariant()

    ##
    # Allows for changing the name of a terrain.
    ##
    def setData(self, index, value, role):
        if (role == Qt.EditRole):
            newName = value.toString()
            terrain = self.terrainAt(index)
            if (terrain.name() != newName):
                rename = RenameTerrain(self.mMapDocument,
                                                          terrain.tileset(),
                                                          terrain.id(),
                                                          newName)
                self.mMapDocument.undoStack().push(rename)

            return True

        return False

    ##
    # Makes terrain names editable.
    ##
    def flags(self, index):
        rc = super().flags(index)
        if (index.parent().isValid()):  # can edit terrain names
            rc |= Qt.ItemIsEditable
        return rc

    ##
    # Returns the tileset at the given \a index, or 0 if there is no tileset.
    ##
    def tilesetAt(self, index):
        if (not index.isValid()):
            return None
        if (index.parent().isValid()): # tilesets don't have parents
            return None
        if (index.row() >= self.mMapDocument.map().tilesetCount()):
            return None
        return self.mMapDocument.map().tilesetAt(index.row())
    ##
    # Returns the terrain at the given \a index, or 0 if there is no terrain.
    ##
    def terrainAt(self, index):
        if (not index.isValid()):
            return None
        tileset = index.internalPointer()
        if tileset:
            return tileset.terrain(index.row())
        return None

    ##
    # Adds a terrain type to the given \a tileset at \a index. Emits the
    # appropriate signal.
    ##
    def insertTerrain(self, tileset, index, terrain):
        tilesetIndex = TerrainModel.index(tileset)
        self.beginInsertRows(tilesetIndex, index, index)
        tileset.insertTerrain(index, terrain)
        self.endInsertRows()
        self.terrainAdded.emit(tileset, index)
        self.dataChanged.emit(tilesetIndex, tilesetIndex) # for TerrainFilterModel

    ##
    # Removes the terrain type from the given \a tileset at \a index and returns
    # it. The caller becomes responsible for the lifetime of the terrain type.
    # Emits the appropriate signal.
    #
    # \warning This will update terrain information of all the tiles in the
    #          tileset, clearing references to the removed terrain.
    ##
    def takeTerrainAt(self, tileset, index):
        tilesetIndex = TerrainModel.index(tileset)

        self.beginRemoveRows(tilesetIndex, index, index)
        terrain = tileset.takeTerrainAt(index)
        self.endRemoveRows()
        self.terrainRemoved.emit(terrain)
        self.dataChanged.emit(tilesetIndex, tilesetIndex) # for TerrainFilterModel

        return terrain

    def setTerrainName(self, tileset, index, name):
        terrain = tileset.terrain(index)
        terrain.setName(name)
        self.emitTerrainChanged(terrain)

    def setTerrainImage(self, tileset, index, tileId):
        terrain = tileset.terrain(index)
        terrain.setImageTileId(tileId)
        self.emitTerrainChanged(terrain)

    def tilesetAboutToBeAdded(self, index):
        self.beginInsertRows(QModelIndex(), index, index)

    def tilesetAdded(self):
        self.endInsertRows()

    def tilesetAboutToBeRemoved(self, index):
        self.beginRemoveRows(QModelIndex(), index, index)

    def tilesetRemoved(self):
        self.endRemoveRows()

    def tilesetNameChanged(self, tileset):
        index = TerrainModel.index(tileset)
        self.dataChanged.emit(index, index)

    def emitTerrainChanged(self, terrain):
        index = TerrainModel.index(terrain)
        self.dataChanged.emit(index, index)
        self.terrainChanged.emit(terrain.tileset(), index.row())
