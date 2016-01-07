##
# newtilesetdialog.py
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

from utils import Utils
from tileset import Tileset
import preferences
from Ui_newtilesetdialog import Ui_NewTilesetDialog
from PyQt5.QtCore import (
    Qt,
    QFileInfo
)
from PyQt5.QtGui import (
    QColor
)
from PyQt5.QtWidgets import (
    QDialogButtonBox,
    QMessageBox,
    QFileDialog,
    QDialog
)
TYPE_KEY = "Tileset/Type"
COLOR_ENABLED_KEY = "Tileset/UseTransparentColor"
COLOR_KEY = "Tileset/TransparentColor"
SPACING_KEY = "Tileset/Spacing"
MARGIN_KEY = "Tileset/Margin"

class TilesetType():
    TilesetImage = 1
    ImageCollection = 2

def tilesetType(ui):
    x = ui.tilesetType.currentIndex()
    if x==1:
        return TilesetType.ImageCollection
    else:
        return TilesetType.TilesetImage

##
# A dialog for the creation of a new tileset.
##
class NewTilesetDialog(QDialog):
    ##
    # Constructs a new tileset dialog
    #
    # @param path the path to start in by default, or an image file
    ##
    def __init__(self, path, parent = None):
        super().__init__(parent)
        
        self.mPath = path
        self.mUi = Ui_NewTilesetDialog()
        self.mNameWasEdited = False

        self.mUi.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        # Restore previously used settings
        s = preferences.Preferences.instance().settings()
        tilesetType = s.value(TYPE_KEY, 0)
        colorEnabled = bool(s.value(COLOR_ENABLED_KEY))
        colorName = s.value(COLOR_KEY, '')
        if colorName == '':
            color = Qt.magenta
        else:
            color = QColor(colorName)
        spacing = s.value(SPACING_KEY, 0)
        margin = s.value(MARGIN_KEY, 0)
        self.mUi.tilesetType.setCurrentIndex(tilesetType)
        self.mUi.useTransparentColor.setChecked(colorEnabled)
        self.mUi.colorButton.setColor(color)
        self.mUi.spacing.setValue(spacing)
        self.mUi.margin.setValue(margin)
        self.mUi.browseButton.clicked.connect(self.browse)
        self.mUi.name.textEdited.connect(self.nameEdited)
        self.mUi.name.textChanged.connect(self.updateOkButton)
        self.mUi.image.textChanged.connect(self.updateOkButton)
        self.mUi.tilesetType.currentIndexChanged.connect(self.tilesetTypeChanged)
        # Set the image and name fields if the given path is a file
        fileInfo = QFileInfo(path)
        if (fileInfo.isFile()):
            self.mUi.image.setText(path)
            self.mUi.name.setText(fileInfo.completeBaseName())

        self.mUi.imageGroupBox.setVisible(tilesetType == 0)
        self.updateOkButton()

    def __del__(self):
        del self.mUi

    def setTileWidth(self, width):
        self.mUi.tileWidth.setValue(width)

    def setTileHeight(self, height):
        self.mUi.tileHeight.setValue(height)

    ##
    # Shows the dialog and returns the created tileset. Returns 0 if the
    # dialog was cancelled.
    ##
    def createTileset(self):
        if (self.exec() != QDialog.Accepted):
            return None
        return self.mNewTileset

    def browse(self):
        filter = Utils.readableImageFormatsFilter()
        f, _ = QFileDialog.getOpenFileName(self, self.tr("Tileset Image"), self.mPath, filter)
        if f != '':
            self.mUi.image.setText(f)
            self.mPath = f
            if (not self.mNameWasEdited):
                self.mUi.name.setText(QFileInfo(f).completeBaseName())

    def nameEdited(self, name):
        self.mNameWasEdited = name!=''

    def tilesetTypeChanged(self, index):
        self.mUi.imageGroupBox.setVisible(index == 0)
        self.updateOkButton()

    def updateOkButton(self):
        okButton = self.mUi.buttonBox.button(QDialogButtonBox.Ok)
        enabled = self.mUi.name.text()!=''
        if (tilesetType(self.mUi) == TilesetType.TilesetImage):
            enabled &= self.mUi.image.text()!=''
        okButton.setEnabled(enabled)

    def tryAccept(self):
        # Used for storing the settings for next time
        s = preferences.Preferences.instance().settings()
        name = self.mUi.name.text()
        if (tilesetType(self.mUi) == TilesetType.TilesetImage):
            image = self.mUi.image.text()
            useTransparentColor = self.mUi.useTransparentColor.isChecked()
            transparentColor = self.mUi.colorButton.color()
            tileWidth = self.mUi.tileWidth.value()
            tileHeight = self.mUi.tileHeight.value()
            spacing = self.mUi.spacing.value()
            margin = self.mUi.margin.value()
            tileset = Tileset.create(name, tileWidth, tileHeight, spacing, margin)
            if (useTransparentColor):
                tileset.setTransparentColor(transparentColor)
            if image != '':
                if (not tileset.loadFromImage(image)):
                    QMessageBox.critical(self, self.tr("Error"),
                                          self.tr("Failed to load tileset image '%s'."%image))
                    return

                if (tileset.tileCount() == 0):
                    QMessageBox.critical(self, self.tr("Error"),
                                          self.tr("No tiles found in the tileset image "
                                             "when using the given tile size, "
                                             "margin and spacing!"))
                    return

            s.setValue(COLOR_ENABLED_KEY, useTransparentColor)
            s.setValue(COLOR_KEY, transparentColor.name())
            s.setValue(SPACING_KEY, spacing)
            s.setValue(MARGIN_KEY, margin)
        else:
            tileset = Tileset.create(name, 1, 1)

        s.setValue(TYPE_KEY, self.mUi.tilesetType.currentIndex())
        self.mNewTileset = tileset
        self.accept()
