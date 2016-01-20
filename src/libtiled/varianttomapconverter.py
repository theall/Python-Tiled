##
# varianttomapconverter.py
# Copyright 2011, Porfírio José Pereira Ribeiro <porfirioribeiro@gmail.com>
# Copyright 2011-2015, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from tile import Frame
from tileset import Tileset
from tilesetformat import readTileset
from tilelayer import TileLayer
from gidmapper import GidMapper, DecodeError
from properties import Properties
from objectgroup import ObjectGroup, drawOrderFromString
from mapobject import MapObject
from map import (
    Map, 
    orientationFromString, 
    staggerAxisFromString, 
    staggerIndexFromString, 
    renderOrderFromString
)
from imagelayer import ImageLayer
from tiled_global import Int, Int2, Float2
from pyqtcore import (
    QVector
)
from PyQt5.QtCore import (
    QPoint,
    QCoreApplication,
    QPointF,
    QDir,
    QByteArray, 
    QSizeF
)
from PyQt5.QtGui import (
    QPixmap,
    QPolygonF,
    QColor,
    QImage
)
def resolvePath(dir, variant):
    fileName = variant
    if (QDir.isRelativePath(fileName)):
        fileName = QDir.cleanPath(dir.absoluteFilePath(fileName))
    return fileName

##
# Converts a QVariant to a Map instance. Meant to be used together with
# JsonReader.
##
class VariantToMapConverter():

    def __init__(self):
        self.mError = ''
        self.mGidMapper = GidMapper()
        self.mMap = None
        self.mMapDir = QDir()
        self.mReadingExternalTileset = False

    # Using the MapReader context since the messages are the same
    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('MapReader', sourceText, disambiguation, n)

    def trUtf8(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('MapReader', sourceText, disambiguation, n)
        
    ##
    # Tries to convert the given \a variant to a Map instance. The \a mapDir
    # is necessary to resolve any relative references to external images.
    #
    # Returns 0 in case of an error. The error can be obstained using
    # self.errorString().
    ##
    def toMap(self, variant, mapDir):
        self.mGidMapper.clear()
        self.mMapDir = mapDir
        variantMap = variant
        orientationString = variantMap.get("orientation", '')
        orientation = orientationFromString(orientationString)
        if (orientation == Map.Orientation.Unknown):
            self.mError = self.tr("Unsupported map orientation: \"%s\""%orientationString)
            return None
        
        staggerAxisString = variantMap.get("staggeraxis", '')
        staggerAxis = staggerAxisFromString(staggerAxisString)
        staggerIndexString = variantMap.get("staggerindex", '')
        staggerIndex = staggerIndexFromString(staggerIndexString)
        renderOrderString = variantMap.get("renderorder", '')
        renderOrder = renderOrderFromString(renderOrderString)
        nextObjectId = variantMap.get("nextobjectid", 0)
        map = Map(orientation,
                           variantMap.get("width",0),
                           variantMap.get("height",0),
                           variantMap.get("tilewidth",0),
                           variantMap.get("tileheight",0))
        map.setHexSideLength(variantMap.get("hexsidelength", 0))
        map.setStaggerAxis(staggerAxis)
        map.setStaggerIndex(staggerIndex)
        map.setRenderOrder(renderOrder)
        if (nextObjectId):
            map.setNextObjectId(nextObjectId)
        self.mMap = map
        map.setProperties(self.toProperties(variantMap.get("properties", {})))
        bgColor = variantMap.get("backgroundcolor", '')
        if (bgColor!='' and QColor.isValidColor(bgColor)):
            map.setBackgroundColor(QColor(bgColor))
        for tilesetVariant in variantMap.get("tilesets", []):
            tileset = self.__toTileset(tilesetVariant)
            if not tileset:
                return None
            
            map.addTileset(tileset)
        
        for layerVariant in variantMap.get("layers", []):
            layer = self.toLayer(layerVariant)
            if not layer:
                return None
            
            map.addLayer(layer)
        
        return map
        
    ##
    # Returns the last error, if any.
    ##
    def errorString(self):
        return self.mError

    def toProperties(self, variant):
        variantMap = variant
        properties = Properties()
        for it in variantMap.items():
            properties[it[0]] = it[1]
        return properties
    
    def toTileset(self, variant, directory):
        self.mMapDir = directory
        self.mReadingExternalTileset = True
        tileset = self.__toTileset(variant)
        self.mReadingExternalTileset = False
        return tileset

    def __toTileset(self, variant):
        variantMap = variant
        firstGid = variantMap.get("firstgid",0)
        
        # Handle external tilesets
        sourceVariant = variantMap.get("source", '')
        if sourceVariant != '':
            source = resolvePath(self.mMapDir, sourceVariant)
            tileset, error = readTileset(source)
            if not tileset:
                self.mError = self.tr("Error while loading tileset '%s': %s"%(source, error))
            else:
                self.mGidMapper.insert(firstGid, tileset)
            return tileset

        name = variantMap.get("name",'')
        tileWidth = variantMap.get("tilewidth",0)
        tileHeight = variantMap.get("tileheight",0)
        spacing = variantMap.get("spacing",0)
        margin = variantMap.get("margin",0)
        tileOffset = variantMap.get("tileoffset", {})
        tileOffsetX = tileOffset.get("x",0)
        tileOffsetY = tileOffset.get("y",0)
        if (tileWidth <= 0 or tileHeight <= 0 or (firstGid == 0 and not self.mReadingExternalTileset)):
            self.mError = self.tr("Invalid tileset parameters for tileset '%s'"%name)
            return None
        
        tileset = Tileset.create(name, tileWidth, tileHeight, spacing, margin)
        tileset.setTileOffset(QPoint(tileOffsetX, tileOffsetY))
        trans = variantMap.get("transparentcolor", '')
        if (trans!='' and QColor.isValidColor(trans)):
            tileset.setTransparentColor(QColor(trans))
        imageVariant = variantMap.get("image",'')
        if imageVariant != '':
            imagePath = resolvePath(self.mMapDir, imageVariant)
            if (not tileset.loadFromImage(imagePath)):
                self.mError = self.tr("Error loading tileset image:\n'%s'"%imagePath)
                return None

        tileset.setProperties(self.toProperties(variantMap.get("properties", {})))
        
        # Read terrains
        terrainsVariantList = variantMap.get("terrains", [])
        for terrainMap in terrainsVariantList:
            tileset.addTerrain(terrainMap.get("name", ''), terrainMap.get("tile", 0))

        # Read tile terrain and external image information
        tilesVariantMap = variantMap.get("tiles", {})
        for it in tilesVariantMap.items():
            ok = False
            tileIndex = Int(it[0])
            if (tileIndex < 0):
                self.mError = self.tr("Tileset tile index negative:\n'%d'"%tileIndex)
            
            if (tileIndex >= tileset.tileCount()):
                # Extend the tileset to fit the tile
                if (tileIndex >= len(tilesVariantMap)):
                    # If tiles are  defined this way, there should be an entry
                    # for each tile.
                    # Limit the index to number of entries to prevent running out
                    # of memory on malicious input.f
                    self.mError = self.tr("Tileset tile index too high:\n'%d'"%tileIndex)
                    return None
                
                for i in range(tileset.tileCount(), tileIndex+1):
                    tileset.addTile(QPixmap())
            
            tile = tileset.tileAt(tileIndex)
            if (tile):
                tileVar = it[1]
                terrains = tileVar.get("terrain", [])
                if len(terrains) == 4:
                    for i in range(0, 4):
                        terrainId, ok = Int2(terrains[i])
                        if (ok and terrainId >= 0 and terrainId < tileset.terrainCount()):
                            tile.setCornerTerrainId(i, terrainId)

                probability, ok = Float2(tileVar.get("probability", 0.0))
                if (ok):
                    tile.setProbability(probability)
                imageVariant = tileVar.get("image",'')
                if imageVariant != '':
                    imagePath = resolvePath(self.mMapDir, imageVariant)
                    tileset.setTileImage(tileIndex, QPixmap(imagePath), imagePath)
                
                objectGroupVariant = tileVar.get("objectgroup", {})
                if len(objectGroupVariant) > 0:
                    tile.setObjectGroup(self.toObjectGroup(objectGroupVariant))
                frameList = tileVar.get("animation", [])
                lenFrames = len(frameList)
                if lenFrames > 0:
                    frames = QVector()
                    for i in range(lenFrames):
                        frames.append(Frame())
                    for i in range(lenFrames - 1, -1, -1):
                        frameVariantMap = frameList[i]
                        frame = frames[i]
                        frame.tileId = frameVariantMap.get("tileid", 0)
                        frame.duration = frameVariantMap.get("duration", 0)
                    
                    tile.setFrames(frames)

        
        # Read tile properties
        propertiesVariantMap = variantMap.get("tileproperties", {})
        
        for it in propertiesVariantMap.items():
            tileIndex = Int(it[0])
            propertiesVar = it[1]
            if (tileIndex >= 0 and tileIndex < tileset.tileCount()):
                properties = self.toProperties(propertiesVar)
                tileset.tileAt(tileIndex).setProperties(properties)

        if not self.mReadingExternalTileset:        
            self.mGidMapper.insert(firstGid, tileset)

        return tileset

    def toLayer(self, variant):
        variantMap = variant
        layer = None
        if (variantMap["type"] == "tilelayer"):
            layer = self.toTileLayer(variantMap)
        elif (variantMap["type"] == "objectgroup"):
            layer = self.toObjectGroup(variantMap)
        elif (variantMap["type"] == "imagelayer"):
            layer = self.toImageLayer(variantMap)
        if (layer):
            layer.setProperties(self.toProperties(variantMap.get("properties", {})))
            offset = QPointF(variantMap.get("offsetx", 0.0),  variantMap.get("offsety", 0.0))
            layer.setOffset(offset)

        return layer
    
    def toTileLayer(self, variantMap):
        name = variantMap.get("name",'')
        width = variantMap.get("width",0)
        height = variantMap.get("height",0)
        dataVariant = variantMap["data"]
        
        tileLayer = TileLayer(name,
                             variantMap.get("x",0),
                             variantMap.get("y",0),
                             width, height)
        opacity = variantMap.get("opacity", 0.0)
        visible = variantMap.get("visible", True)
        tileLayer.setOpacity(opacity)
        tileLayer.setVisible(visible)

        encoding = variantMap.get("encoding", '')
        compression = variantMap.get("compression", '')

        if encoding=='' or encoding == "csv":
            layerDataFormat = Map.LayerDataFormat.CSV
        elif (encoding == "base64"):
            if compression=='':
                layerDataFormat = Map.LayerDataFormat.Base64
            elif (compression == "gzip"):
                layerDataFormat = Map.LayerDataFormat.Base64Gzip
            elif (compression == "zlib"):
                layerDataFormat = Map.LayerDataFormat.Base64Zlib
            else:
                self.mError = self.tr("Compression method '%s' not supported"%compression)
                return None
        else:
            self.mError = self.tr("Unknown encoding: %1"%encoding)
            return None

        self.mMap.setLayerDataFormat(layerDataFormat)

        if layerDataFormat==Map.LayerDataFormat.XML or layerDataFormat==Map.LayerDataFormat.CSV:
            dataVariantList = dataVariant

            if len(dataVariantList) != width * height:
                self.mError = self.tr("Corrupt layer data for layer '%s'"%name)
                return None
            x = 0
            y = 0
            ok = False
            
            if (len(dataVariantList) != width * height):
                self.mError = self.tr("Corrupt layer data for layer '%s'"%name)
                return None
            for gidVariant in dataVariantList:
                gid, ok = Int2(gidVariant)
                if (not ok):
                    self.mError = self.tr("Unable to parse tile at (%d,%d) on layer '%s'"%(x, y, tileLayer.name()))
                    return None
                
                cell = self.mGidMapper.gidToCell(gid, ok)
                tileLayer.setCell(x, y, cell)
                x += 1
                if (x >= tileLayer.width()):
                    x = 0
                    y += 1
        elif layerDataFormat==Map.LayerDataFormat.Base64 \
            or layerDataFormat==Map.LayerDataFormat.Base64Zlib \
            or layerDataFormat==Map.LayerDataFormat.Base64Gzip:
            data = QByteArray(dataVariant)
            error = self.mGidMapper.decodeLayerData(tileLayer, data, layerDataFormat)

            if error==DecodeError.CorruptLayerData:
                self.mError = self.tr("Corrupt layer data for layer '%s'"%name)
                return None
            elif error==DecodeError.TileButNoTilesets:
                self.mError = self.tr("Tile used but no tilesets specified")
                return None
            elif error==DecodeError.InvalidTile:
                self.mError = self.tr("Invalid tile: %d"%self.mGidMapper.invalidTile())
                return None
            elif error==DecodeError.NoError:
                pass
            
        return tileLayer

    def toObjectGroup(self, variantMap):
        objectGroup = ObjectGroup(variantMap.get("name",''),
                               variantMap.get("x",0),
                               variantMap.get("y",0),
                               variantMap.get("width",0),
                               variantMap.get("height",0))
        opacity = variantMap.get("opacity", 0.0)
        visible = variantMap.get("visible", True)
        objectGroup.setOpacity(opacity)
        objectGroup.setVisible(visible)
        objectGroup.setColor(variantMap.get("color", ''))
        drawOrderString = variantMap.get("draworder", '')
        if drawOrderString != '':
            objectGroup.setDrawOrder(drawOrderFromString(drawOrderString))
            if (objectGroup.drawOrder() == ObjectGroup.DrawOrder.UnknownOrder):
                self.mError = self.tr("Invalid draw order: %s"%drawOrderString)
                return None

        for objectVariant in variantMap.get("objects", []):
            objectVariantMap = objectVariant
            name = objectVariantMap.get("name",'')
            type = objectVariantMap.get("type", '')
            id = objectVariantMap.get("id",0.0)
            gid = objectVariantMap.get("gid",0.0)
            x = objectVariantMap.get("x",0.0)
            y = objectVariantMap.get("y",0.0)
            width = objectVariantMap.get("width",0.0)
            height = objectVariantMap.get("height",0.0)
            rotation = objectVariantMap.get("rotation", 0.0)
            pos = QPointF(x, y)
            size = QSizeF(width, height)
            object = MapObject(name, type, pos, size)
            object.setId(id)
            object.setRotation(rotation)
            if (gid):
                cell, ok = self.mGidMapper.gidToCell(gid)
                object.setCell(cell)
                if not object.cell().isEmpty():
                    tileSize = object.cell().tile.size()
                    if width == 0:
                        object.setWidth(tileSize.width())
                    if height == 0:
                        object.setHeight(tileSize.height())
                        
            if (objectVariantMap.__contains__("visible")):
                object.setVisible(objectVariantMap.get("visible", True))
            object.setProperties(self.toProperties(objectVariantMap.get("properties", {})))
            objectGroup.addObject(object)
            polylineVariant = objectVariantMap.get("polyline", [])
            polygonVariant = objectVariantMap.get("polygon", [])
            if len(polygonVariant) > 0:
                object.setShape(MapObject.Polygon)
                object.setPolygon(self.toPolygon(polygonVariant))
            
            if len(polylineVariant) > 0:
                object.setShape(MapObject.Polyline)
                object.setPolygon(self.toPolygon(polylineVariant))
            
            if (objectVariantMap.__contains__("ellipse")):
                object.setShape(MapObject.Ellipse)
        
        return objectGroup
        
    def toImageLayer(self, variantMap):
        imageLayer = ImageLayer(variantMap.get("name",''),
                                                variantMap.get("x",0),
                                                variantMap.get("y",0),
                                                variantMap.get("width",0),
                                                variantMap.get("height",0))
        opacity = variantMap.get("opacity", 0.0)
        visible = variantMap.get("visible", True)
        imageLayer.setOpacity(opacity)
        imageLayer.setVisible(visible)
        trans = variantMap.get("transparentcolor", '')
        if (not trans.isEmpty() and QColor.isValidColor(trans)):
            imageLayer.setTransparentColor(QColor(trans))
        imageVariant = variantMap.get("image",'')
        if imageVariant != '':
            imagePath = resolvePath(self.mMapDir, imageVariant)
            if (not imageLayer.loadFromImage(QImage(imagePath), imagePath)):
                self.mError = self.tr("Error loading image:\n'%s'"%imagePath)
                return None

        return imageLayer
        
    def toPolygon(self, variant):
        polygon = QPolygonF()
        for pointVariant in variant:
            pointVariantMap = pointVariant
            pointX = pointVariantMap.get("x",0.0)
            pointY = pointVariantMap.get("y",0.0)
            polygon.append(QPointF(pointX, pointY))
        
        return polygon
