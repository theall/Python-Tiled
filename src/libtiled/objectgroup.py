##
# objectgroup.py
# Copyright 2008, Roderic Morris <roderic@ccs.neu.edu>
# Copyright 2008-2014, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2009-2010, Jeff Bland <jeff@teamphobic.com>
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
from tileset import Tileset
from layer import Layer
from pyqtcore import QList, QString, QSet
from PyQt5.QtCore import (
    QRectF,
    QPointF
)
from PyQt5.QtGui import (
    QColor
)

##
# Helper function that converts a drawing order to its string value. Useful
# for map writers.
#
# @return The draw order as a lowercase string.
##
def drawOrderToString(drawOrder):
    if drawOrder==ObjectGroup.DrawOrder.TopDownOrder:
        return "topdown"
    elif drawOrder==ObjectGroup.DrawOrder.IndexOrder:
        return "index"
    return "unknown"

##
# Helper function that converts a string to a drawing order enumerator.
# Useful for map readers.
#
# @return The draw order matching the given string, or
#         ObjectGroup.UnknownOrder if the string is unrecognized.
##
def drawOrderFromString(string):
    drawOrder = ObjectGroup.DrawOrder.UnknownOrder

    if string == "topdown":
        drawOrder = ObjectGroup.DrawOrder.TopDownOrder
    elif string == "index":
        drawOrder = ObjectGroup.DrawOrder.IndexOrder

    return drawOrder

##
# A group of objects on a map.
##
class ObjectGroup(Layer):
    ##
    # Objects within an object group can either be drawn top down (sorted
    # by their y-coordinate) or by index (manual stacking order).
    #
    # The default is top down.
    ##
    class DrawOrder():
        UnknownOrder = -1
        TopDownOrder = 1
        IndexOrder = 2

    ##
    # Default constructor.
    ##
    def __init__(self, *args):
        self.mObjects = QList()
        self.mColor = QColor()

        l = len(args)
        if l==0:
            super().__init__(Layer.ObjectGroupType, QString(), 0, 0, 0, 0)
        elif l==5:
            ##
            # Constructor with some parameters.
            ##
            name, x, y, width, height = args

            super().__init__(Layer.ObjectGroupType, name, x, y, width, height)
        else:
            pass
        self.mDrawOrder = ObjectGroup.DrawOrder.IndexOrder

    ##
    # Destructor.
    ##
    def __del__(self):
        self.mObjects.clear()

    ##
    # Returns a pointer to the list of objects in this object group.
    ##
    def objects(self):
        return QList(self.mObjects)

    ##
    # Returns the number of objects in this object group.
    ##
    def objectCount(self):
        return self.mObjects.size()

    ##
    # Returns the object at the specified index.
    ##
    def objectAt(self, index):
        return self.mObjects.at(index)

    ##
    # Adds an object to this object group.
    ##
    def addObject(self, object):
        self.mObjects.append(object)
        object.setObjectGroup(self)
        if (self.mMap and object.id() == 0):
            object.setId(self.mMap.takeNextObjectId())

    ##
    # Inserts an object at the specified index. This is only used for undoing
    # the removal of an object at the moment, to make sure not to change the
    # saved order of the objects.
    ##
    def insertObject(self, index, object):
        self.mObjects.insert(index, object)
        object.setObjectGroup(self)
        if (self.mMap and object.id() == 0):
            object.setId(self.mMap.takeNextObjectId())

    ##
    # Removes an object from this object group. Ownership of the object is
    # transferred to the caller.
    #
    # @return the index at which the specified object was removed
    ##
    def removeObject(self, object):
        index = self.mObjects.indexOf(object)
        self.mObjects.removeAt(index)
        object.setObjectGroup(None)
        return index

    ##
    # Removes the object at the given index. Ownership of the object is
    # transferred to the caller.
    #
    # This is faster than removeObject when you've already got the index.
    #
    # @param index the index at which to remove an object
    ##
    def removeObjectAt(self, index):
        object = self.mObjects.takeAt(index)
        object.setObjectGroup(None)

    ##
    # Moves \a count objects starting at \a from to the index given by \a to.
    #
    # The \a to index may not lie within the range of objects that is
    # being moved.
    ##
    def moveObjects(self, _from, to, count):
        # It's an error when 'to' lies within the moving range of objects
        # Nothing to be done when 'to' is the start or the end of the range, or
        # when the number of objects to be moved is 0.
        if (to == _from or to == _from + count or count == 0):
            return
        movingObjects = self.mObjects[_from, count]
        self.mObjects.erase(self.mObjects.begin() + _from, self.mObjects.begin() + _from + count)
        if (to > _from):
            to -= count
        for i in range(count):
            self.mObjects.insert(to + i, movingObjects.at(i))

    ##
    # Returns the bounding rect around all objects in this object group.
    ##
    def objectsBoundingRect(self):
        boundingRect = QRectF()
        for object in self.mObjects:
            boundingRect = boundingRect.united(object.bounds())
        return boundingRect

    ##
    # Returns whether this object group contains any objects.
    ##
    def isEmpty(self):
        return self.mObjects.isEmpty()

    ##
    # Computes and returns the set of tilesets used by this object group.
    ##
    def usedTilesets(self):
        tilesets = QSet()
        for object in self.mObjects:
            tile = object.cell().tile
            if tile:
                tilesets.insert(tile.sharedTileset())
        return tilesets

    ##
    # Returns whether any tile objects in this object group reference tiles
    # in the given tileset.
    ##
    def referencesTileset(self, tileset):
        for object in self.mObjects:
            tile = object.cell().tile
            if (tile and tile.tileset() == tileset):
                return True

        return False

    ##
    # Replaces all references to tiles from \a oldTileset with tiles from
    # \a newTileset.
    ##
    def replaceReferencesToTileset(self, oldTileset, newTileset):
        for object in self.mObjects:
            tile = object.cell().tile
            if (tile and tile.tileset() == oldTileset):
                cell = object.cell()
                cell.tile = Tileset.tileAt(tile.id())
                object.setCell(cell)

    ##
    # Offsets all objects within the group by the \a offset given in pixel
    # coordinates, and optionally wraps them. The object's center must be
    # within \a bounds, and wrapping occurs if the displaced center is out of
    # the bounds.
    #
    # \sa TileLayer.offset()
    ##
    def offsetObjects(self, offset, bounds, wrapX, wrapY):
        for object in self.mObjects:
            objectCenter = object.bounds().center()
            if (not bounds.contains(objectCenter)):
                continue
            newCenter = QPointF(objectCenter + offset)
            if (wrapX and bounds.width() > 0):
                nx = math.fmod(newCenter.x() - bounds.left(), bounds.width())
                if nx < 0:
                    x = bounds.width() + nx
                else:
                    x = nx
                newCenter.setX(bounds.left() + x)

            if (wrapY and bounds.height() > 0):
                ny = math.fmod(newCenter.y() - bounds.top(), bounds.height())
                if ny < 0:
                    x = bounds.height() + ny
                else:
                    x = ny
                newCenter.setY(bounds.top() + x)

            object.setPosition(object.position() + (newCenter - objectCenter))

    def canMergeWith(self, other):
        return other.isObjectGroup()

    def mergedWith(self, other):
        og = other
        merged = self.clone()
        for mapObject in og.objects():
            merged.addObject(mapObject.clone())
        return merged

    ##
    # Returns the color of the object group, or an invalid color if no color
    # is set.
    ##
    def color(self):
        return self.mColor

    ##
    # Sets the display color of the object group.
    ##
    def setColor(self, color):
        if type(color) != QColor:
            color = QColor(color)
        self.mColor = color

    ##
    # Returns the draw order for the objects in this group.
    #
    # \sa ObjectGroup.DrawOrder
    ##
    def drawOrder(self):
        return self.mDrawOrder

    ##
    # Sets the draw order for the objects in this group.
    #
    # \sa ObjectGroup.DrawOrder
    ##
    def setDrawOrder(self, drawOrder):
        self.mDrawOrder = drawOrder

    ##
    # Returns a duplicate of this ObjectGroup.
    #
    # \sa Layer.clone()
    ##
    def clone(self):
        return self.initializeClone(ObjectGroup(self.mName, self.mX, self.mY, self.mWidth, self.mHeight))

    def initializeClone(self, clone):
        super().initializeClone(clone)
        for object in self.mObjects:
            clone.addObject(object.clone())
        clone.setColor(self.mColor)
        clone.setDrawOrder(self.mDrawOrder)
        return clone
