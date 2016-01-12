##
# tmxrasterizer.py
# Copyright 2012, Vincent Petithory
#
# This file is part of the TMX Rasterizer.
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

from tilelayer import TileLayer
from imagelayer import ImageLayer
from staggeredrenderer import StaggeredRenderer
from orthogonalrenderer import OrthogonalRenderer
from mapreader import MapReader
from map import Map
from isometricrenderer import IsometricRenderer
from hexagonalrenderer import HexagonalRenderer
from pyqtcore import QStringList
from PyQt5.QtGui import (
    QImage,
    QPainter,
    QImageWriter, 
    QTransform
)
from PyQt5.QtCore import (
    Qt,
    qWarning
)
class TmxRasterizer():
    def __init__(self):
        self.mScale = 0.0
        self.mTileSize = 0
        self.mLayersToHide = QStringList()
        self.mUseAntiAliasing = False
        self.mIgnoreVisibility = False

    def __del__(self):
        pass
    def setScale(self, scale):
        self.mScale = scale

    def setTileSize(self, tileSize):
        self.mTileSize = tileSize

    def setAntiAliasing(self, useAntiAliasing):
        self.mUseAntiAliasing = useAntiAliasing

    def setIgnoreVisibility(self, IgnoreVisibility):
        self.mIgnoreVisibility = IgnoreVisibility

    def setLayersToHide(self, layersToHide):
        self.mLayersToHide = layersToHide

    def render(self, mapFileName, imageFileName):
        map = None
        renderer = None
        reader = MapReader()
        map = reader.readMap(mapFileName)
        if (not map):
            qWarning("Error while reading " + mapFileName + ":\n" + reader.errorString())
            return 1

        x = map.orientation()
        if x==Map.Orientation.Isometric:
            renderer = IsometricRenderer(map)
        elif x==Map.Orientation.Staggered:
            renderer = StaggeredRenderer(map)
        elif x==Map.Orientation.Hexagonal:
            renderer = HexagonalRenderer(map)
        else:
            renderer = OrthogonalRenderer(map)

        if (self.mTileSize > 0):
            xScale = self.mTileSize / map.tileWidth()
            yScale = self.mTileSize / map.tileHeight()
        else:
            xScale = yScale = self.mScale

        mapSize = renderer.mapSize()
        margins = map.computeLayerOffsetMargins()
        mapSize.setWidth(mapSize.width() + margins.left() + margins.right())
        mapSize.setHeight(mapSize.height() + margins.top() + margins.bottom())
    
        mapSize.setWidth(mapSize.width()*xScale)
        mapSize.setHeight(mapSize.height()*yScale)
        image = QImage(mapSize, QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        painter = QPainter(image)
        if (xScale != 1.0 or yScale != 1.0):
            if (self.mUseAntiAliasing):
                painter.setRenderHints(QPainter.SmoothPixmapTransform |
                                       QPainter.Antialiasing)

            painter.setTransform(QTransform.fromScale(xScale, yScale))

        painter.translate(margins.left(), margins.top())
        
        # Perform a similar rendering than found in exportasimagedialog.py
        for layer in map.layers():
            if (not self.shouldDrawLayer(layer)):
                continue
            painter.setOpacity(layer.opacity())
            painter.translate(layer.offset())
            tileLayer = layer
            imageLayer = layer
            tp = type(layer)
            if tp == TileLayer:
                renderer.drawTileLayer(painter, tileLayer)
            elif tp == ImageLayer:
                renderer.drawImageLayer(painter, imageLayer)
            painter.translate(-layer.offset())
        painter.end()
        
        # Save image
        imageWriter = QImageWriter(imageFileName)
        if (not imageWriter.write(image)):
            qWarning("Error while writing " + imageFileName + ": " + imageWriter.errorString())
            return 1
    
        return 0

    def shouldDrawLayer(self, layer):
        if (layer.isObjectGroup()):
            return False
        if (self.mLayersToHide.contains(layer.name(), Qt.CaseInsensitive)):
            return False
        if (self.mIgnoreVisibility):
            return True
        return layer.isVisible()
