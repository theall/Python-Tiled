##
# mapsdock.py
# Copyright 2012, Tim Baker
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

import preferences
from mapformat import MapFormat
from pluginmanager import PluginManager
from pyqtcore import QStringList
from PyQt5.QtCore import (
    Qt,
    QDir,
    QSize,
    QEvent,
    QRegExp,
    QFileInfo
)
from PyQt5.QtWidgets import (
    QPushButton,
    QLineEdit,
    QWidget,
    QHeaderView,
    QFileSystemModel,
    QFileDialog,
    QDirModel,
    QCompleter,
    QVBoxLayout,
    QTreeView,
    QDockWidget,
    QHBoxLayout
)

##
# Class represents the file system model with disabled dragging of directories.
##
class FileSystemModel(QFileSystemModel):
    def __init__(self, parent = None):
        super().__init__(parent)

    def flags(self, i):
        flags = super().flags(i)
        if self.isDir(i):
            flags &= ~Qt.ItemIsDragEnabled
        return flags

class MapsDock(QDockWidget):
    def __init__(self, mainWindow, parent = None):
        super().__init__(parent)
        self.mDirectoryEdit = QLineEdit()
        self.mMapsView = MapsView(mainWindow)

        self.setObjectName("MapsDock")
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        dirLayout = QHBoxLayout()
        # QDirModel is obsolete, but I could not get QFileSystemModel to work here
        model = QDirModel(self)
        model.setFilter(QDir.AllDirs | QDir.Dirs | QDir.Drives | QDir.NoDotAndDotDot)
        completer = QCompleter(model, self)
        self.mDirectoryEdit.setCompleter(completer)
        button = QPushButton(self.tr("Browse..."))
        dirLayout.addWidget(self.mDirectoryEdit)
        dirLayout.addWidget(button)
        layout.addWidget(self.mMapsView)
        layout.addLayout(dirLayout)
        self.setWidget(widget)
        self.retranslateUi()
        button.clicked.connect(self.browse)
        prefs = preferences.Preferences.instance()
        prefs.mapsDirectoryChanged.connect(self.onMapsDirectoryChanged)
        self.mDirectoryEdit.setText(prefs.mapsDirectory())
        self.mDirectoryEdit.returnPressed.connect(self.editedMapsDirectory)

    def browse(self):
        f = QFileDialog.getExistingDirectory(self.window(), 
                                            self.tr("Choose the Maps Folder"),
                                            self.mDirectoryEdit.text())
        if (not f.isEmpty()):
            prefs = preferences.Preferences.instance()
            prefs.setMapsDirectory(f)

    def editedMapsDirectory(self):
        prefs = preferences.Preferences.instance()
        prefs.setMapsDirectory(self.mDirectoryEdit.text())

    def onMapsDirectoryChanged(self):
        prefs = preferences.Preferences.instance()
        self.mDirectoryEdit.setText(prefs.mapsDirectory())

    def changeEvent(self, e):
        super().changeEvent(e)
        x = e.type()
        if x==QEvent.LanguageChange:
            self.retranslateUi()
        else:
            pass

    def retranslateUi(self):
        self.setWindowTitle(self.tr("Maps"))

##
# Shows the list of files and directories.
##
class MapsView(QTreeView):

    def __init__(self, mainWindow, parent = None):
        super().__init__(parent)
        self.mMainWindow = mainWindow

        self.setRootIsDecorated(False)
        self.setHeaderHidden(True)
        self.setItemsExpandable(False)
        self.setUniformRowHeights(True)
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.MoveAction)
        prefs = preferences.Preferences.instance()
        prefs.mapsDirectoryChanged.connect(self.onMapsDirectoryChanged)
        mapsDir = QDir(prefs.mapsDirectory())
        if (not mapsDir.exists()):
            mapsDir.setPath(QDir.currentPath())
        self.mFSModel = FileSystemModel(self)
        self.mFSModel.setRootPath(mapsDir.absolutePath())

        nameFilters = QStringList("*.tmx")
        # The file system model name filters are plain, whereas the plugins expose
        # a filter as part of the file description
        filterFinder = QRegExp("\\((\\*\\.[^\\)\\s]*)")
        for format in PluginManager.objects(MapFormat):
            if not (format.capabilities() & MapFormat.Read):
                continue

            filter = format.nameFilter()
            if (filterFinder.indexIn(filter) != -1):
                nameFilters.append(filterFinder.cap(1))

        self.mFSModel.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDot)
        self.mFSModel.setNameFilters(nameFilters)
        self.mFSModel.setNameFilterDisables(False) # hide filtered files
        self.setModel(self.mFSModel)
        headerView = self.header()
        headerView.hideSection(1) # Size column
        headerView.hideSection(2)
        headerView.hideSection(3)
        self.setRootIndex(self.mFSModel.index(mapsDir.absolutePath()))
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.activated.connect(self.onActivated)

        self.mMainWindow = None
        self.mFSModel = None

    ##
    # Returns a sensible size hint.
    ##
    def sizeHint(self):
        return QSize(130, 100)

    def mousePressEvent(self, event):
        index = self.indexAt(event.pos())
        if (index.isValid()):
            # Prevent drag-and-drop starting when clicking on an unselected item.
            self.setDragEnabled(self.selectionModel().isSelected(index))

        super().mousePressEvent(event)

    def onMapsDirectoryChanged(self):
        prefs = preferences.Preferences.instance()
        mapsDir = QDir(prefs.mapsDirectory())
        if (not mapsDir.exists()):
            mapsDir.setPath(QDir.currentPath())
        self.model().setRootPath(mapsDir.canonicalPath())
        self.setRootIndex(self.model().index(mapsDir.absolutePath()))

    def onActivated(self, index):
        path = self.model().filePath(index)
        fileInfo = QFileInfo(path)
        if (fileInfo.isDir()):
            prefs = preferences.Preferences.instance()
            prefs.setMapsDirectory(fileInfo.canonicalFilePath())
            return

        self.mMainWindow.openFile(path)
