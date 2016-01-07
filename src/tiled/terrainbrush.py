##
# terrainbrush.py
# Copyright 2009-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2010, Stefan Beller, stefanbeller@googlemail.com
# Copyright 2012, Manu Evans
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

from geometry import pointsOnLine
from tilelayer import TileLayer, Cell
from painttilelayer import PaintTileLayer
from abstracttiletool import AbstractTileTool, TilePositionMethod
from array import array
from randompicker import RandomPicker
from pyqtcore import QList, INT_MAX, QString

from PyQt5.QtGui import (
    QKeySequence,
    QIcon
)
from PyQt5.QtCore import (
    Qt,
    QRect,
    QPoint,
    QCoreApplication
)
def firstTerrain(mapDocument):
    if (not mapDocument):
        return None
    for tileset in mapDocument.map().tilesets():
        if (tileset.terrainCount() > 0):
            return tileset.terrain(0)
    return None

def makeTerrain(t):
    t &= 0xFF
    return t << 24 | t << 16 | t << 8 | t

def findBestTile(tileset, terrain, considerationMask):
    # we should have hooked 0xFFFFFFFF terrains outside this function
    # if all quadrants are set to 'no terrain', then the 'empty' tile is the only choice we can deduce
    if (terrain == 0xFFFFFFFF):
        return None
    matches = RandomPicker()
    penalty = INT_MAX
    # TODO: this is a slow linear search, perhaps we could use a better find algorithm...
    for t in tileset.tiles():
        if ((t.terrain() & considerationMask) != (terrain & considerationMask)):
            continue
        # calculate the tile transition penalty based on shortest distance to target terrain type
        tr = tileset.terrainTransitionPenalty(t.terrain() >> 24, terrain >> 24)
        tl = tileset.terrainTransitionPenalty((t.terrain() >> 16) & 0xFF, (terrain >> 16) & 0xFF)
        br = tileset.terrainTransitionPenalty((t.terrain() >> 8) & 0xFF, (terrain >> 8) & 0xFF)
        bl = tileset.terrainTransitionPenalty(t.terrain() & 0xFF, terrain & 0xFF)
        # if there is no path to the destination terrain, this isn't a useful transition
        if (tr < 0 or tl < 0 or br < 0 or bl < 0):
            continue
        # add tile to the candidate list
        transitionPenalty = tr + tl + br + bl
        if (transitionPenalty <= penalty):
            if (transitionPenalty < penalty):
                matches.clear()
            penalty = transitionPenalty
            matches.add(t, t.probability())

    # choose a candidate at random, with consideration for probability
    if (not matches.isEmpty()):
        return matches.pick()

    # TODO: conveniently, the None tile doesn't currently work, but when it does, we need to signal a failure to find any matches some other way
    return None

def terrain(tile):
    if tile:
        _x = tile.terrain()
    else:
        _x = 0xFFFFFFFF
    return _x

def topEdge(tile):
    return terrain(tile) >> 16

def bottomEdge(tile):
    return terrain(tile) & 0xFFFF

def leftEdge(tile):
    t = terrain(tile)
    return((t >> 16) & 0xFF00) | ((t >> 8) & 0xFF)

def rightEdge(tile):
    t = terrain(tile)
    return ((t >> 8) & 0xFF00) | (t & 0xFF)

class BrushMode():
    PaintTile = 1       # paint terrain to whole tiles
    PaintVertex = 2     # paint terrain to map vertices

##
# There are several options how the stamp utility can be used.
# It must be one of the following:
##
class BrushBehavior():
    Free = 1            # nothing special: you can move the mouse,
                        # preview of the selection
    Paint = 2           # left mouse pressed: free painting
    Line = 3            # hold shift: a line
    LineStartSet = 4    # when you have defined a starting point,
                        # cancel with right click
##
# Implements a tile brush that paints terrain with automatic transitions.
##
class TerrainBrush(AbstractTileTool):

    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('TerrainBrush', sourceText, disambiguation, n)

    def __init__(self, parent = None):
        super().__init__(self.tr("Terrain Brush"),
                           QIcon(":images/24x24/terrain-edit.png"),
                           QKeySequence(self.tr("T")),
                           parent)
        ##
        # The terrain we are currently painting.
        ##
        self.mTerrain = None
        self.mPaintX = 0
        self.mPaintY = 0
        self.mOffsetX = 0
        self.mOffsetY = 0
        self.mIsActive = False
        ##
        # This stores the current behavior.
        ##
        self.mBrushBehavior = BrushBehavior.Free
        ##
        # The starting position needed for drawing lines and circles.
        # When drawing lines, this point will be one end.
        # When drawing circles this will be the midpoint.
        ##
        self.mLineReferenceX = 0
        self.mLineReferenceY = 0

        self.setBrushMode(BrushMode.PaintTile)

    def __del__(self):
        pass

    def activate(self, scene):
        super().activate(scene)
        self.mIsActive = True

    def deactivate(self, scene):
        super().deactivate(scene)
        self.mIsActive = False

    def mousePressed(self, event):
        if (not self.brushItem().isVisible()):
            return
        if (event.button() == Qt.LeftButton):
            x = self.mBrushBehavior
            if x==BrushBehavior.Line:
                self.mLineReferenceX = self.mPaintX
                self.mLineReferenceY = self.mPaintY
                self.mBrushBehavior = BrushBehavior.LineStartSet
            elif x==BrushBehavior.LineStartSet:
                self.doPaint(False, self.mPaintX, self.mPaintY)
                self.mLineReferenceX = self.mPaintX
                self.mLineReferenceY = self.mPaintY
            elif x==BrushBehavior.Paint:
                self.beginPaint()
            elif x==BrushBehavior.Free:
                self.beginPaint()
                self.mBrushBehavior = BrushBehavior.Paint

        else:
            if (event.button() == Qt.RightButton):
                self.capture()

    def mouseReleased(self, event):
        x = self.mBrushBehavior
        if x==BrushBehavior.Paint:
            if (event.button() == Qt.LeftButton):
                self.mBrushBehavior = BrushBehavior.Free
        else:
            # do nothing?
            pass

    def modifiersChanged(self, modifiers):
        lineMode = modifiers & Qt.ShiftModifier
        if (lineMode != (self.mBrushBehavior == BrushBehavior.Line or
                         self.mBrushBehavior == BrushBehavior.LineStartSet)):
            if lineMode:
                _x = BrushBehavior.Line
            else:
                _x = BrushBehavior.Free
            self.mBrushBehavior = _x

        if modifiers & Qt.ControlModifier:
            _x = BrushMode.PaintVertex
        else:
            _x = BrushMode.PaintTile
        self.setBrushMode(_x)
        self.updateBrush(self.tilePosition())

    def languageChanged(self):
        self.setName(self.tr("Terrain Brush"))
        self.setShortcut(QKeySequence(self.tr("T")))

    ##
    # Sets the stamp that is drawn when painting. The stamp brush takes
    # ownership over the stamp layer.
    ##
    def setTerrain(self, terrain):
        if (self.mTerrain == terrain):
            return
        self.mTerrain = terrain
        if (self.mIsActive and self.brushItem().isVisible()):
            self.updateBrush(self.tilePosition())

    ##
    # This returns the actual tile layer which is used to define the current
    # state.
    ##
    def terrain(self):
        return self.mTerrain

    ##
    # Set the brush mode.
    ##
    def setBrushMode(self, mode):
        self.mBrushMode = mode
        if mode == BrushMode.PaintTile:
            _x = TilePositionMethod.OnTiles
        else:
            _x = TilePositionMethod.BetweenTiles
        self.setTilePositionMethod(_x)

    def tilePositionChanged(self, pos):
        x = self.mBrushBehavior
        if x==BrushBehavior.Paint:
            x = self.mPaintX
            y = self.mPaintY
            for p in pointsOnLine(x, y, pos.x() , pos.y()):
                self.updateBrush(p)
                self.doPaint(True, p.x(), p.y())
        elif x==BrushBehavior.LineStartSet:
            lineList = pointsOnLine(self.mLineReferenceX, self.mLineReferenceY, pos.x(), pos.y())
            self.updateBrush(pos, lineList)
        elif x==BrushBehavior.Line or x==BrushBehavior.Free:
            self.updateBrush(pos)

    def mapDocumentChanged(self, oldDocument, newDocument):
        super().mapDocumentChanged(oldDocument, newDocument)
        # Reset the brush, since it probably became invalid
        self.brushItem().clear()
        # Don't use setTerrain since we do not want to update the brush right now
        self.mTerrain = firstTerrain(newDocument)

    def beginPaint(self):
        if (self.mBrushBehavior != BrushBehavior.Free):
            return
        self.mBrushBehavior = BrushBehavior.Paint
        self.doPaint(False, self.mPaintX, self.mPaintY)

    ##
    # Merges the tile layer of its brush item into the current map.
    # mergeable determines if this can be merged with similar actions for undo.
    # whereX and whereY give an offset where to merge the brush items tilelayer
    # into the current map.
    ##
    def doPaint(self, mergeable, whereX, whereY):
        stamp = self.brushItem().tileLayer()
        if (not stamp):
            return
        # This method shouldn't be called when current layer is not a tile layer
        tileLayer = self.currentTileLayer()
        whereX -= self.mOffsetX
        whereY -= self.mOffsetY
        if (not tileLayer.bounds().intersects(QRect(whereX, whereY, stamp.width(), stamp.height()))):
            return
        paint = PaintTileLayer(self.mapDocument(), tileLayer, whereX, whereY, stamp)
        paint.setMergeable(mergeable)
        self.mapDocument().undoStack().push(paint)
        self.mapDocument().emitRegionEdited(self.brushItem().tileRegion(), tileLayer)

    def capture(self):
        tileLayer = self.currentTileLayer()
        # TODO: we need to know which corner the mouse is closest to...
        position = self.tilePosition()
        if (not tileLayer.contains(position)):
            return
        cell = tileLayer.cellAt(position)
        if (not cell.tile):
            return
        t = cell.tile.terrainAtCorner(0)
        self.setTerrain(t)

    ##
    # updates the brush given new coordinates.
    ##
    def updateBrush(self, cursorPos, _list = None):
        # get the current tile layer
        currentLayer = self.currentTileLayer()
        layerWidth = currentLayer.width()
        layerHeight = currentLayer.height()
        numTiles = layerWidth * layerHeight
        paintCorner = 0
        # if we are in vertex paint mode, the bottom right corner on the map will appear as an invalid tile offset...
        if (self.mBrushMode == BrushMode.PaintVertex):
            if (cursorPos.x() == layerWidth):
                cursorPos.setX(cursorPos.x() - 1)
                paintCorner |= 1

            if (cursorPos.y() == layerHeight):
                cursorPos.setY(cursorPos.y() - 1)
                paintCorner |= 2

        # if the cursor is outside of the map, bail out
        if (not currentLayer.bounds().contains(cursorPos)):
            return
        terrainTileset = None
        terrainId = -1
        if (self.mTerrain):
            terrainTileset = self.mTerrain.tileset()
            terrainId = self.mTerrain.id()

        # allocate a buffer to build the terrain tilemap (TODO: this could be retained per layer to save regular allocation)
        newTerrain = []
        for i in range(numTiles):
            newTerrain.append(0)
            
        # allocate a buffer of flags for each tile that may be considered (TODO: this could be retained per layer to save regular allocation)
        checked = array('B')
        for i in range(numTiles):
            checked.append(0)
        # create a consideration list, and push the start points
        transitionList = QList()
        initialTiles = 0
        if (_list):
            # if we were supplied a list of start points
            for p in _list:
                transitionList.append(p)
                initialTiles += 1

        else:
            transitionList.append(cursorPos)
            initialTiles = 1

        brushRect = QRect(cursorPos, cursorPos)
        # produce terrain with transitions using a simple, relative naive approach (considers each tile once, and doesn't allow re-consideration if selection was bad)
        while (not transitionList.isEmpty()):
            # get the next point in the consideration list
            p = transitionList.takeFirst()
            x = p.x()
            y = p.y()
            i = y*layerWidth + x
            # if we have already considered this point, skip to the next
            # TODO: we might want to allow re-consideration if prior tiles... but not for now, this would risk infinite loops
            if (checked[i]):
                continue
            tile = currentLayer.cellAt(p).tile
            currentTerrain = terrain(tile)
            # get the tileset for this tile
            tileset = None
            if (terrainTileset):
                # if we are painting a terrain, then we'll use the terrains tileset
                tileset = terrainTileset
            elif (tile):
                # if we're erasing terrain, use the individual tiles tileset (to search for transitions)
                tileset = tile.tileset()
            else:
                # no tile here and we're erasing terrain, not much we can do
                continue

            # calculate the ideal tile for this position
            preferredTerrain = 0xFFFFFFFF
            mask = 0
            if (initialTiles):
                # for the initial tiles, we will insert the selected terrain and add the surroundings for consideration
                if (self.mBrushMode == BrushMode.PaintTile):
                    # set the whole tile to the selected terrain
                    preferredTerrain = makeTerrain(terrainId)
                    mask = 0xFFFFFFFF
                else:
                    # Bail out if encountering a tile from a different tileset
                    if (tile and tile.tileset() != tileset):
                        continue
                    # calculate the corner mask
                    mask = 0xFF << (3 - paintCorner)*8
                    # mask in the selected terrain
                    preferredTerrain = (currentTerrain & ~mask) | (terrainId << (3 - paintCorner)*8)

                initialTiles -= 1
                # if there's nothing to paint... skip this tile
                if (preferredTerrain == currentTerrain and (not tile or tile.tileset() == tileset)):
                    continue
            else:
                # Bail out if encountering a tile from a different tileset
                if (tile and tile.tileset() != tileset):
                    continue
                # following tiles each need consideration against their surroundings
                preferredTerrain = currentTerrain
                mask = 0
                # depending which connections have been set, we update the preferred terrain of the tile accordingly
                if (y > 0 and checked[i - layerWidth]):
                    preferredTerrain = ((terrain(newTerrain[i - layerWidth]) << 16) | (preferredTerrain & 0x0000FFFF))&0xFFFFFFFF
                    mask |= 0xFFFF0000

                if (y < layerHeight - 1 and checked[i + layerWidth]):
                    preferredTerrain = ((terrain(newTerrain[i + layerWidth]) >> 16) | (preferredTerrain & 0xFFFF0000))&0xFFFFFFFF
                    mask |= 0x0000FFFF

                if (x > 0 and checked[i - 1]):
                    preferredTerrain = (((terrain(newTerrain[i - 1]) << 8) & 0xFF00FF00) | (preferredTerrain & 0x00FF00FF))&0xFFFFFFFF
                    mask |= 0xFF00FF00

                if (x < layerWidth - 1 and checked[i + 1]):
                    preferredTerrain = (((terrain(newTerrain[i + 1]) >> 8) & 0x00FF00FF) | (preferredTerrain & 0xFF00FF00))&0xFFFFFFFF
                    mask |= 0x00FF00FF

            # find the most appropriate tile in the tileset
            paste = None
            if (preferredTerrain != 0xFFFFFFFF):
                paste = findBestTile(tileset, preferredTerrain, mask)
                if (not paste):
                    continue

            # add tile to the brush
            newTerrain[i] = paste
            checked[i] = True
            # expand the brush rect to fit the edit set
            brushRect |= QRect(p, p)
            # consider surrounding tiles if terrain constraints were not satisfied
            if (y > 0 and not checked[i - layerWidth]):
                above = currentLayer.cellAt(x, y - 1).tile
                if (topEdge(paste) != bottomEdge(above)):
                    transitionList.append(QPoint(x, y - 1))

            if (y < layerHeight - 1 and not checked[i + layerWidth]):
                below = currentLayer.cellAt(x, y + 1).tile
                if (bottomEdge(paste) != topEdge(below)):
                    transitionList.append(QPoint(x, y + 1))

            if (x > 0 and not checked[i - 1]):
                left = currentLayer.cellAt(x - 1, y).tile
                if (leftEdge(paste) != rightEdge(left)):
                    transitionList.append(QPoint(x - 1, y))

            if (x < layerWidth - 1 and not checked[i + 1]):
                right = currentLayer.cellAt(x + 1, y).tile
                if (rightEdge(paste) != leftEdge(right)):
                    transitionList.append(QPoint(x + 1, y))

        # create a stamp for the terrain block
        stamp = TileLayer(QString(), brushRect.left(), brushRect.top(), brushRect.width(), brushRect.height())
        for y in range(brushRect.top(), brushRect.bottom()+1):
            for x in range(brushRect.left(), brushRect.right()+1):
                i = y*layerWidth + x
                if (not checked[i]):
                    continue
                tile = newTerrain[i]
                if (tile):
                    stamp.setCell(x - brushRect.left(), y - brushRect.top(), Cell(tile))
                else:
                    # TODO: we need to do something to erase tiles where checked[i] is True, and newTerrain[i] is NULL
                    # is there an eraser stamp? investigate how the eraser works...
                    pass

        # set the new tile layer as the brush
        self.brushItem().setTileLayer(stamp)
        del checked
        del newTerrain
        self.mPaintX = cursorPos.x()
        self.mPaintY = cursorPos.y()
        self.mOffsetX = cursorPos.x() - brushRect.left()
        self.mOffsetY = cursorPos.y() - brushRect.top()
