##
# tilelayer.py
# Copyright 2008-2011, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2009, Jeff Bland <jeff@teamphobic.com>
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

from libtiled.tiled import FlipDirection, RotateDirection
from layer import Layer
from pyqtcore import QSet, QString, QVector
from PyQt5.QtGui import (
    QRegion
)
from PyQt5.QtCore import (
    QSize,
    QRect,
    QMargins
)
def maxSize(a, b):
    return QSize(max(a.width(), b.width()),
                 max(a.height(), b.height()))

def maxMargins(a, b):
    return QMargins(max(a.left(), b.left()),
                    max(a.top(), b.top()),
                    max(a.right(), b.right()),
                    max(a.bottom(), b.bottom()))

##
# A cell on a tile layer grid.
##
class Cell():
    def __init__(self, *args):
        l = len(args)
        if l==0:
            self.tile = None
        elif l==1:
            tile = args[0]
            self.tile = tile
        self.flippedHorizontally = False
        self.flippedVertically = False
        self.flippedAntiDiagonally = False

    def isEmpty(self):
        return self.tile == None

    def __eq__(self, other):
        return self.tile == other.tile \
            and self.flippedHorizontally == other.flippedHorizontally \
            and self.flippedVertically == other.flippedVertically \
            and self.flippedAntiDiagonally == other.flippedAntiDiagonally

    def __ne__(self, other):
        return self.tile != other.tile \
                or self.flippedHorizontally != other.flippedHorizontally \
                or self.flippedVertically != other.flippedVertically \
                or self.flippedAntiDiagonally != other.flippedAntiDiagonally

##
# A tile layer is a grid of cells. Each cell refers to a specific tile, and
# stores how the tile is flipped.
#
# Coordinates and regions passed to function parameters are in local
# coordinates and do not take into account the position of the layer.
##
class TileLayer(Layer):
    ##
    # Constructor.
    ##
    def __init__(self, name, x, y, width, height):
        super().__init__(Layer.TileLayerType, name, x, y, width, height)
        self.mMaxTileSize = QSize(0, 0)
        self.mGrid = QVector()
        for i in range(width * height):
            self.mGrid.append(Cell())
        self.mOffsetMargins = QMargins()

    def __iter__(self):
        return self.mGrid.__iter__()
        
    ##
    # Returns the maximum tile size of this layer.
    ##
    def maxTileSize(self):
        return self.mMaxTileSize

    ##
    # Returns the margins that have to be taken into account while drawing
    # this tile layer. The margins depend on the maximum tile size and the
    # offset applied to the tiles.
    ##
    def drawMargins(self):
        return QMargins(self.mOffsetMargins.left(),
                        self.mOffsetMargins.top() + self.mMaxTileSize.height(),
                        self.mOffsetMargins.right() + self.mMaxTileSize.width(),
                        self.mOffsetMargins.bottom())

    ##
    # Recomputes the draw margins. Needed after the tile offset of a tileset
    # has changed for example.
    #
    # Generally you want to call Map.recomputeDrawMargins instead.
    ##
    def recomputeDrawMargins(self):
        maxTileSize = QSize(0, 0)
        offsetMargins = QMargins()
        i = 0
        while(i<self.mGrid.size()):
            cell = self.mGrid.at(i)
            tile = cell.tile
            if tile:
                size = tile.size()
                if (cell.flippedAntiDiagonally):
                    size.transpose()
                offset = tile.offset()
                maxTileSize = maxSize(size, maxTileSize)
                offsetMargins = maxMargins(QMargins(-offset.x(),
                                                     -offset.y(),
                                                     offset.x(),
                                                     offset.y()),
                                            offsetMargins)
            i += 1

        self.mMaxTileSize = maxTileSize
        self.mOffsetMargins = offsetMargins
        if (self.mMap):
            self.mMap.adjustDrawMargins(self.drawMargins())

    ##
    # Returns whether (x, y) is inside this map layer.
    ##
    def contains(self, *args):
        l = len(args)
        if l==2:
            x, y = args
            return x >= 0 and y >= 0 and x < self.mWidth and y < self.mHeight
        elif l==1:
            point = args[0]
            return self.contains(point.x(), point.y())

    ##
    # Calculates the region of cells in this tile layer for which the given
    # \a condition returns True.
    ##
    def region(self, *args):
        l = len(args)
        if l==1:
            condition = args[0]
            region = QRegion()
            for y in range(self.mHeight):
                for x in range(self.mWidth):
                    if (condition(self.cellAt(x, y))):
                        rangeStart = x
                        x += 1
                        while(x<=self.mWidth):
                            if (x == self.mWidth or not condition(self.cellAt(x, y))):
                                rangeEnd = x
                                region += QRect(rangeStart + self.mX, y + self.mY,
                                                rangeEnd - rangeStart, 1)
                                break
                            x += 1

            return region
        elif l==0:
            ##
            # Calculates the region occupied by the tiles of this layer. Similar to
            # Layer.bounds(), but leaves out the regions without tiles.
            ##
            return self.region(lambda cell:not cell.isEmpty())

    ##
    # Returns a read-only reference to the cell at the given coordinates. The
    # coordinates have to be within this layer.
    ##
    def cellAt(self, *args):
        l = len(args)
        if l==2:
            x, y = args
            return self.mGrid.at(x + y * self.mWidth)
        elif l==1:
            point = args[0]
            return self.cellAt(point.x(), point.y())

    ##
    # Sets the cell at the given coordinates.
    ##
    def setCell(self, x, y, cell):
        if (cell.tile):
            size = cell.tile.size()
            if (cell.flippedAntiDiagonally):
                size.transpose()
            offset = cell.tile.offset()
            self.mMaxTileSize = maxSize(size, self.mMaxTileSize)
            self.mOffsetMargins = maxMargins(QMargins(-offset.x(),
                                                 -offset.y(),
                                                 offset.x(),
                                                 offset.y()),
                                        self.mOffsetMargins)
            if (self.mMap):
                self.mMap.adjustDrawMargins(self.drawMargins())

        self.mGrid[x + y * self.mWidth] = cell

    ##
    # Returns a copy of the area specified by the given \a region. The
    # caller is responsible for the returned tile layer.
    ##
    def copy(self, *args):
        l = len(args)
        if l==1:
            region = args[0]
            if type(region) != QRegion:
                region = QRegion(region)
            area = region.intersected(QRect(0, 0, self.width(), self.height()))
            bounds = region.boundingRect()
            areaBounds = area.boundingRect()
            offsetX = max(0, areaBounds.x() - bounds.x())
            offsetY = max(0, areaBounds.y() - bounds.y())
            copied = TileLayer(QString(), 0, 0, bounds.width(), bounds.height())
            for rect in area.rects():
                for x in range(rect.left(), rect.right()+1):
                    for y in range(rect.top(), rect.bottom()+1):
                        copied.setCell(x - areaBounds.x() + offsetX,
                                        y - areaBounds.y() + offsetY,
                                        self.cellAt(x, y))
            return copied
        elif l==4:
            x, y, width, height = args

            return self.copy(QRegion(x, y, width, height))

    ##
    # Merges the given \a layer onto this layer at position \a pos. Parts that
    # fall outside of this layer will be lost and empty tiles in the given
    # layer will have no effect.
    ##
    def merge(self, pos, layer):
        # Determine the overlapping area
        area = QRect(pos, QSize(layer.width(), layer.height()))
        area &= QRect(0, 0, self.width(), self.height())
        for y in range(area.top(), area.bottom()+1):
            for x in range(area.left(), area.right()+1):
                cell = layer.cellAt(x - pos.x(), y - pos.y())
                if (not cell.isEmpty()):
                    self.setCell(x, y, cell)

    ##
    # Removes all cells in the specified region.
    ##
    def erase(self, area):
        emptyCell = Cell()
        for rect in area.rects():
            for x in range(rect.left(), rect.right()+1):
                for y in range(rect.top(), rect.bottom()+1):
                    self.setCell(x, y, emptyCell)

    ##
    # Sets the cells starting at the given position to the cells in the given
    # \a tileLayer. Parts that fall outside of this layer will be ignored.
    #
    # When a \a mask is given, only cells that fall within this mask are set.
    # The mask is applied in local coordinates.
    ##
    def setCells(self, x, y, layer, mask = QRegion()):
        # Determine the overlapping area
        area = QRegion(QRect(x, y, layer.width(), layer.height()))
        area &= QRect(0, 0, self.width(), self.height())
        if (not mask.isEmpty()):
            area &= mask
        for rect in area.rects():
            for _x in range(rect.left(), rect.right()+1):
                for _y in range(rect.top(), rect.bottom()+1):
                    self.setCell(_x, _y, layer.cellAt(_x - x, _y - y))

    ##
    # Flip this tile layer in the given \a direction. Direction must be
    # horizontal or vertical. This doesn't change the dimensions of the
    # tile layer.
    ##
    def flip(self, direction):
        newGrid = QVector()
        for i in range(self.mWidth * self.mHeight):
            newGrid.append(Cell())
        for y in range(self.mHeight):
            for x in range(self.mWidth):
                dest = newGrid[x + y * self.mWidth]
                if (direction == FlipDirection.FlipHorizontally):
                    source = self.cellAt(self.mWidth - x - 1, y)
                    dest = source
                    dest.flippedHorizontally = not source.flippedHorizontally
                elif (direction == FlipDirection.FlipVertically):
                    source = self.cellAt(x, self.mHeight - y - 1)
                    dest = source
                    dest.flippedVertically = not source.flippedVertically

        self.mGrid = newGrid

    ##
    # Rotate this tile layer by 90 degrees left or right. The tile positions
    # are rotated within the layer, and the tiles themselves are rotated. The
    # dimensions of the tile layer are swapped.
    ##
    def rotate(self, direction):
        rotateRightMask = [5, 4, 1, 0, 7, 6, 3, 2]
        rotateLeftMask  = [3, 2, 7, 6, 1, 0, 5, 4]
        if direction == RotateDirection.RotateRight:
            rotateMask = rotateRightMask
        else:
            rotateMask = rotateLeftMask
        newWidth = self.mHeight
        newHeight = self.mWidth
        newGrid = QVector(newWidth * newHeight)
        for y in range(self.mHeight):
            for x in range(self.mWidth):
                source = self.cellAt(x, y)
                dest = source
                mask = (dest.flippedHorizontally << 2) | (dest.flippedVertically << 1) | (dest.flippedAntiDiagonally << 0)
                mask = rotateMask[mask]
                dest.flippedHorizontally = (mask & 4) != 0
                dest.flippedVertically = (mask & 2) != 0
                dest.flippedAntiDiagonally = (mask & 1) != 0
                if (direction == RotateDirection.RotateRight):
                    newGrid[x * newWidth + (self.mHeight - y - 1)] = dest
                else:
                    newGrid[(self.mWidth - x - 1) * newWidth + y] = dest

        t = self.mMaxTileSize.width()
        self.mMaxTileSize.setWidth(self.mMaxTileSize.height())
        self.mMaxTileSize.setHeight(t)
        self.mWidth = newWidth
        self.mHeight = newHeight
        self.mGrid = newGrid

    ##
    # Computes and returns the set of tilesets used by this tile layer.
    ##
    def usedTilesets(self):
        tilesets = QSet()
        i = 0
        while(i<self.mGrid.size()):
            tile = self.mGrid.at(i).tile
            if tile:
                tilesets.insert(tile.tileset())
            i += 1
        return tilesets

    ##
    # Returns whether this tile layer has any cell for which the given
    # \a condition returns True.
    ##
    def hasCell(self, condition):
        i = 0
        for cell in self.mGrid:
            if (condition(cell)):
                return True
            i += 1
        return False

    ##
    # Returns whether this tile layer is referencing the given tileset.
    ##
    def referencesTileset(self, tileset):
        i = 0
        while(i<self.mGrid.size()):
            tile = self.mGrid.at(i).tile
            if (tile and tile.tileset() == tileset):
                return True
            i += 1
        return False

    ##
    # Removes all references to the given tileset. This sets all tiles on this
    # layer that are from the given tileset to null.
    ##
    def removeReferencesToTileset(self, tileset):
        i = 0
        while(i<self.mGrid.size()):
            tile = self.mGrid.at(i).tile
            if (tile and tile.tileset() == tileset):
                self.mGrid.replace(i, Cell())
            i += 1

    ##
    # Replaces all tiles from \a oldTileset with tiles from \a newTileset.
    ##
    def replaceReferencesToTileset(self, oldTileset, newTileset):
        i = 0
        while(i<self.mGrid.size()):
            tile = self.mGrid.at(i).tile
            if (tile and tile.tileset() == oldTileset):
                self.mGrid[i].tile = newTileset.tileAt(tile.id())
            i += 1

    ##
    # Resizes this tile layer to \a size, while shifting all tiles by
    # \a offset.
    ##
    def resize(self, size, offset):
        if (self.size() == size and offset.isNull()):
            return
        newGrid = QVector()
        for i in range(size.width() * size.height()):
            newGrid.append(Cell())
        # Copy over the preserved part
        startX = max(0, -offset.x())
        startY = max(0, -offset.y())
        endX = min(self.mWidth, size.width() - offset.x())
        endY = min(self.mHeight, size.height() - offset.y())
        for y in range(startY, endY):
            for x in range(startX, endX):
                index = x + offset.x() + (y + offset.y()) * size.width()
                newGrid[index] = self.cellAt(x, y)

        self.mGrid = newGrid
        self.setSize(size)

    ##
    # Offsets the tiles in this layer within \a bounds by \a offset,
    # and optionally wraps them.
    #
    # \sa ObjectGroup.offset()
    ##
    def offsetTiles(self, offset, bounds, wrapX, wrapY):
        newGrid = QVector()
        for i in range(self.mWidth * self.mHeight):
            newGrid.append(Cell())
        for y in range(self.mHeight):
            for x in range(self.mWidth):
                # Skip out of bounds tiles
                if (not bounds.contains(x, y)):
                    newGrid[x + y * self.mWidth] = self.cellAt(x, y)
                    continue

                # Get position to pull tile value from
                oldX = x - offset.x()
                oldY = y - offset.y()
                # Wrap x value that will be pulled from
                if (wrapX and bounds.width() > 0):
                    while oldX < bounds.left():
                        oldX += bounds.width()
                    while oldX > bounds.right():
                        oldX -= bounds.width()

                # Wrap y value that will be pulled from
                if (wrapY and bounds.height() > 0):
                    while oldY < bounds.top():
                        oldY += bounds.height()
                    while oldY > bounds.bottom():
                        oldY -= bounds.height()

                # Set the new tile
                if (self.contains(oldX, oldY) and bounds.contains(oldX, oldY)):
                    newGrid[x + y * self.mWidth] = self.cellAt(oldX, oldY)
                else:
                    newGrid[x + y * self.mWidth] = Cell()

        self.mGrid = newGrid

    def canMergeWith(self, other):
        return other.isTileLayer()

    def mergedWith(self, other):
        o = other
        unitedBounds = self.bounds().united(o.bounds())
        offset = self.position() - unitedBounds.topLeft()
        merged = self.clone()
        merged.resize(unitedBounds.size(), offset)
        merged.merge(o.position() - unitedBounds.topLeft(), o)
        return merged

    ##
    # Returns the region where this tile layer and the given tile layer
    # are different. The relative positions of the layers are taken into
    # account. The returned region is relative to this tile layer.
    ##
    def computeDiffRegion(self, other):
        ret = QRegion()
        dx = other.x() - self.mX
        dy = other.y() - self.mY
        r = QRect(0, 0, self.width(), self.height())
        r &= QRect(dx, dy, other.width(), other.height())
        for y in range(r.top(), r.bottom()+1):
            for x in range(r.left(), r.right()+1):
                if (self.cellAt(x, y) != other.cellAt(x - dx, y - dy)):
                    rangeStart = x
                    while (x <= r.right() and self.cellAt(x, y) != other.cellAt(x - dx, y - dy)):
                        x += 1

                    rangeEnd = x
                    ret += QRect(rangeStart, y, rangeEnd - rangeStart, 1)

        return ret

    ##
    # Returns True if all tiles in the layer are empty.
    ##
    def isEmpty(self):
        i = 0
        while(i<self.mGrid.size()):
            if (not self.mGrid.at(i).isEmpty()):
                return False
            i += 1
        return True

    ##
    # Returns a duplicate of this TileLayer.
    #
    # \sa Layer.clone()
    ##
    def clone(self):
        return self.initializeClone(TileLayer(self.mName, self.mX, self.mY, self.mWidth, self.mHeight))

    def begin(self):
        return self.mGrid.begin()
    
    def end(self):
        return self.mGrid.end()
        
    def initializeClone(self, clone):
        super().initializeClone(clone)
        clone.mGrid = self.mGrid
        clone.mMaxTileSize = self.mMaxTileSize
        clone.mOffsetMargins = self.mOffsetMargins
        return clone
