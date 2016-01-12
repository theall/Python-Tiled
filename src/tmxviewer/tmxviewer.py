##
# tmxviewer.py
# Copyright 2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
#
# This file is part of the TMX Viewer example.
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

from staggeredrenderer import StaggeredRenderer
from orthogonalrenderer import OrthogonalRenderer
from objectgroup import ObjectGroup
from mapreader import MapReader
from map import Map
from isometricrenderer import IsometricRenderer
from hexagonalrenderer import HexagonalRenderer
from PyQt5.QtCore import (
    Qt,
    QRectF,
    qWarning
)
from PyQt5.QtWidgets import (
    QFrame,
    QGraphicsScene,
    QGraphicsItem,
    QGraphicsView
)
class TmxViewer(QGraphicsView):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.mScene = QGraphicsScene(self)
        self.mMap = None
        self.mRenderer = None
        self.setWindowTitle(self.tr("TMX Viewer"))
        self.setScene(self.mScene)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setOptimizationFlags(QGraphicsView.DontAdjustForAntialiasing | QGraphicsView.DontSavePainterState)
        self.setBackgroundBrush(Qt.black)
        self.setFrameStyle(QFrame.NoFrame)
        self.viewport().setAttribute(Qt.WA_StaticContents)

    def __del__(self):
        if (self.mMap):
            self.mMap.tilesets().clear()
        del self.mMap
        del self.mRenderer

    def viewMap(self, fileName):
        del self.mRenderer
        self.mRenderer = None
        self.mScene.clear()
        self.centerOn(0, 0)
        reader = MapReader()
        self.mMap = reader.readMap(fileName)
        if (not self.mMap):
            qWarning("Error:"+reader.errorString())
            return False

        x = self.mMap.orientation()
        if x==Map.Orientation.Isometric:
            self.mRenderer = IsometricRenderer(self.mMap)
        elif x==Map.Orientation.Staggered:
            self.mRenderer = StaggeredRenderer(self.mMap)
        elif x==Map.Orientation.Hexagonal:
            self.mRenderer = HexagonalRenderer(self.mMap)
        else:
            self.mRenderer = OrthogonalRenderer(self.mMap)

        self.mScene.addItem(MapItem(self.mMap, self.mRenderer))
        return True

##
# Item that represents a map object.
##
class MapObjectItem(QGraphicsItem):

    def __init__(self, mapObject, renderer, parent = None):
        super().__init__(parent)
        
        self.mMapObject = mapObject
        self.mRenderer = renderer

        position = mapObject.position()
        pixelPos = renderer.pixelToScreenCoords_(position)
        boundingRect = QRectF(renderer.boundingRect(mapObject))
        boundingRect.translate(-pixelPos)
        self.mBoundingRect = boundingRect
        self.setPos(pixelPos)
        self.setRotation(mapObject.rotation())

    def boundingRect(self):
        return self.mBoundingRect

    def paint(self, p, arg2, arg3):
        color = self.mMapObject.objectGroup().color()
        p.translate(-self.pos())
        if color.isValid():
            _x = color
        else:
            _x = Qt.darkGray
        self.mRenderer.drawMapObject(p, self.mMapObject, _x)

##
# Item that represents a tile layer.
##
class TileLayerItem(QGraphicsItem):

    def __init__(self, tileLayer, renderer, parent = None):
        super().__init__(parent)
        
        self.mTileLayer = tileLayer
        self.mRenderer = renderer

        self.setFlag(QGraphicsItem.ItemUsesExtendedStyleOption)
        self.setPos(self.mTileLayer.offset())

    def boundingRect(self):
        return QRectF(self.mRenderer.boundingRect(self.mTileLayer.bounds()))

    def paint(self, p, option, arg3):
        self.mRenderer.drawTileLayer(p, self.mTileLayer, option.exposedRect)

##
# Item that represents an object group.
##
class ObjectGroupItem(QGraphicsItem):

    def __init__(self, objectGroup, renderer, parent = None):
        super().__init__(parent)

        self.setFlag(QGraphicsItem.ItemHasNoContents)
        self.setPos(objectGroup.offset())
        
        drawOrder = objectGroup.drawOrder()
        # Create a child item for each object
        for object in objectGroup.objects():
            item = MapObjectItem(object, renderer, self)
            if (drawOrder == ObjectGroup.DrawOrder.TopDownOrder):
                item.setZValue(item.y())

    def boundingRect(self):
        return QRectF()

    def paint(self, arg1, arg2, arg3):
        pass

##
# Item that represents a map.
##
class MapItem(QGraphicsItem):
    def __init__(self, map, renderer, parent = None):
        super().__init__(parent)

        self.setFlag(QGraphicsItem.ItemHasNoContents)
        # Create a child item for each layer
        for layer in map.layers():
            tileLayer = layer.asTileLayer()
            if tileLayer:
                TileLayerItem(tileLayer, renderer, self)
            else:
                objectGroup = layer.asObjectGroup()
                if objectGroup:
                    ObjectGroupItem(objectGroup, renderer, self)

    def boundingRect(self):
        return QRectF()

    def paint(self, arg1, arg2, arg3):
        pass
