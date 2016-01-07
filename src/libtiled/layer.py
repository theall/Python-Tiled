##
# layer.py
# Copyright 2008-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from object import Object
from PyQt5.QtCore import (
    QRect,
    QSize,
    QPoint,
    QPointF
)

##
# A map layer.
##
class Layer(Object):
    AnyLayerType = 0xFF
    TileLayerType   = 0x01
    ObjectGroupType = 0x02
    ImageLayerType  = 0x04
    ##
    # Constructor.
    ##
    def __init__(self, type, name, x, y, width, height):
        super().__init__(Object.LayerType)

        self.mName = name
        self.mLayerType = type
        self.mX = x
        self.mY = y
        self.mWidth = width
        self.mHeight = height
        self.mOpacity = 1.0
        self.mVisible = True
        self.mMap = None
        self.mOffset = QPointF()

    ##
    # Returns the type of this layer.
    ##
    def layerType(self):
        return self.mLayerType

    ##
    # Returns the name of this layer.
    ##
    def name(self):
        return self.mName

    ##
    # Sets the name of this layer.
    ##
    def setName(self, name):
        self.mName = name

    ##
    # Returns the opacity of this layer.
    ##
    def opacity(self):
        return self.mOpacity

    ##
    # Sets the opacity of this layer.
    ##
    def setOpacity(self, opacity):
        self.mOpacity = opacity

    ##
    # Returns the visibility of this layer.
    ##
    def isVisible(self):
        return self.mVisible

    ##
    # Sets the visibility of this layer.
    ##
    def setVisible(self, visible):
        self.mVisible = visible

    ##
    # Returns the map this layer is part of.
    ##
    def map(self):
        return self.mMap

    ##
    # Sets the map this layer is part of. Should only be called from the
    # Map class.
    ##
    def setMap(self, map):
        self.mMap = map

    ##
    # Returns the x position of this layer (in tiles).
    ##
    def x(self):
        return self.mX

    ##
    # Sets the x position of this layer (in tiles).
    ##
    def setX(self, x):
        self.mX = x

    ##
    # Returns the y position of this layer (in tiles).
    ##
    def y(self):
        return self.mY

    ##
    # Sets the y position of this layer (in tiles).
    ##
    def setY(self, y):
        self.mY = y

    ##
    # Returns the position of this layer (in tiles).
    ##
    def position(self):
        return QPoint(self.mX, self.mY)

    ##
    # Sets the position of this layer (in tiles).
    ##
    def setPosition(self, *args):
        l = len(args)
        if l==1:
            pos = args[0]
            self.setPosition(pos.x(), pos.y())
        elif l==2:
            x, y = args
            self.mX = x
            self.mY = y

    ##
    # Returns the width of this layer.
    ##
    def width(self):
        return self.mWidth

    ##
    # Returns the height of this layer.
    ##
    def height(self):
        return self.mHeight

    ##
    # Returns the size of this layer.
    ##
    def size(self, *args):
        l = len(args)
        if l==0:
            return QSize(self.mWidth, self.mHeight)
        elif l==1:
            size = args[0]
            self.mWidth = size.width()
            self.mHeight = size.height()

    ##
    # Returns the bounds of this layer.
    ##
    def bounds(self):
        return QRect(self.mX, self.mY, self.mWidth, self.mHeight)

    ##
    # Sets the drawing offset in pixels of this layer.
    ##
    def setOffset(self, offset):
        self.mOffset = offset

    ##
    # Returns the drawing offset in pixels of this layer.
    ##
    def offset(self):
        return self.mOffset

    def isEmpty(self):
        pass

    ##
    # Computes and returns the set of tilesets used by this layer.
    ##
    def usedTilesets(self):
        pass
    ##
    # Returns whether this layer is referencing the given tileset.
    ##
    def referencesTileset(self, tileset):
        pass
    ##
    # Replaces all references to tiles from \a oldTileset with tiles from
    # \a newTileset.
    ##
    def replaceReferencesToTileset(self, oldTileset, newTileset):
        pass
    ##
    # Returns whether this layer can merge together with the \a other layer.
    ##
    def canMergeWith(self, other):
        pass
    ##
    # Returns a newly allocated layer that is the result of merging this layer
    # with the \a other layer. Where relevant, the other layer is considered
    # to be on top of this one.
    #
    # Should only be called when canMergeWith returns True.
    ##
    def mergedWith(self, other):
        pass
    ##
    # Returns a duplicate of this layer. The caller is responsible for the
    # ownership of this newly created layer.
    ##
    def clone(self):
        pass
    # These functions allow checking whether this Layer is an instance of the
    # given subclass without relying on a dynamic_cast.
    def isTileLayer(self):
        return self.mLayerType == Layer.TileLayerType

    def isObjectGroup(self):
        return self.mLayerType == Layer.ObjectGroupType

    def isImageLayer(self):
        return self.mLayerType == Layer.ImageLayerType

    # These actually return this layer cast to one of its subclasses.
    def asTileLayer(self):
        if self.isTileLayer():
            return self
        return None

    def asObjectGroup(self):
        if self.isObjectGroup():
            return self
        return None

    def asImageLayer(self):
        if self.isImageLayer():
            return self
        return None

    ##
    # A helper function for initializing the members of the given instance to
    # those of this layer. Used by subclasses when cloning.
    #
    # Layer name, position and size are not cloned, since they are assumed to have
    # already been passed to the constructor. Also, map ownership is not cloned,
    # since the clone is not added to the map.
    #
    # \return the initialized clone (the same instance that was passed in)
    # \sa clone()
    ##
    def initializeClone(self, clone):
        clone.mOffset = self.mOffset
        clone.mOpacity = self.mOpacity
        clone.mVisible = self.mVisible
        clone.setProperties(self.properties())
        return clone

    ##
    # Sets the size of this layer.
    ##
    def setSize(self, size):
        self.mWidth = size.width()
        self.mHeight = size.height()
