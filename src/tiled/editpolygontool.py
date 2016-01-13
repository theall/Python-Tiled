##
# editpolygontool.py
# Copyright 2011, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
#
# This file is part of Tiled.
#
# This program is free software you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
##

from utils import Utils
from mapobjectitem import MapObjectItem
from snaphelper import SnapHelper
from selectionrectangle import SelectionRectangle
from mapobject import MapObject
from changepolygon import ChangePolygon
from addremovemapobject import RemoveMapObject
from abstractobjecttool import AbstractObjectTool
from pyqtcore import QSet, QVector, QMap
from PyQt5.QtGui import (
    QIcon,
    QCursor,
    QTransform,
    QKeySequence
)
from PyQt5.QtCore import (
    Qt,
    QRectF,
    QPoint,
    QPointF, 
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QMenu,
    QGraphicsItem,
    QApplication
)
from pyqtcore import QMapList
##
# A tool that allows dragging around the points of a polygon.
##
class EditPolygonTool(AbstractObjectTool):
    NoMode, Selecting, Moving = range(3)

    def __init__(self, parent = None):
        super().__init__(self.tr("Edit Polygons"),
              QIcon(":images/24x24/tool-edit-polygons.png"),
              QKeySequence(self.tr("E")),
              parent)

        self.mSelectedHandles = QSet()
        self.mModifiers = Qt.KeyboardModifiers()
        self.mScreenStart = QPoint()
        self.mOldHandlePositions = QVector()
        self.mAlignPosition = QPointF()
        ## The list of handles associated with each selected map object
        self.mHandles = QMapList()
        self.mOldPolygons = QMap()
        self.mStart = QPointF()

        self.mSelectionRectangle = SelectionRectangle()
        self.mMousePressed = False
        self.mClickedHandle = None
        self.mClickedObjectItem = None
        self.mMode = EditPolygonTool.NoMode

    def __del__(self):
        del self.mSelectionRectangle

    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('EditPolygonTool', sourceText, disambiguation, n)

    def activate(self, scene):
        super().activate(scene)
        self.updateHandles()
        # TODO: Could be more optimal by separating the updating of handles from
        # the creation and removal of handles depending on changes in the
        # selection, and by only updating the handles of the objects that changed.
        self.mapDocument().objectsChanged.connect(self.updateHandles)
        scene.selectedObjectItemsChanged.connect(self.updateHandles)
        self.mapDocument().objectsRemoved.connect(self.objectsRemoved)

    def deactivate(self, scene):
        try:
            self.mapDocument().objectsChanged.disconnect(self.updateHandles)
            scene.selectedObjectItemsChanged.disconnect(self.updateHandles)
        except:
            pass
        # Delete all handles
        self.mHandles.clear()
        self.mSelectedHandles.clear()
        self.mClickedHandle = None
        super().deactivate(scene)

    def mouseEntered(self):
        pass
    def mouseMoved(self, pos, modifiers):
        super().mouseMoved(pos, modifiers)
        if (self.mMode == EditPolygonTool.NoMode and self.mMousePressed):
            screenPos = QCursor.pos()
            dragDistance = (self.mScreenStart - screenPos).manhattanLength()
            if (dragDistance >= QApplication.startDragDistance()):
                if (self.mClickedHandle):
                    self.startMoving()
                else:
                    self.startSelecting()

        x = self.mMode
        if x==EditPolygonTool.Selecting:
            self.mSelectionRectangle.setRectangle(QRectF(self.mStart, pos).normalized())
        elif x==EditPolygonTool.Moving:
            self.updateMovingItems(pos, modifiers)
        elif x==EditPolygonTool.NoMode:
            pass

    def mousePressed(self, event):
        if (self.mMode != EditPolygonTool.NoMode): # Ignore additional presses during select/move
            return
        x = event.button()
        if x==Qt.LeftButton:
            self.mMousePressed = True
            self.mStart = event.scenePos()
            self.mScreenStart = event.screenPos()
            items = self.mapScene().items(self.mStart,
                                                                   Qt.IntersectsItemShape,
                                                                   Qt.DescendingOrder,
                                                                   viewTransform(event))
            self.mClickedObjectItem = first(items, MapObjectItem)
            self.mClickedHandle = first(items, PointHandle)
        elif x==Qt.RightButton:
            items = self.mapScene().items(event.scenePos(),
                                                                   Qt.IntersectsItemShape,
                                                                   Qt.DescendingOrder,
                                                                   viewTransform(event))
            clickedHandle = first(items)
            if (clickedHandle or not self.mSelectedHandles.isEmpty()):
                self.showHandleContextMenu(clickedHandle,
                                      event.screenPos())
            else:
                super().mousePressed(event)
        else:
            super().mousePressed(event)

    def mouseReleased(self, event):
        if (event.button() != Qt.LeftButton):
            return
        x = self.mMode
        if x==EditPolygonTool.NoMode:
            if (self.mClickedHandle):
                selection = self.mSelectedHandles
                modifiers = event.modifiers()
                if (modifiers & (Qt.ShiftModifier | Qt.ControlModifier)):
                    if (selection.contains(self.mClickedHandle)):
                        selection.remove(self.mClickedHandle)
                    else:
                        selection.insert(self.mClickedHandle)
                else:
                    selection.clear()
                    selection.insert(self.mClickedHandle)

                self.setSelectedHandles(selection)
            elif (self.mClickedObjectItem):
                selection = self.mapScene().selectedObjectItems()
                modifiers = event.modifiers()
                if (modifiers & (Qt.ShiftModifier | Qt.ControlModifier)):
                    if (selection.contains(self.mClickedObjectItem)):
                        selection.remove(self.mClickedObjectItem)
                    else:
                        selection.insert(self.mClickedObjectItem)
                else:
                    selection.clear()
                    selection.insert(self.mClickedObjectItem)

                self.mapScene().setSelectedObjectItems(selection)
                self.updateHandles()
            elif (not self.mSelectedHandles.isEmpty()):
                # First clear the handle selection
                self.setSelectedHandles(QSet())
            else:
                # If there is no handle selection, clear the object selection
                self.mapScene().setSelectedObjectItems(QSet())
                self.updateHandles()
        elif x==EditPolygonTool.Selecting:
            self.updateSelection(event)
            self.mapScene().removeItem(self.mSelectionRectangle)
            self.mMode = EditPolygonTool.NoMode
        elif x==EditPolygonTool.Moving:
            self.finishMoving(event.scenePos())

        self.mMousePressed = False
        self.mClickedHandle = None

    def modifiersChanged(self, modifiers):
        self.mModifiers = modifiers

    def languageChanged(self):
        self.setName(self.tr("Edit Polygons"))
        self.setShortcut(QKeySequence(self.tr("E")))

    def updateHandles(self):
        selection = self.mapScene().selectedObjectItems()
        # First destroy the handles for objects that are no longer selected

        for l in range(len(self.mHandles)):
            i = self.mHandles.itemByIndex(l)
            if (not selection.contains(i[0])):
                for handle in i[1]:
                    if (handle.isSelected()):
                        self.mSelectedHandles.remove(handle)
                    del handle

                del self.mHandles[l]

        renderer = self.mapDocument().renderer()
        for item in selection:
            object = item.mapObject()
            if (not object.cell().isEmpty()):
                continue
            polygon = object.polygon()
            polygon.translate(object.position())
            pointHandles = self.mHandles.get(item)
            # Create missing handles
            while (pointHandles.size() < polygon.size()):
                handle = PointHandle(item, pointHandles.size())
                pointHandles.append(handle)
                self.mapScene().addItem(handle)

            # Remove superfluous handles
            while (pointHandles.size() > polygon.size()):
                handle = pointHandles.takeLast()
                if (handle.isSelected()):
                    self.mSelectedHandles.remove(handle)
                del handle

            # Update the position of all handles
            for i in range(pointHandles.size()):
                point = polygon.at(i)
                handlePos = renderer.pixelToScreenCoords_(point)
                internalHandlePos = handlePos - item.pos()
                pointHandles.at(i).setPos(item.mapToScene(internalHandlePos))

            self.mHandles.insert(item, pointHandles)

    def objectsRemoved(self, objects):
        if (self.mMode == EditPolygonTool.Moving):
            # Make sure we're not going to try to still change these objects when
            # finishing the move operation.
            # TODO: In addition to avoiding crashes, it would also be good to
            # disallow other actions while moving.
            for object in objects:
                self.mOldPolygons.remove(object)

    def deleteNodes(self):
        if (self.mSelectedHandles.isEmpty()):
            return
        p = groupIndexesByObject(self.mSelectedHandles)
        undoStack = self.mapDocument().undoStack()
        delText = self.tr("Delete %n Node(s)", "", self.mSelectedHandles.size())
        undoStack.beginMacro(delText)
        for i in p:
            object = i[0]
            indexRanges = i[1]
            oldPolygon = object.polygon()
            newPolygon = oldPolygon
            # Remove points, back to front to keep the indexes valid
            it = indexRanges.end()
            begin = indexRanges.begin()
            # assert: end != begin, since there is at least one entry
            while(it != begin):
                it -= 1
                newPolygon.remove(it.first(), it.length())
            if (newPolygon.size() < 2):
                # We've removed the entire object
                undoStack.push(RemoveMapObject(self.mapDocument(), object))
            else:
                undoStack.push(ChangePolygon(self.mapDocument(), object, newPolygon, oldPolygon))

        undoStack.endMacro()

    def joinNodes(self):
        if (self.mSelectedHandles.size() < 2):
            return
        p = groupIndexesByObject(self.mSelectedHandles)
        undoStack = self.mapDocument().undoStack()
        macroStarted = False
        for i in p:
            object = i[0]
            indexRanges = i[1]
            closed = object.shape() == MapObject.Polygon
            oldPolygon = object.polygon()
            newPolygon = joinPolygonNodes(oldPolygon, indexRanges,
                                                    closed)
            if (newPolygon.size() < oldPolygon.size()):
                if (not macroStarted):
                    undoStack.beginMacro(self.tr("Join Nodes"))
                    macroStarted = True

                undoStack.push(ChangePolygon(self.mapDocument(), object, newPolygon, oldPolygon))

        if (macroStarted):
            undoStack.endMacro()

    def splitSegments(self):
        if (self.mSelectedHandles.size() < 2):
            return
        p = groupIndexesByObject(self.mSelectedHandles)
        undoStack = self.mapDocument().undoStack()
        macroStarted = False
        for i in p:
            object = i[0]
            indexRanges = i[1]
            closed = object.shape() == MapObject.Polygon
            oldPolygon = object.polygon()
            newPolygon = splitPolygonSegments(oldPolygon, indexRanges,
                                                        closed)
            if (newPolygon.size() > oldPolygon.size()):
                if (not macroStarted):
                    undoStack.beginMacro(self.tr("Split Segments"))
                    macroStarted = True

                undoStack.push(ChangePolygon(self.mapDocument(), object, newPolygon, oldPolygon))

        if (macroStarted):
            undoStack.endMacro()

    def setSelectedHandles(self, handles):
        for handle in self.mSelectedHandles:
            if (not handles.contains(handle)):
                handle.setSelected(False)
        for handle in handles:
            if (not self.mSelectedHandles.contains(handle)):
                handle.setSelected(True)
        self.mSelectedHandles = handles

    def setSelectedHandle(self, handle):
        self.setSelectedHandles(QSet([handle]))

    def updateSelection(self, event):
        rect = QRectF(self.mStart, event.scenePos()).normalized()
        # Make sure the rect has some contents, otherwise intersects returns False
        rect.setWidth(max(1.0, rect.width()))
        rect.setHeight(max(1.0, rect.height()))
        oldSelection = self.mapScene().selectedObjectItems()
        if (oldSelection.isEmpty()):
            # Allow selecting some map objects only when there aren't any selected
            selectedItems = QSet()
            for item in self.mapScene().items(rect, Qt.IntersectsItemShape, Qt.DescendingOrder, viewTransform(event)):
                if type(item) == MapObjectItem:
                    selectedItems.insert(item)

            newSelection = QSet()
            if (event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)):
                newSelection = oldSelection | selectedItems
            else:
                newSelection = selectedItems

            self.mapScene().setSelectedObjectItems(newSelection)
            self.updateHandles()
        else:
            # Update the selected handles
            selectedHandles = QSet()
            for item in self.mapScene().items(rect, Qt.IntersectsItemShape, Qt.DescendingOrder, viewTransform(event)):
                if type(item) == PointHandle:
                    selectedHandles.insert(item)

            if (event.modifiers() & (Qt.ControlModifier | Qt.ShiftModifier)):
                self.setSelectedHandles(self.mSelectedHandles | selectedHandles)
            else:
                self.setSelectedHandles(selectedHandles)

    def startSelecting(self):
        self.mMode = EditPolygonTool.Selecting
        self.mapScene().addItem(self.mSelectionRectangle)

    def startMoving(self):
        # Move only the clicked handle, if it was not part of the selection
        if (not self.mSelectedHandles.contains(self.mClickedHandle)):
            self.setSelectedHandle(self.mClickedHandle)
        self.mMode = EditPolygonTool.Moving
        renderer = self.mapDocument().renderer()
        # Remember the current object positions
        self.mOldHandlePositions.clear()
        self.mOldPolygons.clear()
        self.mAlignPosition = renderer.screenToPixelCoords_((self.mSelectedHandles.begin()).pos())
        for handle in self.mSelectedHandles:
            pos = renderer.screenToPixelCoords_(handle.pos())
            self.mOldHandlePositions.append(handle.pos())
            if (pos.x() < self.mAlignPosition.x()):
                self.mAlignPosition.setX(pos.x())
            if (pos.y() < self.mAlignPosition.y()):
                self.mAlignPosition.setY(pos.y())
            mapObject = handle.mapObject()
            if (not self.mOldPolygons.contains(mapObject)):
                self.mOldPolygons.insert(mapObject, mapObject.polygon())

    def updateMovingItems(self, pos, modifiers):
        renderer = self.mapDocument().renderer()
        diff = pos - self.mStart
        snapHelper = SnapHelper(renderer, modifiers)
        if (snapHelper.snaps()):
            alignScreenPos = renderer.pixelToScreenCoords_(self.mAlignPosition)
            newAlignScreenPos = alignScreenPos + diff
            newAlignPixelPos = renderer.screenToPixelCoords_(newAlignScreenPos)
            snapHelper.snap(newAlignPixelPos)
            diff = renderer.pixelToScreenCoords_(newAlignPixelPos) - alignScreenPos

        i = 0
        for handle in self.mSelectedHandles:
            # update handle position
            newScreenPos = self.mOldHandlePositions.at(i) + diff
            handle.setPos(newScreenPos)

            # calculate new pixel position of polygon node
            item = handle.mapObjectItem()
            newInternalPos = item.mapFromScene(newScreenPos)
            newScenePos = item.pos() + newInternalPos
            newPixelPos = renderer.screenToPixelCoords_(newScenePos)

            # update the polygon
            mapObject = item.mapObject()
            polygon = mapObject.polygon()
            polygon[handle.pointIndex()] = newPixelPos - mapObject.position()
            self.mapDocument().mapObjectModel().setObjectPolygon(mapObject, polygon)

            i += 1

    def finishMoving(self, pos):
        self.mMode = EditPolygonTool.NoMode
        if (self.mStart == pos or self.mOldPolygons.isEmpty()): # Move is a no-op
            return
        undoStack = self.mapDocument().undoStack()
        undoStack.beginMacro(self.tr("Move %n Point(s)", "", self.mSelectedHandles.size()))
        # TODO: This isn't really optimal. Would be better to have a single undo
        # command that supports changing multiple map objects.
        for i in self.mOldPolygons:
            undoStack.push(ChangePolygon(self.mapDocument(), i[0], i[1]))

        undoStack.endMacro()
        self.mOldHandlePositions.clear()
        self.mOldPolygons.clear()

    def showHandleContextMenu(self, clickedHandle, screenPos):
        if (clickedHandle and not self.mSelectedHandles.contains(clickedHandle)):
            self.setSelectedHandle(clickedHandle)
        n = self.mSelectedHandles.size()
        delIcon = QIcon(":images/16x16/edit-delete.png")
        delText = self.tr("Delete %n Node(s)", "", n)
        menu = QMenu()
        deleteNodesAction = menu.addAction(delIcon, delText)
        joinNodesAction = menu.addAction(self.tr("Join Nodes"))
        splitSegmentsAction = menu.addAction(self.tr("Split Segments"))
        Utils.setThemeIcon(deleteNodesAction, "edit-delete")
        joinNodesAction.setEnabled(n > 1)
        splitSegmentsAction.setEnabled(n > 1)
        deleteNodesAction.triggered.connect(self.deleteNodes)
        joinNodesAction.triggered.connect(self.joinNodes)
        splitSegmentsAction.triggered.connect(self.splitSegments)
        menu.exec(screenPos)

##
# A handle that allows moving around a point of a polygon.
##
class PointHandle(QGraphicsItem):
    _Type = QGraphicsItem.UserType + 2
    def __init__(self, mapObjectItem, pointIndex):
        super().__init__()
        
        self.mMapObjectItem = mapObjectItem
        self.mPointIndex = pointIndex
        self.mSelected = False

        self.setFlags(QGraphicsItem.ItemIgnoresTransformations | QGraphicsItem.ItemIgnoresParentOpacity)
        self.setZValue(10000)
        self.setCursor(Qt.SizeAllCursor)

    def type(self):
        return PointHandle._Type

    def mapObjectItem(self):
        return self.mMapObjectItem
        
    def mapObject(self):
        return self.mMapObjectItem.mapObject()

    def pointIndex(self):
        return self.mPointIndex
        
    def setPointPosition(self, pos):
        # TODO: It could be faster to update the polygon only once when changing
        # multiple points of the same polygon.
        mapObject = self.mMapObjectItem.mapObject()
        polygon = mapObject.polygon()
        polygon[self.mPointIndex] = pos - mapObject.position()
        self.mMapObjectItem.setPolygon(polygon)

    # These hide the QGraphicsItem members
    def setSelected(self, selected):
        self.mSelected = selected
        self.update()

    def boundingRect(self):
        return QRectF(-5, -5, 10 + 1, 10 + 1)

    def paint(self, painter, option, widget = None):
        painter.setPen(Qt.black)
        if (self.mSelected):
            painter.setBrush(QApplication.palette().highlight())
            painter.drawRect(QRectF(-4, -4, 8, 8))
        else:
            painter.setBrush(Qt.lightGray)
            painter.drawRect(QRectF(-3, -3, 6, 6))

def first(items,_type):
    for item in items:
        t = item
        if type(t) == _type:
            return t
    return None

def viewTransform(event):
    widget = event.widget()
    if widget:
        view = widget.parent()
        if view:
            return view.transform()
    return QTransform()

##
# Creates and removes handle instances as necessary to adapt to a new object
# selection.
##
def groupIndexesByObject(handles):
    result = QMap()
    # Build the list of point indexes for each map object
    for handle in handles:
        pointIndexes = result[handle.mapObject()]
        pointIndexes.insert(handle.pointIndex())

    return result

##
# Joins the nodes at the given \a indexRanges. Each consecutive sequence
# of nodes will be joined into a single node at the average location.
#
# This method can deal with both polygons as well as polylines. For polygons,
# pass <code>true</code> for \a closed.
##
def joinPolygonNodes(polygon, indexRanges, closed):
    if (indexRanges.isEmpty()):
        return polygon
    # Do nothing when dealing with a polygon with less than 3 points
    # (we'd no longer have a polygon)
    n = polygon.size()
    if (n < 3):
        return polygon
    firstRange = indexRanges.begin()
    it = indexRanges.end()
    lastRange = it
    lastRange -= 1# We know there is at least one range
    result = polygon
    # Indexes need to be offset when first and last range are joined.
    indexOffset = 0
    # Check whether the first and last ranges connect
    if (firstRange.first() == 0 and lastRange.last() == n - 1):
        # Do nothing when the selection spans the whole polygon
        if (firstRange == lastRange):
            return polygon
        # Join points of the first and last range when the polygon is closed
        if (closed):
            averagePoint = QPointF()
            for i in range(firstRange.first(), firstRange.last()+1):
                averagePoint += polygon.at(i)
            for i in range(lastRange.first(), lastRange.last()+1):
                averagePoint += polygon.at(i)
            averagePoint /= firstRange.length() + lastRange.length()
            result.remove(lastRange.first(), lastRange.length())
            result.remove(1, firstRange.length() - 1)
            result.replace(0, averagePoint)
            indexOffset = firstRange.length() - 1
            # We have dealt with these ranges now
            # assert: firstRange != lastRange
            firstRange += 1
            it -= 1

    while (it != firstRange):
        it -= 1
        # Merge the consecutive nodes into a single average point
        averagePoint = QPointF()
        for i in range(it.first(), it.last()+1):
            averagePoint += polygon.at(i - indexOffset)
        averagePoint /= it.length()
        result.remove(it.first() + 1 - indexOffset, it.length() - 1)
        result.replace(it.first() - indexOffset, averagePoint)

    return result

##
# Splits the selected segments by inserting new nodes in the middle. The
# selected segments are defined by each pair of consecutive \a indexRanges.
#
# This method can deal with both polygons as well as polylines. For polygons,
# pass <code>true</code> for \a closed.
##
def splitPolygonSegments(polygon, indexRanges, closed):
    if (indexRanges.isEmpty()):
        return polygon
    n = polygon.size()
    result = polygon
    firstRange = indexRanges.begin()
    it = indexRanges.end()
    # assert: firstRange != it
    if (closed):
        lastRange = it
        lastRange -= 1# We know there is at least one range
        # Handle the case where the first and last nodes are selected
        if (indexRanges.item(firstRange)[0] == 0 and indexRanges.item(lastRange)[1] == n - 1):
            splitPoint = (result.first() + result.last()) / 2
            result.append(splitPoint)

    while (it != firstRange):
        it -= 1
        item = indexRanges.item(it)
        for i in range(item[1], item[0], -1):
            splitPoint = (result.at(i) + result.at(i - 1)) / 2
            result.insert(i, splitPoint)

    return result

