##
# tileset.py
# Copyright 2008-20015, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2009, Edward Hutchins <eah1@yahoo.com>
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

from terrain import Terrain
from tile import Tile
from object import Object
from pyqtcore import QString, QList, QVector
from PyQt5.QtCore import (
    QPoint,
    QSize
)
from PyQt5.QtGui import (
    QImage,
    QBitmap,
    QPixmap,
    QColor
)

def sameTileImages(a, b):
    for i in range(a.tileCount()):
        tileA = a.tileAt(i)
        tileB = b.tileAt(i)
        if (tileA.imageSource() != tileB.imageSource()):
            return False
    return True

##
# A tileset, representing a set of tiles.
#
# This class is meant to be used by either loading tiles from a tileset image
# (using loadFromImage) or by adding/removing individual tiles (using
# addTile, insertTiles and removeTiles). These two use-cases are not meant to
# be mixed.
##
class Tileset(Object):
    ##
    # Constructor.
    #
    # @param name        the name of the tileset
    # @param tileWidth   the width of the tiles in the tileset
    # @param tileHeight  the height of the tiles in the tileset
    # @param tileSpacing the spacing between the tiles in the tileset image
    # @param margin      the margin around the tiles in the tileset image
    ##
    def __init__(self, name, tileWidth, tileHeight, tileSpacing = 0, margin = 0):
        super().__init__(Object.TilesetType)

        self.mName = name
        self.mTileWidth = tileWidth
        self.mTileHeight = tileHeight
        self.mTileSpacing = tileSpacing
        self.mMargin = margin
        self.mImageWidth = 0
        self.mImageHeight = 0
        self.mColumnCount = 0
        self.mTerrainDistancesDirty = False

        self.mTileOffset = QPoint()
        self.mFileName = QString()
        self.mTiles = QList()
        self.mTransparentColor = QColor()
        self.mImageSource = QString()
        self.mTerrainTypes = QList()
        self.mWeakPointer = None

    ##
    # Destructor.
    ##
    def __del__(self):
        self.mTiles.clear()
        self.mTerrainTypes.clear()

    def create(name, tileWidth, tileHeight, tileSpacing = 0, margin = 0):
        tileset = Tileset(name, tileWidth, tileHeight, tileSpacing, margin)
        tileset.mWeakPointer = tileset
        return tileset
    
    def __iter__(self):
        return self.mTiles.__iter__()
        
    ##
    # Returns the name of this tileset.
    ##
    def name(self):
        return self.mName

    ##
    # Sets the name of this tileset.
    ##
    def setName(self, name):
        self.mName = name

    ##
    # Returns the file name of this tileset. When the tileset isn't an
    # external tileset, the file name is empty.
    ##
    def fileName(self):
        return self.mFileName

    ##
    # Sets the filename of this tileset.
    ##
    def setFileName(self, fileName):
        self.mFileName = fileName

    ##
    # Returns whether this tileset is external.
    ##
    def isExternal(self):
        return self.mFileName!=''

    ##
    # Returns the maximum width of the tiles in this tileset.
    ##
    def tileWidth(self):
        return self.mTileWidth

    ##
    # Returns the maximum height of the tiles in this tileset.
    ##
    def tileHeight(self):
        return self.mTileHeight

    ##
    # Returns the maximum size of the tiles in this tileset.
    ##
    def tileSize(self):
        return QSize(self.mTileWidth, self.mTileHeight)

    ##
    # Returns the spacing between the tiles in the tileset image.
    ##
    def tileSpacing(self):
        return self.mTileSpacing

    ##
    # Returns the margin around the tiles in the tileset image.
    ##
    def margin(self):
        return self.mMargin

    ##
    # Returns the offset that is applied when drawing the tiles in this
    # tileset.
    ##
    def tileOffset(self):
        return self.mTileOffset

    ##
    # @see tileOffset
    ##
    def setTileOffset(self, offset):
        self.mTileOffset = offset

    ##
    # Returns a const reference to the list of tiles in this tileset.
    ##
    def tiles(self):
        return QList(self.mTiles)

    ##
    # Returns the tile for the given tile ID.
    # The tile ID is local to this tileset, which means the IDs are in range
    # [0, tileCount() - 1].
    ##
    def tileAt(self, id):
        if id < self.mTiles.size():
            return self.mTiles.at(id)
        return None

    ##
    # Returns the number of tiles in this tileset.
    ##
    def tileCount(self):
        return self.mTiles.size()

    ##
    # Returns the number of tile columns in the tileset image.
    ##
    def columnCount(self):
        return self.mColumnCount

    ##
    # Returns the width of the tileset image.
    ##
    def imageWidth(self):
        return self.mImageWidth

    ##
    # Returns the height of the tileset image.
    ##
    def imageHeight(self):
        return self.mImageHeight

    ##
    # Returns the transparent color, or an invalid color if no transparent
    # color is used.
    ##
    def transparentColor(self):
        return QColor(self.mTransparentColor)

    ##
    # Sets the transparent color. Pixels with this color will be masked out
    # when loadFromImage() is called.
    ##
    def setTransparentColor(self, c):
        self.mTransparentColor = c

    ##
    # Load this tileset from the given tileset \a image. This will replace
    # existing tile images in this tileset with new ones. If the new image
    # contains more tiles than exist in the tileset new tiles will be
    # appended, if there are fewer tiles the excess images will be blanked.
    #
    # The tile width and height of this tileset must be higher than 0.
    #
    # @param image    the image to load the tiles from
    # @param fileName the file name of the image, which will be remembered
    #                 as the image source of this tileset.
    # @return <code>true</code> if loading was successful, otherwise
    #         returns <code>false</code>
    ##
    def loadFromImage(self, *args):
        l = len(args)
        if l==2:
            image, fileName = args

            tileSize = self.tileSize()
            margin = self.margin()
            spacing = self.tileSpacing()
    
            if (image.isNull()):
                return False
            stopWidth = image.width() - tileSize.width()
            stopHeight = image.height() - tileSize.height()
            oldTilesetSize = self.tileCount()
            tileNum = 0
            for y in range(margin, stopHeight+1, tileSize.height() + spacing):
                for x in range(margin, stopWidth+1, tileSize.width() + spacing):
                    tileImage = image.copy(x, y, tileSize.width(), tileSize.height())
                    tilePixmap = QPixmap.fromImage(tileImage)
                    if (self.mTransparentColor.isValid()):
                        mask = tileImage.createMaskFromColor(self.mTransparentColor.rgb())
                        tilePixmap.setMask(QBitmap.fromImage(mask))

                    if (tileNum < oldTilesetSize):
                        self.mTiles.at(tileNum).setImage(tilePixmap)
                    else:
                        self.mTiles.append(Tile(tilePixmap, tileNum, self))

                    tileNum += 1

            # Blank out any remaining tiles to avoid confusion
            while (tileNum < oldTilesetSize):
                tilePixmap = QPixmap(tileSize)
                tilePixmap.fill()
                self.mTiles.at(tileNum).setImage(tilePixmap)
                tileNum += 1

            self.mImageWidth = image.width()
            self.mImageHeight = image.height()
            self.mColumnCount = self.columnCountForWidth(self.mImageWidth)
            self.mImageSource = fileName
            return True
        elif l==1:
            ##
            # Convenience override that loads the image using the QImage constructor.
            ##
            fileName = args[0]
            return self.loadFromImage(QImage(fileName), fileName)

    ##
    # This checks if there is a similar tileset in the given list.
    # It is needed for replacing this tileset by its similar copy.
    ##
    def findSimilarTileset(self, tilesets):
        for candidate in tilesets:
            if (candidate.tileCount() != self.tileCount()):
                continue
            if (candidate.imageSource() != self.imageSource()):
                continue
            if (candidate.tileSize() != self.tileSize()):
                continue
            if (candidate.tileSpacing() != self.tileSpacing()):
                continue
            if (candidate.margin() != self.margin()):
                continue
            if (candidate.tileOffset() != self.tileOffset()):
                continue

            # For an image collection tileset, check the image sources
            if (self.imageSource()==''):
                if (not sameTileImages(self, candidate)):
                    continue

            return candidate
            
        return None

    ##
    # Returns the file name of the external image that contains the tiles in
    # this tileset. Is an empty string when this tileset doesn't have a
    # tileset image.
    ##
    def imageSource(self):
        return self.mImageSource

    ##
    # Returns the column count that this tileset would have if the tileset
    # image would have the given \a width. This takes into account the tile
    # size, margin and spacing.
    ##
    def columnCountForWidth(self, width):
        return int((width - self.mMargin + self.mTileSpacing) / (self.mTileWidth + self.mTileSpacing))

    ##
    # Returns a const reference to the list of terrains in this tileset.
    ##
    def terrains(self):
        return QList(self.mTerrainTypes)

    ##
    # Returns the number of terrain types in this tileset.
    ##
    def terrainCount(self):
        return self.mTerrainTypes.size()

    ##
    # Returns the terrain type at the given \a index.
    ##
    def terrain(self, index):
        if index >= 0:
            _x = self.mTerrainTypes[index]
        else:
            _x = None
        return _x

    ##
    # Adds a new terrain type.
    #
    # @param name      the name of the terrain
    # @param imageTile the id of the tile that represents the terrain visually
    # @return the created Terrain instance
    ##
    def addTerrain(self, name, imageTileId):
        terrain = Terrain(self.terrainCount(), self, name, imageTileId)
        self.insertTerrain(self.terrainCount(), terrain)
        return terrain

    ##
    # Adds the \a terrain type at the given \a index.
    #
    # The terrain should already have this tileset associated with it.
    ##
    def insertTerrain(self, index, terrain):
        self.mTerrainTypes.insert(index, terrain)
        # Reassign terrain IDs
        for terrainId in range(index, self.mTerrainTypes.size()):
            self.mTerrainTypes.at(terrainId).mId = terrainId
        # Adjust tile terrain references
        for tile in self.mTiles:
            for corner in range(4):
                terrainId = tile.cornerTerrainId(corner)
                if (terrainId >= index):
                    tile.setCornerTerrainId(corner, terrainId + 1)

        self.mTerrainDistancesDirty = True

    ##
    # Removes the terrain type at the given \a index and returns it. The
    # caller becomes responsible for the lifetime of the terrain type.
    #
    # This will cause the terrain ids of subsequent terrains to shift up to
    # fill the space and the terrain information of all tiles in this tileset
    # will be updated accordingly.
    ##
    def takeTerrainAt(self, index):
        terrain = self.mTerrainTypes.takeAt(index)
        # Reassign terrain IDs
        for terrainId in range(index, self.mTerrainTypes.size()):
            self.mTerrainTypes.at(terrainId).mId = terrainId

        # Clear and adjust tile terrain references
        for tile in self.mTiles:
            for corner in range(4):
                terrainId = tile.cornerTerrainId(corner)
                if (terrainId == index):
                    tile.setCornerTerrainId(corner, 0xFF)
                elif (terrainId > index):
                    tile.setCornerTerrainId(corner, terrainId - 1)

        self.mTerrainDistancesDirty = True
        return terrain

    ##
    # Returns the transition penalty(/distance) between 2 terrains. -1 if no
    # transition is possible.
    ##
    def terrainTransitionPenalty(self, terrainType0, terrainType1):
        if (self.mTerrainDistancesDirty):
            self.recalculateTerrainDistances()
            self.mTerrainDistancesDirty = False

        if terrainType0 == 255:
            terrainType0 = -1
        if terrainType1 == 255:
            terrainType1 = -1

        # Do some magic, since we don't have a transition array for no-terrain
        if (terrainType0 == -1 and terrainType1 == -1):
            return 0
        if (terrainType0 == -1):
            return self.mTerrainTypes.at(terrainType1).transitionDistance(terrainType0)
        return self.mTerrainTypes.at(terrainType0).transitionDistance(terrainType1)

    ##
    # Adds a new tile to the end of the tileset.
    ##
    def addTile(self, image, source=QString()):
        newTile = Tile(image, source, self.tileCount(), self)
        self.mTiles.append(newTile)
        if (self.mTileHeight < image.height()):
            self.mTileHeight = image.height()
        if (self.mTileWidth < image.width()):
            self.mTileWidth = image.width()
        return newTile

    def insertTiles(self, index, tiles):
        count = tiles.count()
        for i in range(count):
            self.mTiles.insert(index + i, tiles.at(i))
        # Adjust the tile IDs of the remaining tiles
        for i in range(index + count, self.mTiles.size()):
            self.mTiles.at(i).mId += count
        self.updateTileSize()

    def removeTiles(self, index, count):
        first = self.mTiles.begin() + index
        last = first + count
        last = self.mTiles.erase(first, last)
        # Adjust the tile IDs of the remaining tiles
        for last in self.mTiles:
            last.mId -= count
        self.updateTileSize()

    ##
    # Sets the \a image to be used for the tile with the given \a id.
    ##
    def setTileImage(self, id, image, source = QString()):
        # This operation is not supposed to be used on tilesets that are based
        # on a single image
        tile = self.tileAt(id)
        if (not tile):
            return
        previousImageSize = tile.image().size()
        newImageSize = image.size()
        tile.setImage(image)
        tile.setImageSource(source)
        if (previousImageSize != newImageSize):
            # Update our max. tile size
            if (previousImageSize.height() == self.mTileHeight or
                    previousImageSize.width() == self.mTileWidth):
                # This used to be the max image; we have to recompute
                self.updateTileSize()
            else:
                # Check if we have a new maximum
                if (self.mTileHeight < newImageSize.height()):
                    self.mTileHeight = newImageSize.height()
                if (self.mTileWidth < newImageSize.width()):
                    self.mTileWidth = newImageSize.width()

    ##
    # Used by the Tile class when its terrain information changes.
    ##
    def markTerrainDistancesDirty(self):
        self.mTerrainDistancesDirty = True

    ##
    # Sets tile size to the maximum size.
    ##
    def updateTileSize(self):
        maxWidth = 0
        maxHeight = 0
        for tile in self.mTiles:
            size = tile.size()
            if (maxWidth < size.width()):
                maxWidth = size.width()
            if (maxHeight < size.height()):
                maxHeight = size.height()

        self.mTileWidth = maxWidth
        self.mTileHeight = maxHeight

    ##
    # Calculates the transition distance matrix for all terrain types.
    ##
    def recalculateTerrainDistances(self):
        # some fancy macros which can search for a value in each byte of a word simultaneously
        def hasZeroByte(dword):
            return (dword - 0x01010101) & ~dword & 0x80808080

        def hasByteEqualTo(dword, value):
            return hasZeroByte(dword ^ int(~0/255 * value))

        # Terrain distances are the number of transitions required before one terrain may meet another
        # Terrains that have no transition path have a distance of -1
        for i in range(self.terrainCount()):
            type = self.terrain(i)
            distance = QVector()
            for _x in range(self.terrainCount() + 1):
                distance.append(-1)
            # Check all tiles for transitions to other terrain types
            for j in range(self.tileCount()):
                t = self.tileAt(j)
                if (not hasByteEqualTo(t.terrain(), i)):
                    continue
                # This tile has transitions, add the transitions as neightbours (distance 1)
                tl = t.cornerTerrainId(0)
                tr = t.cornerTerrainId(1)
                bl = t.cornerTerrainId(2)
                br = t.cornerTerrainId(3)
                # Terrain on diagonally opposite corners are not actually a neighbour
                if (tl == i or br == i):
                    distance[tr + 1] = 1
                    distance[bl + 1] = 1

                if (tr == i or bl == i):
                    distance[tl + 1] = 1
                    distance[br + 1] = 1

                # terrain has at least one tile of its own type
                distance[i + 1] = 0

            type.setTransitionDistances(distance)

        # Calculate indirect transition distances
        bNewConnections = False
        # Repeat while we are still making new connections (could take a
        # number of iterations for distant terrain types to connect)
        while bNewConnections:
            bNewConnections = False
            # For each combination of terrain types
            for i in range(self.terrainCount()):
                t0 = self.terrain(i)
                for j in range(self.terrainCount()):
                    if (i == j):
                        continue
                    t1 = self.terrain(j)
                    # Scan through each terrain type, and see if we have any in common
                    for t in range(-1, self.terrainCount()):
                        d0 = t0.transitionDistance(t)
                        d1 = t1.transitionDistance(t)
                        if (d0 == -1 or d1 == -1):
                            continue
                        # We have cound a common connection
                        d = t0.transitionDistance(j)
                        # If the new path is shorter, record the new distance
                        if (d == -1 or d0 + d1 < d):
                            d = d0 + d1
                            t0.setTransitionDistance(j, d)
                            t1.setTransitionDistance(i, d)
                            # We're making progress, flag for another iteration...
                            bNewConnections = True

    def sharedPointer(self):
        return self.mWeakPointer
