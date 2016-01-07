##
# stampbrush.py
# Copyright 2009-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2010 Stefan Beller, stefanbeller@googlemail.com
#
# This file is part of Tiled.
#
# This program is BrushBehavior.Free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the BrushBehavior.Free
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

from geometry import pointsOnLine, pointsOnEllipse
from tilestamp import TileStamp
from map import Map
from randompicker import RandomPicker
from painttilelayer import PaintTileLayer
from abstracttiletool import AbstractTileTool
from addremovetileset import AddTileset
from pyqtcore import QVector, QHash, QString
from tilelayer import TileLayer
from PyQt5.QtGui import (
    QIcon,
    QRegion,
    QKeySequence
)
from PyQt5.QtCore import (
    Qt,
    QRect,
    QSize,
    QPoint,
    pyqtSignal, 
    QCoreApplication
)

class PaintFlags():
    Mergeable               = 0x1
    SuppressRegionEdited    = 0x2
    
class PaintOperation():
    def __init__(self, pos=QPoint(), stamp=None):
        self.pos = pos
        self.stamp = stamp
    
##
# There are several options how the stamp utility can be used.
# It must be one of the following:
##
class BrushBehavior():
    Free=0           # nothing special: you can move the mouse,
                     # preview of the selection
    Paint=1          # left mouse pressed: BrushBehavior.Free painting
    Capture=2        # right mouse pressed: capture a rectangle
    Line=3           # hold shift: a line
    LineStartSet=4   # when you have defined a starting point,
                     # cancel with right click
    Circle=5         # hold Shift + Ctrl: a circle
    CircleMidSet=6

##
# Implements a tile brush that acts like a stamp. It is able to paint a block
# of tiles at the same time. The blocks can be captured from the map by
# right-click dragging, or selected from the tileset view.
##
class StampBrush(AbstractTileTool):
    ##
    # Emitted when the currently selected tiles changed. The stamp brush emits
    # this signal instead of setting its stamp directly so that the fill tool
    # also gets the new stamp.
    ##
    currentTilesChanged = pyqtSignal(list)
    
    ##
    # Emitted when a stamp was captured from the map. The stamp brush emits
    # this signal instead of setting its stamp directly so that the fill tool
    # also gets the new stamp.
    ##
    stampCaptured = pyqtSignal(TileStamp)
    
    def __init__(self, parent = None):
        super().__init__(self.tr("Stamp Brush"),
                           QIcon(":images/22x22/stock-tool-clone.png"),
                           QKeySequence(self.tr("B")),
                           parent)
        ##
        # This stores the current behavior.
        ##
        self.mBrushBehavior = BrushBehavior.Free

        self.mIsRandom = False
        self.mCaptureStart = QPoint()
        self.mRandomCellPicker = RandomPicker()
        ##
        # mStamp is a tile layer in which is the selection the user made
        # either by rightclicking (Capture) or at the tilesetdock
        ##
        self.mStamp = TileStamp()
        self.mPreviewLayer = None
        self.mMissingTilesets = QVector()
        self.mPrevTilePosition = QPoint()
        self.mStampReference = QPoint()

    def __del__(self):
        pass

    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('StampBrush', sourceText, disambiguation, n)

    def mousePressed(self, event):
        if (not self.brushItem().isVisible()):
            return
        if (event.button() == Qt.LeftButton):
            x = self.mBrushBehavior
            if x==BrushBehavior.Line:
                self.mStampReference = self.tilePosition()
                self.mBrushBehavior = BrushBehavior.LineStartSet
            elif x==BrushBehavior.Circle:
                self.mStampReference = self.tilePosition()
                self.mBrushBehavior = BrushBehavior.CircleMidSet
            elif x==BrushBehavior.LineStartSet:
                self.doPaint()
                self.mStampReference = self.tilePosition()
            elif x==BrushBehavior.CircleMidSet:
                self.doPaint()
            elif x==BrushBehavior.Paint:
                self.beginPaint()
            elif x==BrushBehavior.Free:
                self.beginPaint()
                self.mBrushBehavior = BrushBehavior.Paint
            elif x==BrushBehavior.Capture:
                pass
        else:
            if (event.button() == Qt.RightButton):
                self.beginCapture()

    def mouseReleased(self, event):
        x = self.mBrushBehavior
        if x==BrushBehavior.Capture:
            if (event.button() == Qt.RightButton):
                self.endCapture()
                self.mBrushBehavior = BrushBehavior.Free
        elif x==BrushBehavior.Paint:
            if (event.button() == Qt.LeftButton):
                self.mBrushBehavior = BrushBehavior.Free
                # allow going over different variations by repeatedly clicking
                self.updatePreview()
        else:
            # do nothing?
            pass

    def modifiersChanged(self, modifiers):
        if self.mStamp.isEmpty():
            return
        if (modifiers & Qt.ShiftModifier):
            if (modifiers & Qt.ControlModifier):
                if self.mBrushBehavior == BrushBehavior.LineStartSet:
                    self.mBrushBehavior = BrushBehavior.CircleMidSet
                else:
                    self.mBrushBehavior = BrushBehavior.Circle
            else:
                if self.mBrushBehavior == BrushBehavior.CircleMidSet:
                    self.mBrushBehavior = BrushBehavior.LineStartSet
                else:
                    self.mBrushBehavior = BrushBehavior.Line
        else:
            self.mBrushBehavior = BrushBehavior.Free
        
        self.updatePreview()
        
    def languageChanged(self):
        self.setName(self.tr("Stamp Brush"))
        self.setShortcut(QKeySequence(self.tr("B")))

    ##
    # Sets the stamp that is drawn when painting. The stamp brush takes
    # ownership over the stamp layer.
    ##
    def setStamp(self, stamp):
        if (self.mStamp == stamp):
            return
        
        self.mStamp = stamp
        self.updateRandomList()
        self.updatePreview()

    ##
    # This returns the current tile stamp used for painting.
    ##
    def stamp(self):
        return self.mStamp
        
    def setRandom(self, value):
        if self.mIsRandom == value:
            return
        self.mIsRandom = value

        self.updateRandomList()
        self.updatePreview()

    def tilePositionChanged(self, pos):
        x = self.mBrushBehavior
        if x==BrushBehavior.Paint:
            # Draw a line from the previous point to avoid gaps, skipping the
            # first point, since it was painted when the mouse was pressed, or the
            # last time the mouse was moved.
            points = pointsOnLine(self.mPrevTilePosition, pos)
            editedRegion = QRegion()
            
            ptSize = points.size()
            ptLast = ptSize - 1
            for i in range(1, ptSize):
                self.drawPreviewLayer(QVector(points[i]))

                # Only update the brush item for the last drawn piece
                if i == ptLast:
                    self.brushItem().setTileLayer(self.mPreviewLayer)

                editedRegion |= self.doPaint(PaintFlags.Mergeable | PaintFlags.SuppressRegionEdited)

            self.mapDocument().emitRegionEdited(editedRegion, self.currentTileLayer())
        else:
            self.updatePreview()
            
        self.mPrevTilePosition = pos

    def mapDocumentChanged(self, oldDocument, newDocument):
        super().mapDocumentChanged(oldDocument, newDocument)
        
        if newDocument:
            self.updateRandomList()
            self.updatePreview()

    def beginPaint(self):
        if (self.mBrushBehavior != BrushBehavior.Free):
            return
        self.mBrushBehavior = BrushBehavior.Paint
        self.doPaint()

    ##
    # Merges the tile layer of its brush item into the current map.
    #
    # \a flags can be set to Mergeable, which applies to the undo command.
    #
    # \a offsetX and \a offsetY give an offset where to merge the brush items tile
    # layer into the current map.
    #
    # Returns the edited region.
    ##
    def doPaint(self, flags = 0):
        preview = self.mPreviewLayer
        if not preview:
            return QRegion()

        # This method shouldn't be called when current layer is not a tile layer
        tileLayer = self.currentTileLayer()
        if (not tileLayer.bounds().intersects(QRect(preview.x(), preview.y(), preview.width(), preview.height()))):
            return QRegion()

        paint = PaintTileLayer(self.mapDocument(),
                                           tileLayer,
                                           preview.x(),
                                           preview.y(),
                                           preview)

        if not self.mMissingTilesets.isEmpty():
            for tileset in self.mMissingTilesets:
                AddTileset(self.mapDocument(), tileset, paint)

            self.mMissingTilesets.clear()

        paint.setMergeable(flags & PaintFlags.Mergeable)
        self.mapDocument().undoStack().push(paint)

        editedRegion = preview.region()
        if (not (flags & PaintFlags.SuppressRegionEdited)):
            self.mapDocument().emitRegionEdited(editedRegion, tileLayer)
        return editedRegion

    def beginCapture(self):
        if (self.mBrushBehavior != BrushBehavior.Free):
            return
        self.mBrushBehavior = BrushBehavior.Capture
        self.mCaptureStart = self.tilePosition()
        self.setStamp(TileStamp())

    def endCapture(self):
        if (self.mBrushBehavior != BrushBehavior.Capture):
            return
        self.mBrushBehavior = BrushBehavior.Free
        tileLayer = self.currentTileLayer()
        # Intersect with the layer and translate to layer coordinates
        captured = self.capturedArea()
        captured &= QRect(tileLayer.x(), tileLayer.y(),
                          tileLayer.width(), tileLayer.height())
        if (captured.isValid()):
            captured.translate(-tileLayer.x(), -tileLayer.y())
            map = tileLayer.map()
            capture = tileLayer.copy(captured)
            
            stamp = Map(map.orientation(),
                             capture.width(),
                             capture.height(),
                             map.tileWidth(),
                             map.tileHeight())
            # Add tileset references to map
            for tileset in capture.usedTilesets():
                stamp.addTileset(tileset)

            stamp.addLayer(capture)

            self.stampCaptured.emit(TileStamp(stamp))
        else:
            self.updatePreview()

    def capturedArea(self):
        captured = QRect(self.mCaptureStart, self.tilePosition()).normalized()
        if (captured.width() == 0):
            captured.adjust(-1, 0, 1, 0)
        if (captured.height() == 0):
            captured.adjust(0, -1, 0, 1)
        return captured

    ##
    # Updates the position of the brush item.
    ##
    def updatePreview(self, *args):
        l = len(args)
        if l==0:
            ##
            # Updates the position of the brush item based on the mouse position.
            ##
            self.updatePreview(self.tilePosition())
        elif l==1:
            tilePos = args[0]
            
            if not self.mapDocument():
                return

            tileRegion = QRegion()

            if self.mBrushBehavior == BrushBehavior.Capture:
                self.mPreviewLayer = None
                tileRegion = self.capturedArea()
            elif self.mStamp.isEmpty():
                self.mPreviewLayer = None
                tileRegion = QRect(tilePos, QSize(1, 1))
            else:
                if self.mBrushBehavior == BrushBehavior.LineStartSet:
                    self.drawPreviewLayer(pointsOnLine(self.mStampReference, tilePos))
                elif self.mBrushBehavior == BrushBehavior.CircleMidSet:
                    self.drawPreviewLayer(pointsOnEllipse(self.mStampReference, tilePos))
                elif self.mBrushBehavior == BrushBehavior.Capture:
                    # already handled above
                    pass
                elif self.mBrushBehavior == BrushBehavior.Circle:
                    # while finding the mid point, there is no need to show
                    # the (maybe bigger than 1x1) stamp
                    self.mPreviewLayer.clear()
                    tileRegion = QRect(tilePos, QSize(1, 1))
                elif self.mBrushBehavior==BrushBehavior.Line or self.mBrushBehavior==BrushBehavior.Free or self.mBrushBehavior==BrushBehavior.Paint:
                    self.drawPreviewLayer(QVector(tilePos))

            self.brushItem().setTileLayer(self.mPreviewLayer)
            if not tileRegion.isEmpty():
                self.brushItem().setTileRegion(tileRegion)

    ##
    # Updates the list used random stamps.
    # This is done by taking all non-null tiles from the original stamp mStamp.
    ##
    def updateRandomList(self):
        self.mRandomCellPicker.clear()

        if not self.mIsRandom:
            return

        self.mMissingTilesets.clear()
        
        for variation in self.mStamp.variations():
            self.mapDocument().unifyTilesets(variation.map, self.mMissingTilesets)
            tileLayer = variation.tileLayer()
            for x in range(tileLayer.width()):
                for y in range(tileLayer.height()):
                    cell = tileLayer.cellAt(x, y)
                    if not cell.isEmpty():
                        self.mRandomCellPicker.add(cell, cell.tile.probability())

    ##
    # Draws the preview layer.
    # It tries to put at all given points a stamp of the current stamp at the
    # corresponding position.
    # It also takes care, that no overlaps appear.
    # So it will check for every point if it can place a stamp there without
    # overlap.
    ##
    def drawPreviewLayer(self, _list):
        self.mPreviewLayer = None

        if self.mStamp.isEmpty():
            return

        if self.mIsRandom:
            if self.mRandomCellPicker.isEmpty():
                return

            paintedRegion = QRegion()
            for p in _list:
                paintedRegion += QRect(p, QSize(1, 1))

            bounds = paintedRegion.boundingRect()
            preview = TileLayer(QString(),
                                  bounds.x(), bounds.y(),
                                  bounds.width(), bounds.height())

            for p in _list:
                cell = self.mRandomCellPicker.pick()
                preview.setCell(p.x() - bounds.left(),
                                 p.y() - bounds.top(),
                                 cell)

            self.mPreviewLayer = preview
        else:
            self.mMissingTilesets.clear()

            paintedRegion = QRegion()
            operations = QVector()
            regionCache = QHash()

            for p in _list:
                variation = self.mStamp.randomVariation()
                self.mapDocument().unifyTilesets(variation.map, self.mMissingTilesets)

                stamp = variation.tileLayer()

                stampRegion = QRegion()
                if regionCache.contains(stamp):
                    stampRegion = regionCache.value(stamp)
                else:
                    stampRegion = stamp.region()
                    regionCache.insert(stamp, stampRegion)

                centered = QPoint(p.x() - int(stamp.width() / 2), p.y() - int(stamp.height() / 2))

                region = stampRegion.translated(centered.x(), centered.y())
                if not paintedRegion.intersects(region):
                    paintedRegion += region

                    op = PaintOperation(centered, stamp)
                    operations.append(op)

            bounds = paintedRegion.boundingRect()
            preview = TileLayer(QString(),
                                      bounds.x(), bounds.y(),
                                      bounds.width(), bounds.height())

            for op in operations:
                preview.merge(op.pos - bounds.topLeft(), op.stamp)
            
            self.mPreviewLayer = preview
