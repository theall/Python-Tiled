##
# JSON Tiled Plugin
# Copyright 2011, Porfírio José Pereira Ribeiro <porfirioribeiro@gmail.com>
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

from tileset import Tileset
from tilelayer import TileLayer
from gidmapper import GidMapper
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
from tiled_global import Int2, Float2
from pyqtcore import (
    QVector
)
from PyQt5.QtCore import (
    QPoint,
    QCoreApplication,
    QPointF,
    QDir,
    QSizeF
)
from PyQt5.QtGui import (
    QPixmap,
    QPolygonF,
    QColor,
    QImage
)
def resolvePath(dir, variant):
    fileName = variant.toString()
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
        variantMap = variant.toMap()
        orientationString = variantMap["orientation"].toString()
        orientation = orientationFromString(orientationString)
        if (orientation == Map.Unknown):
            self.mError = self.tr("Unsupported map orientation: \"%s\""%orientationString)
            return 0
        
        staggerAxisString = variantMap["staggeraxis"].toString()
        staggerAxis = staggerAxisFromString(staggerAxisString)
        staggerIndexString = variantMap["staggerindex"].toString()
        staggerIndex = staggerIndexFromString(staggerIndexString)
        renderOrderString = variantMap["renderorder"].toString()
        renderOrder = renderOrderFromString(renderOrderString)
        nextObjectId = variantMap["nextobjectid"].toString().toInt()
        map = Map(orientation,
                           variantMap["width"].toInt(),
                           variantMap["height"].toInt(),
                           variantMap["tilewidth"].toInt(),
                           variantMap["tileheight"].toInt())
        map.setHexSideLength(variantMap["hexsidelength"].toInt())
        map.setStaggerAxis(staggerAxis)
        map.setStaggerIndex(staggerIndex)
        map.setRenderOrder(renderOrder)
        if (nextObjectId):
            map.setNextObjectId(nextObjectId)
        self.mMap = map.data()
        map.setProperties(self.toProperties(variantMap["properties"]))
        bgColor = variantMap["backgroundcolor"].toString()
        if (not bgColor.isEmpty() and QColor.isValidColor(bgColor)):
            map.setBackgroundColor(QColor(bgColor))
        for tilesetVariant in variantMap["tilesets"].toList():
            tileset = self.toTileset(tilesetVariant)
            if not tileset:
                return None
            
            map.addTileset(tileset)
        
        for layerVariant in variantMap["layers"].toList():
            layer = self.toLayer(layerVariant)
            if not layer:
                return None
            
            map.addLayer(layer)
        
        return map.take()
        
    ##
    # Returns the last error, if any.
    ##
    def errorString(self):
        return self.mError

    def toProperties(self, variant):
        variantMap = variant.toMap()
        properties = Properties()
        for it in variantMap:
            properties[it.key()] = it.value().toString()
        return properties
    
    def toTileset(self, variant):
        variantMap = variant.toMap()
        firstGid = variantMap["firstgid"].toInt()
        name = variantMap["name"].toString()
        tileWidth = variantMap["tilewidth"].toInt()
        tileHeight = variantMap["tileheight"].toInt()
        spacing = variantMap["spacing"].toInt()
        margin = variantMap["margin"].toInt()
        tileOffset = variantMap["tileoffset"].toMap()
        tileOffsetX = tileOffset["x"].toInt()
        tileOffsetY = tileOffset["y"].toInt()
        if (tileWidth <= 0 or tileHeight <= 0 or firstGid == 0):
            self.mError = self.tr("Invalid tileset parameters for tileset '%1'").arg(name)
            return 0
        
        tileset = Tileset(name, tileWidth, tileHeight, spacing, margin)
        tileset.setTileOffset(QPoint(tileOffsetX, tileOffsetY))
        trans = variantMap["transparentcolor"].toString()
        if (not trans.isEmpty() and QColor.isValidColor(trans)):
            tileset.setTransparentColor(QColor(trans))
        imageVariant = variantMap["image"]
        if (not imageVariant.isNull()):
            imagePath = resolvePath(self.mMapDir, imageVariant)
            if (not tileset.loadFromImage(imagePath)):
                self.mError = self.tr("Error loading tileset image:\n'%1'").arg(imagePath)
                return 0

        tileset.setProperties(self.toProperties(variantMap["properties"]))
        # Read tile terrain and external image information
        tilesVariantMap = variantMap["tiles"].toMap()
        it = tilesVariantMap.constBegin()
        for it in tilesVariantMap:
            ok = False
            tileIndex = it.key().toInt()
            if (tileIndex < 0):
                self.mError = self.tr("Tileset tile index negative:\n'%1'").arg(tileIndex)
            
            if (tileIndex >= tileset.tileCount()):
                # Extend the tileset to fit the tile
                if (tileIndex >= tilesVariantMap.count()):
                    # If tiles are  defined this way, there should be an entry
                    # for each tile.
                    # Limit the index to number of entries to prevent running out
                    # of memory on malicious input.
                    self.mError = self.tr("Tileset tile index too high:\n'%1'").arg(tileIndex)
                    return 0
                
                for i in range(tileset.tileCount(), tileIndex+1):
                    tileset.addTile(QPixmap())
            
            tile = tileset.tileAt(tileIndex)
            if (tile):
                tileVar = it.value().toMap()
                terrains = tileVar["terrain"].toList()
                if (terrains.count() == 4):
                    for i in range(0, 4):
                        terrainID, ok = Int2(terrains.at(i))
                        if (ok and terrainID >= 0 and terrainID < tileset.terrainCount()):
                            tile.setCornerTerrain(i, terrainID)

                terrainProbability, ok = Float2(tileVar["probability"])
                if (ok):
                    tile.setProbability(terrainProbability)
                imageVariant = tileVar["image"]
                if (not imageVariant.isNull()):
                    imagePath = resolvePath(self.mMapDir, imageVariant)
                    tileset.setTileImage(tileIndex, QPixmap(imagePath), imagePath)
                
                objectGroupVariant = tileVar["objectgroup"].toMap()
                if (not objectGroupVariant.isEmpty()):
                    tile.setObjectGroup(self.toObjectGroup(objectGroupVariant))
                frameList = tileVar["animation"].toList()
                if (not frameList.isEmpty()):
                    frames = QVector(frameList.size())
                    for i in range(frameList.size() - 1, -1, -1):
                        frameVariantMap = frameList[i].toMap()
                        frame = frames[i]
                        frame.tileId = frameVariantMap["tileid"].toInt()
                        frame.duration = frameVariantMap["duration"].toInt()
                    
                    tile.setFrames(frames)

        
        # Read tile properties
        propertiesVariantMap = variantMap["tileproperties"].toMap()
        for it in propertiesVariantMap:
            tileIndex = it[0]
            propertiesVar = it[1]
            if (tileIndex >= 0 and tileIndex < tileset.tileCount()):
                properties = self.toProperties(propertiesVar)
                tileset.tileAt(tileIndex).setProperties(properties)

        # Read terrains
        terrainsVariantList = variantMap["terrains"].toList()
        for i in range(0, terrainsVariantList.count()):
            terrainMap = terrainsVariantList[i].toMap()
            tileset.addTerrain(terrainMap["name"].toString(),
                                terrainMap["tile"].toInt())
        
        self.mGidMapper.insert(firstGid, tileset)
        return tileset.take()

    def toLayer(self, variant):
        variantMap = variant.toMap()
        layer = 0
        if (variantMap["type"] == "tilelayer"):
            layer = self.toTileLayer(variantMap)
        elif (variantMap["type"] == "objectgroup"):
            layer = self.toObjectGroup(variantMap)
        elif (variantMap["type"] == "imagelayer"):
            layer = self.toImageLayer(variantMap)
        if (layer):
            layer.setProperties(self.toProperties(variantMap["properties"]))
        return layer
    
    def toTileLayer(self, variantMap):
        name = variantMap["name"].toString()
        width = variantMap["width"].toInt()
        height = variantMap["height"].toInt()
        dataVariantList = variantMap["data"].toList()
        if (dataVariantList.size() != width * height):
            self.mError = self.tr("Corrupt layer data for layer '%s'"%name)
            return 0
        
        tileLayer = TileLayer(name,
                             variantMap["x"].toInt(),
                             variantMap["y"].toInt(),
                             width, height)
        opacity = variantMap["opacity"].toReal()
        visible = variantMap["visible"].toBool()
        tileLayer.setOpacity(opacity)
        tileLayer.setVisible(visible)
        x = 0
        y = 0
        ok = False
        for gidVariant in dataVariantList:
            gid, ok = Int2(gidVariant)
            if (not ok):
                self.mError = self.tr("Unable to parse tile at (%1,%2) on layer '%3'"%(x, y, tileLayer.name()))
                return 0
            
            cell = self.mGidMapper.gidToCell(gid, ok)
            tileLayer.setCell(x, y, cell)
            x += 1
            if (x >= tileLayer.width()):
                x = 0
                y += 1

        return tileLayer.take()

    def toObjectGroup(self, variantMap):
        objectGroup = ObjectGroup(variantMap["name"].toString(),
                               variantMap["x"].toInt(),
                               variantMap["y"].toInt(),
                               variantMap["width"].toInt(),
                               variantMap["height"].toInt())
        opacity = variantMap["opacity"].toReal()
        visible = variantMap["visible"].toBool()
        objectGroup.setOpacity(opacity)
        objectGroup.setVisible(visible)
        objectGroup.setColor(variantMap.value("color").value())
        drawOrderString = variantMap.value("draworder").toString()
        if (not drawOrderString.isEmpty()):
            objectGroup.setDrawOrder(drawOrderFromString(drawOrderString))
            if (objectGroup.drawOrder() == ObjectGroup.UnknownOrder):
                self.mError = self.tr("Invalid draw order: %1").arg(drawOrderString)
                return 0

        for objectVariant in variantMap["objects"].toList():
            objectVariantMap = objectVariant.toMap()
            name = objectVariantMap["name"].toString()
            type = objectVariantMap["type"].toString()
            id = objectVariantMap["id"].toString().toInt()
            gid = objectVariantMap["gid"].toInt()
            x = objectVariantMap["x"].toReal()
            y = objectVariantMap["y"].toReal()
            width = objectVariantMap["width"].toReal()
            height = objectVariantMap["height"].toReal()
            rotation = objectVariantMap["rotation"].toReal()
            pos = QPointF(x, y)
            size = QSizeF(width, height)
            object = MapObject(name, type, pos, size)
            object.setId(id)
            object.setRotation(rotation)
            if (gid):
                ok = False
                object.setCell(self.mGidMapper.gidToCell(gid, ok))
            
            if (objectVariantMap.contains("visible")):
                object.setVisible(objectVariantMap["visible"].toBool())
            object.setProperties(self.toProperties(objectVariantMap["properties"]))
            objectGroup.addObject(object)
            polylineVariant = objectVariantMap["polyline"]
            polygonVariant = objectVariantMap["polygon"]
            if (polygonVariant.isValid()):
                object.setShape(MapObject.Polygon)
                object.setPolygon(self.toPolygon(polygonVariant))
            
            if (polylineVariant.isValid()):
                object.setShape(MapObject.Polyline)
                object.setPolygon(self.toPolygon(polylineVariant))
            
            if (objectVariantMap.contains("ellipse")):
                object.setShape(MapObject.Ellipse)
        
        return objectGroup.take()
    def toImageLayer(self, variantMap):
        imageLayer = ImageLayer(variantMap["name"].toString(),
                                                variantMap["x"].toInt(),
                                                variantMap["y"].toInt(),
                                                variantMap["width"].toInt(),
                                                variantMap["height"].toInt())
        opacity = variantMap["opacity"].toReal()
        visible = variantMap["visible"].toBool()
        imageLayer.setOpacity(opacity)
        imageLayer.setVisible(visible)
        trans = variantMap["transparentcolor"].toString()
        if (not trans.isEmpty() and QColor.isValidColor(trans)):
            imageLayer.setTransparentColor(QColor(trans))
        imageVariant = variantMap["image"].toString()
        if (not imageVariant.isNull()):
            imagePath = resolvePath(self.mMapDir, imageVariant)
            if (not imageLayer.loadFromImage(QImage(imagePath), imagePath)):
                self.mError = self.tr("Error loading image:\n'%1'").arg(imagePath)
                return 0

        return imageLayer.take()
        
    def toPolygon(self, variant):
        polygon = QPolygonF()
        for pointVariant in variant.toList():
            pointVariantMap = pointVariant.toMap()
            pointX = pointVariantMap["x"].toReal()
            pointY = pointVariantMap["y"].toReal()
            polygon.append(QPointF(pointX, pointY))
        
        return polygon
