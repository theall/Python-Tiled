##
# terrain.py
# Copyright 2012, Manu Evans
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

from object import Object
from pyqtcore import (
    QVector
)
##*
# Represents a terrain type.
##
class Terrain(Object):

    def __init__(self, id, tileset, name, imageTileId):
        super().__init__(Object.TerrainType)
        self.mId = id
        self.mTileset = tileset
        self.mName = name
        self.mImageTileId = imageTileId
        self.mTransitionDistance = QVector()

    ##*
    # Returns ID of this terrain type.
    ##
    def id(self):
        return self.mId

    ##*
    # Sets the ID of this terrain type.
    ##
    def setId(self, id):
        self.mId = id

    ##*
    # Returns the tileset this terrain type belongs to.
    ##
    def tileset(self):
        return self.mTileset

    ##
    # Returns the tileset this terrain type belongs to as a shared pointer.
    ##
    def sharedTileset(self):
        return self.mTileset.sharedPointer()

    ##*
    # Returns the name of this terrain type.
    ##
    def name(self):
        return self.mName

    ##*
    # Sets the name of this terrain type.
    ##
    def setName(self, name):
        self.mName = name

    ##*
    # Returns the index of the tile that visually represents this terrain type.
    ##
    def imageTileId(self):
        return self.mImageTileId

    ##*
    # Sets the index of the tile that visually represents this terrain type.
    ##
    def setImageTileId(self, imageTileId):
        self.mImageTileId = imageTileId

    ##*
    # Returns a Tile that represents this terrain type in the terrain palette.
    ##
    def imageTile(self):
        pass#return self.mImageTileId >= 0 ? self.mTileset.tileAt(self.mImageTileId) : 0
    ##*
    # Returns the transition penalty(/distance) from this terrain type to another terrain type.
    ##
    def transitionDistance(self, targetTerrainType):
        return self.mTransitionDistance[targetTerrainType + 1]

    ##*
    # Sets the transition penalty(/distance) from this terrain type to another terrain type.
    ##
    def setTransitionDistance(self, targetTerrainType, distance):
        self.mTransitionDistance[targetTerrainType + 1] = distance

    ##*
    # Returns the array of terrain penalties(/distances).
    ##
    def setTransitionDistances(self, transitionDistances):
        self.mTransitionDistance = transitionDistances

