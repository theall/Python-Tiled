##
# preferencesdialog.py
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
from objecttypes import ObjectTypesReader, ObjectTypesWriter
import preferences
from objecttypesmodel import ObjectTypesModel
from languagemanager import LanguageManager
from Ui_preferencesdialog import Ui_PreferencesDialog
from PyQt5.QtCore import (
    Qt,
    QSize,
    QPoint,
    QLocale, 
    QEvent,
    QItemSelectionModel
)
from PyQt5.QtGui import (
    QPen,
    QColor,
    QBrush
)
from PyQt5.QtWidgets import (
    QHeaderView,
    QStyledItemDelegate,
    QMessageBox,
    QFileDialog,
    QColorDialog,
    QDialog
)
##
# The preferences dialog. Allows the user to configure some general behaviour
# settings of Tiled and choose the language.
##
class PreferencesDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.mUi = Ui_PreferencesDialog()
        self.mLanguages = LanguageManager.instance().availableLanguages()

        self.mUi.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.mUi.openGL.setEnabled(False)
        for name in self.mLanguages:
            locale = QLocale(name)
            string = "%s (%s)"%(QLocale.languageToString(locale.language()), QLocale.countryToString(locale.country()))
            self.mUi.languageCombo.addItem(string, name)

        self.mUi.languageCombo.model().sort(0)
        self.mUi.languageCombo.insertItem(0, self.tr("System default"))
        self.mObjectTypesModel = ObjectTypesModel(self)
        self.mUi.objectTypesTable.setModel(self.mObjectTypesModel)
        self.mUi.objectTypesTable.setItemDelegateForColumn(1, ColorDelegate(self))
        horizontalHeader = self.mUi.objectTypesTable.horizontalHeader()
        horizontalHeader.setSectionResizeMode(QHeaderView.Stretch)
        Utils.setThemeIcon(self.mUi.addObjectTypeButton, "add")
        Utils.setThemeIcon(self.mUi.removeObjectTypeButton, "remove")
        self.fromPreferences()
        self.mUi.languageCombo.currentIndexChanged.connect(self.languageSelected)
        self.mUi.openGL.toggled.connect(self.useOpenGLToggled)
        self.mUi.gridColor.colorChanged.connect(preferences.Preferences.instance().setGridColor)
        self.mUi.gridFine.valueChanged.connect(preferences.Preferences.instance().setGridFine)
        self.mUi.objectLineWidth.valueChanged.connect(self.objectLineWidthChanged)
        self.mUi.objectTypesTable.selectionModel().selectionChanged.connect(self.selectedObjectTypesChanged)
        self.mUi.objectTypesTable.doubleClicked.connect(self.objectTypeIndexClicked)
        self.mUi.addObjectTypeButton.clicked.connect(self.addObjectType)
        self.mUi.removeObjectTypeButton.clicked.connect(self.removeSelectedObjectTypes)
        self.mUi.importObjectTypesButton.clicked.connect(self.importObjectTypes)
        self.mUi.exportObjectTypesButton.clicked.connect(self.exportObjectTypes)
        self.mObjectTypesModel.dataChanged.connect(self.applyObjectTypes)
        self.mObjectTypesModel.rowsRemoved.connect(self.applyObjectTypes)
        self.mUi.autoMapWhileDrawing.toggled.connect(self.useAutomappingDrawingToggled)
        self.mUi.openLastFiles.toggled.connect(self.openLastFilesToggled)

    def __del__(self):
        self.toPreferences()
        del self.mUi

    def changeEvent(self, e):
        super().changeEvent(e)
        x = e.type()
        if x==QEvent.LanguageChange:
            self.mUi.retranslateUi(self)
            self.mUi.languageCombo.setItemText(0, self.tr("System default"))
        else:
            pass

    def languageSelected(self, index):
        language = self.mUi.languageCombo.itemData(index)
        prefs = preferences.Preferences.instance()
        prefs.setLanguage(language)

    def objectLineWidthChanged(self, lineWidth):
        preferences.Preferences.instance().setObjectLineWidth(lineWidth)

    def useOpenGLToggled(self, useOpenGL):
        preferences.Preferences.instance().setUseOpenGL(useOpenGL)

    def useAutomappingDrawingToggled(self, enabled):
        preferences.Preferences.instance().setAutomappingDrawing(enabled)

    def openLastFilesToggled(self, enabled):
        preferences.Preferences.instance().setOpenLastFilesOnStartup(enabled)
        
    def addObjectType(self):
        newRow = self.mObjectTypesModel.objectTypes().size()
        self.mObjectTypesModel.appendNewObjectType()
        # Select and focus the new row and ensure it is visible
        sm = self.mUi.objectTypesTable.selectionModel()
        newIndex = self.mObjectTypesModel.index(newRow, 0)
        sm.select(newIndex, QItemSelectionModel.ClearAndSelect | QItemSelectionModel.Rows)
        sm.setCurrentIndex(newIndex, QItemSelectionModel.Current)
        self.mUi.objectTypesTable.setFocus()
        self.mUi.objectTypesTable.scrollTo(newIndex)

    def selectedObjectTypesChanged(self):
        sm = self.mUi.objectTypesTable.selectionModel()
        self.mUi.removeObjectTypeButton.setEnabled(sm.hasSelection())

    def removeSelectedObjectTypes(self):
        sm = self.mUi.objectTypesTable.selectionModel()
        self.mObjectTypesModel.removeObjectTypes(sm.selectedRows())

    def objectTypeIndexClicked(self, index):
        if (index.column() == 1):
            color = self.mObjectTypesModel.objectTypes().at(index.row()).color
            newColor = QColorDialog.getColor(color, self)
            if (newColor.isValid()):
                self.mObjectTypesModel.setObjectTypeColor(index.row(), newColor)

    def applyObjectTypes(self):
        prefs = preferences.Preferences.instance()
        prefs.setObjectTypes(self.mObjectTypesModel.objectTypes())

    def importObjectTypes(self):
        prefs = preferences.Preferences.instance()
        lastPath = prefs.lastPath(preferences.Preferences.ObjectTypesFile)
        fileName, _ = QFileDialog.getOpenFileName(self, self.tr("Import Object Types"),
                                             lastPath,
                                             self.tr("Object Types files (*.xml)"))
        if fileName == '':
            return
        prefs.setLastPath(preferences.Preferences.ObjectTypesFile, fileName)
        reader = ObjectTypesReader()
        objectTypes = reader.readObjectTypes(fileName)
        if (reader.errorString().isEmpty()):
            prefs.setObjectTypes(objectTypes)
            self.mObjectTypesModel.setObjectTypes(objectTypes)
        else:
            QMessageBox.critical(self, self.tr("Error Reading Object Types"), reader.errorString())

    def exportObjectTypes(self):
        prefs = preferences.Preferences.instance()
        lastPath = prefs.lastPath(preferences.Preferences.ObjectTypesFile)
        if (not lastPath.endsWith(".xml")):
            lastPath.append("/objecttypes.xml")
        fileName, _ = QFileDialog.getSaveFileName(self, self.tr("Export Object Types"),
                                             lastPath,
                                             self.tr("Object Types files (*.xml)"))
        if fileName == '':
            return
        prefs.setLastPath(preferences.Preferences.ObjectTypesFile, fileName)
        writer = ObjectTypesWriter()
        if (not writer.writeObjectTypes(fileName, prefs.objectTypes())):
            QMessageBox.critical(self, self.tr("Error Writing Object Types"), writer.errorString())

    def fromPreferences(self):
        prefs = preferences.Preferences.instance()
        self.mUi.reloadTilesetImages.setChecked(prefs.reloadTilesetsOnChange())
        self.mUi.enableDtd.setChecked(prefs.dtdEnabled())
        self.mUi.openLastFiles.setChecked(prefs.openLastFilesOnStartup())
        if (self.mUi.openGL.isEnabled()):
            self.mUi.openGL.setChecked(prefs.useOpenGL())
        # Not found (-1) ends up at index 0, system default
        languageIndex = self.mUi.languageCombo.findData(prefs.language())
        if (languageIndex == -1):
            languageIndex = 0
        self.mUi.languageCombo.setCurrentIndex(languageIndex)
        self.mUi.gridColor.setColor(prefs.gridColor())
        self.mUi.gridFine.setValue(prefs.gridFine())
        self.mUi.objectLineWidth.setValue(prefs.objectLineWidth())
        self.mUi.autoMapWhileDrawing.setChecked(prefs.automappingDrawing())
        self.mObjectTypesModel.setObjectTypes(prefs.objectTypes())

    def toPreferences(self):
        prefs = preferences.Preferences.instance()
        prefs.setReloadTilesetsOnChanged(self.mUi.reloadTilesetImages.isChecked())
        prefs.setDtdEnabled(self.mUi.enableDtd.isChecked())
        prefs.setAutomappingDrawing(self.mUi.autoMapWhileDrawing.isChecked())
        prefs.setOpenLastFilesOnStartup(self.mUi.openLastFiles.isChecked())

class ColorDelegate(QStyledItemDelegate):

    def __init__(self, parent = None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        super().paint(painter, option, index)

        displayData = index.model().data(index, ObjectTypesModel.ColorRole)
        color = displayData.value()
        rect = option.rect.adjusted(4, 4, -4, -4)
        linePen = QPen(QBrush(color), 2)
        shadowPen = QPen(QBrush(Qt.black), 2)
        brushColor = QColor(color)
        brushColor.setAlpha(50)
        fillBrush = QBrush(brushColor)
        # Draw the shadow
        painter.setPen(shadowPen)
        painter.setBrush(QBrush())
        painter.drawRect(rect.translated(QPoint(1, 1)))
        painter.setPen(linePen)
        painter.setBrush(fillBrush)
        painter.drawRect(rect)

    def sizeHint(self, arg1, arg2):
        return QSize(50, 20)

