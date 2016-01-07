##
# tilesetmodel.py
# Copyright 2008-2009, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2009, Edward Hutchins
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

from pyqtcore import QStringList
from libtiled.tiled import TILES_MIMETYPE
from PyQt5.QtCore import (
    Qt,
    QSize,
    QVariant,
    QMimeData,
    QIODevice,
    QModelIndex,
    QByteArray,
    QDataStream,
    QAbstractTableModel
)

##
# A model wrapping a tileset of a map. Used to display the tiles.
##
class TilesetModel(QAbstractTableModel):
    ##
    # The TerrainRole allows querying the terrain info.
    ##
    class UserRoles():
        TerrainRole = Qt.UserRole

    ##
    # Constructor.
    #
    # @param tileset the initial tileset to display
    ##
    def __init__(self, tileset, parent):
        super().__init__(parent)
        
        self.mTileset = tileset

    ##
    # Returns the number of rows.
    ##
    def rowCount(self, parent = QModelIndex()):
        if (parent.isValid()):
            return 0
        tiles = self.mTileset.tileCount()
        columns = self.columnCount()
        rows = 1
        if (columns > 0):
            rows = int(tiles / columns)
            if (tiles % columns > 0):
                rows += 1

        return rows

    ##
    # Returns the number of columns.
    ##
    def columnCount(self, parent = QModelIndex()):
        if (parent.isValid()):
            return 0
        x = self.mTileset.columnCount()
        if x>0:
            return x
        # TODO: Non-table tilesets should use a different model.
        # For now use an arbitrary number of columns.
        return 5

    ##
    # Returns the data stored under the given <i>role</i> for the item
    # referred to by the <i>index</i>.
    ##
    def data(self, index, role = Qt.DisplayRole):
        if (role == Qt.DecorationRole):
            tile = self.tileAt(index)
            if tile:
                return tile.image()
        elif (role == TilesetModel.UserRoles.TerrainRole):
            tile = self.tileAt(index)
            if tile:
                return tile.terrain()

        return QVariant()

    ##
    # Returns a small size hint, to prevent the headers from affecting the
    # minimum width and height of the sections.
    ##
    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if (role == Qt.SizeHintRole):
            return QSize(1, 1)
        return QVariant()

    def flags(self, index):
        defaultFlags = super().flags(index)
        if (index.isValid()):
            defaultFlags |= Qt.ItemIsDragEnabled
        return defaultFlags

    def mimeTypes(self):
        types = QStringList()
        types.append(TILES_MIMETYPE)
        return types

    def mimeData(self, indexes):
        mimeData = QMimeData()
        encodedData = QByteArray()
        stream = QDataStream(encodedData, QIODevice.WriteOnly)
        for index in indexes:
            if (index.isValid()):
                stream.writeInt(self.tileIndexAt(index))

        mimeData.setData(TILES_MIMETYPE, encodedData)
        return mimeData

    ##
    # Returns the tile at the given index.
    ##
    def tileAt(self, index):
        if (not index.isValid()):
            return None
        i = index.column() + index.row() * self.columnCount()
        return self.mTileset.tileAt(i)

    def tileIndexAt(self, index):
        return index.column() + index.row() * self.columnCount()

    ##
    # Returns the index of the given \a tile. The tile is required to be from
    # the tileset used by this model.
    ##
    def tileIndex(self, tile):
        columnCount = self.columnCount()
        id = tile.id()
        row = id / columnCount
        column = id % columnCount
        return self.index(row, column)

    ##
    # Returns the tileset associated with this model.
    ##
    def tileset(self):
        return self.mTileset

    ##
    # Sets the tileset associated with this model.
    ##
    def setTileset(self, tileset):
        if (self.mTileset == tileset):
            return
        self.beginResetModel()
        self.mTileset = tileset
        self.endResetModel()

    ##
    # Performs a reset on the model.
    ##
    def tilesetChanged(self):
        self.beginResetModel()
        self.endResetModel()

    ##
    # Should be called when anything changes about the given \a tiles that
    # affects their display in any views on this model.
    #
    # Tiles that are not from the tileset displayed by this model are simply
    # ignored. All tiles in the list are assumed to be from the same tileset.
    #
    # \sa MapDocument.tileTerrainChanged
    ##
    def tilesChanged(self, tiles):
        if (tiles.first().tileset() != self.mTileset):
            return
        topLeft = QModelIndex()
        bottomRight = QModelIndex()
        for tile in tiles:
            i = self.tileIndex(tile)
            if (not topLeft.isValid()):
                topLeft = i
                bottomRight = i
                continue

            if (i.row() < topLeft.row() or i.column() < topLeft.column()):
                topLeft = self.index(min(topLeft.row(), i.row()),
                                min(topLeft.column(), i.column()))
            if (i.row() > bottomRight.row() or i.column() > bottomRight.column()):
                bottomRight = self.index(max(bottomRight.row(), i.row()),
                                    max(bottomRight.column(), i.column()))

        if (topLeft.isValid()):
            self.dataChanged.emit(topLeft, bottomRight)

    ##
    # Should be called when anything changes about the given \a tile that
    # affects its display in any views on this model.
    #
    # \sa MapDocument.tileAnimationChanged
    ##
    def tileChanged(self, tile):
        if (tile.tileset() != self.mTileset):
            return
        i = self.tileIndex(tile)
        self.dataChanged.emit(i, i)
