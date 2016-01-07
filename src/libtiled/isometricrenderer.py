##
# isometricrenderer.py
# Copyright 2009-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
from mapobject import MapObject
from maprenderer import MapRenderer, CellRenderer, RenderFlag
from pyqtcore import QVector
from PyQt5.QtGui import (
    QPen,
    QColor,
    QBrush,
    QPainterPath,
    QPainter,
    QTransform, 
    QPolygonF
)
from PyQt5.QtCore import (
    Qt,
    QSize,
    QSizeF,
    QPoint,
    QRect,
    QRectF,
    QPointF,
)
##
# An isometric map renderer.
#
# Isometric maps have diamond shaped tiles. This map renderer renders them in
# such a way that the map will also be diamond shaped. The X axis points to
# the bottom right while the Y axis points to the bottom left.
##
class IsometricRenderer(MapRenderer):
    def __init__(self, map):
        super().__init__(map)

    def mapSize(self):
        # Map width and height contribute equally in both directions
        side = self.map().height() + self.map().width()
        return QSize(side * self.map().tileWidth() / 2,
                     side * self.map().tileHeight() / 2)

    def boundingRect(self, arg):
        tp = type(arg)
        if tp == QRect:
            rect = arg
            tileWidth = self.map().tileWidth()
            tileHeight = self.map().tileHeight()
            originX = int(self.map().height() * tileWidth / 2)
            pos = QPoint((rect.x() - (rect.y() + rect.height())) * tileWidth / 2 + originX, (rect.x() + rect.y()) * tileHeight / 2)
            side = rect.height() + rect.width()
            size = QSize(side * tileWidth / 2, side * tileHeight / 2)
            return QRect(pos, size)
        elif tp == MapObject:
            object = arg
            if (not object.cell().isEmpty()):
                bottomCenter = self.pixelToScreenCoords_(object.position())
                tile = object.cell().tile
                imgSize = tile.image().size()
                tileOffset = tile.offset()
                objectSize = object.size()
                scale = QSizeF(objectSize.width() / imgSize.width(), objectSize.height() / imgSize.height())
                return QRectF(bottomCenter.x() + (tileOffset.x() * scale.width()) - objectSize.width() / 2,
                              bottomCenter.y() + (tileOffset.y() * scale.height()) - objectSize.height(),
                              objectSize.width(),
                              objectSize.height()).adjusted(-1, -1, 1, 1)
            elif (not object.polygon().isEmpty()):
                extraSpace = max(self.objectLineWidth(), 1.0)
                
                # Make some more room for the starting dot
                extraSpace += self.objectLineWidth() * 4
                pos = object.position()
                polygon = object.polygon().translated(pos)
                screenPolygon = self.pixelToScreenCoords_(polygon)
                return screenPolygon.boundingRect().adjusted(-extraSpace,
                                                             -extraSpace - 1,
                                                             extraSpace,
                                                             extraSpace)
            else:
                # Take the bounding rect of the projected object, and then add a few
                # pixels on all sides to correct for the line width.
                base = self.pixelRectToScreenPolygon(object.bounds()).boundingRect()
                extraSpace = max(self.objectLineWidth() / 2, 1.0)
                return base.adjusted(-extraSpace,
                                     -extraSpace - 1,
                                     extraSpace, extraSpace)

    def shape(self, object):
        path = QPainterPath()
        if (not object.cell().isEmpty()):
            path.addRect(self.boundingRect(object))
        else:
            x = object.shape()
            if x==MapObject.Ellipse or x==MapObject.Rectangle:
                path.addPolygon(self.pixelRectToScreenPolygon(object.bounds()))
            elif x==MapObject.Polygon or x==MapObject.Polyline:
                pos = object.position()
                polygon = object.polygon().translated(pos)
                screenPolygon = self.pixelToScreenCoords_(polygon)
                if (object.shape() == MapObject.Polygon):
                    path.addPolygon(screenPolygon)
                else:
                    for i in range(1, screenPolygon.size()):
                        path.addPolygon(self.lineToPolygon(screenPolygon[i - 1],
                                                      screenPolygon[i]))

                    path.setFillRule(Qt.WindingFill)

        return path

    def drawGrid(self, painter, rect, gridColor):
        tileWidth = self.map().tileWidth()
        tileHeight = self.map().tileHeight()
        r = rect.toAlignedRect()
        r.adjust(-tileWidth / 2, -tileHeight / 2, tileWidth / 2, tileHeight / 2)
        startX = int(max(0.0, self.screenToTileCoords_(r.topLeft()).x()))
        startY = int(max(0.0, self.screenToTileCoords_(r.topRight()).y()))
        endX = int(min(self.map().width(), self.screenToTileCoords_(r.bottomRight()).x()))
        endY = int(min(self.map().height(), self.screenToTileCoords_(r.bottomLeft()).y()))
        gridColor.setAlpha(128)
        gridPen = QPen(gridColor)
        gridPen.setCosmetic(True)
        _x = QVector()
        _x.append(2)
        _x.append(2)
        gridPen.setDashPattern(_x)
        painter.setPen(gridPen)
        for y in range(startY, endY+1):
            start = self.tileToScreenCoords(startX, y)
            end = self.tileToScreenCoords(endX, y)
            painter.drawLine(start, end)

        for x in range(startX, endX+1):
            start = self.tileToScreenCoords(x, startY)
            end = self.tileToScreenCoords(x, endY)
            painter.drawLine(start, end)

    def drawTileLayer(self, painter, layer, exposed = QRectF()):
        tileWidth = self.map().tileWidth()
        tileHeight = self.map().tileHeight()
        if (tileWidth <= 0 or tileHeight <= 1):
            return
        rect = exposed.toAlignedRect()
        if (rect.isNull()):
            rect = self.boundingRect(layer.bounds())
        drawMargins = layer.drawMargins()
        drawMargins.setTop(drawMargins.top() - tileHeight)
        drawMargins.setRight(drawMargins.right() - tileWidth)
        rect.adjust(-drawMargins.right(),
                    -drawMargins.bottom(),
                    drawMargins.left(),
                    drawMargins.top())
        # Determine the tile and pixel coordinates to start at
        tilePos = self.screenToTileCoords(rect.x(), rect.y())
        rowItr = QPoint( math.floor(tilePos.x()),
                                math.floor(tilePos.y()))
        startPos = self.tileToScreenCoords_(rowItr)
        startPos.setX(startPos.x() - tileWidth / 2)
        startPos.setY(startPos.y() + tileHeight)
        # Compensate for the layer position
        rowItr -= QPoint(layer.x(), layer.y())
        ## Determine in which half of the tile the top-left corner of the area we
        # need to draw is. If we're in the upper half, we need to start one row
        # up due to those tiles being visible as well. How we go up one row
        # depends on whether we're in the left or right half of the tile.
        ##
        inUpperHalf = startPos.y() - rect.y() > tileHeight / 2
        inLeftHalf = rect.x() - startPos.x() < tileWidth / 2
        if (inUpperHalf):
            if (inLeftHalf):
                rowItr.setX(rowItr.x() - 1)
                startPos.setX(startPos.x() - tileWidth / 2)
            else:
                rowItr.setY(rowItr.y() - 1)
                startPos.setX(startPos.x() + tileWidth / 2)

            startPos.setY(startPos.y() - tileHeight / 2)

        # Determine whether the current row is shifted half a tile to the right
        shifted = inUpperHalf ^ inLeftHalf
        renderer = CellRenderer(painter)

        y = startPos.y()
        while(y - tileHeight < rect.bottom()):
            columnItr = QPoint(rowItr)
            x = startPos.x()
            while(x < rect.right()):
                if (layer.contains(columnItr)):
                    cell = layer.cellAt(columnItr)
                    if (not cell.isEmpty()):
                        renderer.render(cell, QPointF(x, y), QSizeF(0, 0),
                                        CellRenderer.BottomLeft)

                # Advance to the next column
                columnItr.setX(columnItr.x() + 1)
                columnItr.setY(columnItr.y() - 1)
                x += tileWidth

            # Advance to the next row
            if (not shifted):
                rowItr.setX(rowItr.x() + 1)
                startPos.setX(startPos.x() + tileWidth / 2)
                shifted = True
            else:
                rowItr.setY(rowItr.y() + 1)
                startPos.setX(startPos.x() - tileWidth / 2)
                shifted = False
            y += int(tileHeight / 2)

    def drawTileSelection(self, painter, region, color, exposed):
        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        for r in region.rects():
            polygon = self.tileRectToScreenPolygon(r)
            if (QRectF(polygon.boundingRect()).intersects(exposed)):
                painter.drawConvexPolygon(polygon)

    def drawMapObject(self, painter, object, color):
        painter.save()
        pen = QPen(Qt.black)
        pen.setCosmetic(True)
        cell = object.cell()
        if (not cell.isEmpty()):
            tile = cell.tile
            imgSize = tile.size()
            pos = self.pixelToScreenCoords_(object.position())
            tileOffset = tile.offset()
            CellRenderer(painter).render(cell, pos, object.size(), CellRenderer.BottomCenter)
            if (self.testFlag(RenderFlag.ShowTileObjectOutlines)):
                rect = QRectF(QPointF(pos.x() - imgSize.width() / 2 + tileOffset.x(),
                                    pos.y() - imgSize.height() + tileOffset.y()),
                            imgSize)
                pen.setStyle(Qt.SolidLine)
                painter.setPen(pen)
                painter.drawRect(rect)
                pen.setStyle(Qt.DotLine)
                pen.setColor(color)
                painter.setPen(pen)
                painter.drawRect(rect)
        else:
            lineWidth = self.objectLineWidth()
            scale = self.painterScale()
            x = 1
            if lineWidth != 0:
                x = lineWidth
            shadowOffset = x / scale
            brushColor = QColor(color)
            brushColor.setAlpha(50)
            brush = QBrush(brushColor)
            pen.setJoinStyle(Qt.RoundJoin)
            pen.setCapStyle(Qt.RoundCap)
            pen.setWidth(lineWidth)
            
            colorPen = QPen(pen)
            colorPen.setColor(color)
        
            painter.setPen(pen)
            painter.setRenderHint(QPainter.Antialiasing)
            # TODO: Do something sensible to make null-sized objects usable
            x = object.shape()
            if x==MapObject.Ellipse:
                polygon = self.pixelRectToScreenPolygon(object.bounds())
                tw = self.map().tileWidth()
                th = self.map().tileHeight()
                transformScale = QPointF(1, 1)
                if (tw > th):
                    transformScale = QPointF(1, th/tw)
                else:
                    transformScale = QPointF(tw/th, 1)
                l1 = polygon.at(1) - polygon.at(0)
                l2 = polygon.at(3) - polygon.at(0)
                trans = QTransform()
                trans.scale(transformScale.x(), transformScale.y())
                trans.rotate(45)
                iTrans, ok = trans.inverted()
                l1x = iTrans.map(l1)
                l2x = iTrans.map(l2)
                ellipseSize = QSizeF(l1x.manhattanLength(), l2x.manhattanLength())
                if (ellipseSize.width() > 0 and ellipseSize.height() > 0):
                    painter.save()
                    painter.setPen(pen)
                    painter.translate(polygon.at(0))
                    painter.scale(transformScale.x(), transformScale.y())
                    painter.rotate(45)
                    painter.drawEllipse(QRectF(QPointF(0, 0), ellipseSize))
                    painter.restore()

                painter.setBrush(Qt.NoBrush)
                painter.drawPolygon(polygon)
                
                painter.setPen(colorPen)
                painter.setBrush(Qt.NoBrush)
                painter.translate(QPointF(0, -shadowOffset))
                painter.drawPolygon(polygon)
                painter.setBrush(brush)
                if (ellipseSize.width() > 0 and ellipseSize.height() > 0):
                    painter.save()
                    painter.translate(polygon.at(0))
                    painter.scale(transformScale.x(), transformScale.y())
                    painter.rotate(45)
                    painter.drawEllipse(QRectF(QPointF(0, 0), ellipseSize))
                    painter.restore()
            elif x==MapObject.Rectangle:
                polygon = self.pixelRectToScreenPolygon(object.bounds())
                painter.drawPolygon(polygon)
                painter.setPen(colorPen)
                painter.setBrush(brush)
                polygon.translate(0, -shadowOffset)
                painter.drawPolygon(polygon)
            elif x==MapObject.Polygon:
                pos = object.position()
                polygon = object.polygon().translated(pos)
                screenPolygon = self.pixelToScreenCoords_(polygon)
                thickPen = QPen(pen)
                thickColorPen = QPen(colorPen)
                thickPen.setWidthF(thickPen.widthF() * 4)
                thickColorPen.setWidthF(thickColorPen.widthF() * 4)
            
                painter.drawPolygon(screenPolygon)
                
                painter.setPen(thickPen)
                painter.drawPoint(screenPolygon.first())

                painter.setPen(colorPen)
                painter.setBrush(brush)
                screenPolygon.translate(0, -shadowOffset)
                painter.drawPolygon(screenPolygon)
                painter.setPen(thickColorPen)
                painter.drawPoint(screenPolygon.first())
                
            elif x==MapObject.Polyline:
                pos = object.position()
                polygon = object.polygon().translated(pos)
                screenPolygon = self.pixelToScreenCoords_(polygon)
                thickPen = QPen(pen)
                thickColorPen = QPen(colorPen)
                thickPen.setWidthF(thickPen.widthF() * 4)
                thickColorPen.setWidthF(thickColorPen.widthF() * 4)
                
                painter.drawPolyline(screenPolygon)
                painter.setPen(thickPen)
                painter.drawPoint(screenPolygon.first())
                
                painter.setPen(colorPen)
                screenPolygon.translate(0, -shadowOffset)
                painter.drawPolyline(screenPolygon)
                
                painter.setPen(thickColorPen)
                painter.drawPoint(screenPolygon.first())

        painter.restore()

    def pixelToTileCoords(self, x, y):
        tileHeight = self.map().tileHeight()
        return QPointF(x / tileHeight, y / tileHeight)

    def tileToPixelCoords(self, x, y):
        tileHeight = self.map().tileHeight()
        return QPointF(x * tileHeight, y * tileHeight)

    def screenToTileCoords(self, x, y):
        tileWidth = self.map().tileWidth()
        tileHeight = self.map().tileHeight()
        x -= self.map().height() * tileWidth / 2
        tileY = y / tileHeight
        tileX = x / tileWidth
        return QPointF(tileY + tileX, tileY - tileX)

    def tileToScreenCoords(self, x, y):
        tileWidth = self.map().tileWidth()
        tileHeight = self.map().tileHeight()
        originX = int(self.map().height() * tileWidth / 2)
        return QPointF((x - y) * tileWidth / 2 + originX,
                       (x + y) * tileHeight / 2)

    def screenToPixelCoords(self, x, y):
        tileWidth = self.map().tileWidth()
        tileHeight = self.map().tileHeight()
        x -= self.map().height() * tileWidth / 2
        tileY = y / tileHeight
        tileX = x / tileWidth
        return QPointF((tileY + tileX) * tileHeight,
                       (tileY - tileX) * tileHeight)

    def pixelToScreenCoords(self, x, y):
        tileWidth = self.map().tileWidth()
        tileHeight = self.map().tileHeight()
        originX = int(self.map().height() * tileWidth / 2)
        tileY = y / tileHeight
        tileX = x / tileHeight
        return QPointF((tileX - tileY) * tileWidth / 2 + originX,
                       (tileX + tileY) * tileHeight / 2)

    def pixelRectToScreenPolygon(self, rect):
        polygon = QPolygonF()
        polygon.append(QPointF(self.pixelToScreenCoords_(rect.topLeft())))
        polygon.append(QPointF(self.pixelToScreenCoords_(rect.topRight())))
        polygon.append(QPointF(self.pixelToScreenCoords_(rect.bottomRight())))
        polygon.append(QPointF(self.pixelToScreenCoords_(rect.bottomLeft())))
        return polygon

    def tileRectToScreenPolygon(self, rect):
        tileWidth = self.map().tileWidth()
        tileHeight = self.map().tileHeight()
        topRight = self.tileToScreenCoords_(rect.topRight())
        bottomRight = self.tileToScreenCoords_(rect.bottomRight())
        bottomLeft = self.tileToScreenCoords_(rect.bottomLeft())
        polygon = QPolygonF()
        polygon.append(QPointF(self.tileToScreenCoords_(rect.topLeft())))
        polygon.append(QPointF(topRight.x() + tileWidth / 2, topRight.y() + tileHeight / 2))
        polygon.append(QPointF(bottomRight.x(), bottomRight.y() + tileHeight))
        polygon.append(QPointF(bottomLeft.x() - tileWidth / 2, bottomLeft.y() + tileHeight / 2))
        return polygon
