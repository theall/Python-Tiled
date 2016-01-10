##
# Lua Tiled Plugin
# Copyright 2011, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from layer import Layer
from mapobject import MapObject
from gidmapper import GidMapper
from map import Map, orientationToString, staggerAxisToString, staggerIndexToString, renderOrderToString
from lua.luatablewriter import LuaTableWriter
from mapformat import WritableMapFormat
from pyqtcore import (
    QString
)
from PyQt5.QtCore import (
    QFile,
    QSaveFile,
    QFileInfo,
    QByteArray, 
    QCoreApplication,
    QIODevice,
    QDir
)

POLYGON_FORMAT_FULL = True
POLYGON_FORMAT_PAIRS = False
POLYGON_FORMAT_OPTIMAL = False

##
# This plugin allows exporting maps as Lua files.
##
class LuaPlugin(WritableMapFormat):
    def __init__(self):
        super().__init__()

        self.mMapDir = QDir()
        self.mError = ''
        self.mGidMapper = GidMapper()

    # MapWriterInterface
    def write(self, map, fileName):
        file = QSaveFile(fileName)
        if (not file.open(QIODevice.WriteOnly | QIODevice.Text)) :
            self.mError = self.tr("Could not open file for writing.")
            return False
        
        self.mMapDir = QDir(QFileInfo(fileName).path())
        writer = LuaTableWriter(file)
        writer.writeStartDocument()
        self.writeMap(writer, map)
        writer.writeEndDocument()
        if (file.error() != QFile.NoError) :
            self.mError = file.errorString()
            return False
        
        if (not file.commit()) :
            self.mError = file.errorString()
            return False
        return True
    
    def nameFilter(self):
        return self.tr("Lua files (*.lua)")
    
    def errorString(self):
        return self.mError

    def writeMap(self, writer, map):
        writer.writeStartReturnTable()
        writer.writeKeyAndValue("version", "1.1")
        writer.writeKeyAndValue("luaversion", "5.1")
        writer.writeKeyAndValue("tiledversion", QCoreApplication.applicationVersion())
        orientation = orientationToString(map.orientation())
        renderOrder = renderOrderToString(map.renderOrder())
        writer.writeKeyAndValue("orientation", orientation)
        writer.writeKeyAndValue("renderorder", renderOrder)
        writer.writeKeyAndValue("width", map.width())
        writer.writeKeyAndValue("height", map.height())
        writer.writeKeyAndValue("tilewidth", map.tileWidth())
        writer.writeKeyAndValue("tileheight", map.tileHeight())
        writer.writeKeyAndValue("nextobjectid", map.nextObjectId())
        if (map.orientation() == Map.Orientation.Hexagonal):
            writer.writeKeyAndValue("hexsidelength", map.hexSideLength())
        if (map.orientation() == Map.Orientation.Staggered or map.orientation() == Map.Orientation.Hexagonal) :
            writer.writeKeyAndValue("staggeraxis", staggerAxisToString(map.staggerAxis()))
            writer.writeKeyAndValue("staggerindex", staggerIndexToString(map.staggerIndex()))
        
        backgroundColor = map.backgroundColor()
        if (backgroundColor.isValid()) :
            # Example: backgroundcolor = { 255, 200, 100 }
            writer.writeStartTable("backgroundcolor")
            writer.setSuppressNewlines(True)
            writer.writeValue(backgroundColor.red())
            writer.writeValue(backgroundColor.green())
            writer.writeValue(backgroundColor.blue())
            if (backgroundColor.alpha() != 255):
                writer.writeValue(backgroundColor.alpha())
            writer.writeEndTable()
            writer.setSuppressNewlines(False)
        
        self.writeProperties(writer, map.properties())
        writer.writeStartTable("tilesets")
        self.mGidMapper.clear()
        firstGid = 1
        for tileset in map.tilesets():
            self.writeTileset(writer, tileset, firstGid)
            self.mGidMapper.insert(firstGid, tileset)
            firstGid += tileset.tileCount()
        
        writer.writeEndTable()
        writer.writeStartTable("layers")
        for layer in map.layers():
            x = layer.layerType()
            if x==Layer.TileLayerType:
                self.writeTileLayer(writer, layer, map.layerDataFormat())
            elif x==Layer.ObjectGroupType:
                self.writeObjectGroup(writer, layer)
            elif x==Layer.ImageLayerType:
                self.writeImageLayer(writer, layer)

        writer.writeEndTable()
        writer.writeEndTable()
    
    def writeProperties(self, writer, properties):
        writer.writeStartTable("properties")
        for it in properties:
            writer.writeQuotedKeyAndValue(it[0], it[1])
        writer.writeEndTable()

    def writeTileset(self, writer, tileset, firstGid):
        writer.writeStartTable()
        writer.writeKeyAndValue("name", tileset.name())
        writer.writeKeyAndValue("firstgid", firstGid)
        if tileset.fileName() != '':
            rel = self.mMapDir.relativeFilePath(tileset.fileName())
            writer.writeKeyAndValue("filename", rel)
        
        ## 
        # Include all tileset information even for external tilesets, since the
        # external reference is generally a .tsx file (in XML format).
        ##
        writer.writeKeyAndValue("tilewidth", tileset.tileWidth())
        writer.writeKeyAndValue("tileheight", tileset.tileHeight())
        writer.writeKeyAndValue("spacing", tileset.tileSpacing())
        writer.writeKeyAndValue("margin", tileset.margin())
        if tileset.imageSource() != '':
            rel = self.mMapDir.relativeFilePath(tileset.imageSource())
            writer.writeKeyAndValue("image", rel)
            writer.writeKeyAndValue("imagewidth", tileset.imageWidth())
            writer.writeKeyAndValue("imageheight", tileset.imageHeight())
        
        if (tileset.transparentColor().isValid()):
            writer.writeKeyAndValue("transparentcolor",tileset.transparentColor().name())

        offset = tileset.tileOffset()
        writer.writeStartTable("tileoffset")
        writer.writeKeyAndValue("x", offset.x())
        writer.writeKeyAndValue("y", offset.y())
        writer.writeEndTable()
        self.writeProperties(writer, tileset.properties())
        writer.writeStartTable("terrains")
        for i in range(tileset.terrainCount()):
            t = tileset.terrain(i)
            writer.writeStartTable()
            writer.writeKeyAndValue("name", t.name())
            writer.writeKeyAndValue("tile", t.imageTileId())
            self.writeProperties(writer, t.properties())
            writer.writeEndTable()

        writer.writeEndTable()
        writer.writeKeyAndValue("tilecount", tileset.tileCount())
        writer.writeStartTable("tiles")
        for i in range(0, tileset.tileCount()):
            tile = tileset.tileAt(i)
            # For brevity only write tiles with interesting properties
            if (not includeTile(tile)):
                continue
            writer.writeStartTable()
            writer.writeKeyAndValue("id", i)
            if (not tile.properties().isEmpty()):
                self.writeProperties(writer, tile.properties())
            if tile.imageSource() != '':
                src = self.mMapDir.relativeFilePath(tile.imageSource())
                tileSize = tile.size()
                writer.writeKeyAndValue("image", src)
                if (not tileSize.isNull()) :
                    writer.writeKeyAndValue("width", tileSize.width())
                    writer.writeKeyAndValue("height", tileSize.height())

            terrain = tile.terrain()
            if (terrain != 0xFFFFFFFF) :
                writer.writeStartTable("terrain")
                writer.setSuppressNewlines(True)
                for i in range(0, 4):
                    writer.writeValue(tile.cornerTerrainId(i))
                writer.writeEndTable()
                writer.setSuppressNewlines(False)
            
            if (tile.probability() != 1.0):
                writer.writeKeyAndValue("probability", tile.probability())
            objectGroup = tile.objectGroup()
            if objectGroup:
                self.writeObjectGroup(writer, objectGroup, "objectGroup")
            if (tile.isAnimated()) :
                frames = tile.frames()
                writer.writeStartTable("animation")
                for frame in frames:
                    writer.writeStartTable()
                    writer.writeKeyAndValue("tileid", QString.number(frame.tileId))
                    writer.writeKeyAndValue("duration", QString.number(frame.duration))
                    writer.writeEndTable()
                
                writer.writeEndTable() # animation
            
            writer.writeEndTable() # tile
        
        writer.writeEndTable() # tiles
        writer.writeEndTable() # tileset
    
    def writeTileLayer(self, writer, tileLayer, format):
        writer.writeStartTable()
        writer.writeKeyAndValue("type", "tilelayer")
        writer.writeKeyAndValue("name", tileLayer.name())
        writer.writeKeyAndValue("x", tileLayer.x())
        writer.writeKeyAndValue("y", tileLayer.y())
        writer.writeKeyAndValue("width", tileLayer.width())
        writer.writeKeyAndValue("height", tileLayer.height())
        writer.writeKeyAndValue("visible", tileLayer.isVisible())
        writer.writeKeyAndValue("opacity", tileLayer.opacity())
        offset = tileLayer.offset()
        writer.writeKeyAndValue("offsetx", offset.x())
        writer.writeKeyAndValue("offsety", offset.y())

        if format==Map.LayerDataFormat.XML or format==Map.LayerDataFormat.CSV:
            self.writeProperties(writer, tileLayer.properties())
            writer.writeKeyAndValue("encoding", "lua")
            writer.writeStartTable("data")
            for y in range(0, tileLayer.height()):
                if (y > 0):
                    writer.prepareNewLine()
                for x in range(0, tileLayer.width()):
                    writer.writeValue(self.mGidMapper.cellToGid(tileLayer.cellAt(x, y)))
        elif format==Map.LayerDataFormat.Base64 \
            or format==Map.LayerDataFormat.Base64Zlib \
            or format==Map.LayerDataFormat.Base64Gzip:
            writer.writeKeyAndValue("encoding", "base64")

            if format == Map.LayerDataFormat.Base64Zlib:
                writer.writeKeyAndValue("compression", "zlib")
            elif format == Map.LayerDataFormat.Base64Gzip:
                writer.writeKeyAndValue("compression", "gzip")

            layerData = self.mGidMapper.encodeLayerData(tileLayer, format)
            writer.writeKeyAndValue("data", layerData)

        writer.writeEndTable()
        writer.writeEndTable()
    
    def writeObjectGroup(self, writer, objectGroup, key=QByteArray()):
        if key=='':
            writer.writeStartTable()
        else:
            writer.writeStartTable(key)
        writer.writeKeyAndValue("type", "objectgroup")
        writer.writeKeyAndValue("name", objectGroup.name())
        writer.writeKeyAndValue("visible", objectGroup.isVisible())
        writer.writeKeyAndValue("opacity", objectGroup.opacity())
        
        offset = objectGroup.offset()
        writer.writeKeyAndValue("offsetx", offset.x())
        writer.writeKeyAndValue("offsety", offset.y())

        self.writeProperties(writer, objectGroup.properties())
        writer.writeStartTable("objects")
        for mapObject in objectGroup.objects():
            self.writeMapObject(writer, mapObject)
        writer.writeEndTable()
        writer.writeEndTable()
    
    def writeImageLayer(self, writer, imageLayer):
        writer.writeStartTable()
        writer.writeKeyAndValue("type", "imagelayer")
        writer.writeKeyAndValue("name", imageLayer.name())
        writer.writeKeyAndValue("x", imageLayer.x())
        writer.writeKeyAndValue("y", imageLayer.y())
        writer.writeKeyAndValue("visible", imageLayer.isVisible())
        writer.writeKeyAndValue("opacity", imageLayer.opacity())
        rel = self.mMapDir.relativeFilePath(imageLayer.imageSource())
        writer.writeKeyAndValue("image", rel)
        if (imageLayer.transparentColor().isValid()) :
            writer.writeKeyAndValue("transparentcolor",
                                    imageLayer.transparentColor().name())
        
        self.writeProperties(writer, imageLayer.properties())
        writer.writeEndTable()
    
    def writeMapObject(self, writer, mapObject):
        writer.writeStartTable()
        writer.writeKeyAndValue("id", mapObject.id())
        writer.writeKeyAndValue("name", mapObject.name())
        writer.writeKeyAndValue("type", mapObject.type())
        writer.writeKeyAndValue("shape", toString(mapObject.shape()))
        writer.writeKeyAndValue("x", mapObject.x())
        writer.writeKeyAndValue("y", mapObject.y())
        writer.writeKeyAndValue("width", mapObject.width())
        writer.writeKeyAndValue("height", mapObject.height())
        writer.writeKeyAndValue("rotation", mapObject.rotation())
        if (not mapObject.cell().isEmpty()):
            writer.writeKeyAndValue("gid", self.mGidMapper.cellToGid(mapObject.cell()))
        writer.writeKeyAndValue("visible", mapObject.isVisible())
        polygon = mapObject.polygon()
        if (not polygon.isEmpty()) :
            if (mapObject.shape() == MapObject.Polygon):
                writer.writeStartTable("polygon")
            else:
                writer.writeStartTable("polyline")
    #if defined(POLYGON_FORMAT_FULL)
            ## This format is the easiest to read and understand:
            #
            #  :
            #    { x = 1, y = 1 },
            #    { x = 2, y = 2 },
            #    { x = 3, y = 3 },
            #    ...
            #  }
            ##
            for point in polygon:
                writer.writeStartTable()
                writer.setSuppressNewlines(True)
                writer.writeKeyAndValue("x", point.x())
                writer.writeKeyAndValue("y", point.y())
                writer.writeEndTable()
                writer.setSuppressNewlines(False)
            
    #elif defined(POLYGON_FORMAT_PAIRS)
            ## This is an alternative that takes about 25% less memory.
            #
            #  :
            #    { 1, 1 },
            #    { 2, 2 },
            #    { 3, 3 },
            #    ...
            #  }
            ##
            for point in polygon:
                writer.writeStartTable()
                writer.setSuppressNewlines(True)
                writer.writeValue(point.x())
                writer.writeValue(point.y())
                writer.writeEndTable()
                writer.setSuppressNewlines(False)
            
    #elif defined(POLYGON_FORMAT_OPTIMAL)
            ## Writing it out in two tables, one for the x coordinates and one for
            # the y coordinates. It is a compromise between code readability and # performance. This takes the least amount of memory (60% less than
            # the first approach).
            #
            # x = { 1, 2, 3, ... }
            # y = { 1, 2, 3, ... }
            ##
            writer.writeStartTable("x")
            writer.setSuppressNewlines(True)
            for point in polygon:
                writer.writeValue(point.x())
            writer.writeEndTable()
            writer.setSuppressNewlines(False)
            writer.writeStartTable("y")
            writer.setSuppressNewlines(True)
            for point in polygon:
                writer.writeValue(point.y())
            writer.writeEndTable()
            writer.setSuppressNewlines(False)
    #endif
            writer.writeEndTable()
        
        self.writeProperties(writer, mapObject.properties())
        writer.writeEndTable()

def includeTile(tile):
    if (not tile.properties().isEmpty()):
        return True
    if tile.imageSource() != '':
        return True
    if (tile.objectGroup()):
        return True
    if (tile.isAnimated()):
        return True
    if (tile.terrain() != 0xFFFFFFFF):
        return True
    if (tile.probability() != 1.0):
        return True
    return False

def toString(shape):
    x = shape
    if x==MapObject.Rectangle:
        return "rectangle"
    elif x==MapObject.Polygon:
        return "polygon"
    elif x==MapObject.Polyline:
        return "polyline"
    elif x==MapObject.Ellipse:
        return "ellipse"
    
    return "unknown"
