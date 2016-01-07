##
# converterwindow.py
# Copyright 2011, 2012, Stefan Beller, stefanbeller@googlemail.com
#
# This file is part of the AutomappingConverter, which converts old rulemaps
# of Tiled to work with the latest version of Tiled.
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

from Ui_converterwindow import ui_MainWindow
from convertercontrol import ConverterControl
from converterdatamodel import ConverterDataModel

from pyqtcore import QString
from PyQt5.QtWidgets import (
    QHeaderView,
    QFileDialog,
    QMainWindow
)
class ConverterWindow(QMainWindow):
    def __init__(self, parent = None):
        self.ui = ui_MainWindow()
        self.mControl = ConverterControl()
        self.mDataModel = ConverterDataModel(self.mControl, self)
        self.ui.setupself.ui(self)
        self.ui.saveButton.setText(self.tr("Save all as %s"%self.mControl.version2()))
        self.ui.addbutton.clicked.connect(self.addRule)
        self.ui.saveButton.clicked.connect(self.mDataModel.updateVersions)
        self.ui.treeView.setModel(self.mDataModel)
        header = self.ui.treeView.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)

    def __del__(self):
        pass

    def addRule(self):
        filter = self.tr("All Files (*)")
        filter += ";;"
        selectedFilter = self.tr("Tiled map files (*.tmx)")
        filter += selectedFilter
        fileNames, _ = QFileDialog.getOpenFileNames(self, self.tr("Open Map"),
                                                              QString(), filter,
                                                              selectedFilter)
        if len(fileNames)==0:
            return
        self.mDataModel.insertFileNames(fileNames)
        self.ui.saveButton.setEnabled(True)

    def getVersion(self, filename):
        pass
