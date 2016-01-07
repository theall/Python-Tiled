##
# staggeredrenderer.py
# Copyright 2011-2014, Thorbj?rn Lindeijer <thorbjorn@lindeijer.nl>
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
from map import Map
from mapobject import MapObject
from maprenderer import CellRenderer
from orthogonalrenderer import OrthogonalRenderer

from PyQt5.QtCore import (
    Qt,
    QRectF,
    QSize,
    QRect,
    QPoint,
    QLineF,
    QSizeF,
    QPointF
)
from PyQt5.QtGui import (
    QPen,
    QPolygonF, 
    QVector2D
)
from pyqtcore import QVector

class RenderParams():
    def __init__(self, map):
        self.tileWidth = map.tileWidth() & ~1
        self.tileHeight = map.tileHeight() & ~1
        self.sideLengthX = 0
        self.sideLengthY = 0
        self.staggerX = map.staggerAxis() == Map.StaggerAxis.StaggerX
        self.staggerEven = map.staggerIndex() == Map.StaggerIndex.StaggerEven

        if (map.orientation() == Map.Orientation.Hexagonal):
            if (self.staggerX):
                self.sideLengthX = map.hexSideLength()
            else:
                self.sideLengthY = map.hexSideLength()

        self.sideOffsetX = int((self.tileWidth - self.sideLengthX) / 2)
        self.sideOffsetY = int((self.tileHeight - self.sideLengthY) / 2)
        self.columnWidth = self.sideOffsetX + self.sideLengthX
        self.rowHeight = self.sideOffsetY + self.sideLengthY

    def doStaggerX(self, x):
        return self.staggerX and (x & 1) ^ self.staggerEven

    def doStaggerY(self, y):
        return not self.staggerX and (y & 1) ^ self.staggerEven

##
# A hexagonal renderer.
#
# Only pointy-topped hexagons are supported at the moment, shifting either the
# odd or the even rows to the right.
#
# The same problems as present when using the StaggeredRenderer happen with
# this renderer.
##
class HexagonalRenderer(OrthogonalRenderer):
    def __init__(self, map):
        super().__init__(map)

    def mapSize(self):
        p = RenderParams(self.map())
        # The map size is the same regardless of which indexes are shifted.
        if (p.staggerX):
            size = QSize(self.map().width() * p.columnWidth + p.sideOffsetX,
                       self.map().height() * (p.tileHeight + p.sideLengthY))
            if (self.map().width() > 1):
                size.setHeight(size.height() + p.rowHeight)
            return size
        else:
            size = QSize(self.map().width() * (p.tileWidth + p.sideLengthX),
                       self.map().height() * p.rowHeight + p.sideOffsetY)
            if (self.map().height() > 1):
                size.setWidth(size.width() + p.columnWidth)
            return size

    def boundingRect(self, rect):
        tp = type(rect)
        if tp==MapObject:
            ##
            # python doesn't surpport overwride function, call super().boundingRect
            ##
            return super().boundingRect(rect)
        elif tp==QRect:
            p = RenderParams(self.map())
            topLeft = self.tileToScreenCoords_(rect.topLeft()).toPoint()
            if (p.staggerX):
                width = rect.width() * p.columnWidth + p.sideOffsetX
                height = rect.height() * (p.tileHeight + p.sideLengthY)
                if (rect.width() > 1):
                    height += p.rowHeight
                    if (p.doStaggerX(rect.x())):
                        topLeft.setY(topLeft.y() - p.rowHeight)
            else:
                width = rect.width() * (p.tileWidth + p.sideLengthX)
                height = rect.height() * p.rowHeight + p.sideOffsetY
                if (rect.height() > 1):
                    width += p.columnWidth
                    if (p.doStaggerY(rect.y())):
                        topLeft.setX(topLeft.x() - p.columnWidth)

            return QRect(topLeft.x(), topLeft.y(), width, height)

    def drawGrid(self, painter, exposed, gridColor):
        rect = exposed.toAlignedRect()
        if (rect.isNull()):
            return
        p = RenderParams(self.map())
        # Determine the tile and pixel coordinates to start at
        startTile = self.screenToTileCoords_(rect.topLeft()).toPoint()
        startPos = self.tileToScreenCoords_(startTile).toPoint()
        ## Determine in which half of the tile the top-left corner of the area we
        # need to draw is. If we're in the upper half, we need to start one row
        # up due to those tiles being visible as well. How we go up one row
        # depends on whether we're in the left or right half of the tile.
        ##
        inUpperHalf = rect.y() - startPos.y() < p.sideOffsetY
        inLeftHalf = rect.x() - startPos.x() < p.sideOffsetX
        if (inUpperHalf):
            startTile.setY(startTile.y() - 1)
        if (inLeftHalf):
            startTile.setX(startTile.x() - 1)
        startTile.setX(max(0, startTile.x()))
        startTile.setY(max(0, startTile.y()))
        startPos = self.tileToScreenCoords_(startTile).toPoint()
        oct = [
            QPoint(0, p.tileHeight - p.sideOffsetY),
            QPoint(0, p.sideOffsetY),
            QPoint(p.sideOffsetX, 0),
            QPoint(p.tileWidth - p.sideOffsetX, 0),
            QPoint(p.tileWidth, p.sideOffsetY),
            QPoint(p.tileWidth, p.tileHeight - p.sideOffsetY),
            QPoint(p.tileWidth - p.sideOffsetX, p.tileHeight),
            QPoint(p.sideOffsetX, p.tileHeight)]

        lines = QVector()
        #lines.reserve(8)
        gridColor.setAlpha(128)
        gridPen = QPen(gridColor)
        gridPen.setCosmetic(True)
        _x = QVector()
        _x.append(2)
        _x.append(2)
        gridPen.setDashPattern(_x)
        painter.setPen(gridPen)
        if (p.staggerX):
            # Odd row shifting is applied in the rendering loop, so un-apply it here
            if (p.doStaggerX(startTile.x())):
                startPos.setY(startPos.y() - p.rowHeight)
            while(startPos.x() <= rect.right() and startTile.x() < self.map().width()):
                rowTile = QPoint(startTile)
                rowPos = QPoint(startPos)
                if (p.doStaggerX(startTile.x())):
                    rowPos.setY(rowPos.y() + p.rowHeight)
                while(rowPos.y() <= rect.bottom() and rowTile.y() < self.map().height()):
                    lines.append(QLineF(rowPos + oct[1], rowPos + oct[2]))
                    lines.append(QLineF(rowPos + oct[2], rowPos + oct[3]))
                    lines.append(QLineF(rowPos + oct[3], rowPos + oct[4]))
                    isStaggered = p.doStaggerX(startTile.x())
                    lastRow = rowTile.y() == self.map().height() - 1
                    lastColumn = rowTile.x() == self.map().width() - 1
                    bottomLeft = rowTile.x() == 0 or (lastRow and isStaggered)
                    bottomRight = lastColumn or (lastRow and isStaggered)
                    if (bottomRight):
                        lines.append(QLineF(rowPos + oct[5], rowPos + oct[6]))
                    if (lastRow):
                        lines.append(QLineF(rowPos + oct[6], rowPos + oct[7]))
                    if (bottomLeft):
                        lines.append(QLineF(rowPos + oct[7], rowPos + oct[0]))
                    painter.drawLines(lines)
                    lines.resize(0)
                    rowPos.setY(rowPos.y() + p.tileHeight + p.sideLengthY)
                    rowTile.setY(rowTile.y() + 1)

                startPos.setX(startPos.x() + p.columnWidth)
                startTile.setX(startTile.x() + 1)
        else:
            # Odd row shifting is applied in the rendering loop, so un-apply it here
            if (p.doStaggerY(startTile.y())):
                startPos.setX(startPos.x() - p.columnWidth)
            while(startPos.y() <= rect.bottom() and startTile.y() < self.map().height()):
                rowTile = QPoint(startTile)
                rowPos = QPoint(startPos)
                if (p.doStaggerY(startTile.y())):
                    rowPos.setX(rowPos.x() + p.columnWidth)
                while(rowPos.x() <= rect.right() and rowTile.x() < self.map().width()):
                    lines.append(QLineF(rowPos + oct[0], rowPos + oct[1]))
                    lines.append(QLineF(rowPos + oct[1], rowPos + oct[2]))
                    lines.append(QLineF(rowPos + oct[3], rowPos + oct[4]))
                    isStaggered = p.doStaggerY(startTile.y())
                    lastRow = rowTile.y() == self.map().height() - 1
                    lastColumn = rowTile.x() == self.map().width() - 1
                    bottomLeft = lastRow or (rowTile.x() == 0 and not isStaggered)
                    bottomRight = lastRow or (lastColumn and isStaggered)
                    if (lastColumn):
                        lines.append(QLineF(rowPos + oct[4], rowPos + oct[5]))
                    if (bottomRight):
                        lines.append(QLineF(rowPos + oct[5], rowPos + oct[6]))
                    if (bottomLeft):
                        lines.append(QLineF(rowPos + oct[7], rowPos + oct[0]))
                    painter.drawLines(lines)
                    lines.resize(0)
                    rowPos.setX(rowPos.x() + p.tileWidth + p.sideLengthX)
                    rowTile.setX(rowTile.x() + 1)

                startPos.setY(startPos.y() + p.rowHeight)
                startTile.setY(startTile.y() + 1)

    def drawTileLayer(self, painter, layer, exposed = QRectF()):
        p = RenderParams(self.map())
        rect = exposed.toAlignedRect()
        if (rect.isNull()):
            rect = self.boundingRect(layer.bounds())
        drawMargins = layer.drawMargins()
        drawMargins.setBottom(drawMargins.bottom() + p.tileHeight)
        drawMargins.setRight(drawMargins.right() - p.tileWidth)
        rect.adjust(-drawMargins.right(),
                    -drawMargins.bottom(),
                    drawMargins.left(),
                    drawMargins.top())
        # Determine the tile and pixel coordinates to start at
        startTile = self.screenToTileCoords_(rect.topLeft()).toPoint()
        # Compensate for the layer position
        startTile -= layer.position()
        startPos = self.tileToScreenCoords_(startTile + layer.position())
        ## Determine in which half of the tile the top-left corner of the area we
        # need to draw is. If we're in the upper half, we need to start one row
        # up due to those tiles being visible as well. How we go up one row
        # depends on whether we're in the left or right half of the tile.
        ##
        inUpperHalf = rect.y() - startPos.y() < p.sideOffsetY
        inLeftHalf = rect.x() - startPos.x() < p.sideOffsetX
        if (inUpperHalf):
            startTile.setY(startTile.y() - 1)
        if (inLeftHalf):
            startTile.setX(startTile.x() - 1)
        renderer = CellRenderer(painter)
        if (p.staggerX):
            startTile.setX(max(-1, startTile.x()))
            startTile.setY(max(-1, startTile.y()))
            startPos = self.tileToScreenCoords_(startTile + layer.position()).toPoint()
            startPos.setY(startPos.y() + p.tileHeight)
            staggeredRow = p.doStaggerX(startTile.x() + layer.x())
            while(startPos.y() < rect.bottom() and startTile.y() < layer.height()):
                rowTile = QPoint(startTile)
                rowPos = QPoint(startPos)
                while(rowPos.x() < rect.right() and rowTile.x() < layer.width()):
                    if (layer.contains(rowTile)):
                        cell = layer.cellAt(rowTile)
                        if (not cell.isEmpty()):
                            renderer.render(cell, rowPos, QSizeF(0, 0), CellRenderer.BottomLeft)

                    rowPos.setX(rowPos.x() + p.tileWidth + p.sideLengthX)
                    rowTile.setX(rowTile.x() + 2)

                if (staggeredRow):
                    startTile.setX(startTile.x() - 1)
                    startTile.setY(startTile.y() + 1)
                    startPos.setX(startPos.x() - p.columnWidth)
                    staggeredRow = False
                else:
                    startTile.setX(startTile.x() + 1)
                    startPos.setX(startPos.x() + p.columnWidth)
                    staggeredRow = True

                startPos.setY(startPos.y() + p.rowHeight)

        else:
            startTile.setX(max(0, startTile.x()))
            startTile.setY(max(0, startTile.y()))
            startPos = self.tileToScreenCoords_(startTile + layer.position()).toPoint()
            startPos.setY(startPos.y() + p.tileHeight)
            # Odd row shifting is applied in the rendering loop, so un-apply it here
            if (p.doStaggerY(startTile.y() + layer.y())):
                startPos.setX(startPos.x() - p.columnWidth)
            while(startPos.y() < rect.bottom() and startTile.y() < layer.height()):
                rowTile = QPoint(startTile)
                rowPos = QPoint(startPos)
                if (p.doStaggerY(startTile.y() + layer.y())):
                    rowPos.setX(rowPos.x() + p.columnWidth)
                while(rowPos.x() < rect.right() and rowTile.x() < layer.width()):
                    cell = layer.cellAt(rowTile)
                    if (not cell.isEmpty()):
                        renderer.render(cell, rowPos, QSizeF(0, 0), CellRenderer.BottomLeft)
                    rowPos.setX(rowPos.x() + p.tileWidth + p.sideLengthX)
                    rowTile.setX(rowTile.x() + 1)

                startPos.setY(startPos.y() + p.rowHeight)
                startTile.setY(startTile.y() + 1)

    def drawTileSelection(self, painter, region, color, exposed):
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        for r in region.rects():
            for y in range(r.top(), r.bottom()+1):
                for x in range(r.left(), r.right()+1):
                    polygon = self.tileToScreenPolygon(x, y)
                    if (QRectF(polygon.boundingRect()).intersects(exposed)):
                        painter.drawConvexPolygon(polygon)

    def pixelToTileCoords(self, x, y):
        return self.screenToTileCoords(x, y)

    def tileToPixelCoords(self, x, y):
        return self.tileToScreenCoords(x, y)

    ##
    # Converts screen to tile coordinates. Sub-tile return values are not
    # supported by this renderer.
    ##
    def screenToTileCoords(self, x, y):
        p = RenderParams(self.map())
        if (p.staggerX):
            if p.staggerEven:
                x -= p.tileWidth
            else:
                x -= p.sideOffsetX
        else:
            if p.staggerEven:
                y -= p.tileHeight
            else:
                y -= p.sideOffsetY
        # Start with the coordinates of a grid-aligned tile
        lenx = p.tileWidth + p.sideLengthX
        leny = p.tileHeight + p.sideLengthY
        referencePoint = QPoint(math.floor(x / lenx), math.floor(y / leny))
        # Relative x and y position on the base square of the grid-aligned tile
        rel = QVector2D(x - referencePoint.x() * lenx, y - referencePoint.y() * leny)
        # Adjust the reference point to the correct tile coordinates
        if p.staggerX:
            staggerAxisIndex = referencePoint.x()
        else:
            staggerAxisIndex = referencePoint.y()
            
        staggerAxisIndex *= 2

        if (p.staggerEven):
            staggerAxisIndex += 1
            
        if p.staggerX:
            referencePoint.setX(staggerAxisIndex)
        else:
            referencePoint.setY(staggerAxisIndex)
            
        # Determine the nearest hexagon tile by the distance to the center
        centers = [0, 0, 0, 0]
        if (p.staggerX):
            left = int(p.sideLengthX / 2)
            centerX = left + p.columnWidth
            centerY = int(p.tileHeight / 2)
            centers[0] = QVector2D(left, centerY)
            centers[1] = QVector2D(centerX, centerY - p.rowHeight)
            centers[2] = QVector2D(centerX, centerY + p.rowHeight)
            centers[3] = QVector2D(centerX + p.columnWidth, centerY)
        else:
            top = int(p.sideLengthY / 2)
            centerX = int(p.tileWidth / 2)
            centerY = top + p.rowHeight
            centers[0] = QVector2D(centerX, top)
            centers[1] = QVector2D(centerX - p.columnWidth, centerY)
            centers[2] = QVector2D(centerX + p.columnWidth, centerY)
            centers[3] = QVector2D(centerX, centerY + p.rowHeight)

        nearest = 0
        minDist = 1.7976931348623157e+308
        for i in range(4):
            center = centers[i]
            dc = (center - rel).lengthSquared()
            if (dc < minDist):
                minDist = dc
                nearest = i

        offsetsStaggerX = [
            QPoint( 0,  0),
            QPoint(+1, -1),
            QPoint(+1,  0),
            QPoint(+2,  0),
        ]
        offsetsStaggerY = [
            QPoint( 0,  0),
            QPoint(-1, +1),
            QPoint( 0, +1),
            QPoint( 0, +2),
        ]
        if p.staggerX:
            offsets = offsetsStaggerX
        else:
            offsets = offsetsStaggerY
        return QPointF(referencePoint + offsets[nearest])

    ##
    # Converts tile to screen coordinates. Sub-tile return values are not
    # supported by this renderer.
    ##
    def tileToScreenCoords(self, x, y):
        p = RenderParams(self.map())
        tileX = math.floor(x)
        tileY = math.floor(y)
        if (p.staggerX):
            pixelY = tileY * (p.tileHeight + p.sideLengthY)
            if (p.doStaggerX(tileX)):
                pixelY += p.rowHeight
            pixelX = tileX * p.columnWidth
        else:
            pixelX = tileX * (p.tileWidth + p.sideLengthX)
            if (p.doStaggerY(tileY)):
                pixelX += p.columnWidth
            pixelY = tileY * p.rowHeight
        return QPointF(pixelX, pixelY)

    # Functions specific to this type of renderer
    def topLeft(self, x, y):
        if (self.map().staggerAxis() == Map.StaggerAxis.StaggerY):
            if ((y & 1) ^ self.map().staggerIndex().value):
                return QPoint(x, y - 1)
            else:
                return QPoint(x - 1, y - 1)
        else:
            if ((x & 1) ^ self.map().staggerIndex().value):
                return QPoint(x - 1, y)
            else:
                return QPoint(x - 1, y - 1)

    def topRight(self, x, y):
        if (self.map().staggerAxis() == Map.StaggerAxis.StaggerY):
            if ((y & 1) ^ self.map().staggerIndex().value):
                return QPoint(x + 1, y - 1)
            else:
                return QPoint(x, y - 1)
        else:
            if ((x & 1) ^ self.map().staggerIndex().value):
                return QPoint(x + 1, y)
            else:
                return QPoint(x + 1, y - 1)

    def bottomLeft(self, x, y):
        if (self.map().staggerAxis() == Map.StaggerAxis.StaggerY):
            if ((y & 1) ^ self.map().staggerIndex().value):
                return QPoint(x, y + 1)
            else:
                return QPoint(x - 1, y + 1)
        else:
            if ((x & 1) ^ self.map().staggerIndex().value):
                return QPoint(x - 1, y + 1)
            else:
                return QPoint(x - 1, y)

    def bottomRight(self, x, y):
        if (self.map().staggerAxis() == Map.StaggerAxis.StaggerY):
            if ((y & 1) ^ self.map().staggerIndex().value):
                return QPoint(x + 1, y + 1)
            else:
                return QPoint(x, y + 1)
        else:
            if ((x & 1) ^ self.map().staggerIndex().value):
                return QPoint(x + 1, y + 1)
            else:
                return QPoint(x + 1, y)

    def tileToScreenPolygon(self, x, y):
        p = RenderParams(self.map())
        topRight = self.tileToScreenCoords(x, y)
        polygon = QPolygonF(8)
        polygon[0] = topRight + QPoint(0, p.tileHeight - p.sideOffsetY)
        polygon[1] = topRight + QPoint(0, p.sideOffsetY)
        polygon[2] = topRight + QPoint(p.sideOffsetX, 0)
        polygon[3] = topRight + QPoint(p.tileWidth - p.sideOffsetX, 0)
        polygon[4] = topRight + QPoint(p.tileWidth, p.sideOffsetY)
        polygon[5] = topRight + QPoint(p.tileWidth, p.tileHeight - p.sideOffsetY)
        polygon[6] = topRight + QPoint(p.tileWidth - p.sideOffsetX, p.tileHeight)
        polygon[7] = topRight + QPoint(p.sideOffsetX, p.tileHeight)
        return polygon
