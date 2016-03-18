##
# documentmanager.py
# Copyright 2010, Stefan Beller, stefanbeller@googlemail.com
# Copyright 2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
#
# This file is part of Tiled.
#
# This program is free software you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
##

from movabletabwidget import MovableTabWidget
from mapview import MapView
from mapscene import MapScene
from mapdocument import MapDocument
from filesystemwatcher import FileSystemWatcher
from PyQt5.QtCore import (
    Qt,
    QFileInfo,
    QObject,
    pyqtSignal
)
from PyQt5.QtWidgets import (
    QWidget,
    QDialogButtonBox,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QUndoGroup
)
from pyqtcore import QList
##
# This class controls the open documents.
##
class DocumentManager(QObject):
    ##
    # Emitted when the current displayed map document changed.
    ##
    currentDocumentChanged = pyqtSignal(list)
    ##
    # Emitted when the user requested the document at \a index to be closed.
    ##
    documentCloseRequested = pyqtSignal(int)
    ##
    # Emitted when a document is about to be closed.
    ##
    documentAboutToClose = pyqtSignal(MapDocument)
    ##
    # Emitted when an error occurred while reloading the map.
    ##
    reloadError = pyqtSignal(str)

    mInstance = None

    def __init__(self, parent = None):
        super().__init__(parent)

        self.mDocuments = QList()
        self.mTabWidget = MovableTabWidget()
        self.mUndoGroup = QUndoGroup(self)
        self.mSelectedTool = None
        self.mViewWithTool = None
        self.mFileSystemWatcher = FileSystemWatcher(self)

        self.mTabWidget.setDocumentMode(True)
        self.mTabWidget.setTabsClosable(True)
        self.mTabWidget.currentChanged.connect(self.currentIndexChanged)
        self.mTabWidget.tabCloseRequested.connect(self.documentCloseRequested)
        self.mTabWidget.tabMoved.connect(self.documentTabMoved)
        self.mFileSystemWatcher.fileChanged.connect(self.fileChanged)

    def __del__(self):
        # All documents should be closed gracefully beforehand
        del self.mTabWidget

    def instance():
        if not DocumentManager.mInstance:
            DocumentManager.mInstance = DocumentManager()
        return DocumentManager.mInstance

    def deleteInstance():
        del DocumentManager.mInstance
        DocumentManager.mInstance = None

    ##
    # Returns the document manager widget. It contains the different map views
    # and a tab bar to switch between them.
    ##
    def widget(self):
        return self.mTabWidget

    ##
    # Returns the undo group that combines the undo stacks of all opened map
    # documents.
    #
    # @see MapDocument.undoStack()
    ##
    def undoGroup(self):
        return self.mUndoGroup

    ##
    # Returns the current map document, or 0 when there is none.
    ##
    def currentDocument(self):
        index = self.mTabWidget.currentIndex()
        if (index == -1):
            return None
        return self.mDocuments.at(index)

    ##
    # Returns the map view of the current document, or 0 when there is none.
    ##
    def currentMapView(self):
        widget = self.mTabWidget.currentWidget()
        if widget:
            return widget.mapView()
        return None

    ##
    # Returns the map scene of the current document, or 0 when there is none.
    ##
    def currentMapScene(self):
        mapView = self.currentMapView()
        if mapView:
            return mapView.mapScene()
        return None

    ##
    # Returns the map view that displays the given document, or 0 when there
    # is none.
    ##
    def viewForDocument(self, mapDocument):
        index = self.mDocuments.indexOf(mapDocument)
        if (index == -1):
            return None
        return self.mTabWidget.widget(index).mapView()

    ##
    # Returns the number of map documents.
    ##
    def documentCount(self):
        return self.mDocuments.size()

    ##
    # Searches for a document with the given \a fileName and returns its
    # index. Returns -1 when the document isn't open.
    ##
    def findDocument(self, fileName):
        canonicalFilePath = QFileInfo(fileName).canonicalFilePath()
        if (canonicalFilePath==''): # file doesn't exist
            return -1
        for i in range(self.mDocuments.size()):
            fileInfo = QFileInfo(self.mDocuments.at(i).fileName())
            if (fileInfo.canonicalFilePath() == canonicalFilePath):
                return i

        return -1

    ##
    # Switches to the map document at the given \a index.
    ##
    def switchToDocument(self, arg):
        tp = type(arg)
        if tp==int:
            index = arg
            self.mTabWidget.setCurrentIndex(index)
        elif tp==MapDocument:
            mapDocument = arg
            index = self.mDocuments.indexOf(mapDocument)
            if (index != -1):
                self.switchToDocument(index)

    ##
    # Adds the new or opened \a mapDocument to the document manager.
    ##
    def addDocument(self, mapDocument):
        self.mDocuments.append(mapDocument)
        self.mUndoGroup.addStack(mapDocument.undoStack())
        if (mapDocument.fileName()!=''):
            self.mFileSystemWatcher.addPath(mapDocument.fileName())
        view = MapView()
        scene = MapScene(view) # scene is owned by the view
        container = MapViewContainer(view, self.mTabWidget)
        scene.setMapDocument(mapDocument)
        view.setScene(scene)
        documentIndex = self.mDocuments.size() - 1
        self.mTabWidget.addTab(container, mapDocument.displayName())
        self.mTabWidget.setTabToolTip(documentIndex, mapDocument.fileName())
        mapDocument.fileNameChanged.connect(self.fileNameChanged)
        mapDocument.modifiedChanged.connect(self.updateDocumentTab)
        mapDocument.saved.connect(self.documentSaved)
        container.reload.connect(self.reloadRequested)
        self.switchToDocument(documentIndex)
        self.centerViewOn(0, 0)

    ##
    # Closes the current map document. Will not ask the user whether to save
    # any changes!
    ##
    def closeCurrentDocument(self):
        index = self.mTabWidget.currentIndex()
        if (index == -1):
            return
        self.closeDocumentAt(index)

    ##
    # Closes the document at the given \a index. Will not ask the user whether
    # to save any changes!
    ##
    def closeDocumentAt(self, index):
        mapDocument = self.mDocuments.at(index)
        self.documentAboutToClose.emit(mapDocument)

        self.mDocuments.removeAt(index)
        self.mTabWidget.removeTab(index)
        
        if (mapDocument.fileName() != ''):
            self.mFileSystemWatcher.removePath(mapDocument.fileName())

        self.mUndoGroup.removeStack(mapDocument.undoStack())
        
    ##
    # Reloads the current document. Will not ask the user whether to save any
    # changes!
    #
    # \sa reloadDocumentAt()
    ##
    def reloadCurrentDocument(self):
        index = self.mTabWidget.currentIndex()
        if (index == -1):
            return False
        return self.reloadDocumentAt(index)

    ##
    # Reloads the document at the given \a index. It will lose any undo
    # history and current selections. Will not ask the user whether to save
    # any changes!
    #
    # Returns whether the map loaded successfully.
    ##
    def reloadDocumentAt(self, index):
        oldDocument = self.mDocuments.at(index)
        
        newDocument, error = MapDocument.load(oldDocument.fileName(), oldDocument.readerFormat())
        if (not newDocument):
            self.reloadError.emit(self.tr("%s:\n\n%s"%(oldDocument.fileName(), error)))
            return False

        # Remember current view state
        mapView = self.viewForDocument(oldDocument)
        layerIndex = oldDocument.currentLayerIndex()
        scale = mapView.zoomable().scale()
        horizontalPosition = mapView.horizontalScrollBar().sliderPosition()
        verticalPosition = mapView.verticalScrollBar().sliderPosition()
        # Replace old tab
        self.addDocument(newDocument)
        self.closeDocumentAt(index)
        self.mTabWidget.moveTab(self.mDocuments.size() - 1, index)
        # Restore previous view state
        mapView = self.currentMapView()
        mapView.zoomable().setScale(scale)
        mapView.horizontalScrollBar().setSliderPosition(horizontalPosition)
        mapView.verticalScrollBar().setSliderPosition(verticalPosition)
        if (layerIndex > 0 and layerIndex < newDocument.map().layerCount()):
            newDocument.setCurrentLayerIndex(layerIndex)
        return True

    ##
    # Close all documents. Will not ask the user whether to save any changes!
    ##
    def closeAllDocuments(self):
        while (not self.mDocuments.isEmpty()):
            self.closeCurrentDocument()

    ##
    # Returns all open map documents.
    ##
    def documents(self):
        return self.mDocuments

    ##
    # Centers the current map on the tile coordinates \a x, \a y.
    ##
    def centerViewOn(self, *args):
        l = len(args)
        if l==2:
            x, y = args
            view = self.currentMapView()
            if (not view):
                return
            view.centerOn(self.currentDocument().renderer().pixelToScreenCoords(x, y))
        elif l==1:
            pos = args[0]
            self.centerViewOn(pos.x(), pos.y())

    def switchToLeftDocument(self):
        tabCount = self.mTabWidget.count()
        if (tabCount < 2):
            return
        currentIndex = self.mTabWidget.currentIndex()
        if currentIndex > 0:
            x = currentIndex
        else:
            x = tabCount
        self.switchToDocument(x - 1)

    def switchToRightDocument(self):
        tabCount = self.mTabWidget.count()
        if (tabCount < 2):
            return
        currentIndex = self.mTabWidget.currentIndex()
        self.switchToDocument((currentIndex + 1) % tabCount)

    def setSelectedTool(self, tool):
        if type(tool)==list:
            tool = tool[0]
        if (self.mSelectedTool == tool):
            return
        
        if self.mSelectedTool:
            self.mSelectedTool.cursorChanged.disconnect(self.cursorChanged)

        self.mSelectedTool = tool
        
        if self.mViewWithTool:
            mapScene = self.mViewWithTool.mapScene()
            mapScene.disableSelectedTool()

            if tool:
                mapScene.setSelectedTool(tool)
                mapScene.enableSelectedTool()

            if tool:
                self.mViewWithTool.viewport().setCursor(tool.cursor)
            else:
                self.mViewWithTool.viewport().unsetCursor()

        if tool:
            tool.cursorChanged.connect(self.cursorChanged)

    def currentIndexChanged(self):
        if self.mViewWithTool:
            mapScene = self.mViewWithTool.mapScene()
            mapScene.disableSelectedTool()
            self.mViewWithTool = None
        
        mapDocument = self.currentDocument()
        if (mapDocument):
            self.mUndoGroup.setActiveStack(mapDocument.undoStack())

        self.currentDocumentChanged.emit([mapDocument])
        
        mapView = self.currentMapView()
        if mapView:
            mapScene = mapView.mapScene()
            mapScene.setSelectedTool(self.mSelectedTool)
            mapScene.enableSelectedTool()
            if self.mSelectedTool:
                mapView.viewport().setCursor(self.mSelectedTool.cursor)
            else:
                mapView.viewport().unsetCursor()
            self.mViewWithTool = mapView

    def fileNameChanged(self, fileName, oldFileName):
        if fileName != '':
            self.mFileSystemWatcher.addPath(fileName)
        if oldFileName != '':
            self.mFileSystemWatcher.removePath(oldFileName)
        self.updateDocumentTab()

    def updateDocumentTab(self):
        mapDocument = self.sender()
        index = self.mDocuments.indexOf(mapDocument)
        tabText = mapDocument.displayName()
        if (mapDocument.isModified()):
            tabText = '*' + tabText
        self.mTabWidget.setTabText(index, tabText)
        self.mTabWidget.setTabToolTip(index, mapDocument.fileName())

    def documentSaved(self):
        document = self.sender()
        index = self.mDocuments.indexOf(document)
        widget = self.mTabWidget.widget(index)
        container = widget
        container.setFileChangedWarningVisible(False)

    def documentTabMoved(self, _from, to):
        self.mDocuments.move(_from, to)

    def fileChanged(self, fileName):
        index = self.findDocument(fileName)
        # Most likely the file was removed
        if (index == -1):
            return
        document = self.mDocuments.at(index)
        # Ignore change event when it seems to be our own save
        if (QFileInfo(fileName).lastModified() == document.lastSaved()):
            return
        # Automatically reload when there are no unsaved changes
        if (not document.isModified()):
            self.reloadDocumentAt(index)
            return

        widget = self.mTabWidget.widget(index)
        container = widget
        container.setFileChangedWarningVisible(True)

    def cursorChanged(self, cursor):
        if self.mViewWithTool:
            self.mViewWithTool.viewport().setCursor(cursor)
        
    def reloadRequested(self):
        index = self.mTabWidget.indexOf(self.sender())
        self.reloadDocumentAt(index)

class FileChangedWarning(QWidget):
    reload = pyqtSignal()
    ignore = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent)

        self.mLabel = QLabel(self)
        self.mButtons = QDialogButtonBox(QDialogButtonBox.Yes |
                                        QDialogButtonBox.No,
                                        Qt.Horizontal, self)

        self.mLabel.setText(self.tr("File change detected. Discard changes and reload the map?"))
        layout = QHBoxLayout()
        layout.addWidget(self.mLabel)
        layout.addStretch(1)
        layout.addWidget(self.mButtons)
        self.setLayout(layout)
        self.mButtons.accepted.connect(self.reload)
        self.mButtons.rejected.connect(self.ignore)

class MapViewContainer(QWidget):
    reload = pyqtSignal()

    def __init__(self, mapView, parent = None):
        super().__init__(parent)

        self.mMapView = mapView
        self.mWarning = FileChangedWarning()

        self.mWarning.setVisible(False)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(mapView)
        layout.addWidget(self.mWarning)
        self.setLayout(layout)
        self.mWarning.reload.connect(self.reload)
        self.mWarning.ignore.connect(self.mWarning.hide)
        
    def __del__(self):
        del self.mMapView
        del self.mWarning
        
    def mapView(self):
        return self.mMapView

    def setFileChangedWarningVisible(self, visible):
        self.mWarning.setVisible(visible)

