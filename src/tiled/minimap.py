##
# minimap.py
# Copyright 2012, Christoph Schnackenberg
# Copyright 2012, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
#
# This file is part of Tiled.
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
##

import preferences
from pyqtcore import QList
from tilelayer import TileLayer
from imagelayer import ImageLayer
from objectgroup import ObjectGroup
from maprenderer import RenderFlag
from mapobjectitem import MapObjectItem
from documentmanager import DocumentManager
from PyQt5.QtCore import (
    Qt,
    QRect,
    QSize,
    QPoint,
    QRectF,
    QTimer,
    QPointF
)
from PyQt5.QtGui import (
    QPainter,
    QImage,
    QPen,
    QColor, 
    QTransform
)
from PyQt5.QtWidgets import (
    QFrame
)
def objectLessThan(a, b):
    return a.y() < b.y()

class MiniMapRenderFlag():
    DrawObjects             = 0x0001
    DrawTiles               = 0x0002
    DrawImages              = 0x0004
    IgnoreInvisibleLayer    = 0x0008
    DrawGrid                = 0x0010

class MiniMap(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.mMapDocument = None
        self.mDragging = False
        self.mMouseMoveCursorState = False
        self.mRedrawMapImage = False
        self.mRenderFlags = MiniMapRenderFlag.DrawTiles | MiniMapRenderFlag.DrawObjects | MiniMapRenderFlag.DrawImages | MiniMapRenderFlag.IgnoreInvisibleLayer

        self.mMapImageUpdateTimer = QTimer()
        self.mImageRect = QRect()
        self.mMapImage = QImage()
        self.mDragOffset = QPoint()

        self.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
        self.setMinimumSize(50, 50)
        # for cursor changes
        self.setMouseTracking(True)
        self.mMapImageUpdateTimer.setSingleShot(True)
        self.mMapImageUpdateTimer.timeout.connect(self.redrawTimeout)

    def setMapDocument(self, map):
        dm = DocumentManager.instance()
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
            mapView = dm.viewForDocument(self.mMapDocument)
#            if mapView:
#                mapView.zoomable().disconnect()
#                mapView.horizontalScrollBar().disconnect()
#                mapView.verticalScrollBar().disconnect()
        
        self.mMapDocument = map
        
        if (self.mMapDocument):
            self.mMapDocument.undoStack().indexChanged.connect(self.scheduleMapImageUpdate)
            mapView = dm.viewForDocument(self.mMapDocument)
            if mapView:
                mapView.horizontalScrollBar().valueChanged.connect(self.update)
                mapView.verticalScrollBar().valueChanged.connect(self.update)
                mapView.zoomable().scaleChanged.connect(self.update)
            
        self.scheduleMapImageUpdate()

    def setRenderFlags(self, flags):
        self.mRenderFlags = flags

    def sizeHint(self):
        return QSize(200, 200)

    ## Schedules a redraw of the minimap image. */
    def scheduleMapImageUpdate(self):
        self.mMapImageUpdateTimer.start(100)

    def paintEvent(self, pe):
        super().paintEvent(pe)
        if (self.mRedrawMapImage):
            self.renderMapToImage()
            self.mRedrawMapImage = False

        if (self.mMapImage.isNull() or self.mImageRect.isEmpty()):
            return
        p = QPainter(self)
        p.setRenderHints(QPainter.SmoothPixmapTransform)
        backgroundColor = QColor(Qt.darkGray)
        if (self.mMapDocument and self.mMapDocument.map().backgroundColor().isValid()):
            backgroundColor = self.mMapDocument.map().backgroundColor()
        p.setBrush(backgroundColor)
        p.setPen(Qt.NoPen)
        p.drawRect(self.contentsRect())
        p.drawImage(self.mImageRect, self.mMapImage)
        viewRect = self.viewportRect()
        p.setBrush(Qt.NoBrush)
        p.setPen(QColor(0, 0, 0, 128))
        p.translate(1, 1)
        p.drawRect(viewRect)
        outLinePen = QPen(QColor(255, 0, 0), 2)
        outLinePen.setJoinStyle(Qt.MiterJoin)
        p.translate(-1, -1)
        p.setPen(outLinePen)
        p.drawRect(viewRect)
        p.end()

    def resizeEvent(self, arg1):
        self.updateImageRect()
        self.scheduleMapImageUpdate()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if (delta != 0):
            self.centerViewOnLocalPixel(event.pos(), delta)
            return

        super().wheelEvent(event)

    def mousePressEvent(self, event):
        if (event.button() == Qt.LeftButton):
            cursorPos = event.pos()
            viewPort = self.viewportRect()
            if (viewPort.contains(cursorPos)):
                self.mDragOffset = viewPort.center() - cursorPos + QPoint(1, 1)
                cursorPos += self.mDragOffset
            else:
                self.mDragOffset = QPoint()
                self.centerViewOnLocalPixel(cursorPos)

            self.mDragging = True
            self.setCursor(Qt.ClosedHandCursor)
            return

        super().mouseReleaseEvent(event)

    def mouseReleaseEvent(self, event):
        if (event.button() == Qt.LeftButton and self.mDragging):
            self.mDragging = False
            viewPort = self.viewportRect()
            if (viewPort.contains(event.pos())):
                self.setCursor(Qt.OpenHandCursor)
                self.mMouseMoveCursorState = True
            elif (self.rect().contains(event.pos())):
                self.unsetCursor()
                self.mMouseMoveCursorState = False

            return

        super().mouseReleaseEvent(event)

    def mouseMoveEvent(self, event):
        if (self.mDragging):
            self.centerViewOnLocalPixel(event.pos() + self.mDragOffset)
            return

        if (self.viewportRect().contains(event.pos())):
            if (not self.mMouseMoveCursorState):
                self.setCursor(Qt.OpenHandCursor)
                self.mMouseMoveCursorState = True
        else:
            if (self.mMouseMoveCursorState):
                self.unsetCursor()
                self.mMouseMoveCursorState = False

        super().mouseMoveEvent(event)

    def redrawTimeout(self):
        self.mRedrawMapImage = True
        self.update()

    def viewportRect(self):
        mapView = DocumentManager.instance().currentMapView()
        if (not mapView):
            return QRect(0, 0, 1, 1)
        sceneRect = mapView.sceneRect()
        viewRect = mapView.mapToScene(mapView.viewport().geometry()).boundingRect()
        return QRect((viewRect.x() - sceneRect.x()) / sceneRect.width() * self.mImageRect.width() + self.mImageRect.x(),
                 (viewRect.y() - sceneRect.y()) / sceneRect.height() * self.mImageRect.height() + self.mImageRect.y(),
                 viewRect.width() / sceneRect.width() * self.mImageRect.width(),
                 viewRect.height() / sceneRect.height() * self.mImageRect.height())

    def mapToScene(self, p):
        if (self.mImageRect.isEmpty()):
            return QPointF()
        mapView = DocumentManager.instance().currentMapView()
        if (not mapView):
            return QPointF()
        sceneRect = mapView.sceneRect()
        p -= self.mImageRect.topLeft()
        return QPointF(p.x() * (sceneRect.width() / self.mImageRect.width()) + sceneRect.x(),
                       p.y() * (sceneRect.height() / self.mImageRect.height()) + sceneRect.y())

    def updateImageRect(self):
        imageRect = self.mMapImage.rect()
        if (imageRect.isEmpty()):
            self.mImageRect = QRect()
            return

        # Scale and center the image
        r = self.contentsRect()
        scale = min( r.width() / imageRect.width(),
                            r.height() / imageRect.height())
        imageRect.setSize(imageRect.size() * scale)
        imageRect.moveCenter(r.center())
        self.mImageRect = imageRect

    def renderMapToImage(self):
        if (not self.mMapDocument):
            self.mMapImage = QImage()
            return

        renderer = self.mMapDocument.renderer()
        r = self.contentsRect()
        mapSize = renderer.mapSize()
        if (mapSize.isEmpty()):
            self.mMapImage = QImage()
            return

        margins = self.mMapDocument.map().computeLayerOffsetMargins()
        mapSize.setWidth(mapSize.width() + margins.left() + margins.right())
        mapSize.setHeight(mapSize.height() + margins.top() + margins.bottom())
        
        # Determine the largest possible scale
        scale = min( r.width() / mapSize.width(), r.height() / mapSize.height())
        # Allocate a new image when the size changed
        imageSize = mapSize * scale
        if (self.mMapImage.size() != imageSize):
            self.mMapImage = QImage(imageSize, QImage.Format_ARGB32_Premultiplied)
            self.updateImageRect()

        if (imageSize.isEmpty()):
            return
        drawObjects = bool(self.mRenderFlags & MiniMapRenderFlag.DrawObjects)
        drawTiles = bool(self.mRenderFlags & MiniMapRenderFlag.DrawTiles)
        drawImages = bool(self.mRenderFlags & MiniMapRenderFlag.DrawImages)
        drawTileGrid = bool(self.mRenderFlags & MiniMapRenderFlag.DrawGrid)
        visibleLayersOnly = bool(self.mRenderFlags & MiniMapRenderFlag.IgnoreInvisibleLayer)
        # Remember the current render flags
        renderFlags = renderer.flags()
        renderer.setFlag(RenderFlag.ShowTileObjectOutlines, False)
        self.mMapImage.fill(Qt.transparent)
        painter = QPainter(self.mMapImage)
        painter.setRenderHints(QPainter.SmoothPixmapTransform)
        painter.setTransform(QTransform.fromScale(scale, scale))
        painter.translate(margins.left(), margins.top())
        renderer.setPainterScale(scale)
        for layer in self.mMapDocument.map().layers():
            if (visibleLayersOnly and not layer.isVisible()):
                continue
            painter.setOpacity(layer.opacity())
            painter.translate(layer.offset())
            tileLayer = layer
            objGroup = layer
            imageLayer = layer
            tp = type(layer)
            if (tp==TileLayer and drawTiles):
                renderer.drawTileLayer(painter, tileLayer)
            elif (tp==ObjectGroup and drawObjects):
                objects = objGroup.objects()
                if (objGroup.drawOrder() == ObjectGroup.DrawOrder.TopDownOrder):
                    objects = QList(sorted(objects, key=lambda x:x.y(), reverse=True))
                for object in objects:
                    if (object.isVisible()):
                        if (object.rotation() != 0.0):
                            origin = renderer.pixelToScreenCoords_(object.position())
                            painter.save()
                            painter.translate(origin)
                            painter.rotate(object.rotation())
                            painter.translate(-origin)

                        color = MapObjectItem.objectColor(object)
                        renderer.drawMapObject(painter, object, color)
                        if (object.rotation() != 0.0):
                            painter.restore()
            elif (tp==ImageLayer and drawImages):
                renderer.drawImageLayer(painter, imageLayer)
                
            painter.translate(-layer.offset())
            
        if (drawTileGrid):
            prefs = preferences.Preferences.instance()
            renderer.drawGrid(painter, QRectF(QPointF(), renderer.mapSize()),
                               prefs.gridColor())
        
        painter.end()
        renderer.setFlags(renderFlags)

    def centerViewOnLocalPixel(self, centerPos, delta = 0):
        mapView = DocumentManager.instance().currentMapView()
        if (not mapView):
            return
        if (delta != 0):
            mapView.zoomable().handleWheelDelta(delta)
        mapView.centerOn(self.mapToScene(centerPos))
