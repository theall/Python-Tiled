##
# maptovariantconverter.py
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

from layer import Layer
from tileset import Tileset
from imagelayer import ImageLayer
from tilelayer import TileLayer
from properties import Properties
from objectgroup import ObjectGroup, drawOrderToString
from mapobject import MapObject
from map import (
    Map, 
    orientationToString, 
    renderOrderToString, 
    staggerAxisToString, 
    staggerIndexToString
)
from gidmapper import GidMapper
from pyqtcore import (
    QMap, 
    QString,
    QList
)
from PyQt5.QtCore import (
    QDir,
    QVariant
)
##
# Converts Map instances to QVariant. Meant to be used together with
# JsonWriter.
##
class MapToVariantConverter():

    def __init__(self):
        pass
        self.mMapDir = QDir()
        self.mGidMapper = GidMapper()
        
    def toVariant(self, arg1, arg2):
        tp1 = type(arg1)
        tp2 = type(arg2)
        if tp1==Map and tp2==QDir:
            ##
            # Converts the given \s map to a QVariant. The \a mapDir is used to
            # construct relative paths to external resources.
            ##
            map, mapDir = arg1, arg2
            self.mMapDir = mapDir
            self.mGidMapper.clear()
            mapVariant = QMap()
            mapVariant["version"] = 1.0
            mapVariant["orientation"] = orientationToString(map.orientation())
            mapVariant["renderorder"] = renderOrderToString(map.renderOrder())
            mapVariant["width"] = map.width()
            mapVariant["height"] = map.height()
            mapVariant["tilewidth"] = map.tileWidth()
            mapVariant["tileheight"] = map.tileHeight()
            mapVariant["properties"] = self.__toVariant(map.properties())
            mapVariant["nextobjectid"] = map.nextObjectId()
            if (map.orientation() == Map.Hexagonal) :
                mapVariant["hexsidelength"] = map.hexSideLength()
            
            if (map.orientation() == Map.Hexagonal or map.orientation() == Map.Staggered) :
                mapVariant["staggeraxis"] = staggerAxisToString(map.staggerAxis())
                mapVariant["staggerindex"] = staggerIndexToString(map.staggerIndex())
            
            bgColor = map.backgroundColor()
            if (bgColor.isValid()):
                mapVariant["backgroundcolor"] = bgColor.name()
            tilesetVariants = QList()
            firstGid = 1
            for tileset in map.tilesets():
                tilesetVariants.append(self.__toVariant(tileset, firstGid))
                self.mGidMapper.insert(firstGid, tileset)
                firstGid += tileset.tileCount()
            
            mapVariant["tilesets"] = tilesetVariants
            layerVariants = QList()
            for layer in map.layers():
                x = layer.layerType()
                if False:
                    pass
                elif x==Layer.TileLayerType:
                    layerVariants.append(self.__toVariant(layer, map.layerDataFormat()))
                    break
                elif x==Layer.ObjectGroupType:
                    layerVariants.append(self.__toVariant(layer))
                    break
                elif x==Layer.ImageLayerType:
                    layerVariants.append(self.__toVariant(layer))
                    break

            mapVariant["layers"] = layerVariants
            return mapVariant
        elif tp1==Tileset and tp2==QDir:
            ##
            # Converts the given \s tileset to a QVariant. The \a directory is used to
            # construct relative paths to external resources.
            ##
            tileset, directory = arg1, arg2
            self.mMapDir = directory
            return self.__toVariant(tileset, 0)
        
    def __toVariant(self, *args):
        l = len(args)
        if l==0:
            arg = args[0]
            tp = type(arg)
            if tp == Properties:
                properties = arg
                variantMap = QMap()
                for it in properties:
                    variantMap[it[0]] = it[1]
                return variantMap
            elif tp == ObjectGroup:
                objectGroup = arg
                objectGroupVariant = QMap()
                objectGroupVariant["type"] = "objectgroup"
                if (objectGroup.color().isValid()):
                    objectGroupVariant["color"] = objectGroup.color().name()
                objectGroupVariant["draworder"] = drawOrderToString(objectGroup.drawOrder())
                self.addLayerAttributes(objectGroupVariant, objectGroup)
                objectVariants = QList()
                for object in objectGroup.objects():
                    objectVariant = QMap()
                    name = object.name()
                    type = object.type()
                    objectVariant["properties"] = self.__toVariant(object.properties())
                    objectVariant["id"] = object.id()
                    objectVariant["name"] = name
                    objectVariant["type"] = type
                    if (not object.cell().isEmpty()):
                        objectVariant["gid"] = self.mGidMapper.cellToGid(object.cell())
                    objectVariant["x"] = object.x()
                    objectVariant["y"] = object.y()
                    objectVariant["width"] = object.width()
                    objectVariant["height"] = object.height()
                    objectVariant["rotation"] = object.rotation()
                    objectVariant["visible"] = object.isVisible()
                    ## Polygons are stored in this format:
                    #
                    #   "polygon/polyline": [
                    #       { "x": 0, "y": 0 },
                    #       { "x": 1, "y": 1 },
                    #       ...
                    #   ]
                    ##
                    polygon = object.polygon()
                    if (not polygon.isEmpty()) :
                        pointVariants = QList()
                        for point in polygon:
                            pointVariant = QMap()
                            pointVariant["x"] = point.x()
                            pointVariant["y"] = point.y()
                            pointVariants.append(pointVariant)
                        
                        if (object.shape() == MapObject.Polygon):
                            objectVariant["polygon"] = pointVariants
                        else:
                            objectVariant["polyline"] = pointVariants
                    
                    if (object.shape() == MapObject.Ellipse):
                        objectVariant["ellipse"] = True
                    objectVariants.append(objectVariant)
                
                objectGroupVariant["objects"] = objectVariants
                return objectGroupVariant
            elif tp == ImageLayer:
                imageLayer = arg
                imageLayerVariant = QMap()
                imageLayerVariant["type"] = "imagelayer"
                self.addLayerAttributes(imageLayerVariant, imageLayer)
                rel = self.mMapDir.relativeFilePath(imageLayer.imageSource())
                imageLayerVariant["image"] = rel
                transColor = imageLayer.transparentColor()
                if (transColor.isValid()):
                    imageLayerVariant["transparentcolor"] = transColor.name()
                return imageLayerVariant
        elif l==2:
            arg1, arg2 = args
            tp1 = type(arg1)
            tp2 = type(arg2)
            if tp1==Tileset and tp2==int:
                tileset, firstGid = arg1, arg2
                tilesetVariant = QMap()
                
                if firstGid > 0:
                    tilesetVariant["firstgid"] = firstGid

                fileName = tileset.fileName()
                if fileName != '':
                    source = self.mMapDir.relativeFilePath(fileName)
                    tilesetVariant["source"] = source
                    # Tileset is external, so no need to write any of the stuff below
                    return tilesetVariant
                
                tilesetVariant["firstgid"] = firstGid
                tilesetVariant["name"] = tileset.name()
                tilesetVariant["tilewidth"] = tileset.tileWidth()
                tilesetVariant["tileheight"] = tileset.tileHeight()
                tilesetVariant["spacing"] = tileset.tileSpacing()
                tilesetVariant["margin"] = tileset.margin()
                tilesetVariant["tilecount"] = tileset.tileCount()
                tilesetVariant["properties"] = self.__toVariant(tileset.properties())
                offset = tileset.tileOffset()
                if (not offset.isNull()) :
                    tileOffset = QMap()
                    tileOffset["x"] = offset.x()
                    tileOffset["y"] = offset.y()
                    tilesetVariant["tileoffset"] = tileOffset
                
                # Write the image element
                imageSource = tileset.imageSource()
                if (not imageSource.isEmpty()) :
                    rel = self.mMapDir.relativeFilePath(tileset.imageSource())
                    tilesetVariant["image"] = rel
                    transColor = tileset.transparentColor()
                    if (transColor.isValid()):
                        tilesetVariant["transparentcolor"] = transColor.name()
                    tilesetVariant["imagewidth"] = tileset.imageWidth()
                    tilesetVariant["imageheight"] = tileset.imageHeight()
                
                # Write the properties, terrain, external image, object group and # animation for those tiles that have them.
                tilePropertiesVariant = QMap()
                tilesVariant = QMap()
                for i in range(0, tileset.tileCount()):
                    tile = tileset.tileAt(i)
                    properties = tile.properties()
                    if (not properties.isEmpty()):
                        tilePropertiesVariant[QString.number(i)] = self.__toVariant(properties)
                    tileVariant = QMap()
                    if (tile.terrain() != 0xFFFFFFFF) :
                        terrainIds = QList()
                        for j in range(0, 4):
                            terrainIds.append(QVariant(tile.cornerTerrainId(j)))
                        tileVariant["terrain"] = terrainIds
                    
                    if (tile.probability() != 1.0):
                        tileVariant["probability"] = tile.probability()
                    if (not tile.imageSource().isEmpty()) :
                        rel = self.mMapDir.relativeFilePath(tile.imageSource())
                        tileVariant["image"] = rel
                    
                    if (tile.objectGroup()):
                        tileVariant["objectgroup"] = self.__toVariant(tile.objectGroup())
                    if (tile.isAnimated()) :
                        frameVariants = QList()
                        for frame in tile.frames():
                            frameVariant = QMap()
                            frameVariant["tileid"] = frame.tileId
                            frameVariant["duration"] = frame.duration
                            frameVariants.append(frameVariant)
                        
                        tileVariant["animation"] = frameVariants
                    
                    if (not tileVariant.empty()):
                        tilesVariant[QString.number(i)] = tileVariant
                
                if (not tilePropertiesVariant.empty()):
                    tilesetVariant["tileproperties"] = tilePropertiesVariant
                if (not tilesVariant.empty()):
                    tilesetVariant["tiles"] = tilesVariant
                # Write terrains
                if (tileset.terrainCount() > 0) :
                    terrainsVariant = QList()
                    for i in range(0, tileset.terrainCount()):
                        terrain = tileset.terrain(i)
                        properties = terrain.properties()
                        terrainVariant = QMap()
                        terrainVariant["name"] = terrain.name()
                        if (not properties.isEmpty()):
                            terrainVariant["properties"] = self.__toVariant(properties)
                        terrainVariant["tile"] = terrain.imageTileId()
                        terrainsVariant.append(terrainVariant)
                    
                    tilesetVariant["terrains"] = terrainsVariant
                
                return tilesetVariant
            elif tp1==TileLayer and tp2==int:
                tileLayer, format = arg1, arg2
                tileLayerVariant = QMap()
                tileLayerVariant["type"] = "tilelayer"
                self.addLayerAttributes(tileLayerVariant, tileLayer)
                
                if format == Map.LayerDataFormat.XML or format == Map.LayerDataFormat.CSV:
                    tileVariants = QList()
                    for y in range(tileLayer.height()):
                        for x in range(tileLayer.width()):
                            tileVariants.append(self.mGidMapper.cellToGid(tileLayer.cellAt(x, y)))
                    tileLayerVariant["data"] = tileVariants
                elif format in [Map.LayerDataFormat.Base64, Map.LayerDataFormat.Base64Zlib, Map.LayerDataFormat.Base64Gzip]:
                    tileLayerVariant["encoding"] = "base64"

                    if format == Map.LayerDataFormat.Base64Zlib:
                        tileLayerVariant["compression"] = "zlib"
                    elif format == Map.LayerDataFormat.Base64Gzip:
                        tileLayerVariant["compression"] = "gzip"

                    layerData = self.mGidMapper.encodeLayerData(tileLayer, format)
                    tileLayerVariant["data"] = layerData
                    
                return tileLayerVariant
    def addLayerAttributes(self, layerVariant, layer):
        layerVariant["name"] = layer.name()
        layerVariant["width"] = layer.width()
        layerVariant["height"] = layer.height()
        layerVariant["x"] = layer.x()
        layerVariant["y"] = layer.y()
        layerVariant["visible"] = layer.isVisible()
        layerVariant["opacity"] = layer.opacity()
        offset = layer.offset()
        if not offset.isNull():
            layerVariant["offsetx"] = offset.x()
            layerVariant["offsety"] = offset.y()

        properties = layer.properties()
        if (not properties.isEmpty()):
            layerVariant["properties"] = self.__toVariant(properties)
