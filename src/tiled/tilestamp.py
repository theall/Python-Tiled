##
# tilestamp.py
# Copyright 2015, Thorbjørn Lindeijer <bjorn@lindeijer.nl>
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

from tilesetmanager import TilesetManager
from randompicker import RandomPicker
from varianttomapconverter import VariantToMapConverter
from maptovariantconverter import MapToVariantConverter
from map import Map
from pyqtcore import QVector
from PyQt5.QtCore import (
    QSize,
    qDebug, 
    QJsonValue
)

class TileStampVariation():

    def __init__(self, map = None, probability = 1.0):
        self.map = map
        self.probability = probability

    def tileLayer(self):
        return self.map.layerAt(0)

class TileStamp():

    def __init__(self, *args):
        l = len(args)
        if l==0:
            self.d = TileStampData()
        elif l==1:
            arg = args[0]
            tp = type(arg)
            if tp == Map:
                self.d = TileStampData()
                self.addVariation(arg)
            elif tp == TileStamp:
                self.d = arg.d

    def __eq__(self, other):
        if type(other) == TileStamp:
            return self.d == other.d
        return False
        
    def __del__(self):
        # destructor needs to be here, where TileStampData is defined
        pass
    
    def name(self):
        return self.d.name
    
    def setName(self, name):
        self.d.name = name
    
    def fileName(self):
        return self.d.fileName
    
    def setFileName(self, fileName):
        self.d.fileName = fileName
    
    def probability(self, index):
        return self.d.variations.at(index).probability
    
    def setProbability(self, index, probability):
        self.d.variations[index].probability = probability
    
    def maxSize(self):
        size = QSize()
        for variation in self.d.variations:
            size.setWidth(max(size.width(), variation.map.width()))
            size.setHeight(max(size.height(), variation.map.height()))
        
        return size
    
    def variations(self):
        return self.d.variations

    def addVariation(self, arg1, probability = 1.0):
        tp = type(arg1)
        if tp==Map:
            ##
            # Adds a variation \a map to this tile stamp with a given \a probability.
            #
            # The tile stamp takes ownership over the map.
            ##
            map = arg1
            # increase tileset reference counts to keep watching them
            TilesetManager.instance().addReferences(map.tilesets())
            self.d.variations.append(TileStampVariation(map, probability))
        elif tp == TileStampVariation:
            ##
            # Adds a \a variation to this tile stamp.
            ##
            variation = arg1
            self.addVariation(Map(variation.map), variation.probability)
    
    ##
    # Takes the variation map at \a index. Ownership of the map is passed to the
    # caller, who also has to make sure to handle tileset reference counting.
    ##
    def takeVariation(self, index):
        return self.d.variations.takeAt(index).map

    def deleteVariation(self, index):
        map = self.takeVariation(index)
        TilesetManager.instance().removeReferences(map.tilesets())
        del map
    
    ##
    # A stamp is considered empty when it has no variations.
    ##
    def isEmpty(self):
        return self.d.variations.isEmpty()
    
    def quickStampIndex(self):
        return self.d.quickStampIndex
    
    def setQuickStampIndex(self, quickStampIndex):
        self.d.quickStampIndex = quickStampIndex
    
    def randomVariation(self):
        randomPicker = RandomPicker()
        for variation in self.d.variations:
            randomPicker.add(variation, variation.probability)
        return TileStampVariation(randomPicker.pick().map)
    
    ##
    # Returns a new stamp where all variations have been flipped in the given
    # \a direction.
    ##
    def flipped(self, direction):
        flipped = TileStamp(self)
        flipped.d.detach()
        for variation in flipped.variations():
            layer = variation.tileLayer()
            layer.flip(direction)
        
        return flipped
    
    ##
    # Returns a new stamp where all variations have been rotated in the given
    # \a direction.
    ##
    def rotated(self, direction):
        rotated = TileStamp(self)
        rotated.d.detach()
        for variation in rotated.variations():
            layer = variation.tileLayer()
            layer.rotate(direction)
            variation.map.setWidth(layer.width())
            variation.map.setHeight(layer.height())
        
        return rotated
    
    ##
    # Clones the tile stamp. Changes made to the clone do not affect the original
    # stamp.
    ##
    def clone(self):
        clone = TileStamp(self)
        clone.d.detach()
        return clone
    
    def toJson(self, dir):
        json = {}
        json["name"] = self.d.name
        if (self.d.quickStampIndex != -1):
            json["quickStampIndex"] = self.d.quickStampIndex
        variations = []
        for variation in self.d.variations:
            converter = MapToVariantConverter()
            mapVariant = converter.toVariant(variation.map, dir)
            mapJson = QJsonValue.fromVariant(mapVariant)
            variationJson = {}
            variationJson["probability"] = variation.probability
            variationJson["map"] = mapJson
            variations.append(variationJson)
        
        json["variations"] = variations
        return json
    
    def fromJson(json, mapDir):
        stamp = TileStamp()
        stamp.setName(json.value("name").toString())
        stamp.setQuickStampIndex(json["quickStampIndex"])
        variations = json["variations"]
        for value in variations:
            variationJson = value.toObject()
            mapVariant = variationJson.value("map").toVariant()
            converter = VariantToMapConverter()
            map = converter.toMap(mapVariant, mapDir)
            if (not map):
                qDebug("Failed to load map for stamp:" + converter.errorString())
                continue
            
            probability = variationJson.value("probability").toDouble(1)
            stamp.addVariation(map, probability)
        
        return stamp

class TileStampData():

    def __init__(self, *args):
        l = len(args)
        if l==0:
            self.name = ''
            self.fileName = ''
            self.variations = QVector()
            self.quickStampIndex = -1
        elif l==1:
            other = args[0]
            self.name = other.name
            self.fileName = ''# not copied
            self.variations = other.variations
            self.quickStampIndex = -1

            tilesetManager = TilesetManager.instance()
            # deep-copy the map data
            for variation in self.variations:
                variation.map = Map(variation.map)
                tilesetManager.addReferences(variation.map.tilesets())

    def __del__(self):
        tilesetManager = TilesetManager.instance()
        # decrease reference to tilesets and delete maps
        for variation in self.variations:
            tilesetManager.removeReferences(variation.map.tilesets())
            del variation.map
