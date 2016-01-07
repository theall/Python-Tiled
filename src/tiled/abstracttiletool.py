# -*- coding: utf-8 -*-
##
# abstracttiletool.py
# Copyright 2009-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
from tilelayer import TileLayer
from abstracttool import AbstractTool
from brushitem import BrushItem
from PyQt5.QtCore import QPoint

###
## Determines what the tile position means.
###
class TilePositionMethod():
    OnTiles = 1       #< Tile position is the tile the mouse is on.
    BetweenTiles = 2  #< Tile position is between the tiles.

###
# A convenient base class for tile based tools.
##
class AbstractTileTool(AbstractTool):
    ###
    # Constructs an abstract tile tool with the given \a name and \a icon.
    ##
    def __init__(self, name, icon, shortcut, parent = None):
        super(AbstractTileTool, self).__init__(name, icon, shortcut, parent)

        self.mTilePositionMethod = TilePositionMethod.OnTiles
        self.mBrushItem = BrushItem()
        self.mBrushVisible = False
        self.mTilePosition = QPoint()
        self.mBrushItem.setVisible(False)
        self.mBrushItem.setZValue(10000)

    def __del__(self):
        self.mBrushItem

    def activate(self, scene):
        scene.addItem(self.mBrushItem)

    def deactivate(self, scene):
        scene.removeItem(self.mBrushItem)

    def mouseEntered(self):
        self.setBrushVisible(True)

    def mouseLeft(self):
        self.setBrushVisible(False)

    def mouseMoved(self, pos, modifiers):
        # Take into account the offset of the current layer
        offsetPos = pos
        layer = self.currentTileLayer()
        if layer:
            offsetPos -= layer.offset()
            self.mBrushItem.setLayerOffset(layer.offset())

        renderer = self.mapDocument().renderer()
        tilePosF = renderer.screenToTileCoords_(offsetPos)
        if (self.mTilePositionMethod == TilePositionMethod.BetweenTiles):
            tilePos = tilePosF.toPoint()
        else:
            tilePos = QPoint(math.floor(tilePosF.x()), math.floor(tilePosF.y()))
        if self.mTilePosition != tilePos:
            self.mTilePosition = tilePos
            
            self.tilePositionChanged(tilePos)
            self.updateStatusInfo()
        
    def mapDocumentChanged(self, oldDocument, newDocument):
        self.mBrushItem.setMapDocument(newDocument)

    ###
    # Overridden to only enable this tool when the currently selected layer is
    # a tile layer.
    ##
    def updateEnabledState(self):
        self.setEnabled(bool(self.currentTileLayer()))

    ###
    # New virtual method to implement for tile tools. This method is called
    # on mouse move events, but only when the tile position changes.
    ##
    def tilePositionChanged(self, tilePos):
        pass

    ###
    ## Updates the status info with the current tile position. When the mouse
    ## is not in the view, the status info is set to an empty string.
    ##
    ## This behaviour can be overridden in a subclass. This method is
    ## automatically called after each call to tilePositionChanged() and when
    ## the brush visibility changes.
    ###
    def updateStatusInfo(self):
        if self.mBrushVisible:
            tile = None
            tileLayer = self.currentTileLayer()
            if type(tileLayer)==TileLayer:
                pos = self.tilePosition() - tileLayer.position()
                if tileLayer.contains(pos):
                    tile = tileLayer.cellAt(pos).tile

            if tile:
                tileIdString = str(tile.id())
            else:
                tileIdString = self.tr("empty")
            self.setStatusInfo("%d, %d [%s]"%(self.mTilePosition.x(), self.mTilePosition.y(), tileIdString))
        else:
            self.setStatusInfo('')

    def isBrushVisible(self):
        return self.mBrushVisible

    def setTilePositionMethod(self, method):
        self.mTilePositionMethod = method

    ###
    # Returns the last recorded tile position of the mouse.
    ##
    def tilePosition(self):
        return self.mTilePosition

    ###
    # Returns the brush item. The brush item is used to give an indication of
    # what a tile tool is going to do when used. It is automatically shown or
    # hidden based on whether the mouse is in the scene and whether the
    # currently selected layer is a tile layer.
    ##
    def brushItem(self):
        return self.mBrushItem

    ###
    # Returns the current tile layer, or 0 if no tile layer is currently
    # selected.
    ##
    def currentTileLayer(self):
        if (not self.mapDocument()):
            return None
        currentLayer = self.mapDocument().currentLayer()
        if type(currentLayer)==TileLayer:
            return currentLayer
        return None

    def setBrushVisible(self, visible):
        if (self.mBrushVisible == visible):
            return
        self.mBrushVisible = visible
        self.updateStatusInfo()
        self.updateBrushVisibility()

    def updateBrushVisibility(self):
        # Show the tile brush only when a visible tile layer is selected
        showBrush = False
        if self.mBrushVisible:
            layer = self.currentTileLayer()
            if layer:
                if (layer.isVisible()):
                    showBrush = True
        self.mBrushItem.setVisible(showBrush)

