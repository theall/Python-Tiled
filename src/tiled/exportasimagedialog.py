##
# exportasimagedialog.py
# Copyright 2009-2015, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

import os
from tilelayer import TileLayer
from imagelayer import ImageLayer
from utils import Utils
import preferences
from objectgroup import ObjectGroup
from maprenderer import RenderFlag
from mapobjectitem import MapObjectItem
from Ui_exportasimagedialog import Ui_ExportAsImageDialog
from PyQt5.QtCore import (
    Qt,
    QFile,
    QRectF,
    QSizeF, 
    QPointF,
    QFileInfo
)
from PyQt5.QtGui import (
    QImage,
    QPainter,
    QTransform
)
from PyQt5.QtWidgets import (
    QMessageBox,
    QFileDialog,
    QDialog, 
    QDialogButtonBox
)
from pyqtcore import QString, QList
VISIBLE_ONLY_KEY = "SaveAsImage/VisibleLayersOnly"
CURRENT_SCALE_KEY = "SaveAsImage/CurrentScale"
DRAW_GRID_KEY = "SaveAsImage/DrawGrid"
INCLUDE_BACKGROUND_COLOR = "SaveAsImage/IncludeBackgroundColor"
def objectLessThan(a, b):
    return a.y() < b.y()

def smoothTransform(scale):
    return scale != 1.0 and scale < 2.0
    
def adjustDir(s):
    if os.path.ismount(s):
        # remove '/' end of root dir
        return s.rstrip()[:-1]
    return s    
##
# The dialog for exporting a map as an image.
##
class ExportAsImageDialog(QDialog):
    mPath = QString()
    ##
    # Creates an Export As Image dialog. The suggested name for the image will
    # be based on the given \a fileName. Use \a currentScale to specify the
    # current zoom level of the map view.
    ##
    def __init__(self, mapDocument, fileName, currentScale, parent = None):
        super().__init__(parent)
        self.mUi = None
        self.mCurrentScale = currentScale
        self.mMapDocument = mapDocument
        self.mUi = Ui_ExportAsImageDialog()
        self.mUi.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        saveButton = self.mUi.buttonBox.button(QDialogButtonBox.Save)
        saveButton.setText(self.tr("Export"))

        # Default to the last chosen location
        suggestion = adjustDir(self.mPath)
            
        # Suggest a nice name for the image
        if fileName != '':
            fileInfo = QFileInfo(fileName)
            path = fileInfo.path()
            baseName = fileInfo.completeBaseName()

            if suggestion=='':
                suggestion = adjustDir(path)
                
            suggestion += '/'
            suggestion += baseName
            suggestion += ".png"
        else:
            suggestion += '/'
            suggestion += "map.png"

        self.mUi.fileNameEdit.setText(suggestion)

        # Restore previously used settings
        s = preferences.Preferences.instance()
        visibleLayersOnly = s.boolValue(VISIBLE_ONLY_KEY, True)
        useCurrentScale = s.boolValue(CURRENT_SCALE_KEY, True)
        drawTileGrid = s.boolValue(DRAW_GRID_KEY, False)
        includeBackgroundColor = s.boolValue(INCLUDE_BACKGROUND_COLOR, False)

        self.mUi.visibleLayersOnly.setChecked(visibleLayersOnly)
        self.mUi.currentZoomLevel.setChecked(useCurrentScale)
        self.mUi.drawTileGrid.setChecked(drawTileGrid)
        self.mUi.includeBackgroundColor.setChecked(includeBackgroundColor)

        self.mUi.browseButton.clicked.connect(self.browse)
        self.mUi.fileNameEdit.textChanged.connect(self.updateAcceptEnabled)

        Utils.restoreGeometry(self)

    def __del__(self):
        Utils.saveGeometry(self)
        del self.mUi

    def accept(self):
        fileName = self.mUi.fileNameEdit.text()
        if fileName == '':
            return
        if (QFile.exists(fileName)):
            button = QMessageBox.warning(self,
                                         self.tr("Export as Image"),
                                         self.tr("%s already exists.\nDo you want to replace it?"%QFileInfo(fileName).fileName()),
                                         QMessageBox.Yes | QMessageBox.No,
                                         QMessageBox.No)
            if (button != QMessageBox.Yes):
                return

        visibleLayersOnly = self.mUi.visibleLayersOnly.isChecked()
        useCurrentScale = self.mUi.currentZoomLevel.isChecked()
        drawTileGrid = self.mUi.drawTileGrid.isChecked()
        includeBackgroundColor = self.mUi.includeBackgroundColor.isChecked()
        renderer = self.mMapDocument.renderer()
        # Remember the current render flags
        renderFlags = renderer.flags()
        renderer.setFlag(RenderFlag.ShowTileObjectOutlines, False)
        mapSize = renderer.mapSize()
        
        margins = self.mMapDocument.map().computeLayerOffsetMargins()
        mapSize.setWidth(mapSize.width() + margins.left() + margins.right())
        mapSize.setHeight(mapSize.height() + margins.top() + margins.bottom())
        
        if (useCurrentScale):
            mapSize *= self.mCurrentScale
        image = QImage()
        try:
            image = QImage(mapSize, QImage.Format_ARGB32_Premultiplied)
            if (includeBackgroundColor):
                if (self.mMapDocument.map().backgroundColor().isValid()):
                    image.fill(self.mMapDocument.map().backgroundColor())
                else:
                    image.fill(Qt.gray)
            else:
                image.fill(Qt.transparent)

        except:
            QMessageBox.critical(self,
                                  self.tr("Out of Memory"),
                                  self.tr("Could not allocate sufficient memory for the image. "
                                     "Try reducing the zoom level or using a 64-bit version of Tiled."))
            return

        if (image.isNull()):
            gigabyte = 1073741824
            memory = mapSize.width() * mapSize.height() * 4
            gigabytes = memory / gigabyte
            QMessageBox.critical(self,
                                  self.tr("Image too Big"),
                                  self.tr("The resulting image would be %d x %d pixels and take %.2f GB of memory. "
                                     "Tiled is unable to create such an image. Try reducing the zoom level."%(mapSize.width(), mapSize.height(), gigabytes)))
            return

        painter = QPainter(image)
        if (useCurrentScale):
            if (smoothTransform(self.mCurrentScale)):
                painter.setRenderHints(QPainter.SmoothPixmapTransform)

            painter.setTransform(QTransform.fromScale(self.mCurrentScale,
                                                       self.mCurrentScale))
            renderer.setPainterScale(self.mCurrentScale)
        else:
            renderer.setPainterScale(1)

        painter.translate(margins.left(), margins.top())
        
        for layer in self.mMapDocument.map().layers():
            if (visibleLayersOnly and not layer.isVisible()):
                continue
            painter.setOpacity(layer.opacity())
            painter.translate(layer.offset())
            
            tileLayer = layer
            objGroup = layer
            imageLayer = layer
            tp = type(layer)
            if tp == TileLayer:
                renderer.drawTileLayer(painter, tileLayer)
            elif tp == ObjectGroup:
                objects = objGroup.objects()
                if (objGroup.drawOrder() == ObjectGroup.DrawOrder.TopDownOrder):
                    objects = QList(sorted(objects, key=lambda x:x.y(), reverse=True))
                for object in objects:
                    if (object.isVisible()):
                        if (object.rotation() != 0.0):
                            origin = renderer.pixelToScreenCoords_(object.position())
                            painter.save()
                            painter.translate(origin)
                            painter.rotate(object.rotation())
                            painter.translate(-origin)

                        color = MapObjectItem.objectColor(object)
                        renderer.drawMapObject(painter, object, color)
                        if (object.rotation() != 0.0):
                            painter.restore()
            elif tp == ImageLayer:
                renderer.drawImageLayer(painter, imageLayer)

        painter.translate(-layer.offset())
        
        if (drawTileGrid):
            prefs = preferences.Preferences.instance()
            renderer.drawGrid(painter, QRectF(QPointF(), QSizeF(renderer.mapSize())), prefs.gridColor())

        painter.end()
        
        # Restore the previous render flags
        renderer.setFlags(renderFlags)
        image.save(fileName)
        self.mPath = QFileInfo(fileName).path()
        # Store settings for next time
        s = preferences.Preferences.instance().settings()
        s.setValue(VISIBLE_ONLY_KEY, visibleLayersOnly)
        s.setValue(CURRENT_SCALE_KEY, useCurrentScale)
        s.setValue(DRAW_GRID_KEY, drawTileGrid)
        s.setValue(INCLUDE_BACKGROUND_COLOR, includeBackgroundColor)
        super().accept()

    def browse(self):
        # Don't confirm overwrite here, since we'll confirm when the user presses
        # the Export button
        filter = Utils.writableImageFormatsFilter()
        f, _ = QFileDialog.getSaveFileName(self, self.tr("Image"),
                                                 self.mUi.fileNameEdit.text(),
                                                 filter, None,
                                                 QFileDialog.DontConfirmOverwrite)
        if f != '':
            self.mUi.fileNameEdit.setText(f)
            self.mPath = f

    def updateAcceptEnabled(self):
        saveButton = self.mUi.buttonBox.button(QDialogButtonBox.Save)
        saveButton.setEnabled(self.mUi.fileNameEdit.text()!='')
