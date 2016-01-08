##
# Replica Island Tiled Plugin
# Copyright 2011, Eric Kidd <eric@kiddsoftware.com>
# Copyright 2011, seeseekey <seeseekey@googlemail.com>
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

from tiled_global import Int2
from tilelayer import TileLayer, Cell
from tileset import Tileset
from mapformat import MapFormat
from map import Map
from pyqtcore import (
    QList,
    QString
)
from PyQt5.QtCore import (
    QByteArray,
    QDataStream,
    QFileInfo,
    QFile,
    QTemporaryFile,
    QIODevice
)
from PyQt5.QtGui import (
    QImage
)
##
# Read and write maps in Replica Island format.  Replica Island is an
# open source side-scrolling video game for Android.
##
class ReplicaIslandPlugin(MapFormat):

    ##
    # Create an instance of the plugin.
    ##
    def __init__(self):
        super().__init__()
        
        self.mError = ''

    # MapReaderInterface
    def read(self, fileName):
        # Read data.
        file = QFile(fileName)
        if (not file.open(QIODevice.ReadOnly)):
            self.mError = self.tr("Cannot open Replica Island map file!")
            return 0
        
        _in = QDataStream(file)
        _in.setByteOrder(QDataStream.LittleEndian)
        _in.setFloatingPointPrecision(QDataStream.SinglePrecision)
        # Parse file header.
        mapSignature = _in.readUInt8()
        layerCount = _in.readUInt8()
        backgroundIndex = _in.readUInt8()
        if (_in.status() == QDataStream.ReadPastEnd or mapSignature != 96):
            self.mError = self.tr("Can't parse file header!")
            return 0
        
        # Create our map, setting width and height to 0 until we load a layer.
        map = Map(Map.Orthogonal, 0, 0, 32, 32)
        map.setProperty("background_index", QString.number(backgroundIndex))
        # Load our Tilesets.
        typeTilesets = QList()
        tileIndexTilesets = QList()
        
        self.loadTilesetsFromResources(map, typeTilesets, tileIndexTilesets)
        # Load each of our layers.
        for i in range(layerCount):
            # Parse layer header.
            _type = _in.readUInt8()
            tileIndex = _in.readUInt8()
            scrollSpeed = _in.readFloat()
            levelSignature = _in.readUInt8()
            width = _in.readUInt32()
            height = _in.readUInt32()
            if (_in.status() == QDataStream.ReadPastEnd or levelSignature != 42):
                self.mError = self.tr("Can't parse layer header!")
                return 0
            
            # Make sure our width and height are consistent.
            if (map.width() == 0):
                map.setWidth(width)
            if (map.height() == 0):
                map.setHeight(height)
            if (map.width() != width or map.height() != height):
                self.mError = self.tr("Inconsistent layer sizes!")
                return 0
            
            # Create a layer object.
            layer = TileLayer(self.layerTypeToName(_type), 0, 0, width, height)
            layer.setProperty("type", QString.number(_type))
            layer.setProperty("tile_index", QString.number(tileIndex))
            layer.setProperty("scroll_speed", QString.number(scrollSpeed, 'f'))
            map.addLayer(layer)
            # Look up the tileset for this layer.
            tileset = self.tilesetForLayer(_type, tileIndex, typeTilesets, tileIndexTilesets)
            # Read our tile data all at once.
            tileData = QByteArray(width*height, '\0')
            bytesRead = _in.readRawData(tileData.data(), tileData.size())
            if (bytesRead != tileData.size()):
                self.mError = self.tr("File ended in middle of layer!")
                return 0
            
            tp = tileData.data()&0xff
            # Add the tiles to our layer.
            for y in range(0, height):
                for x in range(0, width):
                    tile_id = tp
                    tp += 1
                    if (tile_id != 255):
                        tile = tileset.tileAt(tile_id)
                        layer.setCell(x, y, Cell(tile))

        # Make sure we read the entire *.bin file.
        if (_in.status() != QDataStream.Ok or not _in.atEnd()):
            self.mError = self.tr("Unexpected data at end of file!")
            return 0
        
        return map

    def tilesetForLayer(self, _type, tileIndex, typeTilesets, tileIndexTilesets):
        if (_type == 0):
            return tileIndexTilesets[tileIndex]
        else:
            return typeTilesets[_type]
        
    def nameFilter(self):
        return self.tr("Replica Island map files (*.bin)")
    
    def supportsFile(self, fileName):
        # Check the file extension first.
        if (QFileInfo(fileName).suffix() != "bin"):
            return False
        # Since we may have lots of Android-related *.bin files that aren't
        # maps, check our signature byte, too.
        f = QFile(fileName)
        if (not f.open(QIODevice.ReadOnly)):
            return False
        read = 1
        signature = f.read(1)
        return (read == 1 or signature == 96)
    
    def errorString(self):
        return self.mError
    
    # MapWriterInterface
    def write(self, map, fileName):
        # Open up a temporary file for saving the level.
        temp = QTemporaryFile()
        if (not temp.open()):
            self.mError = self.tr("Cannot open temporary file for writing!")
            return False
        
        # Create an output stream for serializing data.
        out = QDataStream(temp)
        out.setByteOrder(QDataStream.LittleEndian)
        out.setFloatingPointPrecision(QDataStream.SinglePrecision)
        # Write out the signature and file header.
        out.write(96) # Signature.
        out.write(map.layerCount())
        ok = False
        x, ok = Int2(map.property("background_index"))
        if (not ok):
            self.mError = self.tr("You must define a background_index property on the map!")
            return False
        out.write(x)
        # Write out each layer.
        for i in range(0, map.layerCount()):
            layer = map.layerAt(i).asTileLayer()
            if (not layer):
                self.mError = self.tr("Can't save non-tile layer!")
                return False
            
            if (not self.writeLayer(out, layer)):
                return False
        
        # Overwrite our destination file with our temporary file.  We only
        # do this once we know we've saved a valid map.
        temp.close()
        QFile.remove(fileName)
        if (not QFile.copy(temp.fileName(), fileName)):
            self.mError = self.tr("Couldn't overwrite old version; may be deleted!")
            return False
        
        return True


    # MapReaderInterface support.
    def loadTilesetsFromResources(self, map, typeTilesets, tileIndexTilesets):
        # Create tilesets for _type 0 to 3, inclusive.
        typeTilesets.append(None); # Use a tileIndexTileset.
        typeTilesets.append(self.loadTilesetFromResource("collision_map"))
        typeTilesets.append(self.loadTilesetFromResource("objects"))
        typeTilesets.append(self.loadTilesetFromResource("hotspots"))
        self.addTilesetsToMap(map, typeTilesets)
        # Create tilesets for tileIndex 0 to 7, inclusive.
        tileIndexTilesets.append(self.loadTilesetFromResource("grass"))
        tileIndexTilesets.append(self.loadTilesetFromResource("island"))
        tileIndexTilesets.append(self.loadTilesetFromResource("sewage"))
        tileIndexTilesets.append(self.loadTilesetFromResource("cave"))
        tileIndexTilesets.append(self.loadTilesetFromResource("lab"))
        # The titletileset is also known as "lighting".
        tileIndexTilesets.append(self.loadTilesetFromResource("titletileset"))
        tileIndexTilesets.append(self.loadTilesetFromResource("tutorial"))
        self.addTilesetsToMap(map, tileIndexTilesets)
    
    def loadTilesetFromResource(self, name):
        tileset = Tileset(name, 32, 32)
        tileset.loadFromImage(QImage(":/" + name + ".png"), name + ".png")
        return tileset
    
    def addTilesetsToMap(self, map, tilesets):
        for i in tilesets:
            if i:
                map.addTileset(i)
    
    def layerTypeToName(self, _type):
        x = _type
        if False:
            pass
        elif x==0: return "Background"
        elif x==1: return "Collision"
        elif x==2: return "Objects"
        elif x==3: return "Hot spots"
        else:
            return "Unknown layer _type"

    # MapWriterInterface support.
    # Write out a map layer.
    def writeLayer(self, out, layer):
        # Write out the layer header.
        x, ok = Int2(layer.property("type"))
        if (not ok):
            self.mError = self.tr("You must define a _type property on each layer!")
            return False
        out.write(x)
        
        x, ok = Int2(layer.property("tile_index"))
        if (not ok):
            self.mError = self.tr("You must define a tile_index property on each layer!")
            return False
        out.write(x)
        
        x, ok = Int2(layer.property("scroll_speed"))
        if (not ok):
            self.mError = self.tr("You must define a scroll_speed property on each layer!")
            return False
        out.write(x)
        
        out.write(42); # Layer signature.
        out.write(layer.width())
        out.write(layer.height())
        # Write out the raw tile data.  We assume that the user has used the
        # correct tileset for this layer.
        for y in range(0, layer.height()):
            for x in range(0, layer.width()):
                tile = layer.cellAt(x, y).tile
                if (tile):
                    out.write(tile.id())
                else:
                    out.write(255)

        return True
