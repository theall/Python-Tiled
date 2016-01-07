##
# maprenderer.py
# Copyright 2009-2011, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from pyqtcore import QVector
from PyQt5.QtCore import (
    Qt,
    QRect, 
    QRectF,
    QSizeF,
    QPoint, 
    QPointF
)
from PyQt5.QtGui import (
    QVector2D,
    QPolygonF, 
    QPaintEngine,
    QPainter
)
##
# Converts a line running from \a start to \a end to a polygon which
# extends 5 pixels from the line in all directions.
##
def hasOpenGLEngine(painter):
    type = painter.paintEngine().type()
    return (type == QPaintEngine.OpenGL or
            type == QPaintEngine.OpenGL2)

##
# Renders any remaining cells.
##

class RenderFlag():
    ShowTileObjectOutlines = 0x1

RenderFlags = RenderFlag

##
# This interface is used for rendering tile layers and retrieving associated
# metrics. The different implementations deal with different map
# orientations.
##
class MapRenderer():

    def __init__(self, map):
        self.mMap = map
        self.mFlags = 0
        self.mObjectLineWidth = 2
        self.mPainterScale = 1

    def __del__(self):
        pass

    ##
    # Returns the size in pixels of the map associated with this renderer.
    ##
    def mapSize(self):
        pass

    ##
    # Returns the bounding rectangle in pixels of the given \a rect given in
    # tile coordinates.
    #
    # This is useful for calculating the bounding rect of a tile layer or of
    # a region of tiles that was changed.
    ##
    def boundingRect(self, rect):
        pass

    ##
    # Returns the bounding rectangle in pixels of the given \a object, as it
    # would be drawn by drawMapObject().
    ##
    #def boundingRect(self, object):
        #pass

    ##
    # Returns the bounding rectangle in pixels of the given \a imageLayer, as
    # it would be drawn by drawImageLayer().
    ##
    def boundingRect_(self, imageLayer):
        return QRectF(QPointF(imageLayer.position()), QSizeF(imageLayer.image().size()))

    ##
    # Returns the shape in pixels of the given \a object. This is used for
    # mouse interaction and should match the rendered object as closely as
    # possible.
    ##
    def shape(self, object):
        pass

    ##
    # Draws the tile grid in the specified \a rect using the given
    # \a painter.
    ##
    def drawGrid(self, painter, rect, gridColor = Qt.black):
        pass

    ##
    # Draws the given \a layer using the given \a painter.
    #
    # Optionally, you can pass in the \a exposed rect (of pixels), so that
    # only tiles that can be visible in this area will be drawn.
    ##
    def drawTileLayer(self, painter, layer, exposed = QRectF()):
        pass

    ##
    # Draws the tile selection given by \a region in the specified \a color.
    #
    # The implementation can be optimized by taking into account the
    # \a exposed rectangle, to avoid drawing too much.
    ##
    def drawTileSelection(self, painter, region, color, exposed):
        pass

    ##
    # Draws the \a object in the given \a color using the \a painter.
    ##
    def drawMapObject(self, painter, object, color):
        pass

    ##
    # Draws the given image \a layer using the given \a painter.
    ##
    def drawImageLayer(self, painter, imageLayer, exposed = QRectF()):
        painter.drawPixmap(imageLayer.position(), imageLayer.image())

    ##
    # Returns the tile coordinates matching the given pixel position.
    ##
    def pixelToTileCoords(self, x, y):
        pass

    def pixelToTileCoords_(self, point):
        return self.pixelToTileCoords(point.x(), point.y())

    ##
    # Returns the screen position matching the given pixel position.
    ##
    def pixelToScreenCoords(self, x, y):
        pass

    def pixelToScreenCoords_(self, arg):
        tp = type(arg)
        if tp==QPointF:
            point = arg
            return self.pixelToScreenCoords(point.x(), point.y())
        elif tp==QPolygonF:
            polygon = arg
            screenPolygon = QPolygonF(polygon.size())
            for i in range(polygon.size() - 1, -1, -1):
                screenPolygon[i] = self.pixelToScreenCoords_(polygon[i])
            return screenPolygon
        elif tp==QRectF:
            return self.pixelToScreenCoords_(QPolygonF(arg))
    
    ##
    # Returns the pixel coordinates matching the given tile coordinates.
    ##
    def tileToPixelCoords(self, x, y):
        pass

    def tileToPixelCoords_(self, arg):
        tp = type(arg)
        if tp==QPoint:
            arg = QPointF(arg)
            tp = QPointF
        elif tp==QRect:
            arg = QRectF(arg)
            tp = QRectF
        if tp==QPointF:
            point = arg
            return self.tileToPixelCoords(point.x(), point.y())
        elif tp==QRectF:
            area = arg
            return QRectF(self.tileToPixelCoords_(area.topLeft()), self.tileToPixelCoords_(area.bottomRight()))

    ##
    # Returns the tile coordinates matching the given screen position.
    ##
    def screenToTileCoords(self, x, y):
        pass

    def screenToTileCoords_(self, point):
        return self.screenToTileCoords(point.x(), point.y())

    ##
    # Returns the screen position matching the given tile coordinates.
    ##
    def tileToScreenCoords(self, x, y):
        pass

    def tileToScreenCoords_(self, point):
        return self.tileToScreenCoords(point.x(), point.y())

    ##
    # Returns the pixel position matching the given screen position.
    ##
    def screenToPixelCoords(self, x, y):
        pass

    def screenToPixelCoords_(self, point):
        return self.screenToPixelCoords(point.x(), point.y())

    def objectLineWidth(self):
        return self.mObjectLineWidth
        
    def setObjectLineWidth(self, lineWidth):
        self.mObjectLineWidth = lineWidth

    def setFlag(self, flag, enabled = True):
        if (enabled):
            self.mFlags |= flag
        else:
            self.mFlags &= ~flag

    def testFlag(self, flag):
        return bool(self.mFlags & flag)

    def painterScale(self):
        return self.mPainterScale
        
    def flags(self):
        return self.mFlags
        
    def setPainterScale(self, painterScale):
        self.mPainterScale = painterScale

    def setFlags(self, flags):
        self.mFlags = flags

    def lineToPolygon(self, start, end):
        direction = QVector2D(end - start).normalized().toPointF()
        perpendicular = QPointF(-direction.y(), direction.x())
        thickness = 5.0 # 5 pixels on each side
        direction *= thickness
        perpendicular *= thickness
        polygon = QPolygonF(4)
        polygon[0] = start + perpendicular - direction
        polygon[1] = start - perpendicular - direction
        polygon[2] = end - perpendicular + direction
        polygon[3] = end + perpendicular + direction
        return polygon

    ##
    # Returns the map this renderer is associated with.
    ##
    def map(self):
        return self.mMap

##
# A utility class for rendering cells.
##
class CellRenderer():
    BottomLeft, BottomCenter, TopLeft = range(3)

    def __init__(self, painter):
        self.mPainter = painter
        self.mTile = None
        self.mIsOpenGL = hasOpenGLEngine(painter)

        self.mFragments = QVector()

    def __del__(self):
        self.flush()

    ##
    # Renders a \a cell with the given \a origin at \a pos, taking into account
    # the flipping and tile offset.
    #
    # For performance reasons, the actual drawing is delayed until a different
    # kind of tile has to be drawn. For this reason it is necessary to call
    # flush when finished doing drawCell calls. This function is also called by
    # the destructor so usually an explicit call is not needed.
    ##
    def render(self, cell, pos, cellSize, origin):
        if (self.mTile != cell.tile):
            self.flush()
        image = cell.tile.currentFrameImage()
        size = image.size()
        if cellSize == QSizeF(0,0):
            objectSize = size
        else:
            objectSize = cellSize
        scale = QSizeF(objectSize.width() / size.width(), objectSize.height() / size.height())
        offset = cell.tile.offset()
        sizeHalf = QPointF(objectSize.width() / 2, objectSize.height() / 2)
        fragment = QPainter.PixmapFragment()
        fragment.x = pos.x() + (offset.x() * scale.width()) + sizeHalf.x()
        fragment.y = pos.y() + (offset.y() * scale.height()) + sizeHalf.y() - objectSize.height()
        fragment.sourceLeft = 0
        fragment.sourceTop = 0
        fragment.width = size.width()
        fragment.height = size.height()
        
        if cell.flippedHorizontally:
            fragment.scaleX = -1
        else:
            fragment.scaleX = 1
        if cell.flippedVertically:
            fragment.scaleY = -1
        else:
            fragment.scaleY = 1

        fragment.rotation = 0
        fragment.opacity = 1
        flippedHorizontally = cell.flippedHorizontally
        flippedVertically = cell.flippedVertically
        if (origin == CellRenderer.BottomCenter):
            fragment.x -= sizeHalf.x()
        if (cell.flippedAntiDiagonally):
            fragment.rotation = 90
            flippedHorizontally = cell.flippedVertically
            flippedVertically = not cell.flippedHorizontally
            # Compensate for the swap of image dimensions
            halfDiff = sizeHalf.y() - sizeHalf.x()
            fragment.y += halfDiff
            if (origin != CellRenderer.BottomCenter):
                fragment.x += halfDiff

        if flippedHorizontally:
            x = -1
        else:
            x = 1
        fragment.scaleX = scale.width() * x

        if flippedVertically:
            x = -1
        else:
            x = 1
        fragment.scaleY = scale.height() * x
        if (self.mIsOpenGL or (fragment.scaleX > 0 and fragment.scaleY > 0)):
            self.mTile = cell.tile
            self.mFragments.append(fragment)
            return

        # The Raster paint engine as of Qt 4.8.4 / 5.0.2 does not support
        # drawing fragments with a negative scaling factor.
        self.flush() # make sure we drew all tiles so far
        oldTransform = self.mPainter.transform()
        transform = oldTransform
        transform.translate(fragment.x, fragment.y)
        transform.rotate(fragment.rotation)
        transform.scale(fragment.scaleX, fragment.scaleY)
        target = QRectF(fragment.width * -0.5, fragment.height * -0.5, fragment.width, fragment.height)
        source = QRectF(0, 0, fragment.width, fragment.height)
        self.mPainter.setTransform(transform)
        self.mPainter.drawPixmap(target, image, source)
        self.mPainter.setTransform(oldTransform)

    def flush(self):
        if (not self.mTile):
            return
        self.mPainter.drawPixmapFragments(self.mFragments, self.mTile.currentFrameImage())
        self.mTile = None
        self.mFragments.resize(0)
