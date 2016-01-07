##
# tile.py
# Copyright 2008-2014, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2009, Edward Hutchins
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
from pyqtcore import QVector, QString
from PyQt5.QtGui import QPixmap

##
# Returns the given \a terrain with the \a corner modified to \a terrainId.
##
def setTerrainCorner(terrain, corner, terrainId):
    mask = 0xFF << (3 - corner) * 8
    insert = terrainId << (3 - corner) * 8
    return (terrain & ~mask) | (insert & mask)

##
# A single frame of an animated tile.
##
class Frame():
    def __init__(self):
        self.tileId = 0
        self.duration = 0

class Tile(Object):
    def __init__(self, *args):
        super().__init__(Object.TileType)
        
        l = len(args)
        if l==3:
            image, id, tileset = args
            self.mImageSource = QString()
        elif l==4:
            image, imageSource, id, tileset = args
            self.mImageSource = imageSource

        self.mId = id
        self.mTileset = tileset
        self.mImage = image
        self.mTerrain = 0xffffffff
        self.mProbability = 1.0
        self.mObjectGroup = None
        self.mFrames = QVector()
        self.mCurrentFrameIndex = 0
        self.mUnusedTime = 0

    def __del__(self):
        del self.mObjectGroup

    ##
    # Returns the tileset that this tile is part of as a shared pointer.
    ##
    def sharedTileset(self):
        return self.mTileset.sharedPointer()

    ##
    # Returns ID of this tile within its tileset.
    ##
    def id(self):
        return self.mId

    ##
    # Returns the tileset that this tile is part of.
    ##
    def tileset(self):
        return self.mTileset

    ##
    # Returns the image of this tile.
    ##
    def image(self):
        return QPixmap(self.mImage)

    ##
    # Returns the image for rendering this tile, taking into account tile
    # animations.
    ##
    def currentFrameImage(self):
        if (self.isAnimated()):
            frame = self.mFrames.at(self.mCurrentFrameIndex)
            return self.mTileset.tileAt(frame.tileId).image()
        else:
            return QPixmap(self.mImage)

    ##
    # Returns the drawing offset of the tile (in pixels).
    ##
    def offset(self):
        return self.mTileset.tileOffset()

    ##
    # Sets the image of this tile.
    ##
    def setImage(self, image):
        self.mImage = image

    ##
    # Returns the file name of the external image that represents this tile.
    # When this tile doesn't refer to an external image, an empty string is
    # returned.
    ##
    def imageSource(self):
        return self.mImageSource

    ##
    # Returns the file name of the external image that represents this tile.
    # When this tile doesn't refer to an external image, an empty string is
    # returned.
    ##
    def setImageSource(self, imageSource):
        self.mImageSource = imageSource

    ##
    # Returns the width of this tile.
    ##
    def width(self):
        return self.mImage.width()

    ##
    # Returns the height of this tile.
    ##
    def height(self):
        return self.mImage.height()

    ##
    # Returns the size of this tile.
    ##
    def size(self):
        return self.mImage.size()

    ##
    # Returns the Terrain of a given corner.
    ##
    def terrainAtCorner(self, corner):
        return self.mTileset.terrain(self.cornerTerrainId(corner))

    ##
    # Returns the terrain id at a given corner.
    ##
    def cornerTerrainId(self, corner):
        t = (self.terrain() >> (3 - corner)*8) & 0xFF
        if t == 0xFF:
            return -1
        return t

    ##
    # Set the terrain type of a given corner.
    ##
    def setCornerTerrainId(self, corner, terrainId):
        self.setTerrain(setTerrainCorner(self.mTerrain, corner, terrainId))

    ##
    # Returns the terrain for each corner of this tile.
    ##
    def terrain(self):
        return self.mTerrain

    ##
    # Set the terrain for each corner of the tile.
    ##
    def setTerrain(self, terrain):
        if (self.mTerrain == terrain):
            return
        self.mTerrain = terrain
        self.mTileset.markTerrainDistancesDirty()

    ##
    # Returns the probability of this terrain type appearing while painting (0-100%).
    ##
    def probability(self):
        return self.mProbability

    ##
    # Set the relative probability of this tile appearing while painting.
    ##
    def setProbability(self, probability):
        self.mProbability = probability

    ##
    # @return The group of objects associated with this tile. This is generally
    #         expected to be used for editing collision shapes.
    ##
    def objectGroup(self):
        return self.mObjectGroup

    ##
    # Sets \a objectGroup to be the group of objects associated with this tile.
    # The Tile takes ownership over the ObjectGroup and it can't also be part of
    # a map.
    ##
    def setObjectGroup(self, objectGroup):
        if (self.mObjectGroup == objectGroup):
            return
        del self.mObjectGroup
        self.mObjectGroup = objectGroup

    ##
    # Swaps the object group of this tile with \a objectGroup. The tile releases
    # ownership over its existing object group and takes ownership over the new
    # one.
    #
    # @return The previous object group referenced by this tile.
    ##
    def swapObjectGroup(self, objectGroup):
        previousObjectGroup = self.mObjectGroup
        self.mObjectGroup = objectGroup
        return previousObjectGroup

    def frames(self):
        return self.mFrames

    ##
    # Sets the animation frames to be used by this tile. Resets any currently
    # running animation.
    ##
    def setFrames(self, frames):
        self.mFrames = frames
        self.mCurrentFrameIndex = 0
        self.mUnusedTime = 0

    def isAnimated(self):
        return not self.mFrames.isEmpty()

    def currentFrameIndex(self):
        return self.mCurrentFrameIndex

    ##
    # Advances this tile animation by the given amount of milliseconds. Returns
    # whether this caused the current tileId to change.
    ##
    def advanceAnimation(self, ms):
        if (not self.isAnimated()):
            return False
        self.mUnusedTime += ms
        frame = self.mFrames.at(self.mCurrentFrameIndex)
        previousTileId = frame.tileId
        while (frame.duration > 0 and self.mUnusedTime > frame.duration):
            self.mUnusedTime -= frame.duration
            self.mCurrentFrameIndex = (self.mCurrentFrameIndex + 1) % self.mFrames.size()
            frame = self.mFrames.at(self.mCurrentFrameIndex)

        return previousTileId != frame.tileId
