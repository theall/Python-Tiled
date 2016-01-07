##
# mapobject.py
# Copyright 2008-2013, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2008, Roderic Morris <roderic@ccs.neu.edu>
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
from map import Map
from tilelayer import Cell
from libtiled.tiled import Alignment, FlipDirection
from object import Object
from PyQt5.QtCore import (
    QRectF,
    QSizeF,
    QPointF
)
from PyQt5.QtGui import (
    QPolygonF
)
from pyqtcore import QString

##
# An object on a map. Objects are positioned and scaled using floating point
# values, ensuring they are not limited to the tile grid. They are suitable
# for adding any kind of annotation to your maps, as well as free placement of
# images.
#
# Common usages of objects include defining portals, monsters spawn areas,
# ambient effects, scripted areas, etc.
##
class MapObject(Object):
    ##
    # Enumerates the different object shapes. Rectangle is the default shape.
    # When a polygon is set, the shape determines whether it should be
    # interpreted as a filled polygon or a line.
    ##
    Rectangle, Polygon, Polyline, Ellipse = range(4)

    def __init__(self, *args):
        super().__init__(Object.MapObjectType)

        self.mPolygon = QPolygonF()
        self.mName = QString()
        self.mPos = QPointF()
        self.mCell = Cell()
        self.mType = QString()
        self.mId = 0
        self.mShape = MapObject.Rectangle
        self.mObjectGroup = None
        self.mRotation = 0.0
        self.mVisible = True

        l = len(args)
        if l==0:
            self.mSize = QSizeF(0, 0)
        elif l==4:
            name, _type, pos, size = args

            self.mName = name
            self.mType = _type
            self.mPos = pos
            self.mSize = QSizeF(size)

    ##
    # Returns the id of this object. Each object gets an id assigned that is
    # unique for the map the object is on.
    ##
    def id(self):
        return self.mId

    ##
    # Sets the id of this object.
    ##
    def setId(self, id):
        self.mId = id

    ##
    # Returns the name of this object. The name is usually just used for
    # identification of the object in the editor.
    ##
    def name(self):
        return self.mName

    ##
    # Sets the name of this object.
    ##
    def setName(self, name):
        self.mName = name

    ##
    # Returns the type of this object. The type usually says something about
    # how the object is meant to be interpreted by the engine.
    ##
    def type(self):
        return self.mType

    ##
    # Sets the type of this object.
    ##
    def setType(self, type):
        self.mType = type

    ##
    # Returns the position of this object.
    ##
    def position(self):
        return QPointF(self.mPos)

    ##
    # Sets the position of this object.
    ##
    def setPosition(self, pos):
        self.mPos = pos

    ##
    # Returns the x position of this object.
    ##
    def x(self):
        return self.mPos.x()

    ##
    # Sets the x position of this object.
    ##
    def setX(self, x):
        self.mPos.setX(x)

    ##
    # Returns the y position of this object.
    ##
    def y(self):
        return self.mPos.y()

    ##
    # Sets the x position of this object.
    ##
    def setY(self, y):
        self.mPos.setY(y)

    ##
    # Returns the size of this object.
    ##
    def size(self):
        return self.mSize

    ##
    # Sets the size of this object.
    ##
    def setSize(self, *args):
        l = len(args)
        if l==1:
            size = args[0]
            self.mSize = QSizeF(size)
        elif l==2:
            width, height = args
            self.setSize(QSizeF(width, height))

    ##
    # Returns the width of this object.
    ##
    def width(self):
        return self.mSize.width()

    ##
    # Sets the width of this object.
    ##
    def setWidth(self, width):
        self.mSize.setWidth(width)

    ##
    # Returns the height of this object.
    ##
    def height(self):
        return self.mSize.height()

    ##
    # Sets the height of this object.
    ##
    def setHeight(self, height):
        self.mSize.setHeight(height)

    ##
    # Sets the polygon associated with this object. The polygon is only used
    # when the object shape is set to either Polygon or Polyline.
    #
    # \sa setShape()
    ##
    def setPolygon(self, polygon):
        self.mPolygon = polygon

    ##
    # Returns the polygon associated with this object. Returns an empty
    # polygon when no polygon is associated with this object.
    ##
    def polygon(self):
        return QPolygonF(self.mPolygon)

    ##
    # Sets the shape of the object.
    ##
    def setShape(self, shape):
        self.mShape = shape

    ##
    # Returns the shape of the object.
    ##
    def shape(self):
        return self.mShape

    ##
    # Shortcut to getting a QRectF from position() and size().
    ##
    def bounds(self):
        return QRectF(self.mPos, self.mSize)

    ##
    # Shortcut to getting a QRectF from position() and size() that uses cell tile if present.
    ##
    def boundsUseTile(self):
        if (self.mCell.isEmpty()):
            # No tile so just use regular bounds
            return self.bounds()

        # Using the tile for determing boundary
        # Note the position given is the bottom-left corner so correct for that
        return QRectF(QPointF(self.mPos.x(),
                              self.mPos.y() - self.mCell.tile.height()),
                      self.mCell.tile.size())

    ##
    # Sets the tile that is associated with this object. The object will
    # display as the tile image.
    #
    # \warning The object shape is ignored for tile objects!
    ##
    def setCell(self, cell):
        self.mCell = cell

    ##
    # Returns the tile associated with this object.
    ##
    def cell(self):
        return self.mCell

    ##
    # Returns the object group this object belongs to.
    ##
    def objectGroup(self):
        return self.mObjectGroup

    ##
    # Sets the object group this object belongs to. Should only be called
    # from the ObjectGroup class.
    ##
    def setObjectGroup(self, objectGroup):
        self.mObjectGroup = objectGroup

    ##
    # Returns the rotation of the object in degrees.
    ##
    def rotation(self):
        return self.mRotation

    ##
    # Sets the rotation of the object in degrees.
    ##
    def setRotation(self, rotation):
        self.mRotation = rotation

    ##
    # This is somewhat of a workaround for dealing with the ways different objects
    # align.
    #
    # Traditional rectangle objects have top-left alignment.
    # Tile objects have bottom-left alignment on orthogonal maps, but
    # bottom-center alignment on isometric maps.
    #
    # Eventually, the object alignment should probably be configurable. For
    # backwards compatibility, it will need to be configurable on a per-object
    # level.
    ##
    def alignment(self):
        if (self.mCell.isEmpty()):
            return Alignment.TopLeft
        elif (self.mObjectGroup):
            map = self.mObjectGroup.map()
            if map:
                if (map.orientation() == Map.Orientation.Isometric):
                    return Alignment.Bottom

        return Alignment.BottomLeft

    def isVisible(self):
        return self.mVisible
    
    def setVisible(self, visible):
        self.mVisible = visible

    ##
    # Flip this object in the given \a direction. This doesn't change the size
    # of the object.
    ##
    def flip(self, direction):
        if (not self.mCell.isEmpty()):
            if (direction == FlipDirection.FlipHorizontally):
                self.mCell.flippedHorizontally = not self.mCell.flippedHorizontally
            elif (direction == FlipDirection.FlipVertically):
                self.mCell.flippedVertically = not self.mCell.flippedVertically

        if (not self.mPolygon.isEmpty()):
            center2 = self.mPolygon.boundingRect().center() * 2
            if (direction == FlipDirection.FlipHorizontally):
                for i in range(self.mPolygon.size()):
                    # oh, QPointF mPolygon returned is a copy of internal object
                    self.mPolygon[i] = QPointF(center2.x() - self.mPolygon[i].x(), self.mPolygon[i].y())
            elif (direction == FlipDirection.FlipVertically):
                for i in range(self.mPolygon.size()):
                    self.mPolygon[i] = QPointF(self.mPolygon[i].x(), center2.y() - self.mPolygon[i].y())

    ##
    # Returns a duplicate of this object. The caller is responsible for the
    # ownership of this newly created object.
    ##
    def clone(self):
        o = MapObject(self.mName, self.mType, self.mPos, self.mSize)
        o.setProperties(self.properties())
        o.setPolygon(self.mPolygon)
        o.setShape(self.mShape)
        o.setCell(self.mCell)
        o.setRotation(self.mRotation)
        return o
