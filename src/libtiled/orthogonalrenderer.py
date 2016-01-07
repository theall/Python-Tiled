##
# orthogonalrenderer.py
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
from map import Map
from maprenderer import MapRenderer, CellRenderer, RenderFlag
from pyqtcore import QVector
from PyQt5.QtGui  import(
    QPen,
    QBrush,
    QColor, 
    QPainter,
    QPainterPath
)
from PyQt5.QtCore import (
    Qt,
    QSize,
    QRect,
    QSizeF,
    QPointF,
    QRectF
)
##
# The orthogonal map renderer. This is the most basic map renderer,
# dealing with maps that use rectangular tiles.
##
class OrthogonalRenderer(MapRenderer):

    def __init__(self, map):
        super().__init__(map)

    def mapSize(self):
        return QSize(self.map().width() * self.map().tileWidth(),
                     self.map().height() * self.map().tileHeight())

    def boundingRect(self, arg):
        tp = type(arg)
        if tp==QRect:
            rect = arg
            tileWidth = self.map().tileWidth()
            tileHeight = self.map().tileHeight()
            return QRect(rect.x() * tileWidth,
                         rect.y() * tileHeight,
                         rect.width() * tileWidth,
                         rect.height() * tileHeight)
        elif tp==MapObject:
            object = arg
            bounds = object.bounds()
            boundingRect = QRectF()
            if (not object.cell().isEmpty()):
                bottomLeft = bounds.topLeft()
                tile = object.cell().tile
                imgSize = tile.image().size()
                tileOffset = tile.offset()
                objectSize = object.size()
                scale = QSizeF(objectSize.width() / imgSize.width(), objectSize.height() / imgSize.height())
                boundingRect = QRectF(bottomLeft.x() + (tileOffset.x() * scale.width()),
                                      bottomLeft.y() + (tileOffset.y() * scale.height() - objectSize.height()),
                                      objectSize.width(),
                                      objectSize.height()).adjusted(-1, -1, 1, 1)
            else:
                extraSpace = max(self.objectLineWidth(), 1.0)
                x = object.shape()
                if x==MapObject.Ellipse or x==MapObject.Rectangle:
                    if (bounds.isNull()):
                        boundingRect = bounds.adjusted(-10 - extraSpace,
                                                       -10 - extraSpace,
                                                       10 + extraSpace + 1,
                                                       10 + extraSpace + 1)
                    else:
                        boundingRect = bounds.adjusted(-extraSpace,
                                                       -extraSpace,
                                                       extraSpace + 1,
                                                       extraSpace + 1)
                elif x==MapObject.Polygon or x==MapObject.Polyline:
                    # Make some more room for the starting dot
                    extraSpace += self.objectLineWidth() * 4
                    
                    pos = object.position()
                    polygon = object.polygon().translated(pos)
                    screenPolygon = self.pixelToScreenCoords_(polygon)
                    boundingRect = screenPolygon.boundingRect().adjusted(-extraSpace,
                                                                         -extraSpace,
                                                                         extraSpace + 1,
                                                                         extraSpace + 1)
            return boundingRect

    def shape(self, object):
        path = QPainterPath()
        if (not object.cell().isEmpty()):
            path.addRect(self.boundingRect(object))
        else:
            x = object.shape()
            if x==MapObject.Rectangle:
                bounds = object.bounds()
                if (bounds.isNull()):
                    path.addEllipse(bounds.topLeft(), 20, 20)
                else:
                    path.addRoundedRect(bounds, 10, 10)
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
            elif x==MapObject.Ellipse:
                bounds = object.bounds()
                if (bounds.isNull()):
                    path.addEllipse(bounds.topLeft(), 20, 20)
                else:
                    path.addEllipse(bounds)

        return path

    def drawGrid(self, painter, rect, gridColor):
        tileWidth = self.map().tileWidth()
        tileHeight = self.map().tileHeight()
        if (tileWidth <= 0 or tileHeight <= 0):
            return
        startX = max(0,  int(rect.x() / tileWidth) * tileWidth)
        startY = max(0,  int(rect.y() / tileHeight) * tileHeight)
        endX = min(math.ceil(rect.right()), self.map().width() * tileWidth + 1)
        endY = min(math.ceil(rect.bottom()), self.map().height() * tileHeight + 1)
        gridColor.setAlpha(128)
        gridPen = QPen(gridColor)
        gridPen.setCosmetic(True)
        _x = QVector()
        _x.append(2)
        _x.append(2)
        gridPen.setDashPattern(_x)
        if (startY < endY):
            gridPen.setDashOffset(startY)
            painter.setPen(gridPen)
            for x in range(startX, endX, tileWidth):
                painter.drawLine(x, startY, x, endY - 1)

        if (startX < endX):
            gridPen.setDashOffset(startX)
            painter.setPen(gridPen)
            for y in range(startY, endY, tileHeight):
                painter.drawLine(startX, y, endX - 1, y)

    def drawTileLayer(self, painter, layer, exposed = QRectF()):
        savedTransform = painter.transform()
        tileWidth = self.map().tileWidth()
        tileHeight = self.map().tileHeight()
        layerPos = QPointF(layer.x() * tileWidth, layer.y() * tileHeight)
        painter.translate(layerPos)
        startX = 0
        startY = 0
        endX = layer.width() - 1
        endY = layer.height() - 1
        if (not exposed.isNull()):
            drawMargins = layer.drawMargins()
            drawMargins.setTop(drawMargins.top() - tileHeight)
            drawMargins.setRight(drawMargins.right() - tileWidth)
            rect = exposed.adjusted(-drawMargins.right(),
                                           -drawMargins.bottom(),
                                           drawMargins.left(),
                                           drawMargins.top())
            rect.translate(-layerPos)
            startX = max(math.floor(rect.x() / tileWidth), 0)
            startY = max(math.floor(rect.y() / tileHeight), 0)
            endX = min(int(math.ceil(rect.right()) / tileWidth), endX)
            endY = min(int(math.ceil(rect.bottom()) / tileHeight), endY)

        # Return immediately when there is nothing to draw
        if (startX > endX or startY > endY):
            return
        renderer = CellRenderer(painter)
        renderOrder = self.map().renderOrder()
        incX = 1
        incY = 1
        x = renderOrder
        if x==Map.RenderOrder.RightUp:
            startY, endY = endY, startY
            incY = -1
        elif x==Map.RenderOrder.LeftDown:
            startX, endX = endX, startX
            incX = -1
        elif x==Map.RenderOrder.LeftUp:
            startX, endX = endX, startX
            startY, endY = endY, startY
            incX = -1
            incY = -1
        elif x==Map.RenderOrder.RightDown:
            pass
        else:
            pass

        endX += incX
        endY += incY
        y = startY
        while(y != endY):
            x = startX
            while(x != endX):
                cell = layer.cellAt(x, y)
                if cell.isEmpty():
                    x += incX
                    continue
                renderer.render(cell,
                                QPointF(x * tileWidth, (y + 1) * tileHeight),
                                QSizeF(0, 0),
                                CellRenderer.BottomLeft)
                x += incX
            y += incY

        renderer.flush()
        painter.setTransform(savedTransform)

    def drawTileSelection(self, painter, region, color, exposed):
        for r in region.rects():
            toFill = QRectF(self.boundingRect(r)).intersected(exposed)
            if (not toFill.isEmpty()):
                painter.fillRect(toFill, color)

    def drawMapObject(self, painter, object, color):
        painter.save()
        bounds = object.bounds()
        rect = QRectF(bounds)
        painter.translate(rect.topLeft())
        rect.moveTopLeft(QPointF(0, 0))
        cell = object.cell()
        if (not cell.isEmpty()):
            CellRenderer(painter).render(cell, QPointF(), object.size(), CellRenderer.BottomLeft)
            if (self.testFlag(RenderFlag.ShowTileObjectOutlines)):
                tile = cell.tile
                imgSize = tile.size()
                tileOffset = tile.offset()
                rect = QRectF(QPointF(tileOffset.x(), tileOffset.y() - imgSize.height()), QSizeF(imgSize))
                pen = QPen(Qt.SolidLine)
                pen.setCosmetic(True)
                painter.setPen(pen)
                painter.drawRect(rect)
                pen.setStyle(Qt.DotLine)
                pen.setColor(color)
                painter.setPen(pen)
                painter.drawRect(rect)
        else:
            lineWidth = self.objectLineWidth()
            scale = self.painterScale()
            if lineWidth == 0:
                x = 1
            else:
                x = lineWidth
            shadowDist = x / scale
            shadowOffset = QPointF(shadowDist * 0.5, shadowDist * 0.5)
            linePen = QPen(color, lineWidth, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
            #linePen.setCosmetic(True)
            shadowPen = QPen(linePen)
            shadowPen.setColor(Qt.black)
            brushColor = QColor(color)
            fillBrush = QBrush(brushColor)
            painter.setRenderHint(QPainter.Antialiasing)
            # Trying to draw an ellipse with 0-width is causing a hang in
            # CoreGraphics when drawing the path requested by the
            # QCoreGraphicsPaintEngine. Draw them as rectangle instead.
            shape = object.shape()
            if (shape == MapObject.Ellipse and ((rect.width() == 0.0) ^ (rect.height() == 0.0))):
                shape = MapObject.Rectangle
            x = shape
            if x==MapObject.Rectangle:
                if (rect.isNull()):
                    rect = QRectF(QPointF(-10, -10), QSizeF(20, 20))
                # Draw the shadow
                painter.setPen(shadowPen)
                painter.drawRect(rect.translated(shadowOffset))
                painter.setPen(linePen)
                painter.setBrush(fillBrush)
                painter.drawRect(rect)
            elif x==MapObject.Polyline:
                screenPolygon = self.pixelToScreenCoords_(object.polygon())
                thickShadowPen = QPen(shadowPen)
                thickLinePen = QPen(linePen)
                thickShadowPen.setWidthF(thickShadowPen.widthF() * 4)
                thickLinePen.setWidthF(thickLinePen.widthF() * 4)
            
                painter.setPen(shadowPen)
                painter.drawPolyline(screenPolygon.translated(shadowOffset))
                painter.setPen(thickShadowPen)
                painter.drawPoint(screenPolygon.first() + shadowOffset)
            
                painter.setPen(linePen)
                painter.setBrush(fillBrush)
                painter.drawPolyline(screenPolygon)
                painter.setPen(thickLinePen)
                painter.drawPoint(screenPolygon.first())
            
            elif x==MapObject.Polygon:
                screenPolygon = self.pixelToScreenCoords_(object.polygon())
                thickShadowPen = QPen(shadowPen)
                thickLinePen = QPen(linePen)
                thickShadowPen.setWidthF(thickShadowPen.widthF() * 4)
                thickLinePen.setWidthF(thickLinePen.widthF() * 4)
                
                painter.setPen(shadowPen)
                painter.drawPolygon(screenPolygon.translated(shadowOffset))
                painter.setPen(thickShadowPen)
                painter.drawPoint(screenPolygon.first() + shadowOffset)
                
                painter.setPen(linePen)
                painter.setBrush(fillBrush)
                painter.drawPolygon(screenPolygon)
                
                painter.setPen(thickLinePen)
                painter.drawPoint(screenPolygon.first())
                
            elif x==MapObject.Ellipse:
                if (rect.isNull()):
                    rect = QRectF(QPointF(-10, -10), QSizeF(20, 20))
                # Draw the shadow
                painter.setPen(shadowPen)
                painter.drawEllipse(rect.translated(shadowOffset))
                painter.setPen(linePen)
                painter.setBrush(fillBrush)
                painter.drawEllipse(rect)

        painter.restore()
        
    def pixelToTileCoords(self, x, y):
        return QPointF(x / self.map().tileWidth(), y / self.map().tileHeight())

    def tileToPixelCoords(self, x, y):
        return QPointF(x * self.map().tileWidth(), y * self.map().tileHeight())

    def screenToTileCoords(self, x, y):
        return QPointF(x / self.map().tileWidth(), y / self.map().tileHeight())

    def tileToScreenCoords(self, x, y):
        return QPointF(x * self.map().tileWidth(), y * self.map().tileHeight())

    def screenToPixelCoords(self, x, y):
        return QPointF(x, y)

    def pixelToScreenCoords(self, x, y):
        return QPointF(x, y)
