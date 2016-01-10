##
# objectselectionitem.py
# Copyright 2015, Thorbjørn Lindeijer <bjorn@lindeijer.nl>
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

from mapobject import MapObject
from libtiled.tiled import Alignment
import preferences as prefs
from mapobjectitem import MapObjectItem
from pyqtcore import (
    QHash
)
from PyQt5.QtCore import (
    QRectF,
    QPointF,
    QLineF,
    Qt
)
from PyQt5.QtGui import (
    QTransform,
    QPainter,
    QPen,
    QFontMetricsF, 
    QGuiApplication
)
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QGraphicsObject
)
labelMargin = 3
labelDistance = 12

# TODO: Unduplicate the following helper functions between this and
# ObjectSelectionTool
def alignmentOffset(r, alignment):
    x = alignment
    if x==Alignment.TopLeft:
        pass
    elif x==Alignment.Top:
    	return QPointF(r.width() / 2, 0)
    elif x==Alignment.TopRight:
    	return QPointF(r.width(), 0)
    elif x==Alignment.Left:
    	return QPointF(0, r.height() / 2)
    elif x==Alignment.Center:
    	return QPointF(r.width() / 2, r.height() / 2)
    elif x==Alignment.Right:
    	return QPointF(r.width(), r.height() / 2)
    elif x==Alignment.BottomLeft:
    	return QPointF(0, r.height())
    elif x==Alignment.Bottom:
    	return QPointF(r.width() / 2, r.height())
    elif x==Alignment.BottomRight:
    	return QPointF(r.width(), r.height())
    
    return QPointF()

# TODO: Check whether this function should be moved into MapObject.bounds
def align(r, alignment):
    r.translate(-alignmentOffset(r, alignment))

## This function returns the actual bounds of the object, as opposed to the
# bounds of its visualization that the MapRenderer.boundingRect function
# returns.
##
def objectBounds(object, renderer):
    if (not object.cell().isEmpty()):
        # Tile objects can have a tile offset, which is scaled along with the image
        tile = object.cell().tile
        imgSize = tile.image().size()
        position = renderer.pixelToScreenCoords_(object.position())
        tileOffset = tile.tileset().tileOffset()
        objectSize = object.size()
        
        if imgSize.width() > 0:
            scaleX = objectSize.width() / imgSize.width()
        else:
            scaleX = 0
        
        if imgSize.height() > 0:
            scaleY = objectSize.height() / imgSize.height()
        else:
            scaleY = 0
        bounds = QRectF(position.x() + (tileOffset.x() * scaleX),
                      position.y() + (tileOffset.y() * scaleY),
                      objectSize.width(),
                      objectSize.height())
        align(bounds, object.alignment())
        return bounds
    else :
        x = object.shape()
        if x==MapObject.Ellipse or x==MapObject.Rectangle:
            bounds = QRectF(object.bounds())
            align(bounds, object.alignment())
            screenPolygon = renderer.pixelToScreenCoords_(bounds)
            return screenPolygon.boundingRect()
        
        elif x==MapObject.Polygon or x==MapObject.Polyline:
            # Alignment is irrelevant for polygon objects since they have no size
            pos = object.position()
            polygon = object.polygon().translated(pos)
            screenPolygon = renderer.pixelToScreenCoords_(polygon)
            return screenPolygon.boundingRect()

    
    return QRectF()
    
class ObjectSelectionItem(QGraphicsObject):
    def __init__(self, mapDocument):
        super().__init__()
        
        self.mObjectLabels = QHash()
        self.mObjectOutlines = QHash()
        self.mMapDocument = mapDocument

        self.setFlag(QGraphicsItem.ItemHasNoContents)
        
        mapDocument.selectedObjectsChanged.connect(self.selectedObjectsChanged)
        mapDocument.mapChanged.connect(self.mapChanged)
        mapDocument.layerChanged.connect(self.layerChanged)
        mapDocument.objectsChanged.connect(self.syncOverlayItems)
        prefs.Preferences.instance().objectLabelVisibilityChanged.connect(self.objectLabelVisibilityChanged)
        if (prefs.Preferences.instance().objectLabelVisibility() == prefs.ObjectLabelVisiblity.AllObjectLabels):
            self.addRemoveObjectLabels()

    # QGraphicsItem interface
    def boundingRect(self):
        return QRectF()
        
    def paint(self, arg1, arg2, arg3):
        pass

    def selectedObjectsChanged(self):
        self.addRemoveObjectLabels()
        self.addRemoveObjectOutlines()
    
    def mapChanged(self):
        self.syncOverlayItems(self.mMapDocument.selectedObjects())
    
    def layerChanged(self, index):
        objectGroup = self.mMapDocument.map().layerAt(index).asObjectGroup()
        if (not objectGroup):
            return
        # If labels for all objects are visible, some labels may need to be added
        # removed based on layer visibility.
        if (prefs.Preferences.instance().objectLabelVisibility() == prefs.ObjectLabelVisiblity.AllObjectLabels):
            self.addRemoveObjectLabels()
        # If an object layer changed, that means its offset may have changed,
        # which affects the outlines of selected objects on that layer and the
        # positions of any name labels that are shown.
        self.syncOverlayItems(objectGroup.objects())
    
    def syncOverlayItems(self, objects):
        renderer = self.mMapDocument.renderer()
        for object in objects:
            outlineItem = self.mObjectOutlines.value(object)
            if outlineItem:
                outlineItem.syncWithMapObject(renderer)
            labelItem = self.mObjectLabels.value(object)
            if labelItem:
                labelItem.syncWithMapObject(renderer)

    def objectLabelVisibilityChanged(self):
        self.addRemoveObjectLabels()

    def addRemoveObjectLabels(self):
        labelItems = QHash()
        renderer = self.mMapDocument.renderer()
        
        def ensureLabel(object):
            if (labelItems.contains(object)):
                return
            labelItem = self.mObjectLabels.take(object)
            if (not labelItem):
                labelItem = MapObjectLabel(object, self)
                labelItem.syncWithMapObject(renderer)
            
            labelItems.insert(object, labelItem)
        
        x = prefs.Preferences.instance().objectLabelVisibility()
        if x==prefs.ObjectLabelVisiblity.AllObjectLabels:
            for layer in self.mMapDocument.map().layers():
                if (not layer.isVisible()):
                    continue
                objectGroup = layer.asObjectGroup()
                if objectGroup:
                    for object in objectGroup.objects():
                        ensureLabel(object)
        
        elif x==prefs.ObjectLabelVisiblity.SelectedObjectLabels:
            for object in self.mMapDocument.selectedObjects():
                ensureLabel(object)
        elif x==prefs.ObjectLabelVisiblity.NoObjectLabels:
            pass

        
        #as python will not clear the object who's reference count is not zero,we have to force remove it from mapscene
        for object in self.mObjectLabels.values():
            object.scene().removeItem(object)
        
        self.mObjectLabels.clear() # delete remaining items
        self.mObjectLabels, labelItems = labelItems, self.mObjectLabels

    def addRemoveObjectOutlines(self):
        outlineItems = QHash()
        renderer = self.mMapDocument.renderer()
        for mapObject in self.mMapDocument.selectedObjects():
            outlineItem = self.mObjectOutlines.take(mapObject)
            if (not outlineItem):
                outlineItem = MapObjectOutline(mapObject, self)
                outlineItem.syncWithMapObject(renderer)
            
            outlineItems.insert(mapObject, outlineItem)
        
        #as python will not clear the object who's reference count is not zero,we have to force remove it from mapscene
        for object in self.mObjectOutlines.values():
            object.scene().removeItem(object)
            
        self.mObjectOutlines.clear() # delete remaining items
        self.mObjectOutlines, outlineItems = outlineItems, self.mObjectOutlines

class MapObjectOutline(QGraphicsItem):

    def __init__(self, object, parent = None):
        super().__init__(parent)
        
        self.mObject = object
        self.mBoundingRect = QRectF()
        self.setZValue(1) # makes sure outlines are above labels
    
    def syncWithMapObject(self, renderer):
        pixelPos = renderer.pixelToScreenCoords_(self.mObject.position())
        bounds = objectBounds(self.mObject, renderer)
        bounds.translate(-pixelPos)
        self.setPos(pixelPos + self.mObject.objectGroup().offset())
        self.setRotation(self.mObject.rotation())
        if (self.mBoundingRect != bounds):
            self.prepareGeometryChange()
            self.mBoundingRect = bounds

    def boundingRect(self):
        return self.mBoundingRect
    
    def paint(self, painter, arg2, arg3):
        horizontal = [
            QLineF(self.mBoundingRect.topRight(), self.mBoundingRect.topLeft()), 
            QLineF(self.mBoundingRect.bottomRight(), self.mBoundingRect.bottomLeft())]
        
        vertical = [
            QLineF(self.mBoundingRect.bottomLeft(), self.mBoundingRect.topLeft()), 
            QLineF(self.mBoundingRect.bottomRight(), self.mBoundingRect.topRight())]
        
        dashPen = QPen(Qt.DashLine)
        dashPen.setCosmetic(True)
        dashPen.setDashOffset(max(0.0, self.x()))
        painter.setPen(dashPen)
        painter.drawLines(horizontal)
        dashPen.setDashOffset(max(0.0, self.y()))
        painter.setPen(dashPen)
        painter.drawLines(vertical)

class MapObjectLabel(QGraphicsItem):

    def __init__(self, object, parent = None):
        super().__init__(parent)
        
        self.mBoundingRect = QRectF()
        self.mObject = object

        self.setFlags(QGraphicsItem.ItemIgnoresTransformations | QGraphicsItem.ItemIgnoresParentOpacity)
    
    def syncWithMapObject(self, renderer):
        nameVisible = self.mObject.isVisible() and self.mObject.name()!=''
        self.setVisible(nameVisible)
        if (not nameVisible):
            return
        metrics = QFontMetricsF(QGuiApplication.font())
        boundingRect = metrics.boundingRect(self.mObject.name())
        boundingRect.translate(-boundingRect.width() / 2, -labelDistance)
        boundingRect.adjust(-labelMargin*2, -labelMargin, labelMargin*2, labelMargin)
        pixelPos = renderer.pixelToScreenCoords_(self.mObject.position())
        bounds = objectBounds(self.mObject, renderer)
        # Adjust the bounding box for object rotation
        transform = QTransform()
        transform.translate(pixelPos.x(), pixelPos.y())
        transform.rotate(self.mObject.rotation())
        transform.translate(-pixelPos.x(), -pixelPos.y())
        bounds = transform.mapRect(bounds)
        # Center the object name on the object bounding box
        pos = QPointF((bounds.left() + bounds.right()) / 2, bounds.top())
        self.setPos(pos + self.mObject.objectGroup().offset())
        if (self.mBoundingRect != boundingRect):
            self.prepareGeometryChange()
            self.mBoundingRect = boundingRect

    def boundingRect(self):
        return self.mBoundingRect.adjusted(0, 0, 1, 1)
    
    def paint(self, painter, arg2, arg3):
        color = MapObjectItem.objectColor(self.mObject)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.black)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(self.mBoundingRect.translated(1, 1), 4, 4)
        painter.setBrush(color)
        painter.drawRoundedRect(self.mBoundingRect, 4, 4)
        textPos = QPointF(-(self.mBoundingRect.width() - labelMargin*4) / 2, -labelDistance)
        painter.drawRoundedRect(self.mBoundingRect, 4, 4)
        painter.setPen(Qt.black)
        painter.drawText(textPos + QPointF(1,1), self.mObject.name())
        painter.setPen(Qt.white)
        painter.drawText(textPos, self.mObject.name())
