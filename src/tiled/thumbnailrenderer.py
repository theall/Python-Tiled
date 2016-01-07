##
# thumbnailrenderer.py
# Copyright 2011-2015, Thorbjørn Lindeijer <bjorn@lindeijer.nl>
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
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
##


from tilelayer import TileLayer
from staggeredrenderer import StaggeredRenderer
from orthogonalrenderer import OrthogonalRenderer
from objectgroup import ObjectGroup
from mapobjectitem import MapObjectItem
from map import Map
from isometricrenderer import IsometricRenderer
from imagelayer import ImageLayer
from hexagonalrenderer import HexagonalRenderer
from pyqtcore import (
    QList, 
    dynamic_cast
)
from PyQt5.QtCore import (
    Qt
)
from PyQt5.QtGui import (
    QImage,
    QPainter
)
def objectLessThan(a, b):
    return a.y() < b.y()

def smoothTransform(scale):
    return scale != 1.0 and scale < 2.0
# TODO: Look into using this class in ExportAsImageDialog, MiniMap and
#       possibly even the tmxrasterizer.
class ThumbnailRenderer():

    def __init__(self, map):
        
        self.mMap = map
        self.mVisibleLayersOnly(True)
        self.mIncludeBackgroundColor(False)

        x = map.orientation()
        if x==Map.Isometric:
            self.mRenderer = IsometricRenderer(map)
        elif x==Map.Staggered:
            self.mRenderer = StaggeredRenderer(map)
        elif x==Map.Hexagonal:
            self.mRenderer = HexagonalRenderer(map)
        else:
            self.mRenderer = OrthogonalRenderer(map)

    def __del__(self):
        del self.mRenderer
    
    def render(self, size):
        image = QImage(size, QImage.Format_ARGB32_Premultiplied)
        if (self.mIncludeBackgroundColor):
            if (self.mMap.backgroundColor().isValid()):
                image.fill(self.mMap.backgroundColor())
            else:
                image.fill(Qt.gray)
        else :
            image.fill(Qt.transparent)
        
        mapSize = self.mRenderer.mapSize()
        margins = self.mRenderer.map().drawMargins()
        mapSize.setWidth(mapSize.width() + margins.left() + margins.right())
        mapSize.setHeight(mapSize.height() + margins.top() + margins.bottom())
        scale = min(size.width() / mapSize.width(), size.height() / mapSize.height())
        scaledSize = mapSize * scale
        painter = QPainter(image)
        # Center the thumbnail in the requested size
        painter.translate((size.width() - scaledSize.width()) / 2,
                          (size.height() - scaledSize.height()) / 2)
        # Scale the map and translate it to adjust for its margins
        painter.scale(scale, scale)
        painter.translate(margins.left() + (size.width() - scaledSize.width()) / 2,
                          margins.top() + (size.height() - scaledSize.height()) / 2)
        if (smoothTransform(scale)):
            painter.setRenderHints(QPainter.SmoothPixmapTransform)
        self.mRenderer.setPainterScale(scale)
        for layer in self.mMap.layers():
            if (self.mVisibleLayersOnly and not layer.isVisible()):
                continue
            painter.setOpacity(layer.opacity())
            tileLayer = dynamic_cast(layer, TileLayer)
            objGroup = dynamic_cast(layer, ObjectGroup)
            imageLayer = dynamic_cast(layer, ImageLayer)
            if (tileLayer):
                self.mRenderer.drawTileLayer(painter, tileLayer)
            elif (objGroup):
                objects = objGroup.objects()
                if (objGroup.drawOrder() == ObjectGroup.TopDownOrder):
                    objects = QList(sorted(objects, key=lambda x:x.y(), reverse=True))
                for object in objects:
                    if (object.isVisible()):
                        if object.rotation() != 0.0:
                            origin = self.mRenderer.pixelToScreenCoords(object.position())
                            painter.save()
                            painter.translate(origin)
                            painter.rotate(object.rotation())
                            painter.translate(-origin)
                        
                        color = MapObjectItem.objectColor(object)
                        self.mRenderer.drawMapObject(painter, object, color)
                        if (object.rotation() != 0):
                            painter.restore()

            elif (imageLayer):
                self.mRenderer.drawImageLayer(painter, imageLayer)

        return image
    
    def visibleLayersOnly(self):
        return self.mVisibleLayersOnly
    
    def setVisibleLayersOnly(self, visibleLayersOnly):
        self.mVisibleLayersOnly = visibleLayersOnly
    
    def includeBackgroundColor(self):
        return self.mIncludeBackgroundColor
    
    def setIncludeBackgroundColor(self, includeBackgroundColor):
        self.mIncludeBackgroundColor = includeBackgroundColor




