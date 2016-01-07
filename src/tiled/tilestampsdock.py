##
# tilestampdock.py
# Copyright 2015, Thorbjørn Lindeijer <bjorn@lindeijer.nl>
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
from map import Map
from tilestamp import TileStamp
import preferences
from PyQt5.QtCore import (
    pyqtSignal,
    QEvent,
    QSize,
    Qt,
    QSortFilterProxyModel
)
from PyQt5.QtGui import (
    QIcon
)
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QTreeView,
    QWidget,
    QSizePolicy,
    QAction,
    QVBoxLayout,
    QHeaderView,
    QLineEdit,
    QDockWidget,
    QToolBar,
    QMenu
)
Preferences = preferences.Preferences

class TileStampsDock(QDockWidget):
    setStamp = pyqtSignal(TileStamp)
    
    def __init__(self, stampManager, parent = None):
        super().__init__(parent)
        
        self.mTileStampManager = stampManager
        self.mTileStampModel = stampManager.tileStampModel()
        self.mProxyModel = QSortFilterProxyModel(self.mTileStampModel)
        self.mFilterEdit = QLineEdit(self)
        self.mNewStamp = QAction(self)
        self.mAddVariation = QAction(self)
        self.mDuplicate = QAction(self)
        self.mDelete = QAction(self)
        self.mChooseFolder = QAction(self)

        self.setObjectName("TileStampsDock")
        self.mProxyModel.setSortLocaleAware(True)
        self.mProxyModel.setSortCaseSensitivity(Qt.CaseInsensitive)
        self.mProxyModel.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.mProxyModel.setSourceModel(self.mTileStampModel)
        self.mProxyModel.sort(0)
        self.mTileStampView = TileStampView(self)
        self.mTileStampView.setModel(self.mProxyModel)
        self.mTileStampView.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.mTileStampView.header().setStretchLastSection(False)
        self.mTileStampView.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.mTileStampView.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.mTileStampView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.mTileStampView.customContextMenuRequested.connect(self.showContextMenu)
        self.mNewStamp.setIcon(QIcon(":images/16x16/document-new.png"))
        self.mAddVariation.setIcon(QIcon(":/images/16x16/add.png"))
        self.mDuplicate.setIcon(QIcon(":/images/16x16/stock-duplicate-16.png"))
        self.mDelete.setIcon(QIcon(":images/16x16/edit-delete.png"))
        self.mChooseFolder.setIcon(QIcon(":images/16x16/document-open.png"))
        Utils.setThemeIcon(self.mNewStamp, "document-new")
        Utils.setThemeIcon(self.mAddVariation, "add")
        Utils.setThemeIcon(self.mDelete, "edit-delete")
        Utils.setThemeIcon(self.mChooseFolder, "document-open")

        self.mFilterEdit.setClearButtonEnabled(True)
        self.mFilterEdit.textChanged.connect(self.mProxyModel.setFilterFixedString)
        self.mTileStampModel.stampRenamed.connect(self.ensureStampVisible)
        self.mNewStamp.triggered.connect(self.newStamp)
        self.mAddVariation.triggered.connect(self.addVariation)
        self.mDuplicate.triggered.connect(self.duplicate)
        self.mDelete.triggered.connect(self.delete_)
        self.mChooseFolder.triggered.connect(self.chooseFolder)
        self.mDuplicate.setEnabled(False)
        self.mDelete.setEnabled(False)
        self.mAddVariation.setEnabled(False)
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        buttonContainer = QToolBar()
        buttonContainer.setFloatable(False)
        buttonContainer.setMovable(False)
        buttonContainer.setIconSize(QSize(16, 16))
        buttonContainer.addAction(self.mNewStamp)
        buttonContainer.addAction(self.mAddVariation)
        buttonContainer.addAction(self.mDuplicate)
        buttonContainer.addAction(self.mDelete)
        stretch = QWidget()
        stretch.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        buttonContainer.addWidget(stretch)
        buttonContainer.addAction(self.mChooseFolder)
        listAndToolBar = QVBoxLayout()
        listAndToolBar.setSpacing(0)
        listAndToolBar.addWidget(self.mFilterEdit)
        listAndToolBar.addWidget(self.mTileStampView)
        listAndToolBar.addWidget(buttonContainer)
        layout.addLayout(listAndToolBar)
        selectionModel = self.mTileStampView.selectionModel()
        selectionModel.currentRowChanged.connect(self.currentRowChanged)
        self.setWidget(widget)
        self.retranslateUi()
        
    def changeEvent(self, e):
        super().changeEvent(e)
        x = e.type()
        if x==QEvent.LanguageChange:
            self.retranslateUi()
        else:
            pass
            
    def keyPressEvent(self, event):
        x = event.key()
        if x==Qt.Key_Delete or x==Qt.Key_Backspace:
            self.delete_()
            return

        super().keyPressEvent(event)

    def currentRowChanged(self, index):
        sourceIndex = self.mProxyModel.mapToSource(index)
        isStamp = self.mTileStampModel.isStamp(sourceIndex)
        self.mDuplicate.setEnabled(isStamp)
        self.mDelete.setEnabled(sourceIndex.isValid())
        self.mAddVariation.setEnabled(isStamp)
        if (isStamp):
            self.setStamp.emit(self.mTileStampModel.stampAt(sourceIndex))
        else:
            variation = self.mTileStampModel.variationAt(sourceIndex)
            if variation:
                # single variation clicked, use it specifically
                self.setStamp.emit(TileStamp(Map(variation.map)))

    def showContextMenu(self, pos):
        index = self.mTileStampView.indexAt(pos)
        if (not index.isValid()):
            return
        menu = QMenu()
        sourceIndex = self.mProxyModel.mapToSource(index)
        if (self.mTileStampModel.isStamp(sourceIndex)):
            addStampVariation = QAction(self.mAddVariation.icon(), self.mAddVariation.text(), menu)
            deleteStamp = QAction(self.mDelete.icon(), self.tr("Delete Stamp"), menu)
            deleteStamp.triggered.connect(self.delete_)
            addStampVariation.triggered.connect(self.addVariation)
            menu.addAction(addStampVariation)
            menu.addSeparator()
            menu.addAction(deleteStamp)
        else :
            removeVariation = QAction(QIcon(":/images/16x16/remove.png"),
                                                   self.tr("Remove Variation"),
                                                   menu)
            Utils.setThemeIcon(removeVariation, "remove")
            removeVariation.triggered.connect(self.delete_)
            menu.addAction(removeVariation)
        
        menu.exec(self.mTileStampView.viewport().mapToGlobal(pos))
    
    def newStamp(self):
        stamp = self.mTileStampManager.createStamp()
        if (self.isVisible() and not stamp.isEmpty()):
            stampIndex = self.mTileStampModel.index(stamp)
            if (stampIndex.isValid()):
                viewIndex = self.mProxyModel.mapFromSource(stampIndex)
                self.mTileStampView.setCurrentIndex(viewIndex)
                self.mTileStampView.edit(viewIndex)

    
    def delete_(self):
        index = self.mTileStampView.currentIndex()
        if (not index.isValid()):
            return
        sourceIndex = self.mProxyModel.mapToSource(index)
        self.mTileStampModel.removeRow(sourceIndex.row(), sourceIndex.parent())
    
    def duplicate(self):
        index = self.mTileStampView.currentIndex()
        if (not index.isValid()):
            return
        sourceIndex = self.mProxyModel.mapToSource(index)
        if (not self.mTileStampModel.isStamp(sourceIndex)):
            return
        stamp = self.mTileStampModel.stampAt = TileStamp(sourceIndex)
        self.mTileStampModel.addStamp(stamp.clone())

    def addVariation(self):
        index = self.mTileStampView.currentIndex()
        if (not index.isValid()):
            return
        sourceIndex = self.mProxyModel.mapToSource(index)
        if (not self.mTileStampModel.isStamp(sourceIndex)):
            return
        stamp = self.mTileStampModel.stampAt(sourceIndex)
        self.mTileStampManager.addVariation(stamp)
    
    def chooseFolder(self):
        prefs = Preferences.instance()
        stampsDirectory = prefs.stampsDirectory()
        stampsDirectory = QFileDialog.getExistingDirectory(self.window(),
                                                            self.tr("Choose the Stamps Folder"),
                                                            stampsDirectory)
        if (not stampsDirectory.isEmpty()):
            prefs.setStampsDirectory(stampsDirectory)
    
    def ensureStampVisible(self, stamp):
        stampIndex = self.mTileStampModel.index(stamp)
        if (stampIndex.isValid()):
            self.mTileStampView.scrollTo(self.mProxyModel.mapFromSource(stampIndex))

    def retranslateUi(self):
        self.setWindowTitle(self.tr("Tile Stamps"))
        self.mNewStamp.setText(self.tr("Add New Stamp"))
        self.mAddVariation.setText(self.tr("Add Variation"))
        self.mDuplicate.setText(self.tr("Duplicate Stamp"))
        self.mDelete.setText(self.tr("Delete Selected"))
        self.mChooseFolder.setText(self.tr("Set Stamps Folder"))
        self.mFilterEdit.setPlaceholderText(self.tr("Filter"))

##
# This view makes sure the size hint makes sense and implements the context
# menu.
##
class TileStampView(QTreeView):


    def __init__(self, parent = None):
        super().__init__(parent)


    def sizeHint(self):
        return QSize(130, 200)
