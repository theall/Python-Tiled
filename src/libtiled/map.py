##
# map.py
# Copyright 2008-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2008, Roderic Morris <roderic@ccs.neu.edu>
# Copyright 2010, Andrew G. Crowell <overkill9999@gmail.com>
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

import math
from enum import Enum
from layer import Layer
from pyqtcore import QList, QVector
from object import Object
from PyQt5.QtGui import (
    QColor
)
from PyQt5.QtCore import (
    QSize,
    QMargins
)
def maxMargins(a, b):
    return QMargins(max(a.left(), b.left()),
                    max(a.top(), b.top()),
                    max(a.right(), b.right()),
                    max(a.bottom(), b.bottom()))

def staggerAxisToString(staggerAxis):
    if staggerAxis == Map.StaggerAxis.StaggerX:
        return "x"
    else:
        return "y"

def staggerAxisFromString(string):
    staggerAxis = Map.StaggerAxis.StaggerY
    if string == "x":
        staggerAxis = Map.StaggerAxis.StaggerX
    return staggerAxis

def staggerIndexToString(staggerIndex):
    if staggerIndex == Map.StaggerIndex.StaggerEven:
        return "even"
    else:
        return "odd"

def staggerIndexFromString(string):
    staggerIndex = Map.StaggerIndex.StaggerOdd
    if string == "even":
        staggerIndex = Map.StaggerIndex.StaggerEven
    return staggerIndex

##
# Helper function that converts the map orientation to a string value. Useful
# for map writers.
#
# @return The map orientation as a lowercase string.
##
def orientationToString(orientation):
    if orientation==Map.Orientation.Orthogonal:
        return "orthogonal"
    elif orientation==Map.Orientation.Isometric:
        return "isometric"
    elif orientation==Map.Orientation.Staggered:
        return "staggered"
    elif orientation==Map.Orientation.Hexagonal:
        return "hexagonal"
    else:
        return "unknown"

##
# Helper function that converts a string to a map orientation enumerator.
# Useful for map readers.
#
# @return The map orientation matching the given string, or Map::Unknown if
#         the string is unrecognized.
##
def orientationFromString(string):
    orientation = Map.Orientation.Unknown
    if string == "orthogonal":
        orientation = Map.Orientation.Orthogonal
    elif string == "isometric":
        orientation = Map.Orientation.Isometric
    elif string == "staggered":
        orientation = Map.Orientation.Staggered
    elif string == "hexagonal":
        orientation = Map.Orientation.Hexagonal
    return orientation

def renderOrderToString(renderOrder):
    if renderOrder==Map.RenderOrder.RightUp:
        return "right-up"
    elif renderOrder==Map.RenderOrder.LeftDown:
        return "left-down"
    elif renderOrder==Map.RenderOrder.LeftUp:
        return "left-up"
    else:
        return "right-down"

def renderOrderFromString(string):
    renderOrder = Map.RenderOrder.RightDown
    if string == "right-up":
        renderOrder = Map.RenderOrder.RightUp
    elif string == "left-down":
        renderOrder = Map.RenderOrder.LeftDown
    elif string == "left-up":
        renderOrder = Map.RenderOrder.LeftUp
    return renderOrder

##
# A tile map. Consists of a stack of layers, each can be either a TileLayer
# or an ObjectGroup.
#
# It also keeps track of the list of referenced tilesets.
##
class Map(Object):

    ##
    # The orientation of the map determines how it should be rendered. An
    # Orthogonal map is using rectangular tiles that are aligned on a
    # straight grid. An Isometric map uses diamond shaped tiles that are
    # aligned on an isometric projected grid. A Hexagonal map uses hexagon
    # shaped tiles that fit into each other by shifting every other row.
    ##
    class Orientation(Enum):
        Unknown, Orthogonal, Isometric, Staggered, Hexagonal = range(5)

    ##
    # The different formats in which the tile layer data can be stored.
    ##
    class LayerDataFormat(Enum):
        XML        = 0
        Base64     = 1
        Base64Gzip = 2
        Base64Zlib = 3
        CSV        = 4

    ##
    # The order in which tiles are rendered on screen.
    ##
    class RenderOrder(Enum):
        RightDown  = 0
        RightUp    = 1
        LeftDown   = 2
        LeftUp     = 3

    ##
    # Which axis is staggered. Only used by the isometric staggered and
    # hexagonal map renderers.
    ##
    class StaggerAxis(Enum):
        StaggerX, StaggerY = range(2)

    ##
    # When staggering, specifies whether the odd or the even rows/columns are
    # shifted half a tile right/down. Only used by the isometric staggered and
    # hexagonal map renderers.
    ##
    class StaggerIndex(Enum):
        StaggerOdd  = 0
        StaggerEven = 1

    def __init__(self, *args):
        self.mOrientation = 0
        self.mRenderOrder = 0
        self.mWidth = 0
        self.mHeight = 0
        self.mTileWidth = 0
        self.mTileHeight = 0
        self.mHexSideLength = 0
        self.mStaggerAxis = 0
        self.mStaggerIndex = 0
        self.mBackgroundColor = QColor()
        self.mDrawMargins = QMargins()
        self.mLayers = QList()
        self.mTilesets = QVector()
        self.mLayerDataFormat = None
        self.mNextObjectId = 0

        l = len(args)
        if l==1:
            ##
            # Copy constructor. Makes sure that a deep-copy of the layers is created.
            ##
            map = args[0]
            super().__init__(map)

            self.mLayers = QList()
            self.mOrientation = map.mOrientation
            self.mRenderOrder = map.mRenderOrder
            self.mWidth = map.mWidth
            self.mHeight = map.mHeight
            self.mTileWidth = map.mTileWidth
            self.mTileHeight = map.mTileHeight
            self.mHexSideLength = map.mHexSideLength
            self.mStaggerAxis = map.mStaggerAxis
            self.mStaggerIndex = map.mStaggerIndex
            self.mBackgroundColor = map.mBackgroundColor
            self.mDrawMargins = map.mDrawMargins
            self.mTilesets = map.mTilesets
            self.mLayerDataFormat = map.mLayerDataFormat
            self.mNextObjectId = 1
            for layer in map.mLayers:
                clone = layer.clone()
                clone.setMap(self)
                self.mLayers.append(clone)
        elif l==5:
            ##
            # Constructor, taking map orientation, size and tile size as parameters.
            ##
            orientation, width, height, tileWidth, tileHeight = args
            super().__init__(Object.MapType)

            self.mLayers = QList()
            self.mTilesets = QList()
            self.mOrientation = orientation
            self.mRenderOrder = Map.RenderOrder.RightDown
            self.mWidth = width
            self.mHeight = height
            self.mTileWidth = tileWidth
            self.mTileHeight = tileHeight
            self.mHexSideLength = 0
            self.mStaggerAxis = Map.StaggerAxis.StaggerY
            self.mStaggerIndex = Map.StaggerIndex.StaggerOdd
            self.mLayerDataFormat = Map.LayerDataFormat.Base64Zlib
            self.mNextObjectId = 1

    ##
    # Destructor.
    ##
    def __del__(self):
        self.mLayers.clear()

    ##
    # Returns the orientation of the map.
    ##
    def orientation(self):
        return self.mOrientation

    ##
    # Sets the orientation of the map.
    ##
    def setOrientation(self, orientation):
        self.mOrientation = orientation

    ##
    # Returns the render order of the map.
    ##
    def renderOrder(self):
        return self.mRenderOrder

    ##
    # Sets the render order of the map.
    ##
    def setRenderOrder(self, renderOrder):
        self.mRenderOrder = renderOrder

    ##
    # Returns the width of this map in tiles.
    ##
    def width(self):
        return self.mWidth

    ##
    # Sets the width of this map in tiles.
    ##
    def setWidth(self, width):
        self.mWidth = width

    ##
    # Returns the height of this map in tiles.
    ##
    def height(self):
        return self.mHeight

    ##
    # Sets the height of this map in tiles.
    ##
    def setHeight(self, height):
        self.mHeight = height

    ##
    # Returns the size of this map. Provided for convenience.
    ##
    def size(self):
        return QSize(self.mWidth, self.mHeight)

    ##
    # Returns the tile width of this map.
    ##
    def tileWidth(self):
        return self.mTileWidth

    ##
    # Sets the width of one tile.
    ##
    def setTileWidth(self, width):
        self.mTileWidth = width

    ##
    # Returns the tile height used by this map.
    ##
    def tileHeight(self):
        return self.mTileHeight

    ##
    # Sets the height of one tile.
    ##
    def setTileHeight(self, height):
        self.mTileHeight = height

    ##
    # Returns the size of one tile. Provided for convenience.
    ##
    def tileSize(self):
        return QSize(self.mTileWidth, self.mTileHeight)

    def hexSideLength(self):
        return self.mHexSideLength

    def setHexSideLength(self, hexSideLength):
        self.mHexSideLength = hexSideLength

    def staggerAxis(self):
        return self.mStaggerAxis

    def setStaggerAxis(self, staggerAxis):
        self.mStaggerAxis = staggerAxis

    def staggerIndex(self):
        return self.mStaggerIndex

    def setStaggerIndex(self, staggerIndex):
        self.mStaggerIndex = staggerIndex

    ##
    # Adjusts the draw margins to be at least as big as the given margins.
    # Called from tile layers when their tiles change.
    ##
    def adjustDrawMargins(self, margins):
        # The TileLayer includes the maximum tile size in its draw margins. So
        # we need to subtract the tile size of the map, since that part does not
        # contribute to additional margin.
        self.mDrawMargins = maxMargins(QMargins(margins.left(),
                                           margins.top() - self.mTileHeight,
                                           margins.right() - self.mTileWidth,
                                           margins.bottom()),
                                  self.mDrawMargins)

    ##
    # Computes the extra margins due to layer offsets. These need to be taken into
    # account when determining the bounding rect of the map for example.
    ##
    def computeLayerOffsetMargins(self):
        offsetMargins = QMargins()

        for layer in self.mLayers:
            offset = layer.offset()
            offsetMargins = maxMargins(QMargins(math.ceil(-offset.x()),
                                                math.ceil(-offset.y()),
                                                math.ceil(offset.x()),
                                                math.ceil(offset.y())),
                                       offsetMargins)

        return offsetMargins

    ##
    # Returns the margins that have to be taken into account when figuring
    # out which part of the map to repaint after changing some tiles.
    #
    # @see TileLayer.drawMargins
    ##
    def drawMargins(self):
        return self.mDrawMargins

    ##
    # Recomputes the draw margins for this map and each of its tile layers. Needed
    # after the tile offset of a tileset has changed for example.
    #
    # \sa TileLayer.recomputeDrawMargins
    ##
    def recomputeDrawMargins(self):
        self.mDrawMargins = QMargins()
        for layer in self.mLayers:
            tileLayer = layer.asTileLayer()
            if tileLayer:
                tileLayer.recomputeDrawMargins()

    ##
    # Returns the number of layers of this map.
    ##
    def layerCount(self, *args):
        l = len(args)
        if l==0:
            return self.mLayers.size()
        elif l==1:
            ##
            # Convenience function that returns the number of layers of this map that
            # match the given \a type.
            ##
            tp = args[0]

            count = 0
            for layer in self.mLayers:
               if (layer.layerType() == tp):
                   count += 1
            return count

    def tileLayerCount(self):
        return self.layerCount(Layer.TileLayerType)

    def objectGroupCount(self):
        return self.layerCount(Layer.ObjectGroupType)

    def imageLayerCount(self):
        return self.layerCount(Layer.ImageLayerType)

    ##
    # Returns the layer at the specified index.
    ##
    def layerAt(self, index):
        return self.mLayers.at(index)

    ##
    # Returns the list of layers of this map. This is useful when you want to
    # use foreach.
    ##
    def layers(self, *args):
        l = len(args)
        if l==0:
            return QList(self.mLayers)
        elif l==1:
            tp = args[0]
            layers = QList()
            for layer in self.mLayers:
                if (layer.layerType() == tp):
                    layers.append(layer)
            return layers

    def objectGroups(self):
        layers = QList()
        for layer in self.mLayers:
            og = layer.asObjectGroup()
            if og:
                layers.append(og)
        return layers

    def tileLayers(self):
        layers = QList()
        for layer in self.mLayers:
            tl = layer.asTileLayer()
            if tl:
                layers.append(tl)
        return layers

    ##
    # Adds a layer to this map.
    ##
    def addLayer(self, layer):
        self.adoptLayer(layer)
        self.mLayers.append(layer)

    ##
    # Returns the index of the layer given by \a layerName, or -1 if no
    # layer with that name is found.
    #
    # The second optional parameter specifies the layer types which are
    # searched.
    ##
    def indexOfLayer(self, layerName, layertypes = Layer.AnyLayerType):
        for index in range(self.mLayers.size()):
            if (self.layerAt(index).name() == layerName and (layertypes & self.layerAt(index).layerType())):
                return index
        return -1

    ##
    # Adds a layer to this map, inserting it at the given index.
    ##
    def insertLayer(self, index, layer):
        self.adoptLayer(layer)
        self.mLayers.insert(index, layer)

    ##
    # Removes the layer at the given index from this map and returns it.
    # The caller becomes responsible for the lifetime of this layer.
    ##
    def takeLayerAt(self, index):
        layer = self.mLayers.takeAt(index)
        layer.setMap(None)
        return layer

    ##
    # Adds a tileset to this map. The map does not take ownership over its
    # tilesets, this is merely for keeping track of which tilesets are used by
    # the map, and their saving order.
    #
    # @param tileset the tileset to add
    ##
    def addTileset(self, tileset):
        self.mTilesets.append(tileset)

    ##
    # Convenience function to be used together with Layer.usedTilesets()
    ##
    def addTilesets(self, tilesets):
        for tileset in tilesets:
            self.addTileset(tileset)
            
    ##
    # Inserts \a tileset at \a index in the list of tilesets used by this map.
    ##
    def insertTileset(self, index, tileset):
        self.mTilesets.insert(index, tileset)

    ##
    # Returns the index of the given \a tileset, or -1 if it is not used in
    # this map.
    ##
    def indexOfTileset(self, tileset):
        return self.mTilesets.indexOf(tileset)

    ##
    # Removes the tileset at \a index from this map.
    #
    # \warning Does not make sure that this map no longer refers to tiles from
    #          the removed tileset!
    #
    # \sa addTileset
    ##
    def removeTilesetAt(self, index):
        self.mTilesets.removeAt(index)

    ##
    # Replaces all tiles from \a oldTileset with tiles from \a newTileset.
    # Also replaces the old tileset with the new tileset in the list of
    # tilesets.
    ##
    def replaceTileset(self, oldTileset, newTileset):
        index = self.mTilesets.indexOf(oldTileset)
        for layer in self.mLayers:
            layer.replaceReferencesToTileset(oldTileset, newTileset)
        self.mTilesets[index] = newTileset

    ##
    # Returns the number of tilesets of this map.
    ##
    def tilesetCount(self):
        return self.mTilesets.size()

    ##
    # Returns the tileset at the given index.
    ##
    def tilesetAt(self, index):
        return self.mTilesets.at(index)

    ##
    # Returns the tilesets that the tiles on this map are using.
    ##
    def tilesets(self):
        return QList(self.mTilesets)

    ##
    # Returns the background color of this map.
    ##
    def backgroundColor(self):
        return QColor(self.mBackgroundColor)

    ##
    # Sets the background color of this map.
    ##
    def setBackgroundColor(self, color):
        self.mBackgroundColor = color

    ##
    # Returns whether the given \a tileset is used by any tile layer of this
    # map.
    ##
    def isTilesetUsed(self, tileset):
        for layer in self.mLayers:
            if (layer.referencesTileset(tileset)):
                return True
        return False

    ##
    # Creates a new map that contains the given \a layer. The map size will be
    # determined by the size of the layer.
    #
    # The orientation defaults to Unknown and the tile width and height will
    # default to 0. In case this map needs to be rendered, these properties
    # will need to be properly set.
    ##
    def fromLayer(layer):
        result = Map(Map.Orientation.Unknown, layer.width(), layer.height(), 0, 0)
        result.addLayer(layer)
        return result

    def layerDataFormat(self):
        return self.mLayerDataFormat

    def setLayerDataFormat(self, format):
        self.mLayerDataFormat = format

    ##
    # Sets the next id to be used for objects on this map.
    ##
    def setNextObjectId(self, nextId):
        self.mNextObjectId = nextId

    ##
    # Returns the next object id for this map.
    ##
    def nextObjectId(self):
        return self.mNextObjectId

    ##
    # Returns the next object id for this map and allocates a new one.
    ##
    def takeNextObjectId(self):
        return self.mNextObjectId+1

    def adoptLayer(self, layer):
        layer.setMap(self)
        tileLayer = layer.asTileLayer()
        if tileLayer:
            self.adjustDrawMargins(tileLayer.drawMargins())
        group = layer.asObjectGroup()
        if group:
            for o in group.objects():
                if (o.id() == 0):
                    o.setId(self.takeNextObjectId())
