##
# tilesetview.py
# Copyright 2008-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from utils import Utils
from tile import Tile, setTerrainCorner
import preferences
from changetileterrain import ChangeTileTerrain
from PyQt5.QtCore import (
    Qt,
    QSize,
    QEvent,
    QRectF,
    QPoint,
    QModelIndex,
    pyqtSignal,
    QItemSelectionModel
)
from PyQt5.QtGui import (
    QPen,
    QIcon,
    QColor,
    QPainter,
    QPainterPath
)
from PyQt5.QtWidgets import (
    QMenu,
    QStyle,
    QHeaderView,
    QAbstractItemDelegate,
    QAbstractItemView,
    QTableView
)
##
# The tileset view. May only be used with the TilesetModel.
##
class TilesetView(QTableView):
    createNewTerrainSignal = pyqtSignal(Tile)
    terrainImageSelected = pyqtSignal(Tile)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.mZoomable = None
        self.mMapDocument = None
        self.mMarkAnimatedTiles = True
        self.mEditTerrain = False
        self.mEraseTerrain = False
        self.mTerrainId = -1
        self.mHoveredCorner = 0
        self.mTerrainChanged = False
        self.mHoveredIndex = QModelIndex()
        self.mDrawGrid = False

        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setItemDelegate(TileDelegate(self, self))
        self.setShowGrid(False)
        hHeader = self.horizontalHeader()
        vHeader = self.verticalHeader()
        hHeader.hide()
        vHeader.hide()
        hHeader.setSectionResizeMode(QHeaderView.ResizeToContents)
        vHeader.setSectionResizeMode(QHeaderView.ResizeToContents)
        hHeader.setMinimumSectionSize(1)
        vHeader.setMinimumSectionSize(1)
        # Hardcode this view on 'left to right' since it doesn't work properly
        # for 'right to left' languages.
        self.setLayoutDirection(Qt.LeftToRight)
        prefs = preferences.Preferences.instance()
        self.mDrawGrid = prefs.showTilesetGrid()
        self.grabGesture(Qt.PinchGesture)
        prefs.showTilesetGridChanged.connect(self.setDrawGrid)

    ##
    # Sets the map document associated with the tileset to be displayed, which
    # is needed for the undo support.
    ##
    def setMapDocument(self, mapDocument):
        self.mMapDocument = mapDocument

    def sizeHint(self):
        return QSize(130, 100)

    def sizeHintForColumn(self, column):
        model = self.tilesetModel()
        if (not model):
            return -1
        if (model.tileset().imageSource()==''):
            return super().sizeHintForColumn(column)
        tileWidth = model.tileset().tileWidth()
        if self.mDrawGrid:
            _x = 1
        else:
            _x = 0
        return round(tileWidth * self.scale()) + _x

    def sizeHintForRow(self, row):
        model = self.tilesetModel()
        if (not model):
            return -1
        if (model.tileset().imageSource()==''):
            return super().sizeHintForRow(row)
        tileHeight = model.tileset().tileHeight()
        if self.mDrawGrid:
            _x = 1
        else:
            _x = 0
        return round(tileHeight * self.scale()) + _x

    def setZoomable(self, zoomable):
        if (self.mZoomable):
            self.mZoomable.disconnect()
        if (zoomable):
            zoomable.scaleChanged.connect(self.adjustScale)
        self.mZoomable = zoomable
        self.adjustScale()

    def zoomable(self):
        return self.mZoomable

    ##
    # Returns the scale at which the tileset is displayed.
    ##
    def scale(self):
        if self.mZoomable:
            _x = self.mZoomable.scale()
        else:
            _x = 1
        return _x

    def drawGrid(self):
        return self.mDrawGrid

    ##
    # Convenience method that returns the model as a TilesetModel.
    ##
    def tilesetModel(self):
        return self.model()

    ##
    # Sets whether animated tiles should be marked graphically. Enabled by
    # default.
    ##
    def setMarkAnimatedTiles(self, enabled):
        if (self.mMarkAnimatedTiles == enabled):
            return
        self.mMarkAnimatedTiles = enabled
        self.viewport().update()

    def markAnimatedTiles(self):
        return self.mMarkAnimatedTiles

    ##
    # Returns whether terrain editing is enabled.
    # \sa terrainId
    ##
    def isEditTerrain(self):
        return self.mEditTerrain

    ##
    # Sets whether terrain editing is enabled.
    # \sa setTerrainId
    ##
    def setEditTerrain(self, enabled):
        if (self.mEditTerrain == enabled):
            return
        self.mEditTerrain = enabled
        self.setMouseTracking(True)
        self.viewport().update()

    ##
    # Sets whether terrain editing is in "erase" mode.
    # \sa setEditTerrain
    ##
    def setEraseTerrain(self, erase):
        self.mEraseTerrain = erase

    ##
    # The id of the terrain currently being specified. Set to -1 for erasing
    # terrain info.
    ##
    def terrainId(self):
        return self.mTerrainId

    ##
    # Sets the id of the terrain to specify on the tiles. An id of -1 allows
    # for erasing terrain information.
    ##
    def setTerrainId(self, terrainId):
        if (self.mTerrainId == terrainId):
            return
        self.mTerrainId = terrainId
        if (self.mEditTerrain):
            self.viewport().update()

    def hoveredIndex(self):
        return self.mHoveredIndex

    def hoveredCorner(self):
        return self.mHoveredCorner

    def event(self, event):
        if (self.mZoomable and event.type() == QEvent.Gesture):
            gestureEvent = event
            gesture = gestureEvent.gesture(Qt.PinchGesture)
            if gesture:
                self.mZoomable.handlePinchGesture(gesture)

        return super().event(event)

    def mousePressEvent(self, event):
        if (not self.mEditTerrain):
            super().mousePressEvent(event)
            return

        if (event.button() == Qt.LeftButton):
            self.applyTerrain()

    def mouseMoveEvent(self, event):
        if (not self.mEditTerrain):
            super().mouseMoveEvent(event)
            return

        pos = event.pos()
        hoveredIndex = self.indexAt(pos)
        hoveredCorner = 0
        if (hoveredIndex.isValid()):
            center = self.visualRect(hoveredIndex).center()
            if (pos.x() > center.x()):
                hoveredCorner += 1
            if (pos.y() > center.y()):
                hoveredCorner += 2

        if (self.mHoveredIndex != hoveredIndex or self.mHoveredCorner != hoveredCorner):
            previousHoveredIndex = self.mHoveredIndex
            self.mHoveredIndex = hoveredIndex
            self.mHoveredCorner = hoveredCorner
            if (previousHoveredIndex.isValid()):
                self.update(previousHoveredIndex)
            if (previousHoveredIndex != self.mHoveredIndex and self.mHoveredIndex.isValid()):
                self.update(self.mHoveredIndex)

        if (event.buttons() & Qt.LeftButton):
            self.applyTerrain()

    def mouseReleaseEvent(self, event):
        if (not self.mEditTerrain):
            super().mouseReleaseEvent(event)
            return

        if (event.button() == Qt.LeftButton):
            self.finishTerrainChange()

    def leaveEvent(self, event):
        if (self.mHoveredIndex.isValid()):
            previousHoveredIndex = self.mHoveredIndex
            self.mHoveredIndex = QModelIndex()
            self.update(previousHoveredIndex)

        super().leaveEvent(event)

    ##
    # Override to support zooming in and out using the mouse wheel.
    ##
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if (self.mZoomable and event.modifiers()&Qt.ControlModifier and delta!=0):
            self.mZoomable.handleWheelDelta(delta)
            return

        super().wheelEvent(event)

    ##
    # Allow changing tile properties through a context menu.
    ##
    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        model = self.tilesetModel()
        if (not model):
            return
        tile = model.tileAt(index)
        isExternal = model.tileset().isExternal()
        menu = QMenu()
        propIcon = QIcon(":images/16x16/document-properties.png")
        if (tile):
            if (self.mEditTerrain):
                # Select this tile to make sure it is clear that only a single
                # tile is being used.
                self.selectionModel().setCurrentIndex(index,
                                                  QItemSelectionModel.SelectCurrent |
                                                  QItemSelectionModel.Clear)
                addTerrain = menu.addAction(self.tr("Add Terrain Type"))
                addTerrain.setEnabled(not isExternal)
                addTerrain.triggered.connect(self.createNewTerrain)
                if (self.mTerrainId != -1):
                    setImage = menu.addAction(self.tr("Set Terrain Image"))
                    setImage.setEnabled(not isExternal)
                    setImage.triggered.connect(self.selectTerrainImage)

            else:
                tileProperties = menu.addAction(propIcon,
                                                         self.tr("Tile Properties..."))
                tileProperties.setEnabled(not isExternal)
                Utils.setThemeIcon(tileProperties, "document-properties")
                tileProperties.triggered.connect(self.editTileProperties)

            menu.addSeparator()

        toggleGrid = menu.addAction(self.tr("Show Grid"))
        toggleGrid.setCheckable(True)
        toggleGrid.setChecked(self.mDrawGrid)
        prefs = preferences.Preferences.instance()
        toggleGrid.toggled.connect(prefs.setShowTilesetGrid)
        menu.exec(event.globalPos())

    def createNewTerrain(self):
        tile = self.currentTile()
        if tile:
            self.createNewTerrainSignal.emit(tile)

    def selectTerrainImage(self):
        tile = self.currentTile()
        if tile:
            self.terrainImageSelected.emit(tile)

    def editTileProperties(self):
        tile = self.currentTile()
        if (not tile):
            return
        self.mMapDocument.setCurrentObject(tile)
        self.mMapDocument.emitEditCurrentObject()

    def setDrawGrid(self, drawGrid):
        self.mDrawGrid = drawGrid
        model = self.tilesetModel()
        if model:
            model.tilesetChanged()

    def adjustScale(self):
        model = self.tilesetModel()
        if model:
            model.tilesetChanged()

    def applyTerrain(self):
        if (not self.mHoveredIndex.isValid()):
            return
        tile = self.tilesetModel().tileAt(self.mHoveredIndex)
        if (not tile):
            return
        if self.mEraseTerrain:
            _x = 0xFF
        else:
            _x = self.mTerrainId
        terrain = setTerrainCorner(tile.terrain(), self.mHoveredCorner, _x)
        if (terrain == tile.terrain()):
            return
        command = ChangeTileTerrain(self.mMapDocument, tile, terrain)
        self.mMapDocument.undoStack().push(command)
        self.mTerrainChanged = True

    def finishTerrainChange(self):
        if (not self.mTerrainChanged):
            return
        # Prevent further merging since mouse was released
        self.mMapDocument.undoStack().push(ChangeTileTerrain())
        self.mTerrainChanged = False

    def currentTile(self):
        model = self.tilesetModel()
        if model:
            _x = model.tileAt(self.currentIndex())
        else:
            _x = None
        return _x

##
# The delegate for drawing tile items in the tileset view.
##
class TileDelegate(QAbstractItemDelegate):

    def __init__(self, tilesetView, parent = None):
        super().__init__(parent)

        self.mTilesetView = tilesetView

    def paint(self, painter, option, index):
        model = index.model()
        tile = model.tileAt(index)
        if (not tile):
            return
        tileImage = tile.image()
        if self.mTilesetView.drawGrid():
            _x = 1
        else:
            _x = 0
        extra = _x
        zoom = self.mTilesetView.scale()
        tileSize = tileImage.size() * zoom
        # Compute rectangle to draw the image in: bottom- and left-aligned
        targetRect = option.rect.adjusted(0, 0, -extra, -extra)
        targetRect.setTop(targetRect.bottom() - tileSize.height() + 1)
        targetRect.setRight(targetRect.left() + tileSize.width() - 1)
        # Draw the tile image
        zoomable = self.mTilesetView.zoomable()
        if zoomable:
            if (zoomable.smoothTransform()):
                painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(targetRect, tileImage)
        # Overlay with film strip when animated
        if (self.mTilesetView.markAnimatedTiles() and tile.isAnimated()):
            painter.save()

            scale = min(tileImage.width() / 32.0, tileImage.height() / 32.0)

            painter.setClipRect(targetRect)
            painter.translate(targetRect.right(), targetRect.bottom())
            painter.scale(scale * zoom, scale * zoom)
            painter.translate(-18, 3)
            painter.rotate(-45)
            painter.setOpacity(0.8)

            strip = QRectF(0, 0, 32, 6)
            
            painter.fillRect(strip, Qt.black)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(Qt.white)
            painter.setPen(Qt.NoPen)

            hole = QRectF(0, 0, strip.height() * 0.6, strip.height() * 0.6)
            step = (strip.height() - hole.height()) + hole.width()
            
            margin = (strip.height() - hole.height()) / 2
            x = (step - hole.width()) / 2
            while x < strip.right():
                hole.moveTo(x, margin)
                painter.drawRoundedRect(hole, 25, 25, Qt.RelativeSize)
                x += step
                
            painter.restore()
        
        # Overlay with highlight color when selected
        if (option.state & QStyle.State_Selected):
            opacity = painter.opacity()
            painter.setOpacity(0.5)
            painter.fillRect(targetRect, option.palette.highlight())
            painter.setOpacity(opacity)

        if (self.mTilesetView.isEditTerrain()):
            terrain = tile.terrain()
            paintTerrainOverlay(painter, terrain,
                                self.mTilesetView.terrainId(), targetRect,
                                option.palette.highlight().color())
            # Overlay with terrain corner indication when hovered
            if (index == self.mTilesetView.hoveredIndex()):
                pos = QPoint()
                x = self.mTilesetView.hoveredCorner()
                if x==0:
                    pos = targetRect.topLeft()
                elif x==1:
                    pos = targetRect.topRight()
                elif x==2:
                    pos = targetRect.bottomLeft()
                elif x==3:
                    pos = targetRect.bottomRight()

                painter.save()
                painter.setBrush(option.palette.highlight())
                painter.setClipRect(targetRect)
                painter.setRenderHint(QPainter.Antialiasing)
                pen = QPen(option.palette.highlight().color().darker(), 2)
                painter.setPen(pen)
                painter.drawEllipse(pos, targetRect.width() / 3, targetRect.height() / 3)
                painter.restore()

    def sizeHint(self, option, index):
        m = index.model()
        if self.mTilesetView.drawGrid():
            _x = 1
        else:
            _x = 0
        extra = _x
        tile = m.tileAt(index)
        if tile:
            tileSize = tile.size() * self.mTilesetView.scale()
            return QSize(tileSize.width() + extra,tileSize.height() + extra)

        return QSize(extra, extra)

class Corners():
    TopLeft = 1
    TopRight = 2
    BottomLeft = 4
    BottomRight = 8

##
# Returns a mask of the corners of a certain tile's \a terrain that contain
# the given \a terrainTypeId.
##
def terrainCorners(terrain, terrainTypeId):
    if terrainTypeId >= 0:
        terrainIndex = terrainTypeId
    else:
        terrainIndex = 0xFF

    if ((terrain >> 24) & 0xFF) == terrainIndex:
        _w = Corners.TopLeft
    else:
        _w = 0

    if ((terrain >> 16) & 0xFF) == terrainIndex:
        _x = Corners.TopRight
    else:
        _x = 0

    if ((terrain >> 8) & 0xFF) == terrainIndex:
        _y = Corners.BottomLeft
    else:
        _y = 0

    if (terrain & 0xFF) == terrainIndex:
        _z = Corners.BottomRight
    else:
        _z = 0

    return _w|_x|_y|_z

def invertCorners(corners):
    return corners ^ (Corners.TopLeft | Corners.TopRight | Corners.BottomLeft | Corners.BottomRight)

def paintCorners(painter, corners, rect):
    # FIXME: This only works right for orthogonal maps right now
    hx = rect.width() / 2
    hy = rect.height() / 2
    x = corners
    if x==Corners.TopLeft:
        painter.drawPie(rect.translated(-hx, -hy), -90 * 16, 90 * 16)
    elif x==Corners.TopRight:
        painter.drawPie(rect.translated(hx, -hy), 180 * 16, 90 * 16)
    elif x==Corners.TopRight | Corners.TopLeft:
        painter.drawRect(rect.x(), rect.y(), rect.width(), hy)
    elif x==Corners.BottomLeft:
        painter.drawPie(rect.translated(-hx, hy), 0, 90 * 16)
    elif x==Corners.BottomLeft | Corners.TopLeft:
        painter.drawRect(rect.x(), rect.y(), hx, rect.height())
    elif x==Corners.BottomLeft | Corners.TopRight:
        painter.drawPie(rect.translated(-hx, hy), 0, 90 * 16)
        painter.drawPie(rect.translated(hx, -hy), 180 * 16, 90 * 16)
    elif x==Corners.BottomLeft | Corners.TopRight | Corners.TopLeft:
        fill = QPainterPath()
        ellipse = QPainterPath()
        fill.addRect(rect)
        ellipse.addEllipse(rect.translated(hx, hy))
        painter.drawPath(fill.subtracted(ellipse))
    elif x==Corners.BottomRight:
        painter.drawPie(rect.translated(hx, hy), 90 * 16, 90 * 16)
    elif x==Corners.BottomRight | Corners.TopLeft:
        painter.drawPie(rect.translated(-hx, -hy), -90 * 16, 90 * 16)
        painter.drawPie(rect.translated(hx, hy), 90 * 16, 90 * 16)
    elif x==Corners.BottomRight | Corners.TopRight:
        painter.drawRect(rect.x() + hx, rect.y(), hx, rect.height())
    elif x==Corners.BottomRight | Corners.TopRight | Corners.TopLeft:
        fill = QPainterPath()
        ellipse = QPainterPath()
        fill.addRect(rect)
        ellipse.addEllipse(rect.translated(-hx, hy))
        painter.drawPath(fill.subtracted(ellipse))
    elif x==Corners.BottomRight | Corners.BottomLeft:
        painter.drawRect(rect.x(), rect.y() + hy, rect.width(), hy)
    elif x==Corners.BottomRight | Corners.BottomLeft | Corners.TopLeft:
        fill = QPainterPath()
        ellipse = QPainterPath()
        fill.addRect(rect)
        ellipse.addEllipse(rect.translated(hx, -hy))
        painter.drawPath(fill.subtracted(ellipse))
    elif x==Corners.BottomRight | Corners.BottomLeft | Corners.TopRight:
        fill = QPainterPath()
        ellipse = QPainterPath()
        fill.addRect(rect)
        ellipse.addEllipse(rect.translated(-hx, -hy))
        painter.drawPath(fill.subtracted(ellipse))
    elif x==Corners.BottomRight | Corners.BottomLeft | Corners.TopRight | Corners.TopLeft:
        painter.drawRect(rect)

def paintTerrainOverlay(painter, terrain, terrainTypeId, rect, color):
    painter.save()
    painter.setClipRect(rect)
    painter.setRenderHint(QPainter.Antialiasing)
    # Draw the "any terrain" background
    painter.setBrush(QColor(128, 128, 128, 100))
    painter.setPen(QPen(Qt.gray, 2))
    paintCorners(painter, invertCorners(terrainCorners(terrain, -1)), rect)
    if (terrainTypeId != -1):
        corners = terrainCorners(terrain, terrainTypeId)
        # Draw the shadow
        painter.translate(1, 1)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(Qt.black, 2))
        paintCorners(painter, corners, rect)
        # Draw the foreground
        painter.translate(-1, -1)
        painter.setBrush(QColor(color.red(), color.green(), color.blue(), 100))
        painter.setPen(QPen(color, 2))
        paintCorners(painter, corners, rect)

    painter.restore()
