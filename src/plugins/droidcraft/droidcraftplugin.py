##
# Droidcraft Tiled Plugin
# Copyrigpyt 2011, seeseekey <seeseekey@googlemail.com>
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
# this program. If not, see .
##

from compression import compress, decompress, CompressionMethod
from tilelayer import TileLayer, Cell
from tileset import Tileset
from map import Map
from mapformat import MapFormat
from PyQt5.QtCore import (
    QFileInfo,
    QIODevice,
    QFile,
    QByteArray
)
from PyQt5.QtGui import (
    QImage
)
class DroidcraftPlugin(MapFormat):
    def __init__(self):
        super().__init__()
        
        self.mError = ''

    # MapReaderInterface
    # Reader
    def read(self, fileName):
        uncompressed = QByteArray()
        # Read data
        f = QFile(fileName)
        if (f.open(QIODevice.ReadOnly)) :
            compressed = f.readAll()
            f.close()
            uncompressed = decompress(compressed, 48 * 48)
        
        # Check the data
        if (uncompressed.count() != 48 * 48) :
            self.mError = self.tr("This is not a valid Droidcraft map file!")
            return 0
        
        # Build 48 x 48 map
        # Create a Map -> Create a Tileset -> Add Tileset to map
        # -> Create a TileLayer -> Fill layer -> Add TileLayer to Map
        map = Map(Map.Orthogonal, 48, 48, 32, 32)
        mapTileset = Tileset("tileset", 32, 32)
        mapTileset.loadFromImage(QImage(":/tileset.png"), "tileset.png")
        map.addTileset(mapTileset)
        # Fill layer
        mapLayer =  TileLayer("map", 0, 0, 48, 48)
        # Load
        for i in range(0, 48 * 48):
            tileFile = uncompressed.at(i)
            y = i / 48
            x = i - (48 * y)
            tile = mapTileset.tileAt(tileFile)
            mapLayer.setCell(x, y, Cell(tile))
        
        map.addLayer(mapLayer)
        return map
    def supportsFile(self, fileName):
        return QFileInfo(fileName).suffix() == "dat"
    
    # MapWriterInterface
    # Writer
    def write(self, map, fileName):
        # Check layer count and type
        if (map.layerCount() != 1 or not map.layerAt(0).isTileLayer()) :
            self.mError = self.tr("The map needs to have exactly one tile layer!")
            return False
        
        mapLayer = map.layerAt(0).asTileLayer()
        # Check layer size
        if (mapLayer.width() != 48 or mapLayer.height() != 48) :
            self.mError = self.tr("The layer must have a size of 48 x 48 tiles!")
            return False
        
        # Create QByteArray and compress it
        uncompressed = QByteArray(48 * 48, 0)
        width = mapLayer.width()
        height = mapLayer.height()
        for y in range(0, height):
            for x in range(0, width):
                tile = mapLayer.cellAt(x, y).tile
                if tile:
                    uncompressed[y * width + x] = tile.id()&0xff

        compressed = compress(uncompressed, CompressionMethod.Gzip)
        # Write QByteArray
        file = QFile(fileName)
        if (not file.open(QIODevice.WriteOnly)) :
            self.mError = self.tr("Could not open file for writing.")
            return False
        
        file.write(compressed)
        file.close()
        return True
    
    def nameFilter(self):
        return self.tr("Droidcraft map files (*.dat)")
    
    def errorString(self):
        return self.mError
