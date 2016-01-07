##
# gidmapper.py
# Copyright 2011, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
#
# This file is part of libtiled.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE CONTRIBUTORS ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##

from map import Map
from compression import compress, decompress, CompressionMethod
from tilelayer import Cell
from pyqtcore import QMap
from PyQt5.QtCore import QByteArray
# Bits on the far end of the 32-bit global tile ID are used for tile flags
FlippedHorizontallyFlag   = 0x80000000
FlippedVerticallyFlag     = 0x40000000
FlippedAntiDiagonallyFlag = 0x20000000

class DecodeError():
    NoError = 0
    CorruptLayerData = 1
    TileButNoTilesets = 2
    InvalidTile = 3
    
##
# A class that maps cells to global IDs (gids) and back.
##
class GidMapper():
    ##
    # Default constructor. Use \l insert to initialize the gid mapper
    # incrementally.
    ##
    def __init__(self, *args):
        self.mInvalidTile = None
        self.mTilesetColumnCounts = QMap()
        self.mFirstGidToTileset = QMap()
        if len(args)==1:
            ##
            # Constructor that initializes the gid mapper using the given \a tilesets.
            ##
            firstGid = 1
            tilesets = args[0]
            for tileset in tilesets:
                self.insert(firstGid, tileset)
                firstGid += tileset.tileCount()

    ##
    # Insert the given \a tileset with \a firstGid as its first global ID.
    ##
    def insert(self, firstGid, tileset):
        self.mFirstGidToTileset.insert(firstGid, tileset)

    ##
    # Clears the gid mapper, so that it can be reused.
    ##
    def clear(self):
        self.mFirstGidToTileset.clear()

    ##
    # Returns True when no tilesets are known to this gid mapper.
    ##
    def isEmpty(self):
        return self.mFirstGidToTileset.isEmpty()

    ##
    # Returns the GID of the invalid tile in case decodeLayerData() returns
    # the InvalidTile error.
    ##
    def invalidTile(self):
        return self.mInvalidTile

    ##
    # Returns the cell data matched by the given \a gid. The \a ok parameter
    # indicates whether an error occurred.
    ##
    def gidToCell(self, gid):
        result = Cell()
        # Read out the flags
        result.flippedHorizontally = (gid & FlippedHorizontallyFlag)
        result.flippedVertically = (gid & FlippedVerticallyFlag)
        result.flippedAntiDiagonally = (gid & FlippedAntiDiagonallyFlag)
        # Clear the flags
        gid &= ~(FlippedHorizontallyFlag |
                 FlippedVerticallyFlag |
                 FlippedAntiDiagonallyFlag)
        if (gid == 0):
            ok = True
        elif (self.isEmpty()):
            ok = False
        else:
            # Find the tileset containing this tile
            index = self.mFirstGidToTileset.upperBound(gid)
            if index==0:
                ok = False
            else:
                item = self.mFirstGidToTileset.itemByIndex(index-1)
                # Navigate one tileset back since upper bound finds the next
                tileId = gid - item[0]
                tileset = item[1]

                columnCount = self.mTilesetColumnCounts.value(tileset, 0)
                if (columnCount > 0 and columnCount != tileset.columnCount()):
                    # Correct tile index for changes in image width
                    row = int(tileId / columnCount)
                    column = int(tileId % columnCount)
                    tileId = row * tileset.columnCount() + column
                result.tile = tileset.tileAt(tileId)
                ok = True

        return result, ok

    ##
    # Returns the global tile ID for the given \a cell. Returns 0 when the
    # cell is empty or when its tileset isn't known.
    ##
    def cellToGid(self, cell):
        if (cell.isEmpty()):
            return 0
        tileset = cell.tile.tileset()
        # Find the first GID for the tileset
        for item in self.mFirstGidToTileset:
            if item[1] == tileset:
                gid = item[0] + cell.tile.id()
                if (cell.flippedHorizontally):
                    gid |= FlippedHorizontallyFlag
                if (cell.flippedVertically):
                    gid |= FlippedVerticallyFlag
                if (cell.flippedAntiDiagonally):
                    gid |= FlippedAntiDiagonallyFlag
                return gid
        return 0

    ##
    # This sets the original tileset width. In case the image size has
    # changed, the tile indexes will be adjusted automatically when using
    # gidToCell().
    ##
    def setTilesetWidth(self, tileset, width):
        if (tileset.tileWidth() == 0):
            return
        self.mTilesetColumnCounts[tileset] = tileset.columnCountForWidth(width)

    ##
    # Encodes the tile layer data of the given \a tileLayer in the given
    # \a format. This function should only be used for base64 encoding, with or
    # without compression.
    ##
    def encodeLayerData(self, tileLayer, format):
        if format in [Map.LayerDataFormat.XML, Map.LayerDataFormat.CSV]:
            raise

        tileData = QByteArray()
        for y in range(tileLayer.height()):
            for x in range(tileLayer.width()):
                gid = self.cellToGid(tileLayer.cellAt(x, y))
                tileData.append(bytes([gid&0xff]))
                tileData.append(bytes([(gid >> 8)&0xff]))
                tileData.append(bytes([(gid >> 16)&0xff]))
                tileData.append(bytes([(gid >> 24)&0xff]))
                
        if len(tileData)%4 != 0:
            raise

        if (format == Map.LayerDataFormat.Base64Gzip):
            tileData = compress(tileData, CompressionMethod.Gzip)
        elif (format == Map.LayerDataFormat.Base64Zlib):
            tileData = compress(tileData, CompressionMethod.Zlib)

        return tileData.toBase64()

    def decodeLayerData(self, tileLayer, layerData, format):
        if format in [Map.LayerDataFormat.XML, Map.LayerDataFormat.CSV]:
            raise

        decodedData = QByteArray.fromBase64(layerData)
        size = (tileLayer.width() * tileLayer.height()) * 4

        if (format == Map.LayerDataFormat.Base64Gzip or format == Map.LayerDataFormat.Base64Zlib):
            decodedData, size = decompress(decodedData, size)

        if (size != decodedData.length()):
            return DecodeError.CorruptLayerData

        data = decodedData.data()
        x = 0
        y = 0

        for i in range(0, size - 3, 4):
            gid = data[i] | data[i + 1] << 8 | data[i + 2] << 16 | data[i + 3] << 24

            result, ok = self.gidToCell(gid)
            if (not ok):
                self.mInvalidTile = gid
                if self.isEmpty():
                    return DecodeError.TileButNoTilesets
                else:
                    return DecodeError.InvalidTile

            tileLayer.setCell(x, y, result)

            x += 1
            if (x == tileLayer.width()):
                x = 0
                y += 1

        return DecodeError.NoError
