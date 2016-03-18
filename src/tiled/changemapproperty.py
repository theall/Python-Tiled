##
# changemapProperty.py
# Copyright 2012, Emmanuel Barroga emmanuelbarroga@gmail.com
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

from map import Map
from PyQt5.QtCore import (
    QCoreApplication
)
from PyQt5.QtGui import (
    QColor
)
from PyQt5.QtWidgets import (
    QUndoCommand
)

class ChangeMapProperty(QUndoCommand):
    TileWidth = 1
    TileHeight = 2
    HexSideLength = 3
    StaggerAxis = 4
    StaggerIndex = 5
    Orientation = 6
    RenderOrder = 7
    BackgroundColor = 8
    LayerDataFormat = 9

    ##
    # Constructs a command that changes the value of the given ChangeMapProperty.
    #
    # Can only be used for the HexSideLength ChangeMapProperty.
    #
    # @param mapDocument       the map document of the map
    # @param backgroundColor   the new color to apply for the background
    ##
    def __init__(self, mapDocument, *args):
        super().__init__()

        self.mProperty = 0
        self.mStaggerIndex = 0
        self.mOrientation = 0
        self.mBackgroundColor = QColor()
        self.mIntValue = 0
        self.mRenderOrder = 0
        self.mMapDocument = mapDocument
        self.mStaggerAxis = 0
        self.mLayerDataFormat = None

        l = len(args)
        if l==2:
            property, value = args
            self.mProperty = property
            self.mIntValue = value

            x = property
            if x==ChangeMapProperty.TileWidth:
                self.setText(QCoreApplication.translate("Undo Commands", "Change Tile Width"))
            elif x==ChangeMapProperty.TileHeight:
                self.setText(QCoreApplication.translate("Undo Commands", "Change Tile Height"))
            elif x==ChangeMapProperty.HexSideLength:
                self.setText(QCoreApplication.translate("Undo Commands", "Change Hex Side Length"))
        elif l==1:
            arg1 = args[0]
            tp = type(arg1)          
            if tp==QColor:
                ##
                # Constructs a command that changes the map background color.
                #
                # @param mapDocument       the map document of the map
                # @param backgroundColor   the new color to apply for the background
                ##
                backgroundColor = arg1
                super().__init__(QCoreApplication.translate("Undo Commands", "Change Background Color"))
                self.mProperty = ChangeMapProperty.BackgroundColor
                self.mBackgroundColor = backgroundColor
            elif tp==Map.StaggerAxis:
                    ##
                    # Constructs a command that changes the map stagger axis.
                    #
                    # @param mapDocument       the map document of the map
                    # @param orientation       the new map stagger axis
                    ##
                    staggerAxis = arg1
                    super().__init__(QCoreApplication.translate("Undo Commands", "Change Stagger Axis"))
                    self.mProperty = ChangeMapProperty.StaggerAxis
                    self.mStaggerAxis = staggerAxis
            elif tp==Map.StaggerIndex:
                ##
                # Constructs a command that changes the map stagger index.
                #
                # @param mapDocument       the map document of the map
                # @param orientation       the new map stagger index
                ##
                staggerIndex = arg1
                super().__init__(QCoreApplication.translate("Undo Commands", "Change Stagger Index"))
                self.mProperty = ChangeMapProperty.StaggerIndex
                self.mStaggerIndex = staggerIndex
            elif tp==Map.Orientation:
                ##
                # Constructs a command that changes the map orientation.
                #
                # @param mapDocument       the map document of the map
                # @param orientation       the new map orientation
                ##
                orientation = arg1
                super().__init__(QCoreApplication.translate("Undo Commands", "Change Orientation"))
                self.mProperty = ChangeMapProperty.Orientation
                self.mOrientation = orientation
            elif tp==Map.RenderOrder:
                ##
                # Constructs a command that changes the render order.
                #
                # @param mapDocument       the map document of the map
                # @param renderOrder       the new map render order
                ##
                renderOrder = arg1
                super().__init__(QCoreApplication.translate("Undo Commands", "Change Render Order"))
                self.mProperty = ChangeMapProperty.RenderOrder
                self.mRenderOrder = renderOrder
            elif tp==Map.LayerDataFormat:
                ##
                # Constructs a command that changes the layer data format.
                #
                # @param mapDocument       the map document of the map
                # @param layerDataFormat   the new layer data format
                ##
                layerDataFormat = arg1
                super().__init__(QCoreApplication.translate("Undo Commands", "Change Layer Data Format"))
                self.mProperty = ChangeMapProperty.LayerDataFormat
                self.mLayerDataFormat = layerDataFormat

    def undo(self):
        self.swap()

    def redo(self):
        self.swap()

    def swap(self):
        map = self.mMapDocument.map()
        x = self.mProperty
        if x==ChangeMapProperty.TileWidth:
            tileWidth = map.tileWidth()
            map.setTileWidth(self.mIntValue)
            self.mIntValue = tileWidth
        elif x==ChangeMapProperty.TileHeight:
            tileHeight = map.tileHeight()
            map.setTileHeight(self.mIntValue)
            self.mIntValue = tileHeight
        elif x==ChangeMapProperty.Orientation:
            orientation = map.orientation()
            map.setOrientation(self.mOrientation)
            self.mOrientation = orientation
            self.mMapDocument.createRenderer()
        elif x==ChangeMapProperty.HexSideLength:
            hexSideLength = map.hexSideLength()
            map.setHexSideLength(self.mIntValue)
            self.mIntValue = hexSideLength
        elif x==ChangeMapProperty.StaggerAxis:
            staggerAxis = map.staggerAxis()
            map.setStaggerAxis(self.mStaggerAxis)
            self.mStaggerAxis = staggerAxis
        elif x==ChangeMapProperty.StaggerIndex:
            staggerIndex = map.staggerIndex()
            map.setStaggerIndex(self.mStaggerIndex)
            self.mStaggerIndex = staggerIndex
        elif x==ChangeMapProperty.RenderOrder:
            renderOrder = map.renderOrder()
            map.setRenderOrder(self.mRenderOrder)
            self.mRenderOrder = renderOrder
        elif x==ChangeMapProperty.BackgroundColor:
            backgroundColor = map.backgroundColor()
            map.setBackgroundColor(self.mBackgroundColor)
            self.mBackgroundColor = backgroundColor
        elif x==ChangeMapProperty.LayerDataFormat:
            layerDataFormat = map.layerDataFormat()
            map.setLayerDataFormat(self.mLayerDataFormat)
            self.mLayerDataFormat = layerDataFormat

        self.mMapDocument.emitMapChanged()
