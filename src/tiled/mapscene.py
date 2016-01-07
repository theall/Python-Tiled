##
# mapscene.py
# Copyright 2008-2013, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2008, Roderic Morris <roderic@ccs.neu.edu>
# Copyright 2009, Edward Hutchins
# Copyright 2010, Jeff Bland <jeff@teamphobic.com>
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

from containerhelpers import contains
from objectselectionitem import ObjectSelectionItem
from tilesetmanager import TilesetManager
from imagelayeritem import ImageLayerItem
from tileselectionitem import TileSelectionItem
from tilelayeritem import TileLayerItem
import preferences
from objectgroupitem import ObjectGroupItem
from objectgroup import ObjectGroup
from maprenderer import RenderFlag
from mapobjectitem import MapObjectItem
from pyqtcore import QVector, QMap, QList, QSet
from PyQt5.QtGui import (
    QPen
)
from PyQt5.QtCore import (
    Qt,
    QRectF,
    QPointF,
    QEvent,
    pyqtSignal, 
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsRectItem,
    QGraphicsScene
)
darkeningFactor = 0.6
opacityFactor = 0.4

##
# A graphics scene that represents the contents of a map.
##
class MapScene(QGraphicsScene):
    selectedObjectItemsChanged = pyqtSignal()

    ##
    # Constructor.
    ##
    def __init__(self, parent):
        super().__init__(parent)
        self.mMapDocument = None
        self.mSelectedTool = None
        self.mActiveTool = None
        self.mObjectSelectionItem = None
        self.mUnderMouse = False
        self.mCurrentModifiers = Qt.NoModifier,
        self.mDarkRectangle = QGraphicsRectItem()
        self.mDefaultBackgroundColor = Qt.darkGray

        self.mLayerItems = QVector()
        self.mObjectItems = QMap()
        self.mObjectLineWidth = 0.0
        self.mSelectedObjectItems = QSet()
        self.mLastMousePos = QPointF()
        self.mShowTileObjectOutlines = False
        self.mHighlightCurrentLayer = False
        self.mGridVisible = False

        self.setBackgroundBrush(self.mDefaultBackgroundColor)
        tilesetManager = TilesetManager.instance()
        tilesetManager.tilesetChanged.connect(self.tilesetChanged)
        tilesetManager.repaintTileset.connect(self.tilesetChanged)
        prefs = preferences.Preferences.instance()
        prefs.showGridChanged.connect(self.setGridVisible)
        prefs.showTileObjectOutlinesChanged.connect(self.setShowTileObjectOutlines)
        prefs.objectTypesChanged.connect(self.syncAllObjectItems)
        prefs.highlightCurrentLayerChanged.connect(self.setHighlightCurrentLayer)
        prefs.gridColorChanged.connect(self.update)
        prefs.objectLineWidthChanged.connect(self.setObjectLineWidth)
        self.mDarkRectangle.setPen(QPen(Qt.NoPen))
        self.mDarkRectangle.setBrush(Qt.black)
        self.mDarkRectangle.setOpacity(darkeningFactor)
        self.addItem(self.mDarkRectangle)
        self.mGridVisible = prefs.showGrid()
        self.mObjectLineWidth = prefs.objectLineWidth()
        self.mShowTileObjectOutlines = prefs.showTileObjectOutlines()
        self.mHighlightCurrentLayer = prefs.highlightCurrentLayer()
        # Install an event filter so that we can get key events on behalf of the
        # active tool without having to have the current focus.
        QCoreApplication.instance().installEventFilter(self)

    ##
    # Destructor.
    ##
    def __del__(self):
        if QCoreApplication.instance():
            QCoreApplication.instance().removeEventFilter(self)

    ##
    # Returns the map document this scene is displaying.
    ##
    def mapDocument(self):
        return self.mMapDocument

    ##
    # Sets the map this scene displays.
    ##
    def setMapDocument(self, mapDocument):
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
            if (not self.mSelectedObjectItems.isEmpty()):
                self.mSelectedObjectItems.clear()
                self.selectedObjectItemsChanged.emit()

        self.mMapDocument = mapDocument
        if (self.mMapDocument):
            renderer = self.mMapDocument.renderer()
            renderer.setObjectLineWidth(self.mObjectLineWidth)
            renderer.setFlag(RenderFlag.ShowTileObjectOutlines, self.mShowTileObjectOutlines)
            self.mMapDocument.mapChanged.connect(self.mapChanged)
            self.mMapDocument.regionChanged.connect(self.repaintRegion)
            self.mMapDocument.tileLayerDrawMarginsChanged.connect(self.tileLayerDrawMarginsChanged)
            self.mMapDocument.layerAdded.connect(self.layerAdded)
            self.mMapDocument.layerRemoved.connect(self.layerRemoved)
            self.mMapDocument.layerChanged.connect(self.layerChanged)
            self.mMapDocument.objectGroupChanged.connect(self.objectGroupChanged)
            self.mMapDocument.imageLayerChanged.connect(self.imageLayerChanged)
            self.mMapDocument.currentLayerIndexChanged.connect(self.currentLayerIndexChanged)
            self.mMapDocument.tilesetTileOffsetChanged.connect(self.tilesetTileOffsetChanged)
            self.mMapDocument.objectsInserted.connect(self.objectsInserted)
            self.mMapDocument.objectsRemoved.connect(self.objectsRemoved)
            self.mMapDocument.objectsChanged.connect(self.objectsChanged)
            self.mMapDocument.objectsIndexChanged.connect(self.objectsIndexChanged)
            self.mMapDocument.selectedObjectsChanged.connect(self.updateSelectedObjectItems)

        self.refreshScene()

    ##
    # Returns whether the tile grid is visible.
    ##
    def isGridVisible(self):
        return self.mGridVisible

    ##
    # Returns the set of selected map object items.
    ##
    def selectedObjectItems(self):
        return QSet(self.mSelectedObjectItems)

    ##
    # Sets the set of selected map object items. This translates to a call to
    # MapDocument.setSelectedObjects.
    ##
    def setSelectedObjectItems(self, items):
        # Inform the map document about the newly selected objects
        selectedObjects = QList()
        #selectedObjects.reserve(items.size())
        for item in items:
            selectedObjects.append(item.mapObject())
        self.mMapDocument.setSelectedObjects(selectedObjects)

    ##
    # Returns the MapObjectItem associated with the given \a mapObject.
    ##
    def itemForObject(self, object):
        return self.mObjectItems[object]

    ##
    # Enables the selected tool at this map scene.
    # Therefore it tells that tool, that this is the active map scene.
    ##
    def enableSelectedTool(self):
        if (not self.mSelectedTool or not self.mMapDocument):
            return
        self.mActiveTool = self.mSelectedTool
        self.mActiveTool.activate(self)
        self.mCurrentModifiers = QApplication.keyboardModifiers()
        if (self.mCurrentModifiers != Qt.NoModifier):
            self.mActiveTool.modifiersChanged(self.mCurrentModifiers)
        if (self.mUnderMouse):
            self.mActiveTool.mouseEntered()
            self.mActiveTool.mouseMoved(self.mLastMousePos, Qt.KeyboardModifiers())

    def disableSelectedTool(self):
        if (not self.mActiveTool):
            return
        if (self.mUnderMouse):
            self.mActiveTool.mouseLeft()
        self.mActiveTool.deactivate(self)
        self.mActiveTool = None

    ##
    # Sets the currently selected tool.
    ##
    def setSelectedTool(self, tool):
        self.mSelectedTool = tool

    ##
    # QGraphicsScene.drawForeground override that draws the tile grid.
    ##
    def drawForeground(self, painter, rect):
        if (not self.mMapDocument or not self.mGridVisible):
            return
            
        offset = QPointF()

        # Take into account the offset of the current layer
        layer = self.mMapDocument.currentLayer()
        if layer:
            offset = layer.offset()
            painter.translate(offset)
        
        prefs = preferences.Preferences.instance()
        self.mMapDocument.renderer().drawGrid(painter, rect.translated(-offset), prefs.gridColor())

    ##
    # Override for handling enter and leave events.
    ##
    def event(self, event):
        x = event.type()
        if x==QEvent.Enter:
            self.mUnderMouse = True
            if (self.mActiveTool):
                self.mActiveTool.mouseEntered()
        elif x==QEvent.Leave:
            self.mUnderMouse = False
            if (self.mActiveTool):
                self.mActiveTool.mouseLeft()
        else:
            pass

        return super().event(event)

    def keyPressEvent(self, event):
        if (self.mActiveTool):
            self.mActiveTool.keyPressed(event)
        if (not (self.mActiveTool and event.isAccepted())):
            super().keyPressEvent(event)

    def mouseMoveEvent(self, mouseEvent):
        self.mLastMousePos = mouseEvent.scenePos()
        if (not self.mMapDocument):
            return
        super().mouseMoveEvent(mouseEvent)
        if (mouseEvent.isAccepted()):
            return
        if (self.mActiveTool):
            self.mActiveTool.mouseMoved(mouseEvent.scenePos(), mouseEvent.modifiers())
            mouseEvent.accept()

    def mousePressEvent(self, mouseEvent):
        super().mousePressEvent(mouseEvent)
        if (mouseEvent.isAccepted()):
            return
        if (self.mActiveTool):
            mouseEvent.accept()
            self.mActiveTool.mousePressed(mouseEvent)

    def mouseReleaseEvent(self, mouseEvent):
        super().mouseReleaseEvent(mouseEvent)
        if (mouseEvent.isAccepted()):
            return
        if (self.mActiveTool):
            mouseEvent.accept()
            self.mActiveTool.mouseReleased(mouseEvent)

    ##
    # Override to ignore drag enter events.
    ##
    def dragEnterEvent(self, event):
        event.ignore()

    ##
    # Sets whether the tile grid is visible.
    ##
    def setGridVisible(self, visible):
        if (self.mGridVisible == visible):
            return
        self.mGridVisible = visible
        self.update()

    def setObjectLineWidth(self, lineWidth):
        if (self.mObjectLineWidth == lineWidth):
            return
        self.mObjectLineWidth = lineWidth
        if (self.mMapDocument):
            self.mMapDocument.renderer().setObjectLineWidth(lineWidth)
            # Changing the line width can change the size of the object items
            if (not self.mObjectItems.isEmpty()):
                for item in self.mObjectItems:
                    item.syncWithMapObject()
                self.update()

    def setShowTileObjectOutlines(self, enabled):
        if (self.mShowTileObjectOutlines == enabled):
            return
        self.mShowTileObjectOutlines = enabled
        if (self.mMapDocument):
            self.mMapDocument.renderer().setFlag(RenderFlag.ShowTileObjectOutlines, enabled)
            if (not self.mObjectItems.isEmpty()):
                self.update()

    ##
    # Sets whether the current layer should be highlighted.
    ##
    def setHighlightCurrentLayer(self, highlightCurrentLayer):
        if (self.mHighlightCurrentLayer == highlightCurrentLayer):
            return
        self.mHighlightCurrentLayer = highlightCurrentLayer
        self.updateCurrentLayerHighlight()

    ##
    # Refreshes the map scene.
    ##
    def refreshScene(self):
        self.mLayerItems.clear()
        self.mObjectItems.clear()
        self.removeItem(self.mDarkRectangle)
        self.clear()
        self.addItem(self.mDarkRectangle)
        if (not self.mMapDocument):
            self.setSceneRect(QRectF())
            return

        self.updateSceneRect()
        
        map = self.mMapDocument.map()
        self.mLayerItems.resize(map.layerCount())
        if (map.backgroundColor().isValid()):
            self.setBackgroundBrush(map.backgroundColor())
        else:
            self.setBackgroundBrush(self.mDefaultBackgroundColor)
        layerIndex = 0
        for layer in map.layers():
            layerItem = self.createLayerItem(layer)
            layerItem.setZValue(layerIndex)
            self.addItem(layerItem)
            self.mLayerItems[layerIndex] = layerItem
            layerIndex += 1

        tileSelectionItem = TileSelectionItem(self.mMapDocument)
        tileSelectionItem.setZValue(10000 - 2)
        self.addItem(tileSelectionItem)
        self.mObjectSelectionItem = ObjectSelectionItem(self.mMapDocument)
        self.mObjectSelectionItem.setZValue(10000 - 1)
        self.addItem(self.mObjectSelectionItem)
        self.updateCurrentLayerHighlight()

    ##
    # Repaints the specified region. The region is in tile coordinates.
    ##
    def repaintRegion(self, region, layer):
        renderer = self.mMapDocument.renderer()
        margins = self.mMapDocument.map().drawMargins()
        for r in region.rects():
            boundingRect = QRectF(renderer.boundingRect(r))
            self.update(QRectF(renderer.boundingRect(r).adjusted(-margins.left(),
                                                      -margins.top(),
                                                      margins.right(),
                                                      margins.bottom())))
            boundingRect.translate(layer.offset())
            self.update(boundingRect)

    def currentLayerIndexChanged(self):
        self.updateCurrentLayerHighlight()
        # New layer may have a different offset, affecting the grid
        if self.mGridVisible:
            self.update()
        
    ##
    # Adapts the scene, layers and objects to new map size, orientation or
    # background color.
    ##
    def mapChanged(self):
        self.updateSceneRect()
        for item in self.mLayerItems:
            tli = item
            if type(tli) == TileLayerItem:
                tli.syncWithTileLayer()

        for item in self.mObjectItems.values():
            item.syncWithMapObject()
        map = self.mMapDocument.map()
        if (map.backgroundColor().isValid()):
            self.setBackgroundBrush(map.backgroundColor())
        else:
            self.setBackgroundBrush(self.mDefaultBackgroundColor)

    def tilesetChanged(self, tileset):
        if (not self.mMapDocument):
            return
        if (contains(self.mMapDocument.map().tilesets(), tileset)):
            self.update()

    def tileLayerDrawMarginsChanged(self, tileLayer):
        index = self.mMapDocument.map().layers().indexOf(tileLayer)
        item = self.mLayerItems.at(index)
        item.syncWithTileLayer()

    def layerAdded(self, index):
        layer = self.mMapDocument.map().layerAt(index)
        layerItem = self.createLayerItem(layer)
        self.addItem(layerItem)
        self.mLayerItems.insert(index, layerItem)
        z = 0
        for item in self.mLayerItems:
            item.setZValue(z)
            z += 1

    def layerRemoved(self, index):
        self.mLayerItems.remove(index)

    ##
    # A layer has changed. This can mean that the layer visibility, opacity or
    # offset changed.
    ##
    def layerChanged(self, index):
        layer = self.mMapDocument.map().layerAt(index)
        layerItem = self.mLayerItems.at(index)
        layerItem.setVisible(layer.isVisible())
        multiplier = 1
        if (self.mHighlightCurrentLayer and self.mMapDocument.currentLayerIndex() < index):
            multiplier = opacityFactor
        layerItem.setOpacity(layer.opacity() * multiplier)
        layerItem.setPos(layer.offset())

        # Layer offset may have changed, affecting the scene rect and grid
        self.updateSceneRect()
        if self.mGridVisible:
            self.update()

    ##
    # When an object group has changed it may mean its color or drawing order
    # changed, which affects all its objects.
    ##
    def objectGroupChanged(self, objectGroup):
        self.objectsChanged(objectGroup.objects())
        self.objectsIndexChanged(objectGroup, 0, objectGroup.objectCount() - 1)

    ##
    # When an image layer has changed, it may change size and it may look
    # differently.
    ##
    def imageLayerChanged(self, imageLayer):
        index = self.mMapDocument.map().layers().indexOf(imageLayer)
        item = self.mLayerItems.at(index)
        item.syncWithImageLayer()
        item.update()

    ##
    # When the tile offset of a tileset has changed, it can affect the bounding
    # rect of all tile layers and tile objects. It also requires a full repaint.
    ##
    def tilesetTileOffsetChanged(self, tileset):
        self.update()
        for item in self.mLayerItems:
            tli = item
            if type(tli) == TileLayerItem:
                tli.syncWithTileLayer()
        for item in self.mObjectItems:
            cell = item.mapObject().cell()
            if (not cell.isEmpty() and cell.tile.tileset() == tileset):
                item.syncWithMapObject()

    ##
    # Inserts map object items for the given objects.
    ##
    def objectsInserted(self, objectGroup, first, last):
        ogItem = None
        # Find the object group item for the object group
        for item in self.mLayerItems:
            ogi = item
            if type(ogi)==ObjectGroupItem:
                if (ogi.objectGroup() == objectGroup):
                    ogItem = ogi
                    break

        drawOrder = objectGroup.drawOrder()
        for i in range(first, last+1):
            object = objectGroup.objectAt(i)
            item = MapObjectItem(object, self.mMapDocument, ogItem)
            if (drawOrder == ObjectGroup.DrawOrder.TopDownOrder):
                item.setZValue(item.y())
            else:
                item.setZValue(i)
            self.mObjectItems.insert(object, item)

    ##
    # Removes the map object items related to the given objects.
    ##
    def objectsRemoved(self, objects):
        for o in objects:
            i = self.mObjectItems.find(o)
            self.mSelectedObjectItems.remove(i)
            self.mObjectItems.erase(o)

    ##
    # Updates the map object items related to the given objects.
    ##
    def objectsChanged(self, objects):
        for object in objects:
            item = self.itemForObject(object)
            item.syncWithMapObject()

    ##
    # Updates the Z value of the objects when appropriate.
    ##
    def objectsIndexChanged(self, objectGroup, first, last):
        if (objectGroup.drawOrder() != ObjectGroup.DrawOrder.IndexOrder):
            return
        for i in range(first, last+1):
            item = self.itemForObject(objectGroup.objectAt(i))
            item.setZValue(i)

    def updateSelectedObjectItems(self):
        objects = self.mMapDocument.selectedObjects()
        items = QSet()
        for object in objects:
            item = self.itemForObject(object)
            if item:
                items.insert(item)

        self.mSelectedObjectItems = items
        self.selectedObjectItemsChanged.emit()

    def syncAllObjectItems(self):
        for item in self.mObjectItems:
            item.syncWithMapObject()

    def createLayerItem(self, layer):
        layerItem = None
        tl = layer.asTileLayer()
        if tl:
            layerItem = TileLayerItem(tl, self.mMapDocument)
        else:
            og = layer.asObjectGroup()
            if og:
                drawOrder = og.drawOrder()
                ogItem = ObjectGroupItem(og)
                objectIndex = 0
                for object in og.objects():
                    item = MapObjectItem(object, self.mMapDocument, ogItem)
                    if (drawOrder == ObjectGroup.DrawOrder.TopDownOrder):
                        item.setZValue(item.y())
                    else:
                        item.setZValue(objectIndex)
                    self.mObjectItems.insert(object, item)
                    objectIndex += 1

                layerItem = ogItem
            else:
                il = layer.asImageLayer()
                if il:
                    layerItem = ImageLayerItem(il, self.mMapDocument)

        layerItem.setVisible(layer.isVisible())
        return layerItem

    def updateSceneRect(self):
        mapSize = self.mMapDocument.renderer().mapSize()
        sceneRect = QRectF(0, 0, mapSize.width(), mapSize.height())

        margins = self.mMapDocument.map().computeLayerOffsetMargins()
        sceneRect.adjust(-margins.left(),
                         -margins.top(),
                         margins.right(),
                         margins.bottom())

        self.setSceneRect(sceneRect)
        self.mDarkRectangle.setRect(sceneRect)
        
    def updateCurrentLayerHighlight(self):
        if (not self.mMapDocument):
            return
        currentLayerIndex = self.mMapDocument.currentLayerIndex()
        if (not self.mHighlightCurrentLayer or currentLayerIndex == -1):
            self.mDarkRectangle.setVisible(False)
            # Restore opacity for all layers
            for i in range(self.mLayerItems.size()):
                layer = self.mMapDocument.map().layerAt(i)
                self.mLayerItems.at(i).setOpacity(layer.opacity())

            return

        # Darken layers below the current layer
        self.mDarkRectangle.setZValue(currentLayerIndex - 0.5)
        self.mDarkRectangle.setVisible(True)
        # Set layers above the current layer to half opacity
        for i in range(1, self.mLayerItems.size()):
            layer = self.mMapDocument.map().layerAt(i)
            if currentLayerIndex < i:
                _x = opacityFactor
            else:
                _x = 1
            multiplier = _x
            self.mLayerItems.at(i).setOpacity(layer.opacity() * multiplier)

    def eventFilter(self, object, event):
        x = event.type()
        if x==QEvent.KeyPress or x==QEvent.KeyRelease:
                keyEvent = event
                newModifiers = keyEvent.modifiers()
                if (self.mActiveTool and newModifiers != self.mCurrentModifiers):
                    self.mActiveTool.modifiersChanged(newModifiers)
                    self.mCurrentModifiers = newModifiers
        else:
            pass

        return False
