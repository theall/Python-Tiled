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


from tileset import tileset
from tilelayer import tilelayer
from tile import tile
from terrain import terrain
from properties import properties
from objectgroup import objectgroup
from mapobject import mapobject
from map import Map
from imagelayer import imagelayer
from luatablewriter import luatablewriter
from mapwriterinterface import MapWriterInterface
from gidmapper import GidMapper
from lua_global import lua_global
from pyqtcore import (
    QuotedKeyAndValue,
    QVector,
    QString
)
from PyQt5.QtCore import (
    QFile,
    QPointF,
    QSaveFile,
    QFileInfo,
    QSize,
    QCoreApplication,
    QObject,
    QByteArray,
    QIODevice,
    QPoint,
    QDir
)
from PyQt5.QtGui import (
    QPolygonF,
    QColor
)
##
# This plugin allows exporting maps as Lua files.
##
class LuaPlugin(QObject, MapWriterInterface):
    def __init__(self):
        self.mMapDir = QDir()
        self.mError = QString()
        self.mGidMapper = super().GidMapper()

    # MapWriterInterface
    def write(self, map, fileName):
    #ifdef HAS_QSAVEFILE_SUPPORT
        fil = QSaveFile(efileName)
    #else
        fil = QFile(efileName)
    #endif
        if (not file.open(QIODevice.WriteOnly | QIODevice.Text)) :
            self.mError = tr("Could not open file for writing.")
            return false
        
        self.mMapDir = QFileInfo(fileName).path()
        write = LuaTableWriter(r&file)
        writer.writeStartDocument()
        self.writeMap(writer, map)
        writer.writeEndDocument()
        if (file.error() != QFile.NoError) :
            self.mError = file.errorString()
            return false
        
    #ifdef HAS_QSAVEFILE_SUPPORT
        if (not file.commit()) :
            self.mError = file.errorString()
            return false
        
    #endif
        return true
    
    def nameFilter(self):
        return tr("Lua files (*.lua)")
    
    def errorString(self):
        return self.mError

    def writeMap(self, writer, arg2):
        writer.writeStartReturnTable()
        writer.writeKeyAndValue("version", "1.1")
        writer.writeKeyAndValue("luaversion", "5.1")
        writer.writeKeyAndValue("tiledversion", QCoreApplication.applicationVersion())
        orientation = orientationToString(map.orientation())
        writer.writeKeyAndValue("orientation", orientation)
        writer.writeKeyAndValue("width", map.width())
        writer.writeKeyAndValue("height", map.height())
        writer.writeKeyAndValue("tilewidth", map.tileWidth())
        writer.writeKeyAndValue("tileheight", map.tileHeight())
        writer.writeKeyAndValue("nextobjectid", map.nextObjectId())
        if (map.orientation() == Map.Hexagonal):
            writer.writeKeyAndValue("hexsidelength", map.hexSideLength())
        if (map.orientation() == Map.Staggered or map.orientation() == Map.Hexagonal) :
            writer.writeKeyAndValue("staggeraxis",
                                    staggerAxisToString(map.staggerAxis()))
            writer.writeKeyAndValue("staggerindex",
                                    staggerIndexToString(map.staggerIndex()))
        
        backgroundColor = map.backgroundColor()
        if (backgroundColor.isValid()) :
            # Example: backgroundcolor = { 255, 200, 100 }
            writer.writeStartTable("backgroundcolor")
            writer.setSuppressNewlines(true)
            writer.writeValue(backgroundColor.red())
            writer.writeValue(backgroundColor.green())
            writer.writeValue(backgroundColor.blue())
            if (backgroundColor.alpha() != 255):
                writer.writeValue(backgroundColor.alpha())
            writer.writeEndTable()
            writer.setSuppressNewlines(false)
        
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
            if False:
                pass
            elif x==Layer.TileLayerType:
                self.writeTileLayer(writer, static_cast(layer))
                break
            elif x==Layer.ObjectGroupType:
                self.writeObjectGroup(writer, static_cast(layer))
                break
            elif x==Layer.ImageLayerType:
                self.writeImageLayer(writer, static_cast(layer))
                break

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
        if (not tileset.fileName().isEmpty()) :
            rel = self.mMapDir.relativeFilePath(tileset.fileName())
            writer.writeKeyAndValue("filename", rel)
        
        ## Include all tileset information even for external tilesets, since the
        # external reference is generally a .tsx file (in XML format).
        ##
        writer.writeKeyAndValue("tilewidth", tileset.tileWidth())
        writer.writeKeyAndValue("tileheight", tileset.tileHeight())
        writer.writeKeyAndValue("spacing", tileset.tileSpacing())
        writer.writeKeyAndValue("margin", tileset.margin())
        if (not tileset.imageSource().isEmpty()) :
            rel = self.mMapDir.relativeFilePath(tileset.imageSource())
            writer.writeKeyAndValue("image", rel)
            writer.writeKeyAndValue("imagewidth", tileset.imageWidth())
            writer.writeKeyAndValue("imageheight", tileset.imageHeight())
        
        if (tileset.transparentColor().isValid()) :
            writer.writeKeyAndValue("transparentcolor",
                                    tileset.transparentColor().name())
        
        offset = tileset.tileOffset()
        writer.writeStartTable("tileoffset")
        writer.writeKeyAndValue("x", offset.x())
        writer.writeKeyAndValue("y", offset.y())
        writer.writeEndTable()
        self.writeProperties(writer, tileset.properties())
        writer.writeStartTable("terrains")
        for i in range(0, tileset.terrainCount()):
            t = tileset.terrain(i)
            writer.writeStartTable()
            writer.writeKeyAndValue("name", t.name())
            writer.writeKeyAndValue("tile", t.imageTileId())
            self.writeProperties(writer, t.properties())
            writer.writeEndTable()
        
        writer.writeEndTable()
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
            if (not tile.imageSource().isEmpty()) :
                src = self.mMapDir.relativeFilePath(tile.imageSource())
                tileSize = tile.size()
                writer.writeKeyAndValue("image", src)
                if (not tileSize.isNull()) :
                    writer.writeKeyAndValue("width", tileSize.width())
                    writer.writeKeyAndValue("height", tileSize.height())

            terrain = tile.terrain()
            if (terrain != 0xFFFFFFFF) :
                writer.writeStartTable("terrain")
                writer.setSuppressNewlines(true)
                for i in range(0, 4):
                    writer.writeValue(tile.cornerTerrainId(i))
                writer.writeEndTable()
                writer.setSuppressNewlines(false)
            
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
                
                writer.writeEndTable(); # animation
            
            writer.writeEndTable(); # tile
        
        writer.writeEndTable(); # tiles
        writer.writeEndTable(); # tileset
    
    def writeTileLayer(self, writer, tileLayer):
        writer.writeStartTable()
        writer.writeKeyAndValue("type", "tilelayer")
        writer.writeKeyAndValue("name", tileLayer.name())
        writer.writeKeyAndValue("x", tileLayer.x())
        writer.writeKeyAndValue("y", tileLayer.y())
        writer.writeKeyAndValue("width", tileLayer.width())
        writer.writeKeyAndValue("height", tileLayer.height())
        writer.writeKeyAndValue("visible", tileLayer.isVisible())
        writer.writeKeyAndValue("opacity", tileLayer.opacity())
        self.writeProperties(writer, tileLayer.properties())
        writer.writeKeyAndValue("encoding", "lua")
        writer.writeStartTable("data")
        for y in range(0, tileLayer.height()):
            if (y > 0):
                writer.prepareNewLine()
            for x in range(0, tileLayer.width()):
                writer.writeValue(self.mGidMapper.cellToGid(tileLayer.cellAt(x, y)))
        
        writer.writeEndTable()
        writer.writeEndTable()
    
    def writeObjectGroup(self, ):
        if (key.isEmpty()):
            writer.writeStartTable()
        else:
            writer.writeStartTable(key)
        writer.writeKeyAndValue("type", "objectgroup")
        writer.writeKeyAndValue("name", objectGroup.name())
        writer.writeKeyAndValue("visible", objectGroup.isVisible())
        writer.writeKeyAndValue("opacity", objectGroup.opacity())
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
                writer.setSuppressNewlines(true)
                writer.writeKeyAndValue("x", point.x())
                writer.writeKeyAndValue("y", point.y())
                writer.writeEndTable()
                writer.setSuppressNewlines(false)
            
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
                writer.setSuppressNewlines(true)
                writer.writeValue(point.x())
                writer.writeValue(point.y())
                writer.writeEndTable()
                writer.setSuppressNewlines(false)
            
    #elif defined(POLYGON_FORMAT_OPTIMAL)
            ## Writing it out in two tables, one for the x coordinates and one for
            # the y coordinates. It is a compromise between code readability and # performance. This takes the least amount of memory (60% less than
            # the first approach).
            #
            # x = { 1, 2, 3, ... }
            # y = { 1, 2, 3, ... }
            ##
            writer.writeStartTable("x")
            writer.setSuppressNewlines(true)
            for point in polygon:
                writer.writeValue(point.x())
            writer.writeEndTable()
            writer.setSuppressNewlines(false)
            writer.writeStartTable("y")
            writer.setSuppressNewlines(true)
            for point in polygon:
                writer.writeValue(point.y())
            writer.writeEndTable()
            writer.setSuppressNewlines(false)
    #endif
            writer.writeEndTable()
        
        self.writeProperties(writer, mapObject.properties())
        writer.writeEndTable()

def includeTile(tile):
    if (not tile.properties().isEmpty()):
        return true
    if (not tile.imageSource().isEmpty()):
        return true
    if (tile.objectGroup()):
        return true
    if (tile.isAnimated()):
        return true
    if (tile.terrain() != 0xFFFFFFFF):
        return true
    if (tile.terrainProbability() != 1.0):
        return true
    return false

def toString(shape):
    x = shape
    if False:
        pass
    elif x==MapObject.Rectangle:
        return "rectangle"
    elif x==MapObject.Polygon:
        return "polygon"
    elif x==MapObject.Polyline:
        return "polyline"
    elif x==MapObject.Ellipse:
        return "ellipse"
    
    return "unknown"
