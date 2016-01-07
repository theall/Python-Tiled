##
# newmapdialog.py
# Copyright 2009, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

ORIENTATION_KEY = "Map/Orientation"
MAP_WIDTH_KEY = "Map/Width"
MAP_HEIGHT_KEY = "Map/Height"
TILE_WIDTH_KEY = "Map/TileWidth"
TILE_HEIGHT_KEY = "Map/TileHeight"
from tilelayer import TileLayer
from mapdocument import MapDocument
from staggeredrenderer import StaggeredRenderer
import preferences
from orthogonalrenderer import OrthogonalRenderer
from map import Map
from hexagonalrenderer import HexagonalRenderer
from isometricrenderer import IsometricRenderer
from Ui_newmapdialog import Ui_NewMapDialog
from PyQt5.QtGui import (
    QFontInfo
)
from PyQt5.QtCore import (
    Qt,
    QSize,
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QMessageBox,
    QDialog
)
##
# A dialog for the creation of a new map.
##
class NewMapDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent),
        self.mUi = Ui_NewMapDialog()
        self.mUi.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        # Restore previously used settings
        prefs = preferences.Preferences.instance()
        s = prefs.settings()
        orientation = s.value(ORIENTATION_KEY, 0)
        mapWidth = s.value(MAP_WIDTH_KEY, 100)
        mapHeight = s.value(MAP_HEIGHT_KEY, 100)
        tileWidth = s.value(TILE_WIDTH_KEY, 32)
        tileHeight = s.value(TILE_HEIGHT_KEY, 32)
        self.mUi.layerFormat.addItem(QCoreApplication.translate("PreferencesDialog", "XML"))
        self.mUi.layerFormat.addItem(QCoreApplication.translate("PreferencesDialog", "Base64 (uncompressed)"))
        self.mUi.layerFormat.addItem(QCoreApplication.translate("PreferencesDialog", "Base64 (gzip compressed)"))
        self.mUi.layerFormat.addItem(QCoreApplication.translate("PreferencesDialog", "Base64 (zlib compressed)"))
        self.mUi.layerFormat.addItem(QCoreApplication.translate("PreferencesDialog", "CSV"))
        self.mUi.renderOrder.addItem(QCoreApplication.translate("PreferencesDialog", "Right Down"))
        self.mUi.renderOrder.addItem(QCoreApplication.translate("PreferencesDialog", "Right Up"))
        self.mUi.renderOrder.addItem(QCoreApplication.translate("PreferencesDialog", "Left Down"))
        self.mUi.renderOrder.addItem(QCoreApplication.translate("PreferencesDialog", "Left Up"))
        self.mUi.orientation.addItem(self.tr("Orthogonal"), Map.Orientation.Orthogonal)
        self.mUi.orientation.addItem(self.tr("Isometric"), Map.Orientation.Isometric)
        self.mUi.orientation.addItem(self.tr("Isometric (Staggered)"), Map.Orientation.Staggered)
        self.mUi.orientation.addItem(self.tr("Hexagonal (Staggered)"), Map.Orientation.Hexagonal)
        self.mUi.orientation.setCurrentIndex(orientation)
        self.mUi.layerFormat.setCurrentIndex(prefs.layerDataFormat().value)
        self.mUi.renderOrder.setCurrentIndex(prefs.mapRenderOrder().value)
        self.mUi.mapWidth.setValue(mapWidth)
        self.mUi.mapHeight.setValue(mapHeight)
        self.mUi.tileWidth.setValue(tileWidth)
        self.mUi.tileHeight.setValue(tileHeight)
        # Make the font of the pixel size label smaller
        font = self.mUi.pixelSizeLabel.font()
        size = QFontInfo(font).pointSizeF()
        font.setPointSizeF(size - 1)
        self.mUi.pixelSizeLabel.setFont(font)
        self.mUi.mapWidth.valueChanged.connect(self.refreshPixelSize)
        self.mUi.mapHeight.valueChanged.connect(self.refreshPixelSize)
        self.mUi.tileWidth.valueChanged.connect(self.refreshPixelSize)
        self.mUi.tileHeight.valueChanged.connect(self.refreshPixelSize)
        self.mUi.orientation.currentIndexChanged.connect(self.refreshPixelSize)
        self.refreshPixelSize()

    def __del__(self):
        del self.mUi

    ##
    # Shows the dialog and returns the created map. Returns 0 if the dialog
    # was cancelled.
    ##
    def createMap(self):
        if (self.exec() != QDialog.Accepted):
            return None
        mapWidth = self.mUi.mapWidth.value()
        mapHeight = self.mUi.mapHeight.value()
        tileWidth = self.mUi.tileWidth.value()
        tileHeight = self.mUi.tileHeight.value()
        orientationIndex = self.mUi.orientation.currentIndex()
        orientationData = self.mUi.orientation.itemData(orientationIndex)
        orientation = orientationData
        layerFormat = Map.LayerDataFormat(self.mUi.layerFormat.currentIndex())
        renderOrder = Map.RenderOrder(self.mUi.renderOrder.currentIndex())
        map = Map(orientation,
                           mapWidth, mapHeight,
                           tileWidth, tileHeight)
        map.setLayerDataFormat(layerFormat)
        map.setRenderOrder(renderOrder)
        gigabyte = 1073741824
        memory = mapWidth * mapHeight * 8#sizeof(Cell)
        # Add a tile layer to new maps of reasonable size
        if (memory < gigabyte):
            map.addLayer(TileLayer(self.tr("Tile Layer 1"), 0, 0,
                                        mapWidth, mapHeight))
        else:
            gigabytes = memory / gigabyte
            QMessageBox.warning(self, self.tr("Memory Usage Warning"),
                                 self.tr("Tile layers for this map will consume %.2f GB "
                                    "of memory each. Not creating one by default."%gigabytes))

        # Store settings for next time
        prefs = preferences.Preferences.instance()
        prefs.setLayerDataFormat(layerFormat)
        prefs.setMapRenderOrder(renderOrder)
        s = preferences.Preferences.instance().settings()
        s.setValue(ORIENTATION_KEY, orientationIndex)
        s.setValue(MAP_WIDTH_KEY, mapWidth)
        s.setValue(MAP_HEIGHT_KEY, mapHeight)
        s.setValue(TILE_WIDTH_KEY, tileWidth)
        s.setValue(TILE_HEIGHT_KEY, tileHeight)
        return MapDocument(map)

    def refreshPixelSize(self):
        orientationIndex = self.mUi.orientation.currentIndex()
        orientationData = self.mUi.orientation.itemData(orientationIndex)
        orientation = orientationData
        map = Map(orientation,
                      self.mUi.mapWidth.value(),
                      self.mUi.mapHeight.value(),
                      self.mUi.tileWidth.value(),
                      self.mUi.tileHeight.value())
        size = QSize()
        x = orientation
        if x==Map.Orientation.Isometric:
            size = IsometricRenderer(map).mapSize()
        elif x==Map.Orientation.Staggered:
            size = StaggeredRenderer(map).mapSize()
        elif x==Map.Orientation.Hexagonal:
            size = HexagonalRenderer(map).mapSize()
        else:
            size = OrthogonalRenderer(map).mapSize()

        self.mUi.pixelSizeLabel.setText(self.tr("%d x %d pixels"%(size.width(), size.height())))
