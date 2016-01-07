##
# bucketfilltool.py
# Copyright 2009-2010, Jeff Bland <jeff@teamphobic.com>
# Copyright 2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2011, Stefan Beller, stefanbeller@googlemail.com
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

from tilestamp import TileStamp
from pyqtcore import QString, QVector
from painttilelayer import PaintTileLayer
from tilepainter import TilePainter
from tilelayer import TileLayer
from abstracttiletool import AbstractTileTool
from randompicker import RandomPicker
from addremovetileset import AddTileset
from PyQt5.QtCore import (
    Qt, 
    QSize, 
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QApplication
)
from PyQt5.QtGui import (
    QRegion,
    QKeySequence,
    QIcon
)

def fillWithStamp(layer, stamp, mask):
    size = stamp.maxSize()

    # Fill the entire layer with random variations of the stamp
    for y in range(0, layer.height(), size.height()):
        for x in range(0, layer.width(), size.width()):
            variation = stamp.randomVariation()
            layer.setCells(x, y, variation.tileLayer())

    # Erase tiles outside of the masked region. This can easily be faster than
    # avoiding to place tiles outside of the region in the first place.
    layer.erase(QRegion(0, 0, layer.width(), layer.height()) - mask)

##
# Implements a tool that bucket fills (flood fills) a region with a repeatable
# stamp.
##
class BucketFillTool(AbstractTileTool):
    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('BucketFillTool', sourceText, disambiguation, n)

    def __init__(self, parent = None):
        super().__init__(self.tr("Bucket Fill Tool"),
                           QIcon(":images/22x22/stock-tool-bucket-fill.png"),
                           QKeySequence(self.tr("F")),
                           parent)
        self.mStamp = TileStamp()
        self.mFillOverlay = None
        self.mFillRegion = QRegion()
        self.mMissingTilesets = QVector()
        self.mIsActive = False
        self.mLastShiftStatus = False
        ##
        # Indicates if the tool is using the random mode.
        ##
        self.mIsRandom = False
        ##
        # Contains the value of mIsRandom at that time, when the latest call of
        # tilePositionChanged() took place.
        # This variable is needed to detect if the random mode was changed during
        # mFillOverlay being brushed at an area.
        ##
        self.mLastRandomStatus = False
        ##
        # Contains all used random cells to use in random mode.
        # The same cell can be in the list multiple times to make different
        # random weights possible.
        ##
        self.mRandomCellPicker = RandomPicker()

    def __del__(self):
        pass

    def activate(self, scene):
        super().activate(scene)
        self.mIsActive = True
        self.tilePositionChanged(self.tilePosition())

    def deactivate(self, scene):
        super().deactivate(scene)
        self.mFillRegion = QRegion()
        self.mIsActive = False

    def mousePressed(self, event):
        if (event.button() != Qt.LeftButton or self.mFillRegion.isEmpty()):
            return
        if (not self.brushItem().isVisible()):
            return
        
        preview = self.mFillOverlay
        if not preview:
            return

        paint = PaintTileLayer(self.mapDocument(),
                                       self.currentTileLayer(),
                                       preview.x(),
                                       preview.y(),
                                       preview)

        paint.setText(QCoreApplication.translate("Undo Commands", "Fill Area"))

        if not self.mMissingTilesets.isEmpty():
            for tileset in self.mMissingTilesets:
                AddTileset(self.mapDocument(), tileset, paint)

            self.mMissingTilesets.clear()
            
        fillRegion = QRegion(self.mFillRegion)
        self.mapDocument().undoStack().push(paint)
        self.mapDocument().emitRegionEdited(fillRegion, self.currentTileLayer())

    def mouseReleased(self, event):
        pass

    def modifiersChanged(self, modifiers):
        # Don't need to recalculate fill region if there was no fill region
        if (not self.mFillOverlay):
            return
        self.tilePositionChanged(self.tilePosition())

    def languageChanged(self):
        self.setName(self.tr("Bucket Fill Tool"))
        self.setShortcut(QKeySequence(self.tr("F")))

    ##
    # Sets the stamp that is drawn when filling. The BucketFillTool takes
    # ownership over the stamp layer.
    ##
    def setStamp(self, stamp):
        # Clear any overlay that we presently have with an old stamp
        self.clearOverlay()
        self.mStamp = stamp
        self.updateRandomListAndMissingTilesets()
        if (self.mIsActive and self.brushItem().isVisible()):
            self.tilePositionChanged(self.tilePosition())

    ##
    # This returns the actual tile layer which is used to define the current
    # state.
    ##
    def stamp(self):
        return TileStamp(self.mStamp)

    def setRandom(self, value):
        if (self.mIsRandom == value):
            return
        self.mIsRandom = value
        self.updateRandomListAndMissingTilesets()
        
        # Don't need to recalculate fill region if there was no fill region
        if (not self.mFillOverlay):
            return
        self.tilePositionChanged(self.tilePosition())

    def tilePositionChanged(self, tilePos):
        # Skip filling if the stamp is empty
        if  self.mStamp.isEmpty():
            return
            
        # Make sure that a tile layer is selected
        tileLayer = self.currentTileLayer()
        if (not tileLayer):
            return
        
        shiftPressed = QApplication.keyboardModifiers() & Qt.ShiftModifier
        fillRegionChanged = False
        
        regionComputer = TilePainter(self.mapDocument(), tileLayer)
        # If the stamp is a single tile, ignore it when making the region
        if (not shiftPressed and self.mStamp.variations().size() == 1):
            variation = self.mStamp.variations().first()
            stampLayer = variation.tileLayer()
            if (stampLayer.size() == QSize(1, 1) and stampLayer.cellAt(0, 0) == regionComputer.cellAt(tilePos)):
                return
            
        # This clears the connections so we don't get callbacks
        self.clearConnections(self.mapDocument())
        # Optimization: we don't need to recalculate the fill area
        # if the new mouse position is still over the filled region
        # and the shift modifier hasn't changed.
        if (not self.mFillRegion.contains(tilePos) or shiftPressed != self.mLastShiftStatus):
            # Clear overlay to make way for a new one
            self.clearOverlay()
            # Cache information about how the fill region was created
            self.mLastShiftStatus = shiftPressed
            # Get the new fill region
            if (not shiftPressed):
                # If not holding shift, a region is generated from the current pos
                self.mFillRegion = regionComputer.computePaintableFillRegion(tilePos)
            else:
                # If holding shift, the region is the selection bounds
                self.mFillRegion = self.mapDocument().selectedArea()
                # Fill region is the whole map if there is no selection
                if (self.mFillRegion.isEmpty()):
                    self.mFillRegion = tileLayer.bounds()
                # The mouse needs to be in the region
                if (not self.mFillRegion.contains(tilePos)):
                    self.mFillRegion = QRegion()

            fillRegionChanged = True

        # Ensure that a fill region was created before making an overlay layer
        if (self.mFillRegion.isEmpty()):
            return
        if (self.mLastRandomStatus != self.mIsRandom):
            self.mLastRandomStatus = self.mIsRandom
            fillRegionChanged = True

        if (not self.mFillOverlay):
            # Create a new overlay region
            fillBounds = self.mFillRegion.boundingRect()
            self.mFillOverlay = TileLayer(QString(),
                                         fillBounds.x(),
                                         fillBounds.y(),
                                         fillBounds.width(),
                                         fillBounds.height())

        # Paint the new overlay
        if (not self.mIsRandom):
            if (fillRegionChanged or self.mStamp.variations().size() > 1):
                fillWithStamp(self.mFillOverlay, self.mStamp, self.mFillRegion.translated(-self.mFillOverlay.position()))
                fillRegionChanged = True
        else:
            self.randomFill(self.mFillOverlay, self.mFillRegion)
            fillRegionChanged = True

        if (fillRegionChanged):
            # Update the brush item to draw the overlay
            self.brushItem().setTileLayer(self.mFillOverlay)

        # Create connections to know when the overlay should be cleared
        self.makeConnections()

    def mapDocumentChanged(self, oldDocument, newDocument):
        super().mapDocumentChanged(oldDocument, newDocument)
        self.clearConnections(oldDocument)
        # Reset things that are probably invalid now
        if newDocument:
            self.updateRandomListAndMissingTilesets()

        self.clearOverlay()

    def clearOverlay(self):
        # Clear connections before clearing overlay so there is no
        # risk of getting a callback and causing an infinite loop
        self.clearConnections(self.mapDocument())
        self.brushItem().clear()
        self.mFillOverlay = None

        self.mFillRegion = QRegion()

    def makeConnections(self):
        if (not self.mapDocument()):
            return
        # Overlay may need to be cleared if a region changed
        self.mapDocument().regionChanged.connect(self.clearOverlay)
        # Overlay needs to be cleared if we switch to another layer
        self.mapDocument().currentLayerIndexChanged.connect(self.clearOverlay)
        # Overlay needs be cleared if the selection changes, since
        # the overlay may be bound or may need to be bound to the selection
        self.mapDocument().selectedAreaChanged.connect(self.clearOverlay)

    def clearConnections(self, mapDocument):
        if (not mapDocument):
            return
        try:
            mapDocument.regionChanged.disconnect(self.clearOverlay)
            mapDocument.currentLayerIndexChanged.disconnect(self.clearOverlay)
            mapDocument.selectedAreaChanged.disconnect(self.clearOverlay)
        except:
            pass

    ##
    # Updates the list of random cells.
    # This is done by taking all non-null tiles from the original stamp mStamp.
    ##
    def updateRandomListAndMissingTilesets(self):
        self.mRandomCellPicker.clear()
        self.mMissingTilesets.clear()
        
        for variation in self.mStamp.variations():
            self.mapDocument().unifyTilesets(variation.map, self.mMissingTilesets)

            if self.mIsRandom:
                for cell in variation.tileLayer():
                    if not cell.isEmpty():
                        self.mRandomCellPicker.add(cell, cell.tile.probability())

    ##
    # Fills the given \a region in the given \a tileLayer with random tiles.
    ##
    def randomFill(self, tileLayer, region):
        if (region.isEmpty() or self.mRandomList.empty()):
            return
        for rect in region.translated(-tileLayer.position()).rects():
            for _x in range(rect.left(), rect.right()+1):
                for _y in range(rect.top(), rect.bottom()+1):
                    tileLayer.setCell(_x, _y, self.mRandomCellPicker.pick())
