##
# tilepainter.py
# Copyright 2009-2011, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2009, Jeff Bland <jeff@teamphobic.com>
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

from tilelayer import Cell
from pyqtcore import QList, QVector
from PyQt5.QtCore import (
    QRect,
    QPoint
)
from PyQt5.QtGui import (
    QRegion
)
##
# The tile painter is meant for painting cells of a tile layer. It makes sure
# that each paint operation sends out the proper events, so that views can
# redraw the changed parts.
#
# This class also does bounds checking and when there is a tile selection, it
# will only draw within this selection.
##
class TilePainter():

    ##
    # Constructs a tile painter.
    #
    # @param mapDocument the map document to send change notifications to
    # @param tileLayer   the tile layer to edit
    ##
    def __init__(self, mapDocument, tileLayer):
        self.mMapDocument = mapDocument
        self.mTileLayer = tileLayer

    ##
    # Returns the cell at the given coordinates. The coordinates are relative
    # to the map origin. Returns an empty cell if the coordinates lay outside
    # of the layer.
    ##
    def cellAt(self, *args):
        l = len(args)
        if l==1:
            pos = args[0]
            return self.cellAt(pos.x(), pos.y())
        elif l==2:
            x, y = args
            layerX = x - self.mTileLayer.x()
            layerY = y - self.mTileLayer.y()
            if (not self.mTileLayer.contains(layerX, layerY)):
                return Cell()
            return self.mTileLayer.cellAt(layerX, layerY)

    ##
    # Sets the cell at the given coordinates. The coordinates are relative to
    # the map origin.
    ##
    def setCell(self, x, y, cell):
        selection = self.mMapDocument.selectedArea()
        if (not (selection.isEmpty() or selection.contains(QPoint(x, y)))):
            return
        layerX = x - self.mTileLayer.x()
        layerY = y - self.mTileLayer.y()
        if (not self.mTileLayer.contains(layerX, layerY)):
            return
        self.watcher = DrawMarginsWatcher(self.mMapDocument, self.mTileLayer)
        self.mTileLayer.setCell(layerX, layerY, cell)
        self.mMapDocument.emitRegionChanged(QRegion(x, y, 1, 1), self.mTileLayer)

    ##
    # Sets the cells at the given coordinates to the cells in the given tile
    # layer. The coordinates \a x and \a y are relative to the map origin.
    #
    # When a \a mask is given, only cells that fall within this mask are set.
    # The mask is applied in map coordinates.
    ##
    def setCells(self, x, y, tileLayer, mask = QRegion):
        region = self.paintableRegion(x, y,
                                         tileLayer.width(),
                                         tileLayer.height())
        if not mask.isEmpty():
            region &= mask
        if (region.isEmpty()):
            return
        self.watcher = DrawMarginsWatcher(self.mMapDocument, self.mTileLayer)
        self.mTileLayer.setCells(x - self.mTileLayer.x(),
                             y - self.mTileLayer.y(),
                             tileLayer,
                             region.translated(-self.mTileLayer.position()))
        self.mMapDocument.emitRegionChanged(region, self.mTileLayer)

    ##
    # Draws the cells in the given tile layer at the given coordinates. The
    # coordinates \a x and \a y are relative to the map origin.
    #
    # Empty cells are skipped.
    ##
    def drawCells(self, x, y, tileLayer):
        region = self.paintableRegion(x, y, tileLayer.width(), tileLayer.height())
        if (region.isEmpty()):
            return
        self.watcher = DrawMarginsWatcher(self.mMapDocument, self.mTileLayer)
        for rect in region.rects():
            for _y in range(rect.top(), rect.bottom()+1):
                for _x in range(rect.left(), rect.right()+1):
                    cell = tileLayer.cellAt(_x - x, _y - y)
                    if (cell.isEmpty()):
                        continue
                    self.mTileLayer.setCell(_x - self.mTileLayer.x(),
                                        _y - self.mTileLayer.y(),
                                        cell)

        self.mMapDocument.emitRegionChanged(region, self.mTileLayer)

    ##
    # Draws the stamp within the given \a drawRegion region, repeating the
    # stamp as needed.
    ##
    def drawStamp(self, stamp, drawRegion):
        if (stamp.bounds().isEmpty()):
            return
        region = self.paintableRegion(drawRegion)
        if (region.isEmpty()):
            return
        self.watcher = DrawMarginsWatcher(self.mMapDocument, self.mTileLayer)
        w = stamp.width()
        h = stamp.height()
        regionBounds = region.boundingRect()
        for rect in region.rects():
            for _y in range(rect.top(), rect.bottom()+1):
                for _x in range(rect.left(), rect.right()+1):
                    stampX = (_x - regionBounds.left()) % w
                    stampY = (_y - regionBounds.top()) % h
                    cell = stamp.cellAt(stampX, stampY)
                    if (cell.isEmpty()):
                        continue
                    self.mTileLayer.setCell(_x - self.mTileLayer.x(),
                                        _y - self.mTileLayer.y(),
                                        cell)

        self.mMapDocument.emitRegionChanged(region, self.mTileLayer)

    ##
    # Erases the cells in the given region.
    ##
    def erase(self, region):
        paintable = self.paintableRegion(region)
        if (paintable.isEmpty()):
            return
        self.mTileLayer.erase(paintable.translated(-self.mTileLayer.position()))
        self.mMapDocument.emitRegionChanged(paintable, self.mTileLayer)

    ##
    # Computes the paintable fill region made up of all cells of the same type
    # as that at \a fillOrigin that are connected.
    ##
    def computePaintableFillRegion(self, fillOrigin):
        region = fillRegion(self.mTileLayer, fillOrigin - self.mTileLayer.position())
        region.translate(self.mTileLayer.position())
        selection = self.mMapDocument.selectedArea()
        if (not selection.isEmpty()):
            region &= selection
        return region

    ##
    # Computes a fill region made up of all cells of the same type as that
    # at \a fillOrigin that are connected. Does not take into account the
    # current selection.
    ##
    def computeFillRegion(self, fillOrigin):
        region = fillRegion(self.mTileLayer, fillOrigin - self.mTileLayer.position())
        return region.translated(self.mTileLayer.position())

    ##
    # Returns True if the given cell is drawable.
    ##
    def isDrawable(self, x, y):
        selection = self.mMapDocument.selectedArea()
        if (not (selection.isEmpty() or selection.contains(QPoint(x, y)))):
            return False
        layerX = x - self.mTileLayer.x()
        layerY = y - self.mTileLayer.y()
        if (not self.mTileLayer.contains(layerX, layerY)):
            return False
        return True

    def paintableRegion(self, *args):
        l = len(args)
        if l==4:
            x, y, width, height = args
            return self.paintableRegion(QRect(x, y, width, height))
        elif l==1:
            region = args[0]
            bounds = QRegion(self.mTileLayer.bounds())
            intersection = bounds.intersected(region)
            selection = self.mMapDocument.selectedArea()
            if (not selection.isEmpty()):
                intersection &= selection
            return intersection

class DrawMarginsWatcher():

    def __init__(self, mapDocument, layer):
        self.mMapDocument = mapDocument
        self.mTileLayer = layer
        self.mDrawMargins = layer.drawMargins()

    def __del__(self):
        if (self.mTileLayer.map() == self.mMapDocument.map()):
            if (self.mTileLayer.drawMargins() != self.mDrawMargins):
                self.mMapDocument.emitTileLayerDrawMarginsChanged(self.mTileLayer)

def fillRegion(layer, fillOrigin):
    # Create that region that will hold the fill
    fillRegion = QRegion()
    # Silently quit if parameters are unsatisfactory
    if (not layer.contains(fillOrigin)):
        return fillRegion
    # Cache cell that we will match other cells against
    matchCell = layer.cellAt(fillOrigin)
    # Grab map dimensions for later use.
    layerWidth = layer.width()
    layerHeight = layer.height()
    layerSize = layerWidth * layerHeight
    # Create a queue to hold cells that need filling
    fillPositions = QList()
    fillPositions.append(fillOrigin)
    # Create an array that will store which cells have been processed
    # This is faster than checking if a given cell is in the region/list
    processedCellsVec = QVector()
    for i in range(layerSize):
        processedCellsVec.append(0xff)
    processedCells = processedCellsVec
    # Loop through queued positions and fill them, while at the same time
    # checking adjacent positions to see if they should be added
    while (not fillPositions.empty()):
        currentPoint = fillPositions.takeFirst()
        startOfLine = currentPoint.y() * layerWidth
        # Seek as far left as we can
        left = currentPoint.x()
        while (left > 0 and layer.cellAt(left - 1, currentPoint.y()) == matchCell):
            left -= 1
        # Seek as far right as we can
        right = currentPoint.x()
        while (right + 1 < layerWidth and layer.cellAt(right + 1, currentPoint.y()) == matchCell):
            right += 1
        # Add cells between left and right to the region
        fillRegion += QRegion(left, currentPoint.y(), right - left + 1, 1)
        # Add cell strip to processed cells
        for i in range(startOfLine + left, right + startOfLine, 1):
            processedCells[i] = 1
        # These variables cache whether the last cell was added to the queue
        # or not as an optimization, since adjacent cells on the x axis
        # do not need to be added to the queue.
        lastAboveCell = False
        lastBelowCell = False
        # Loop between left and right and check if cells above or
        # below need to be added to the queue
        for x in range(left, right+1):
            fillPoint = QPoint(x, currentPoint.y())
            # Check cell above
            if (fillPoint.y() > 0):
                aboveCell = QPoint(fillPoint.x(), fillPoint.y() - 1)
                if (not processedCells[aboveCell.y() * layerWidth + aboveCell.x()] and layer.cellAt(aboveCell) == matchCell):

                    # Do not add the above cell to the queue if its
                    # x-adjacent cell was added.
                    if (not lastAboveCell):
                        fillPositions.append(aboveCell)
                    lastAboveCell = True
                else:
                    lastAboveCell = False

                processedCells[aboveCell.y() * layerWidth + aboveCell.x()] = 1

            # Check cell below
            if (fillPoint.y() + 1 < layerHeight):
                belowCell = QPoint(fillPoint.x(), fillPoint.y() + 1)
                if (not processedCells[belowCell.y() * layerWidth + belowCell.x()] and layer.cellAt(belowCell) == matchCell):

                    # Do not add the below cell to the queue if its
                    # x-adjacent cell was added.
                    if (not lastBelowCell):
                        fillPositions.append(belowCell)
                    lastBelowCell = True
                else:
                    lastBelowCell = False

                processedCells[belowCell.y() * layerWidth + belowCell.x()] = 1

    return fillRegion
