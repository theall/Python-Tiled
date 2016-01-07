##
# objectselectiontool.py
# Copyright 2010-2013, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

import math
from mapobjectitem import MapObjectItem
from snaphelper import SnapHelper
from selectionrectangle import SelectionRectangle
from rotatemapobject import RotateMapObject
from resizemapobject import ResizeMapObject
import preferences
from movemapobject import MoveMapObject
from mapobject import MapObject
from map import Map
from changepolygon import ChangePolygon
from abstractobjecttool import AbstractObjectTool
from libtiled.tiled import Alignment
from pyqtcore import QList, QSet, QVector
from PyQt5.QtCore import (
    Qt,
    QLineF,
    QRectF,
    QPoint,
    QSizeF,
    QPointF, 
    QCoreApplication
)
from PyQt5.QtGui import (
    QPen,
    QIcon,
    QColor,
    QCursor,
    QPolygonF, 
    QTransform,
    QPainterPath,
    QPainter,
    QKeySequence
)
from PyQt5.QtWidgets import (
    QGraphicsItem,
    QApplication
)

M_PI = 3.14159265358979323846

class Action():
    NoAction = 0
    Selecting = 1
    Moving = 2
    Rotating = 3
    Resizing = 4

class Mode():
    Resize = 0
    Rotate = 1

class AnchorPosition():
    TopLeftAnchor = 0
    TopRightAnchor = 1
    BottomLeftAnchor =2
    BottomRightAnchor = 3
    
    TopAnchor = 4
    LeftAnchor = 5
    RightAnchor = 6
    BottomAnchor = 7
    
    CornerAnchorCount = 4
    AnchorCount = 8

class MovingObject():
    def __init__(self):
        self.item = None
        self.oldItemPosition = QPointF()
        self.oldPosition = QPointF()
        self.oldSize = QSizeF()
        self.oldPolygon = QPolygonF()
        self.oldRotation = 0.0

def createRotateArrow():
    arrowHeadPos = 12
    arrowHeadLength = 4.5
    arrowHeadWidth = 5
    bodyWidth = 1.5
    outerArcSize = arrowHeadPos + bodyWidth - arrowHeadLength
    innerArcSize = arrowHeadPos - bodyWidth - arrowHeadLength
    path = QPainterPath()
    path.moveTo(arrowHeadPos, 0)
    path.lineTo(arrowHeadPos + arrowHeadWidth, arrowHeadLength)
    path.lineTo(arrowHeadPos + bodyWidth, arrowHeadLength)
    path.arcTo(QRectF(arrowHeadLength - outerArcSize,
                      arrowHeadLength - outerArcSize,
                      outerArcSize * 2,
                      outerArcSize * 2),
               0, -90)
    path.lineTo(arrowHeadLength, arrowHeadPos + arrowHeadWidth)
    path.lineTo(0, arrowHeadPos)
    path.lineTo(arrowHeadLength, arrowHeadPos - arrowHeadWidth)
    path.lineTo(arrowHeadLength, arrowHeadPos - bodyWidth)
    path.arcTo(QRectF(arrowHeadLength - innerArcSize,
                      arrowHeadLength - innerArcSize,
                      innerArcSize * 2,
                      innerArcSize * 2),
               -90, 90)
    path.lineTo(arrowHeadPos - arrowHeadWidth, arrowHeadLength)
    path.closeSubpath()
    return path

def createResizeArrow(straight):
    if straight:
        arrowLength = 14
    else:
        arrowLength = 16
    arrowHeadLength = 4.5
    arrowHeadWidth = 5
    bodyWidth = 1.5
    path = QPainterPath()
    path.lineTo(arrowHeadWidth, arrowHeadLength)
    path.lineTo(0 + bodyWidth, arrowHeadLength)
    path.lineTo(0 + bodyWidth, arrowLength - arrowHeadLength)
    path.lineTo(arrowHeadWidth, arrowLength - arrowHeadLength)
    path.lineTo(0, arrowLength)
    path.lineTo(-arrowHeadWidth, arrowLength - arrowHeadLength)
    path.lineTo(0 - bodyWidth, arrowLength - arrowHeadLength)
    path.lineTo(0 - bodyWidth, arrowHeadLength)
    path.lineTo(-arrowHeadWidth, arrowHeadLength)
    path.closeSubpath()
    if straight:
        x = 2
    else:
        x =3
    path.translate(0, x)
    return path

##
# Shared superclass for rotation and resizing handles.
##
class Handle(QGraphicsItem):

    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.mUnderMouse = False

        self.setFlags(QGraphicsItem.ItemIgnoresTransformations | QGraphicsItem.ItemIgnoresParentOpacity)
        self.setAcceptHoverEvents(True)
        self.setCursor(Qt.ArrowCursor)

    def hoverEnterEvent(self, event):
        self.mUnderMouse = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.mUnderMouse = False
        self.update()

    def itemChange(self, change, value):
        if (change == QGraphicsItem.ItemVisibleHasChanged and bool(value)):
            if (self.mUnderMouse):
                self.mUnderMouse = self.isUnderMouse()
        return super().itemChange(change, value)

##
# Rotation origin indicator.
##
class OriginIndicator(Handle):

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setZValue(10000 + 1)

    def boundingRect(self):
        return QRectF(-9, -9, 18, 18)

    def paint(self, painter, arg2, arg3):
        lines = [
            QLineF(-8,0, 8,0),
            QLineF(0,-8, 0,8),
        ]
        if self.mUnderMouse:
            _x = Qt.white
        else:
            _x = Qt.lightGray
        painter.setPen(QPen(_x, 1, Qt.DashLine))
        painter.drawLines(lines)
        painter.translate(1, 1)
        painter.setPen(QPen(Qt.black, 1, Qt.DashLine))
        painter.drawLines(lines)

##
# Corner rotation handle.
##
class RotateHandle(Handle):
    def __init__(self, corner, parent = None):
        super().__init__(parent)

        self.mArrow = createRotateArrow()
        self.setZValue(10000 + 1)
        transform = QTransform()
        x = corner
        if x==AnchorPosition.TopLeftAnchor:
            transform.rotate(180)
        elif x==AnchorPosition.TopRightAnchor:
            transform.rotate(-90)
        elif x==AnchorPosition.BottomLeftAnchor:
            transform.rotate(90)
        else:
            pass # BottomRight

        self.mArrow = transform.map(self.mArrow)

    def boundingRect(self):
        return self.mArrow.boundingRect().adjusted(-1, -1, 1, 1)

    def paint(self, painter, arg2, arg3):
        if self.mUnderMouse:
            pen = QPen(Qt.black, 1)
        else:
            pen = QPen(Qt.lightGray, 1)

        if self.mUnderMouse:
            brush = QColor(Qt.white)
        else:
            brush = QColor(Qt.black)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawPath(self.mArrow)

##
# A resize handle that allows resizing of map objects.
##
class ResizeHandle(Handle):
    def __init__(self, anchorPosition, parent = None):
        super().__init__(parent)
        
        self.mResizingLimitVertical = False
        self.mResizingLimitHorizontal = False
        self.mResizingOrigin = QPointF()
        self.mAnchorPosition = anchorPosition
        self.mArrow = createResizeArrow(anchorPosition > AnchorPosition.BottomRightAnchor)

        # The bottom right anchor takes precedence
        if anchorPosition < AnchorPosition.TopAnchor:
            _x = anchorPosition + 1
        else:
            _x = 0
        self.setZValue(10000 + 1 + _x)
        transform = QTransform()
        x = anchorPosition
        if x==AnchorPosition.TopLeftAnchor:
            transform.rotate(135)
        elif x==AnchorPosition.TopRightAnchor:
            transform.rotate(-135)
        elif x==AnchorPosition.BottomLeftAnchor:
            transform.rotate(45)
        elif x==AnchorPosition.BottomRightAnchor:
            transform.rotate(-45)
        elif x==AnchorPosition.TopAnchor:
            transform.rotate(180)
            self.mResizingLimitHorizontal = True
        elif x==AnchorPosition.LeftAnchor:
            transform.rotate(90)
            self.mResizingLimitVertical = True
        elif x==AnchorPosition.RightAnchor:
            transform.rotate(-90)
            self.mResizingLimitVertical = True
        else:
            self.mResizingLimitHorizontal = True

        self.mArrow = transform.map(self.mArrow)
    
    def anchorPosition(self):
        return self.mAnchorPosition
        
    def setResizingOrigin(self, resizingOrigin):
        self.mResizingOrigin = resizingOrigin

    def resizingOrigin(self):
        return self.mResizingOrigin

    def resizingLimitHorizontal(self):
        return self.mResizingLimitHorizontal
    
    def resizingLimitVertical(self):
        return self.mResizingLimitVertical
        
    def boundingRect(self):
        return self.mArrow.boundingRect().adjusted(-1, -1, 1, 1)

    def paint(self, painter, arg2, arg3):
        if self.mUnderMouse:
            _x = Qt.black
        else:
            _x = Qt.lightGray
        pen = QPen(_x, 1)
        if self.mUnderMouse:
            _x = Qt.white
        else:
            _x = Qt.black
        brush = QColor(_x)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(pen)
        painter.setBrush(brush)
        painter.drawPath(self.mArrow)

def findView(event):
    viewport = event.widget()
    if viewport:
        return viewport.parent()
    return None

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
    return r

def unalign(r, alignment):
    r.translate(alignmentOffset(r, alignment))
    return r

def pixelBounds(object):
    x = object.shape()
    if x==MapObject.Ellipse or x==MapObject.Rectangle:
        bounds = QRectF(object.bounds())
        bounds = align(bounds, object.alignment())
        return bounds
    elif x==MapObject.Polygon or x==MapObject.Polyline:
        # Alignment is irrelevant for polygon objects since they have no size
        pos = object.position()
        polygon = object.polygon().translated(pos)
        return polygon.boundingRect()

    return QRectF()

def resizeInPixelSpace(object):
    return object.cell().isEmpty()

## This function returns the actual bounds of the object, as opposed to the
# bounds of its visualization that the MapRenderer.boundingRect function
# returns.
#
# Before calculating the final bounding rectangle, the object is transformed
# by the given transformation.
##
def objectBounds(object, renderer, transform):
    if (not object.cell().isEmpty()):
        # Tile objects can have a tile offset, which is scaled along with the image
        tile = object.cell().tile
        imgSize = tile.image().size()
        position = renderer.pixelToScreenCoords_(object.position())
        tileOffset = tile.offset()
        objectSize = object.size()
        if imgSize.width() > 0:
            _x = objectSize.width() / imgSize.width()
        else:
            _x = 0
        scaleX = _x
        if imgSize.height() > 0:
            _x = objectSize.height() / imgSize.height()
        else:
            _x = 0
        scaleY = _x
        bounds = QRectF(position.x() + (tileOffset.x() * scaleX),
                      position.y() + (tileOffset.y() * scaleY),
                      objectSize.width(),
                      objectSize.height())
        bounds = align(bounds, object.alignment())
        return transform.mapRect(bounds)
    else:
        x = object.shape()
        if x==MapObject.Ellipse or x==MapObject.Rectangle:
            bounds = QRectF(object.bounds())
            bounds = align(bounds, object.alignment())
            screenPolygon = QPolygonF(renderer.pixelToScreenCoords_(bounds))
            return transform.map(screenPolygon).boundingRect()
        elif x==MapObject.Polygon or x==MapObject.Polyline:
            # Alignment is irrelevant for polygon objects since they have no size
            pos = object.position()
            polygon = object.polygon().translated(pos)
            screenPolygon = renderer.pixelToScreenCoords_(polygon)
            return transform.map(screenPolygon).boundingRect()

    return QRectF()

def rotateAt(position, rotation):
    transform = QTransform()
    transform.translate(position.x(), position.y())
    transform.rotate(rotation)
    transform.translate(-position.x(), -position.y())
    return transform

def objectTransform(object, renderer):
    transform = QTransform()
    if (object.rotation() != 0):
        pos = renderer.pixelToScreenCoords_(object.position())
        transform = rotateAt(pos, object.rotation())

    offset = object.objectGroup().offset()
    if not offset.isNull():
        transform *= QTransform.fromTranslate(offset.x(), offset.y())
        
    return transform

class ObjectSelectionTool(AbstractObjectTool):
    def __init__(self, parent = None):
        super().__init__(self.tr("Select Objects"),
              QIcon(":images/22x22/tool-select-objects.png"),
              QKeySequence(self.tr("S")),
              parent)
        self.mSelectionRectangle = SelectionRectangle()
        self.mOriginIndicator = OriginIndicator()
        self.mMousePressed = False
        self.mHoveredObjectItem = None
        self.mClickedObjectItem = None
        self.mClickedRotateHandle = None
        self.mClickedResizeHandle = None
        self.mResizingLimitHorizontal = False
        self.mResizingLimitVertical = False
        self.mMode = Mode.Resize
        self.mAction = Action.NoAction
        self.mRotateHandles = [0, 0, 0, 0]
        self.mResizeHandles = [0, 0, 0, 0, 0, 0, 0, 0]
        self.mAlignPosition = QPointF()
        self.mMovingObjects = QVector()
        self.mScreenStart = QPoint()
        self.mStart = QPointF()
        self.mModifiers = 0
        self.mOrigin = QPointF()

        for i in range(AnchorPosition.CornerAnchorCount):
            self.mRotateHandles[i] = RotateHandle(i)
        for i in range(AnchorPosition.AnchorCount):
            self.mResizeHandles[i] = ResizeHandle(i)

    def __del__(self):
        if self.mSelectionRectangle.scene():
            self.mSelectionRectangle.scene().removeItem(self.mSelectionRectangle)
        if self.mOriginIndicator.scene():
            self.mOriginIndicator.scene().removeItem(self.mOriginIndicator)
        for i in range(AnchorPosition.CornerAnchorCount):
            handle = self.mRotateHandles[i]
            scene = handle.scene()
            if scene:
                scene.removeItem(handle)
        self.mRotateHandles.clear()
        for i in range(AnchorPosition.AnchorCount):
            handle = self.mResizeHandles[i]
            scene = handle.scene()
            if scene:
                scene.removeItem(handle)
        self.mResizeHandles.clear()

    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('ObjectSelectionTool', sourceText, disambiguation, n)

    def activate(self, scene):
        super().activate(scene)
        self.updateHandles()
        self.mapDocument().objectsChanged.connect(self.updateHandles)
        self.mapDocument().mapChanged.connect(self.updateHandles)
        scene.selectedObjectItemsChanged.connect(self.updateHandles)
        self.mapDocument().objectsRemoved.connect(self.objectsRemoved)
        if self.mOriginIndicator.scene() != scene:
            scene.addItem(self.mOriginIndicator)
        for i in range(AnchorPosition.CornerAnchorCount):
            handle = self.mRotateHandles[i]
            if handle.scene() != scene:
                scene.addItem(handle)
        for i in range(AnchorPosition.AnchorCount):
            handle = self.mResizeHandles[i]
            if handle.scene() != scene:
                scene.addItem(handle)

    def deactivate(self, scene):
        if self.mOriginIndicator.scene() == scene:
            scene.removeItem(self.mOriginIndicator)
        for i in range(AnchorPosition.CornerAnchorCount):
            handle = self.mRotateHandles[i]
            if handle.scene() == scene:
                scene.removeItem(handle)
        for i in range(AnchorPosition.AnchorCount):
            handle = self.mResizeHandles[i]
            if handle.scene() == scene:
                scene.removeItem(handle)
        self.mapDocument().objectsChanged.disconnect(self.updateHandles)
        self.mapDocument().mapChanged.disconnect(self.updateHandles)
        scene.selectedObjectItemsChanged.disconnect(self.updateHandles)
        super().deactivate(scene)

    def keyPressed(self, event):
        if (self.mAction != Action.NoAction):
            event.ignore()
            return

        moveBy = QPointF()
        x = event.key()
        if x==Qt.Key_Up:
            moveBy = QPointF(0, -1)
        elif x==Qt.Key_Down:
            moveBy = QPointF(0, 1)
        elif x==Qt.Key_Left:
            moveBy = QPointF(-1, 0)
        elif x==Qt.Key_Right:
            moveBy = QPointF(1, 0)
        else:
            super().keyPressed(event)
            return

        items = self.mapScene().selectedObjectItems()
        modifiers = event.modifiers()
        if (moveBy.isNull() or items.isEmpty() or (modifiers & Qt.ControlModifier)):
            event.ignore()
            return

        moveFast = modifiers & Qt.ShiftModifier
        snapToFineGrid = preferences.Preferences.instance().snapToFineGrid()
        if (moveFast):
            # TODO: This only makes sense for orthogonal maps
            moveBy.setX(moveBy.x() * self.mapDocument().map().tileWidth())
            moveBy.setX(moveBy.y() * self.mapDocument().map().tileHeight())
            if (snapToFineGrid):
                moveBy /= preferences.Preferences.instance().gridFine()

        undoStack = self.mapDocument().undoStack()
        undoStack.beginMacro(self.tr("Move %n Object(s)", "", items.size()))
        i = 0
        for objectItem in items:
            object = objectItem.mapObject()
            oldPos = object.position()
            newPos = oldPos + moveBy
            undoStack.push(MoveMapObject(self.mapDocument(), object, newPos, oldPos))
            i += 1

        undoStack.endMacro()

    def mouseEntered(self):
        pass
        
    def mouseMoved(self, pos, modifiers):
        super().mouseMoved(pos, modifiers)
        
        # Update the hovered item (for mouse cursor)
        hoveredRotateHandle = None
        hoveredResizeHandle = None
        hoveredObjectItem = None
        
        view = self.mapScene().views()[0]
        if view:
            hoveredItem = self.mapScene().itemAt(pos,view.transform())
            hoveredRotateHandle = None
            hoveredResizeHandle = None
            tp = type(hoveredItem)
            if tp==RotateHandle:
                hoveredRotateHandle = hoveredItem
            elif tp==ResizeHandle:
                hoveredResizeHandle = hoveredItem

        if (not hoveredRotateHandle and not hoveredResizeHandle):
            hoveredObjectItem = self.topMostObjectItemAt(pos)

        self.mHoveredObjectItem = hoveredObjectItem
        
        if (self.mAction == Action.NoAction and self.mMousePressed):
            screenPos = QCursor.pos()
            dragDistance = (self.mScreenStart - screenPos).manhattanLength()
            if (dragDistance >= QApplication.startDragDistance()):
                hasSelection = not self.mapScene().selectedObjectItems().isEmpty()
                # Holding Alt forces moving current selection
                # Holding Shift forces selection rectangle
                if ((self.mClickedObjectItem or (modifiers & Qt.AltModifier) and hasSelection) and not (modifiers & Qt.ShiftModifier)):
                    self.startMoving(modifiers)
                elif (self.mClickedRotateHandle):
                    self.startRotating()
                elif (self.mClickedResizeHandle):
                    self.startResizing()
                else:
                    self.startSelecting()

        x = self.mAction
        if x==Action.Selecting:
            self.mSelectionRectangle.setRectangle(QRectF(self.mStart, pos).normalized())
        elif x==Action.Moving:
            self.updateMovingItems(pos, modifiers)
        elif x==Action.Rotating:
            self.updateRotatingItems(pos, modifiers)
        elif x==Action.Resizing:
            self.updateResizingItems(pos, modifiers)
        elif x==Action.NoAction:
            pass
        self.refreshCursor()

    def mousePressed(self, event):
        if (self.mAction != Action.NoAction): # Ignore additional presses during select/move
            return
        x = event.button()
        if x==Qt.LeftButton:
            self.mMousePressed = True
            self.mStart = event.scenePos()
            self.mScreenStart = event.screenPos()
            clickedRotateHandle = 0
            clickedResizeHandle = 0
            view = findView(event)
            if view:
                clickedItem = self.mapScene().itemAt(event.scenePos(), view.transform())
                clickedRotateHandle = None
                clickedResizeHandle = None
                tp = type(clickedItem)
                if tp==RotateHandle:
                    clickedRotateHandle = clickedItem
                elif tp==ResizeHandle:
                    clickedResizeHandle = clickedItem
            self.mClickedRotateHandle = clickedRotateHandle
            self.mClickedResizeHandle = clickedResizeHandle
            if (not clickedRotateHandle and not clickedResizeHandle):
                self.mClickedObjectItem = self.topMostObjectItemAt(self.mStart)
        else:
            super().mousePressed(event)

    def mouseReleased(self, event):
        if (event.button() != Qt.LeftButton):
            return
        x = self.mAction
        if x==Action.NoAction:
            if (not self.mClickedRotateHandle and not self.mClickedResizeHandle):
                # Don't change selection as a result of clicking on a handle
                modifiers = event.modifiers()
                if (self.mClickedObjectItem):
                    selection = self.mapScene().selectedObjectItems()
                    if (modifiers & (Qt.ShiftModifier | Qt.ControlModifier)):
                        if (selection.contains(self.mClickedObjectItem)):
                            selection.remove(self.mClickedObjectItem)
                        else:
                            selection.insert(self.mClickedObjectItem)
                    elif (selection.contains(self.mClickedObjectItem)):
                        # Clicking one of the selected items changes the edit mode
                        if self.mMode == Mode.Resize:
                            _x = Mode.Rotate
                        else:
                            _x = Mode.Resize
                        self.setMode(_x)
                    else:
                        selection.clear()
                        selection.insert(self.mClickedObjectItem)
                        self.setMode(Mode.Resize)
                    self.mapScene().setSelectedObjectItems(selection)
                elif (not (modifiers & Qt.ShiftModifier)):
                    self.mapScene().setSelectedObjectItems(QSet())
        elif x==Action.Selecting:
            self.updateSelection(event.scenePos(), event.modifiers())
            self.mapScene().removeItem(self.mSelectionRectangle)
            self.mAction = Action.NoAction
        elif x==Action.Moving:
            self.finishMoving(event.scenePos())
        elif x==Action.Rotating:
            self.finishRotating(event.scenePos())
        elif x==Action.Resizing:
            self.finishResizing(event.scenePos())

        self.mMousePressed = False
        self.mClickedObjectItem = None
        self.mClickedRotateHandle = None
        self.mClickedResizeHandle = None
        self.refreshCursor()
        
    def modifiersChanged(self, modifiers):
        self.mModifiers = modifiers
        self.refreshCursor()

    def languageChanged(self):
        self.setName(self.tr("Select Objects"))
        self.setShortcut(QKeySequence(self.tr("S")))

    def updateHandles(self):
        if (self.mAction == Action.Moving or self.mAction == Action.Rotating or self.mAction == Action.Resizing):
            return
        objects = self.mapDocument().selectedObjects()
        showHandles = objects.size() > 0
        if (showHandles):
            renderer = self.mapDocument().renderer()
            boundingRect = objectBounds(objects.first(), renderer, objectTransform(objects.first(), renderer))
            for i in range(1, objects.size()):
                object = objects.at(i)
                boundingRect |= objectBounds(object, renderer, objectTransform(object, renderer))

            topLeft = boundingRect.topLeft()
            topRight = boundingRect.topRight()
            bottomLeft = boundingRect.bottomLeft()
            bottomRight = boundingRect.bottomRight()
            center = boundingRect.center()
            handleRotation = 0
            # If there is only one object selected, align to its orientation.
            if (objects.size() == 1):
                object = objects.first()
                handleRotation = object.rotation()
                if (resizeInPixelSpace(object)):
                    bounds = pixelBounds(object)
                    transform = QTransform(objectTransform(object, renderer))
                    topLeft = transform.map(renderer.pixelToScreenCoords_(bounds.topLeft()))
                    topRight = transform.map(renderer.pixelToScreenCoords_(bounds.topRight()))
                    bottomLeft = transform.map(renderer.pixelToScreenCoords_(bounds.bottomLeft()))
                    bottomRight = transform.map(renderer.pixelToScreenCoords_(bounds.bottomRight()))
                    center = transform.map(renderer.pixelToScreenCoords_(bounds.center()))
                    # Ugly hack to make handles appear nicer in this case
                    if (self.mapDocument().map().orientation() == Map.Orientation.Isometric):
                        handleRotation += 45
                else:
                    bounds = objectBounds(object, renderer, QTransform())
                    transform = QTransform(objectTransform(object, renderer))
                    topLeft = transform.map(bounds.topLeft())
                    topRight = transform.map(bounds.topRight())
                    bottomLeft = transform.map(bounds.bottomLeft())
                    bottomRight = transform.map(bounds.bottomRight())
                    center = transform.map(bounds.center())

            self.mOriginIndicator.setPos(center)
            self.mRotateHandles[AnchorPosition.TopLeftAnchor].setPos(topLeft)
            self.mRotateHandles[AnchorPosition.TopRightAnchor].setPos(topRight)
            self.mRotateHandles[AnchorPosition.BottomLeftAnchor].setPos(bottomLeft)
            self.mRotateHandles[AnchorPosition.BottomRightAnchor].setPos(bottomRight)
            top = (topLeft + topRight) / 2
            left = (topLeft + bottomLeft) / 2
            right = (topRight + bottomRight) / 2
            bottom = (bottomLeft + bottomRight) / 2
            self.mResizeHandles[AnchorPosition.TopAnchor].setPos(top)
            self.mResizeHandles[AnchorPosition.TopAnchor].setResizingOrigin(bottom)
            self.mResizeHandles[AnchorPosition.LeftAnchor].setPos(left)
            self.mResizeHandles[AnchorPosition.LeftAnchor].setResizingOrigin(right)
            self.mResizeHandles[AnchorPosition.RightAnchor].setPos(right)
            self.mResizeHandles[AnchorPosition.RightAnchor].setResizingOrigin(left)
            self.mResizeHandles[AnchorPosition.BottomAnchor].setPos(bottom)
            self.mResizeHandles[AnchorPosition.BottomAnchor].setResizingOrigin(top)
            self.mResizeHandles[AnchorPosition.TopLeftAnchor].setPos(topLeft)
            self.mResizeHandles[AnchorPosition.TopLeftAnchor].setResizingOrigin(bottomRight)
            self.mResizeHandles[AnchorPosition.TopRightAnchor].setPos(topRight)
            self.mResizeHandles[AnchorPosition.TopRightAnchor].setResizingOrigin(bottomLeft)
            self.mResizeHandles[AnchorPosition.BottomLeftAnchor].setPos(bottomLeft)
            self.mResizeHandles[AnchorPosition.BottomLeftAnchor].setResizingOrigin(topRight)
            self.mResizeHandles[AnchorPosition.BottomRightAnchor].setPos(bottomRight)
            self.mResizeHandles[AnchorPosition.BottomRightAnchor].setResizingOrigin(topLeft)
            for i in range(AnchorPosition.CornerAnchorCount):
                self.mRotateHandles[i].setRotation(handleRotation)
            for i in range(AnchorPosition.AnchorCount):
                self.mResizeHandles[i].setRotation(handleRotation)

        self.updateHandleVisibility()

    def updateHandleVisibility(self):
        hasSelection = not self.mapDocument().selectedObjects().isEmpty()
        showHandles = hasSelection and (self.mAction == Action.NoAction or self.mAction == Action.Selecting)
        showOrigin = hasSelection and self.mAction != Action.Moving and (self.mMode == Mode.Rotate or self.mAction == Action.Resizing)
        for i in range(AnchorPosition.CornerAnchorCount):
            self.mRotateHandles[i].setVisible(showHandles and self.mMode == Mode.Rotate)
        for i in range(AnchorPosition.AnchorCount):
            self.mResizeHandles[i].setVisible(showHandles and self.mMode == Mode.Resize)
        self.mOriginIndicator.setVisible(showOrigin)

    def objectsRemoved(self, objects):
        if (self.mAction != Action.Moving and self.mAction != Action.Rotating and self.mAction != Action.Resizing):
            return
        # Abort move/rotate/resize to avoid crashing...
        # TODO: This should really not be allowed to happen in the first place.
        # since it breaks the undo history, for example.
        for i in range(self.mMovingObjects.size() - 1, -1, -1):
            object = self.mMovingObjects[i]
            mapObject = object.item.mapObject()
            if objects.contains(mapObject):
                # Avoid referencing the removed object
                self.mMovingObjects.remove(i)
            else:
                mapObject.setPosition(object.oldPosition)
                mapObject.setSize(object.oldSize)
                mapObject.setPolygon(object.oldPolygon)
                mapObject.setRotation(object.oldRotation)
        
        self.mapDocument().mapObjectModel().emitObjectsChanged(self.changingObjects)
        self.mMovingObjects.clear()

    def updateSelection(self, pos, modifiers):
        rect = QRectF(self.mStart, pos).normalized()
        # Make sure the rect has some contents, otherwise intersects returns False
        rect.setWidth(max(1.0, rect.width()))
        rect.setHeight(max(1.0, rect.height()))
        selectedItems = QSet()
        for item in self.mapScene().items(rect):
            if type(item) == MapObjectItem:
                selectedItems.insert(item)

        if (modifiers & (Qt.ControlModifier | Qt.ShiftModifier)):
            selectedItems |= self.mapScene().selectedObjectItems()
        else:
            self.setMode(Mode.Resize)
        self.mapScene().setSelectedObjectItems(selectedItems)

    def startSelecting(self):
        self.mAction = Action.Selecting
        self.mapScene().addItem(self.mSelectionRectangle)

    def startMoving(self, modifiers):
        # Move only the clicked item, if it was not part of the selection
        if (self.mClickedObjectItem and not (modifiers & Qt.AltModifier)):
            if (not self.mapScene().selectedObjectItems().contains(self.mClickedObjectItem)):
                self.mapScene().setSelectedObjectItems(QSet([self.mClickedObjectItem]))

        self.saveSelectionState()
        self.mAction = Action.Moving
        self.mAlignPosition = self.mMovingObjects[0].oldPosition
        for object in self.mMovingObjects:
            pos = object.oldPosition
            if (pos.x() < self.mAlignPosition.x()):
                self.mAlignPosition.setX(pos.x())
            if (pos.y() < self.mAlignPosition.y()):
                self.mAlignPosition.setY(pos.y())

        self.updateHandleVisibility()

    def updateMovingItems(self, pos, modifiers):
        renderer = self.mapDocument().renderer()

        diff = self.snapToGrid(pos-self.mStart, modifiers)
        for object in self.mMovingObjects:
            newPixelPos = object.oldItemPosition + diff
            newPos = renderer.screenToPixelCoords_(newPixelPos)

            mapObject = object.item.mapObject()
            mapObject.setPosition(newPos)
        self.mapDocument().mapObjectModel().emitObjectsChanged(self.changingObjects())
        
    def finishMoving(self, pos):
        self.mAction = Action.NoAction
        self.updateHandles()
        if (self.mStart == pos): # Move is a no-op
            return
        undoStack = self.mapDocument().undoStack()
        undoStack.beginMacro(self.tr("Move %n Object(s)", "", self.mMovingObjects.size()))
        for object in self.mMovingObjects:
            undoStack.push(MoveMapObject(self.mapDocument(), object.item.mapObject(), object.oldPosition))

        undoStack.endMacro()
        self.mMovingObjects.clear()

    def startRotating(self):
        self.mAction = Action.Rotating
        self.mOrigin = self.mOriginIndicator.pos()
        self.saveSelectionState()
        self.updateHandleVisibility()

    def updateRotatingItems(self, pos, modifiers):
        renderer = self.mapDocument().renderer()
        startDiff = self.mOrigin - self.mStart
        currentDiff = self.mOrigin - pos
        startAngle = math.atan2(startDiff.y(), startDiff.x())
        currentAngle = math.atan2(currentDiff.y(), currentDiff.x())
        angleDiff = currentAngle - startAngle
        snap = 15 * M_PI / 180 # 15 degrees in radians
        if (modifiers & Qt.ControlModifier):
            angleDiff = math.floor((angleDiff + snap / 2) / snap) * snap
        for object in self.mMovingObjects:
            mapObject = object.item.mapObject()
            offset = mapObject.objectGroup().offset()
        
            oldRelPos = object.oldItemPosition + offset - self.mOrigin
            sn = math.sin(angleDiff)
            cs = math.cos(angleDiff)
            newRelPos = QPointF(oldRelPos.x() * cs - oldRelPos.y() * sn, oldRelPos.x() * sn + oldRelPos.y() * cs)
            newPixelPos = self.mOrigin + newRelPos - offset
            newPos = renderer.screenToPixelCoords_(newPixelPos)
            newRotation = object.oldRotation + angleDiff * 180 / M_PI
            mapObject.setPosition(newPos)
            mapObject.setRotation(newRotation)
        
        self.mapDocument().mapObjectModel().emitObjectsChanged(self.changingObjects())
        
    def finishRotating(self, pos):
        self.mAction = Action.NoAction
        self.updateHandles()
        if (self.mStart == pos): # No rotation at all
            return
        undoStack = self.mapDocument().undoStack()
        undoStack.beginMacro(self.tr("Rotate %n Object(s)", "", self.mMovingObjects.size()))
        for object in self.mMovingObjects:
            mapObject = object.item.mapObject()
            undoStack.push(MoveMapObject(self.mapDocument(), mapObject, object.oldPosition))
            undoStack.push(RotateMapObject(self.mapDocument(), mapObject, object.oldRotation))

        undoStack.endMacro()
        self.mMovingObjects.clear()

    def startResizing(self):
        self.mAction = Action.Resizing
        self.mOrigin = self.mOriginIndicator.pos()
        self.mResizingLimitHorizontal = self.mClickedResizeHandle.resizingLimitHorizontal()
        self.mResizingLimitVertical = self.mClickedResizeHandle.resizingLimitVertical()
        self.mStart = self.mClickedResizeHandle.pos()
        self.saveSelectionState()
        self.updateHandleVisibility()

    def updateResizingItems(self, pos, modifiers):
        renderer = self.mapDocument().renderer()
        resizingOrigin = self.mClickedResizeHandle.resizingOrigin()
        if (modifiers & Qt.ShiftModifier):
            resizingOrigin = self.mOrigin
        self.mOriginIndicator.setPos(resizingOrigin)
        ## Alternative toggle snap modifier, since Control is taken by the preserve
        # aspect ratio option.
        ##
        snapHelper = SnapHelper(renderer)
        if (modifiers & Qt.AltModifier):
            snapHelper.toggleSnap()
        pixelPos = renderer.screenToPixelCoords_(pos)
        snapHelper.snap(pixelPos)
        snappedScreenPos = renderer.pixelToScreenCoords_(pixelPos)
        diff = snappedScreenPos - resizingOrigin
        startDiff = self.mStart - resizingOrigin
        if (self.mMovingObjects.size() == 1):
            ## For single items the resizing is performed in object space in order
            # to handle different scaling on X and Y axis as well as to improve
            # handling of 0-sized objects.
            ##
            self.updateResizingSingleItem(resizingOrigin, snappedScreenPos, modifiers)
            return

        ## Calculate the scaling factor. Minimum is 1% to protect against making
        # everything 0-sized and non-recoverable (it's still possibly to run into
        # problems by repeatedly scaling down to 1%, but that's asking for it)
        ##
        scale = 0.0
        if (self.mResizingLimitHorizontal):
            scale = max(0.01, diff.y() / startDiff.y())
        elif (self.mResizingLimitVertical):
            scale = max(0.01, diff.x() / startDiff.x())
        else:
            scale = min(max(0.01, diff.x() / startDiff.x()),
                         max(0.01, diff.y() / startDiff.y()))

        if not math.isfinite(scale):
            scale = 1
        
        for object in self.mMovingObjects:
            mapObject = object.item.mapObject()
            offset = mapObject.objectGroup().offset()
        
            oldRelPos = object.oldItemPosition + offset - resizingOrigin
            scaledRelPos = QPointF(oldRelPos.x() * scale, oldRelPos.y() * scale)
            newScreenPos = resizingOrigin + scaledRelPos - offset
            newPos = renderer.screenToPixelCoords_(newScreenPos)
            origSize = object.oldSize
            newSize = QSizeF(origSize.width() * scale, origSize.height() * scale)
            if (mapObject.polygon().isEmpty() == False):
                # For polygons, we have to scale in object space.
                rotation = object.item.rotation() * M_PI / -180
                sn = math.sin(rotation)
                cs = math.cos(rotation)
                oldPolygon = object.oldPolygon
                newPolygon = QPolygonF(oldPolygon.size())
                for n in range(oldPolygon.size()):
                    oldPoint = QPointF(oldPolygon[n])
                    rotPoint = QPointF(oldPoint.x() * cs + oldPoint.y() * sn, oldPoint.y() * cs - oldPoint.x() * sn)
                    scaledPoint = QPointF(rotPoint.x() * scale, rotPoint.y() * scale)
                    newPoint = QPointF(scaledPoint.x() * cs - scaledPoint.y() * sn, scaledPoint.y() * cs + scaledPoint.x() * sn)
                    newPolygon[n] = newPoint

                mapObject.setPolygon(newPolygon)

            mapObject.setSize(newSize)
            mapObject.setPosition(newPos)
        
        self.mapDocument().mapObjectModel().emitObjectsChanged(self.changingObjects())
        
    def updateResizingSingleItem(self, resizingOrigin, screenPos, modifiers):
        renderer = self.mapDocument().renderer()
        object = self.mMovingObjects.first()
        mapObject = object.item.mapObject()
        
        ## The resizingOrigin, screenPos and mStart are affected by the ObjectGroup
        # offset. We will un-apply it to these variables since the resize for
        # single items happens in local coordinate space.
        ##
        offset = mapObject.objectGroup().offset()
    
        ## These transformations undo and redo the object rotation, which is always
        # applied in screen space.
        ##
        unrotate = rotateAt(object.oldItemPosition, -object.oldRotation)
        rotate = rotateAt(object.oldItemPosition, object.oldRotation)
        origin = (resizingOrigin - offset) * unrotate
        pos = (screenPos - offset) * unrotate
        start = (self.mStart - offset) * unrotate
        oldPos = object.oldItemPosition
        ## In order for the resizing to work somewhat sanely in isometric mode,
        # the resizing is performed in pixel space except for tile objects, which
        # are not affected by isometric projection apart from their position.
        ##
        pixelSpace = resizeInPixelSpace(mapObject)
        preserveAspect = modifiers & Qt.ControlModifier
        if (pixelSpace):
            origin = renderer.screenToPixelCoords_(origin)
            pos = renderer.screenToPixelCoords_(pos)
            start = renderer.screenToPixelCoords_(start)
            oldPos = object.oldPosition

        newPos = oldPos
        newSize = object.oldSize
        ## In case one of the anchors was used as-is, the desired size can be
        # derived directly from the distance from the origin for rectangle
        # and ellipse objects. This allows scaling up a 0-sized object without
        # dealing with infinite scaling factor issues.
        #
        # For obvious reasons this can't work on polygons or polylines, nor when
        # preserving the aspect ratio.
        ##
        if (self.mClickedResizeHandle.resizingOrigin() == resizingOrigin and (mapObject.shape() == MapObject.Rectangle or
                 mapObject.shape() == MapObject.Ellipse) and not preserveAspect):
            newBounds = QRectF(newPos, newSize)
            newBounds = align(newBounds, mapObject.alignment())
            x = self.mClickedResizeHandle.anchorPosition()
            if x==AnchorPosition.LeftAnchor or x==AnchorPosition.TopLeftAnchor or x==AnchorPosition.BottomLeftAnchor:
                newBounds.setLeft(min(pos.x(), origin.x()))
            elif x==AnchorPosition.RightAnchor or x==AnchorPosition.TopRightAnchor or x==AnchorPosition.BottomRightAnchor:
                newBounds.setRight(max(pos.x(), origin.x()))
            else:
                # nothing to do on this axis
                pass

            x = self.mClickedResizeHandle.anchorPosition()
            if x==AnchorPosition.TopAnchor or x==AnchorPosition.TopLeftAnchor or x==AnchorPosition.TopRightAnchor:
                newBounds.setTop(min(pos.y(), origin.y()))
            elif x==AnchorPosition.BottomAnchor or x==AnchorPosition.BottomLeftAnchor or x==AnchorPosition.BottomRightAnchor:
                newBounds.setBottom(max(pos.y(), origin.y()))
            else:
                # nothing to do on this axis
                pass

            newBounds = unalign(newBounds, mapObject.alignment())
            newSize = newBounds.size()
            newPos = newBounds.topLeft()
        else:
            relPos = pos - origin
            startDiff = start - origin
            try:
                newx = relPos.x() / startDiff.x()
            except:
                newx = 0
            try:
                newy = relPos.y() / startDiff.y()
            except:
                newy = 0
            scalingFactor = QSizeF(max(0.01, newx), max(0.01, newy))
            if not math.isfinite(scalingFactor.width()):
                scalingFactor.setWidth(1)
            if not math.isfinite(scalingFactor.height()):
                scalingFactor.setHeight(1)
            
            if (self.mResizingLimitHorizontal):
                if preserveAspect:
                    scalingFactor.setWidth(scalingFactor.height())
                else:
                    scalingFactor.setWidth(1)
            elif (self.mResizingLimitVertical):
                if preserveAspect:
                    scalingFactor.setHeight(scalingFactor.width())
                else:
                    scalingFactor.setHeight(1)
            elif (preserveAspect):
                scale = min(scalingFactor.width(), scalingFactor.height())
                scalingFactor.setWidth(scale)
                scalingFactor.setHeight(scale)

            oldRelPos = oldPos - origin
            newPos = origin + QPointF(oldRelPos.x() * scalingFactor.width(), oldRelPos.y() * scalingFactor.height())
            newSize.setWidth(newSize.width() * scalingFactor.width())
            newSize.setHeight(newSize.height() * scalingFactor.height())
            if (not object.oldPolygon.isEmpty()):
                newPolygon = QPolygonF(object.oldPolygon.size())
                for n in range(object.oldPolygon.size()):
                    point = object.oldPolygon[n]
                    newPolygon[n] = QPointF(point.x() * scalingFactor.width(), point.y() * scalingFactor.height())

                mapObject.setPolygon(newPolygon)

        if (pixelSpace):
            newPos = renderer.pixelToScreenCoords_(newPos)
        newPos = renderer.screenToPixelCoords_(newPos * rotate)
        mapObject.setSize(newSize)
        mapObject.setPosition(newPos)
        self.mapDocument().mapObjectModel().emitObjectsChanged(self.changingObjects())
        
    def finishResizing(self, pos):
        self.mAction = Action.NoAction
        self.updateHandles()
        if (self.mStart == pos): # No scaling at all
            return
        undoStack = self.mapDocument().undoStack()
        undoStack.beginMacro(self.tr("Resize %n Object(s)", "", self.mMovingObjects.size()))
        for object in self.mMovingObjects:
            mapObject = object.item.mapObject()
            undoStack.push(MoveMapObject(self.mapDocument(), mapObject, object.oldPosition))
            undoStack.push(ResizeMapObject(self.mapDocument(), mapObject, object.oldSize))
            if (not object.oldPolygon.isEmpty()):
                undoStack.push(ChangePolygon(self.mapDocument(), mapObject, object.oldPolygon))

        undoStack.endMacro()
        self.mMovingObjects.clear()

    def setMode(self, mode):
        if (self.mMode != mode):
            self.mMode = mode
            self.updateHandles()

    def saveSelectionState(self):
        self.mMovingObjects.clear()
        # Remember the initial state before moving, resizing or rotating
        for item in self.mapScene().selectedObjectItems():
            mapObject = item.mapObject()
            object = MovingObject()
            object.item = item
            object.oldItemPosition = item.pos()
            object.oldPosition = mapObject.position()
            object.oldSize = mapObject.size()
            object.oldPolygon = mapObject.polygon()
            object.oldRotation = mapObject.rotation()

            self.mMovingObjects.append(object)

    def refreshCursor(self):
        cursorShape = Qt.ArrowCursor

        if self.mAction == Action.NoAction:
            hasSelection = not self.mapScene().selectedObjectItems().isEmpty()

            if ((self.mHoveredObjectItem or ((self.mModifiers & Qt.AltModifier) and hasSelection)) and not (self.mModifiers & Qt.ShiftModifier)):
                cursorShape = Qt.SizeAllCursor
        elif self.mAction == Action.Moving:
            cursorShape = Qt.SizeAllCursor

        if self.cursor.shape != cursorShape:
            self.setCursor(cursorShape)

    def snapToGrid(self, diff, modifiers):
        renderer = self.mapDocument().renderer()
        snapHelper = SnapHelper(renderer, modifiers)
        if (snapHelper.snaps()):
            alignScreenPos = renderer.pixelToScreenCoords_(self.mAlignPosition)
            newAlignScreenPos = alignScreenPos + diff
            newAlignPixelPos = renderer.screenToPixelCoords_(newAlignScreenPos)
            snapHelper.snap(newAlignPixelPos)
            return renderer.pixelToScreenCoords_(newAlignPixelPos) - alignScreenPos

        return diff

    def changingObjects(self):
        changingObjects = QList()
        
        for movingObject in self.mMovingObjects:
            changingObjects.append(movingObject.item.mapObject())

        return changingObjects
