##
# tilesetdock.py
# Copyright 2008-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2009, Edward Hutchins
# Copyright 2012, Stefan Beller, stefanbeller@googlemail.com
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

import sys
from object import Object
from zoomable import Zoomable
from utils import Utils
from tilestamp import TileStamp
from tilesetmanager import TilesetManager
from tilesetview import TilesetView
from tilelayer import TileLayer, Cell
from tmxmapformat import TsxTilesetFormat
from tile import Tile
import preferences
from map import Map
from tilesetmodel import TilesetModel
from mapformat import FormatHelper, FileFormat
from containerhelpers import indexOf
from movetileset import MoveTileset
from erasetiles import EraseTiles
from editterraindialog import EditTerrainDialog
from documentmanager import DocumentManager
from addremovetileset import RemoveTileset
from addremovetiles import AddTiles, RemoveTiles
from rangeset import RangeSet
from pyqtcore import QMap, QList, QStringList, QString, QSet, QVector
from addremovemapobject import RemoveMapObject
from PyQt5.QtCore import (
    Qt,
    QSize,
    QEvent,
    QFileInfo,
    QSignalMapper,
    pyqtSignal,
    QModelIndex, 
    QCoreApplication, 
    QItemSelection, 
    QItemSelectionModel
)
from PyQt5.QtGui import (
    QIcon, 
    QPixmap
)
from PyQt5.QtWidgets import (
    QWidget,
    QStyle,
    QMenu, 
    QTabBar, 
    QActionGroup, 
    QStackedWidget, 
    QToolBar, 
    QVBoxLayout,
    QToolButton,
    QStylePainter,
    QMessageBox,
    QHBoxLayout,
    QFileDialog,
    QComboBox,
    QUndoCommand,
    QSizePolicy,
    QAction,
    QDockWidget,
    QStyleOptionToolButton
)
##
# The dock widget that displays the tilesets. Also keeps track of the
# currently selected tile.
##
class TilesetDock(QDockWidget):
    ##
    # Emitted when the current tile changed.
    ##
    currentTileChanged = pyqtSignal(list)
    ##
    # Emitted when the currently selected tiles changed.
    ##
    stampCaptured = pyqtSignal(TileStamp)
    ##
    # Emitted when files are dropped at the tileset dock.
    ##
    tilesetsDropped = pyqtSignal(QStringList)
    newTileset = pyqtSignal()

    ##
    # Constructor.
    ##
    def __init__(self, parent = None):
        super().__init__(parent)

        # Shared tileset references because the dock wants to add new tiles
        self.mTilesets = QVector()
        self.mCurrentTilesets = QMap()
        self.mMapDocument = None
        self.mTabBar = QTabBar()
        self.mViewStack = QStackedWidget()
        self.mToolBar = QToolBar()
        self.mCurrentTile = None
        self.mCurrentTiles = None
        self.mNewTileset = QAction(self)
        self.mImportTileset = QAction(self)
        self.mExportTileset = QAction(self)
        self.mPropertiesTileset = QAction(self)
        self.mDeleteTileset = QAction(self)
        self.mEditTerrain = QAction(self)
        self.mAddTiles = QAction(self)
        self.mRemoveTiles = QAction(self)
        self.mTilesetMenuButton = TilesetMenuButton(self)
        self.mTilesetMenu = QMenu(self) # opens on click of mTilesetMenu
        self.mTilesetActionGroup = QActionGroup(self)
        self.mTilesetMenuMapper = None # needed due to dynamic content
        self.mEmittingStampCaptured = False
        self.mSynchronizingSelection = False
    
        self.setObjectName("TilesetDock")
        self.mTabBar.setMovable(True)
        self.mTabBar.setUsesScrollButtons(True)
        self.mTabBar.currentChanged.connect(self.updateActions)
        self.mTabBar.tabMoved.connect(self.moveTileset)
        w = QWidget(self)
        horizontal = QHBoxLayout()
        horizontal.setSpacing(0)
        horizontal.addWidget(self.mTabBar)
        horizontal.addWidget(self.mTilesetMenuButton)
        vertical = QVBoxLayout(w)
        vertical.setSpacing(0)
        vertical.setContentsMargins(5, 5, 5, 5)
        vertical.addLayout(horizontal)
        vertical.addWidget(self.mViewStack)
        horizontal = QHBoxLayout()
        horizontal.setSpacing(0)
        horizontal.addWidget(self.mToolBar, 1)
        vertical.addLayout(horizontal)
        self.mNewTileset.setIcon(QIcon(":images/16x16/document-new.png"))
        self.mImportTileset.setIcon(QIcon(":images/16x16/document-import.png"))
        self.mExportTileset.setIcon(QIcon(":images/16x16/document-export.png"))
        self.mPropertiesTileset.setIcon(QIcon(":images/16x16/document-properties.png"))
        self.mDeleteTileset.setIcon(QIcon(":images/16x16/edit-delete.png"))
        self.mEditTerrain.setIcon(QIcon(":images/16x16/terrain.png"))
        self.mAddTiles.setIcon(QIcon(":images/16x16/add.png"))
        self.mRemoveTiles.setIcon(QIcon(":images/16x16/remove.png"))
        Utils.setThemeIcon(self.mNewTileset, "document-new")
        Utils.setThemeIcon(self.mImportTileset, "document-import")
        Utils.setThemeIcon(self.mExportTileset, "document-export")
        Utils.setThemeIcon(self.mPropertiesTileset, "document-properties")
        Utils.setThemeIcon(self.mDeleteTileset, "edit-delete")
        Utils.setThemeIcon(self.mAddTiles, "add")
        Utils.setThemeIcon(self.mRemoveTiles, "remove")
        self.mNewTileset.triggered.connect(self.newTileset)
        self.mImportTileset.triggered.connect(self.importTileset)
        self.mExportTileset.triggered.connect(self.exportTileset)
        self.mPropertiesTileset.triggered.connect(self.editTilesetProperties)
        self.mDeleteTileset.triggered.connect(self.removeTileset)
        self.mEditTerrain.triggered.connect(self.editTerrain)
        self.mAddTiles.triggered.connect(self.addTiles)
        self.mRemoveTiles.triggered.connect(self.removeTiles)
        self.mToolBar.addAction(self.mNewTileset)
        self.mToolBar.setIconSize(QSize(16, 16))
        self.mToolBar.addAction(self.mImportTileset)
        self.mToolBar.addAction(self.mExportTileset)
        self.mToolBar.addAction(self.mPropertiesTileset)
        self.mToolBar.addAction(self.mDeleteTileset)
        self.mToolBar.addAction(self.mEditTerrain)
        self.mToolBar.addAction(self.mAddTiles)
        self.mToolBar.addAction(self.mRemoveTiles)
        self.mZoomable = Zoomable(self)
        self.mZoomComboBox = QComboBox()
        self.mZoomable.connectToComboBox(self.mZoomComboBox)
        horizontal.addWidget(self.mZoomComboBox)
        self.mViewStack.currentChanged.connect(self.updateCurrentTiles)
        TilesetManager.instance().tilesetChanged.connect(self.tilesetChanged)
        DocumentManager.instance().documentAboutToClose.connect(self.documentAboutToClose)
        self.mTilesetMenuButton.setMenu(self.mTilesetMenu)
        self.mTilesetMenu.aboutToShow.connect(self.refreshTilesetMenu)
        self.setWidget(w)
        self.retranslateUi()
        self.setAcceptDrops(True)
        self.updateActions()

    def __del__(self):
        del self.mCurrentTiles
        
    ##
    # Sets the map for which the tilesets should be displayed.
    ##
    def setMapDocument(self, mapDocument):
        if (self.mMapDocument == mapDocument):
            return
        # Hide while we update the tab bar, to avoid repeated layouting
        if sys.platform != 'darwin':
            self.widget().hide()
            
        self.setCurrentTiles(None)
        self.setCurrentTile(None)
        
        if (self.mMapDocument):
            # Remember the last visible tileset for this map
            tilesetName = self.mTabBar.tabText(self.mTabBar.currentIndex())
            self.mCurrentTilesets.insert(self.mMapDocument, tilesetName)

        # Clear previous content
        while (self.mTabBar.count()):
            self.mTabBar.removeTab(0)
        while (self.mViewStack.count()):
            self.mViewStack.removeWidget(self.mViewStack.widget(0))
        #self.mTilesets.clear()
        # Clear all connections to the previous document
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
        self.mMapDocument = mapDocument
        if (self.mMapDocument):
            self.mTilesets = self.mMapDocument.map().tilesets()
            for tileset in self.mTilesets:
                view = TilesetView()
                view.setMapDocument(self.mMapDocument)
                view.setZoomable(self.mZoomable)
                self.mTabBar.addTab(tileset.name())
                self.mViewStack.addWidget(view)

            self.mMapDocument.tilesetAdded.connect(self.tilesetAdded)
            self.mMapDocument.tilesetRemoved.connect(self.tilesetRemoved)
            self.mMapDocument.tilesetMoved.connect(self.tilesetMoved)
            self.mMapDocument.tilesetNameChanged.connect(self.tilesetNameChanged)
            self.mMapDocument.tilesetFileNameChanged.connect(self.updateActions)
            self.mMapDocument.tilesetChanged.connect(self.tilesetChanged)
            self.mMapDocument.tileAnimationChanged.connect(self.tileAnimationChanged)
            cacheName = self.mCurrentTilesets.take(self.mMapDocument)
            for i in range(self.mTabBar.count()):
                if (self.mTabBar.tabText(i) == cacheName):
                    self.mTabBar.setCurrentIndex(i)
                    break
            
            object = self.mMapDocument.currentObject()
            if object:
                if object.typeId() == Object.TileType:
                    self.setCurrentTile(object)
                    
        self.updateActions()
        if sys.platform != 'darwin':
            self.widget().show()

    ##
    # Synchronizes the selection with the given stamp. Ignored when the stamp is
    # changing because of a selection change in the TilesetDock.
    ##
    def selectTilesInStamp(self, stamp):
        if self.mEmittingStampCaptured:
            return
        processed = QSet()
        selections = QMap()
        for variation in stamp.variations():
            tileLayer = variation.tileLayer()
            for cell in tileLayer:
                tile = cell.tile
                if tile:
                    if (processed.contains(tile)):
                        continue
                    processed.insert(tile); # avoid spending time on duplicates
                    tileset = tile.tileset()
                    tilesetIndex = self.mTilesets.indexOf(tileset.sharedPointer())
                    if (tilesetIndex != -1):
                        view = self.tilesetViewAt(tilesetIndex)
                        if (not view.model()): # Lazily set up the model
                            self.setupTilesetModel(view, tileset)
                        model = view.tilesetModel()
                        modelIndex = model.tileIndex(tile)
                        selectionModel = view.selectionModel()
                        
                        _x = QItemSelection()
                        _x.select(modelIndex, modelIndex)
                        selections[selectionModel] = _x

        if (not selections.isEmpty()):
            self.mSynchronizingSelection = True
            # Mark captured tiles as selected
            for i in selections:
                selectionModel = i[0]
                selection = i[1]
                selectionModel.select(selection, QItemSelectionModel.SelectCurrent)
            
            # Show/edit properties of all captured tiles
            self.mMapDocument.setSelectedTiles(processed.toList())
            # Update the current tile (useful for animation and collision editors)
            first = selections.first()
            selectionModel = first[0]
            selection = first[1]
            currentIndex = QModelIndex(selection.first().topLeft())
            if (selectionModel.currentIndex() != currentIndex):
                selectionModel.setCurrentIndex(currentIndex, QItemSelectionModel.NoUpdate)
            else:
                self.currentChanged(currentIndex)
            self.mSynchronizingSelection = False
    

    def currentTilesetChanged(self):
        view = self.currentTilesetView()
        if view:
            s = view.selectionModel()
            if s:
                self.setCurrentTile(view.tilesetModel().tileAt(s.currentIndex()))

    ##
    # Returns the currently selected tile.
    ##
    def currentTile(self):
        return self.mCurrentTile

    def changeEvent(self, e):
        super().changeEvent(e)
        x = e.type()
        if x==QEvent.LanguageChange:
            self.retranslateUi()
        else:
            pass

    def dragEnterEvent(self, e):
        urls = e.mimeData().urls()
        if (not urls.isEmpty() and not urls.at(0).toLocalFile().isEmpty()):
            e.accept()

    def dropEvent(self, e):
        paths = QStringList()
        for url in e.mimeData().urls():
            localFile = url.toLocalFile()
            if (not localFile.isEmpty()):
                paths.append(localFile)

        if (not paths.isEmpty()):
            self.tilesetsDropped.emit(paths)
            e.accept()

    def selectionChanged(self):
        self.updateActions()
        if not self.mSynchronizingSelection:
            self.updateCurrentTiles()

    def currentChanged(self, index):
        if (not index.isValid()):
            return
        model = index.model()
        self.setCurrentTile(model.tileAt(index))

    def updateActions(self):
        external = False
        hasImageSource = False
        hasSelection = False
        view = None
        index = self.mTabBar.currentIndex()
        if (index > -1):
            view = self.tilesetViewAt(index)
            if (view):
                tileset = self.mTilesets.at(index)
                if (not view.model()):# Lazily set up the model
                    self.setupTilesetModel(view, tileset)

                self.mViewStack.setCurrentIndex(index)
                external = tileset.isExternal()
                hasImageSource = tileset.imageSource()!=''
                hasSelection = view.selectionModel().hasSelection()

        tilesetIsDisplayed = view != None
        mapIsDisplayed = self.mMapDocument != None
        self.mNewTileset.setEnabled(mapIsDisplayed)
        self.mImportTileset.setEnabled(tilesetIsDisplayed and external)
        self.mExportTileset.setEnabled(tilesetIsDisplayed and not external)
        self.mPropertiesTileset.setEnabled(tilesetIsDisplayed and not external)
        self.mDeleteTileset.setEnabled(tilesetIsDisplayed)
        self.mEditTerrain.setEnabled(tilesetIsDisplayed and not external)
        self.mAddTiles.setEnabled(tilesetIsDisplayed and not hasImageSource and not external)
        self.mRemoveTiles.setEnabled(tilesetIsDisplayed and not hasImageSource
                                 and hasSelection and not external)

    def updateCurrentTiles(self):
        view = self.currentTilesetView()
        if (not view):
            return
        s = view.selectionModel()
        if (not s):
            return
        indexes = s.selection().indexes()
        if len(indexes)==0:
            return
        first = indexes[0]
        minX = first.column()
        maxX = first.column()
        minY = first.row()
        maxY = first.row()
        for index in indexes:
            if minX > index.column():
                minX = index.column()
            if maxX < index.column():
                maxX = index.column()
            if minY > index.row():
                minY = index.row()
            if maxY < index.row():
                maxY = index.row()

        # Create a tile layer from the current selection
        tileLayer = TileLayer(QString(), 0, 0, maxX - minX + 1, maxY - minY + 1)
        model = view.tilesetModel()
        for index in indexes:
            tileLayer.setCell(index.column() - minX,
                               index.row() - minY,
                               Cell(model.tileAt(index)))

        self.setCurrentTiles(tileLayer)

    def indexPressed(self, index):
        view = self.currentTilesetView()
        tile = view.tilesetModel().tileAt(index)
        if tile:
            self.mMapDocument.setCurrentObject(tile)

    def tilesetAdded(self, index, tileset):
        view = TilesetView()
        view.setMapDocument(self.mMapDocument)
        view.setZoomable(self.mZoomable)
        self.mTilesets.insert(index, tileset.sharedPointer())
        self.mTabBar.insertTab(index, tileset.name())
        self.mViewStack.insertWidget(index, view)
        self.updateActions()

    def tilesetChanged(self, tileset):
        # Update the affected tileset model, if it exists
        index = indexOf(self.mTilesets, tileset)
        if (index < 0):
            return
        model = self.tilesetViewAt(index).tilesetModel()
        if model:
            model.tilesetChanged()

    def tilesetRemoved(self, tileset):
        # Delete the related tileset view
        index = indexOf(self.mTilesets, tileset)
        self.mTilesets.removeAt(index)
        self.mTabBar.removeTab(index)
        self.tilesetViewAt(index).close()

        # Make sure we don't reference this tileset anymore
        if (self.mCurrentTiles):
            # TODO: Don't clean unnecessarily (but first the concept of
            #       "current brush" would need to be introduced)
            cleaned = self.mCurrentTiles.clone()
            cleaned.removeReferencesToTileset(tileset)
            self.setCurrentTiles(cleaned)

        if (self.mCurrentTile and self.mCurrentTile.tileset() == tileset):
            self.setCurrentTile(None)
        self.updateActions()

    def tilesetMoved(self, _from, to):
        self.mTilesets.insert(to, self.mTilesets.takeAt(_from))
        # Move the related tileset views
        widget = self.mViewStack.widget(_from)
        self.mViewStack.removeWidget(widget)
        self.mViewStack.insertWidget(to, widget)
        self.mViewStack.setCurrentIndex(self.mTabBar.currentIndex())
        # Update the titles of the affected tabs
        start = min(_from, to)
        end = max(_from, to)
        for i in range(start, end+1):
            tileset = self.mTilesets.at(i)
            if (self.mTabBar.tabText(i) != tileset.name()):
                self.mTabBar.setTabText(i, tileset.name())

    def tilesetNameChanged(self, tileset):
        index = indexOf(self.mTilesets, tileset)
        self.mTabBar.setTabText(index, tileset.name())

    def tileAnimationChanged(self, tile):
        view = self.currentTilesetView()
        if view:
            model = view.tilesetModel()
            if model:
                model.tileChanged(tile)

    ##
    # Removes the currently selected tileset.
    ##
    def removeTileset(self, *args):
        l = len(args)
        if l ==0:
            currentIndex = self.mViewStack.currentIndex()
            if (currentIndex != -1):
                self.removeTileset(self.mViewStack.currentIndex())
        elif l==1:
            ##
            # Removes the tileset at the given index. Prompting the user when the tileset
            # is in use by the map.
            ##
            index = args[0]
            tileset = self.mTilesets.at(index).data()
            inUse = self.mMapDocument.map().isTilesetUsed(tileset)
            # If the tileset is in use, warn the user and confirm removal
            if (inUse):
                warning = QMessageBox(QMessageBox.Warning,
                                    self.tr("Remove Tileset"),
                                    self.tr("The tileset \"%s\" is still in use by the map!"%tileset.name()),
                                    QMessageBox.Yes | QMessageBox.No, self)
                warning.setDefaultButton(QMessageBox.Yes)
                warning.setInformativeText(self.tr("Remove this tileset and all references "
                                              "to the tiles in this tileset?"))
                if (warning.exec() != QMessageBox.Yes):
                    return

            remove = RemoveTileset(self.mMapDocument, index, tileset)
            undoStack = self.mMapDocument.undoStack()
            if (inUse):
                # Remove references to tiles in this tileset from the current map
                def referencesTileset(cell):
                    tile = cell.tile
                    if tile:
                        return tile.tileset() == tileset
                    return False

                undoStack.beginMacro(remove.text())
                removeTileReferences(self.mMapDocument, referencesTileset)

            undoStack.push(remove)
            if (inUse):
                undoStack.endMacro()

    def moveTileset(self, _from, to):
        command = MoveTileset(self.mMapDocument, _from, to)
        self.mMapDocument.undoStack().push(command)

    def editTilesetProperties(self):
        tileset = self.currentTileset()
        if (not tileset):
            return
        self.mMapDocument.setCurrentObject(tileset)
        self.mMapDocument.emitEditCurrentObject()

    def importTileset(self):
        tileset = self.currentTileset()
        if (not tileset):
            return
        command = SetTilesetFileName(self.mMapDocument,
                                                       tileset, QString())
        self.mMapDocument.undoStack().push(command)

    def exportTileset(self):
        tileset = self.currentTileset()
        if (not tileset):
            return
        
        tsxFilter = self.tr("Tiled tileset files (*.tsx)")
        helper = FormatHelper(FileFormat.ReadWrite, tsxFilter)
    
        prefs = preferences.Preferences.instance()
        
        suggestedFileName = prefs.lastPath(preferences.Preferences.ExternalTileset)
        suggestedFileName += '/'
        suggestedFileName += tileset.name()
        
        extension = ".tsx"
        
        if (not suggestedFileName.endswith(extension)):
            suggestedFileName += extension
        
        selectedFilter = tsxFilter
        fileName, _ = QFileDialog.getSaveFileName(self, self.tr("Export Tileset"),
                                             suggestedFileName,
                                             helper.filter(), 
                                             selectedFilter)
        if fileName=='':
            return
        prefs.setLastPath(preferences.Preferences.ExternalTileset, QFileInfo(fileName).path())
        
        tsxFormat = TsxTilesetFormat()
        format = helper.formatByNameFilter(selectedFilter)
        if not format:
            format = tsxFormat
        
        if format.write(tileset, fileName):
            command = SetTilesetFileName(self.mMapDocument, tileset, fileName)
            self.mMapDocument.undoStack().push(command)
        else:
            error = format.errorString()
            QMessageBox.critical(self.window(),
                                  self.tr("Export Tileset"),
                                  self.tr("Error saving tileset: %s"%error))
                              
    def editTerrain(self):
        tileset = self.currentTileset()
        if (not tileset):
            return
        editTerrainDialog = EditTerrainDialog(self.mMapDocument, tileset, self)
        editTerrainDialog.exec()

    def addTiles(self):
        tileset = self.currentTileset()
        if (not tileset):
            return
        prefs = preferences.Preferences.instance()
        startLocation = QFileInfo(prefs.lastPath(preferences.Preferences.ImageFile)).absolutePath()
        filter = Utils.readableImageFormatsFilter()
        files = QFileDialog.getOpenFileNames(self.window(),
                                            self.tr("Add Tiles"),
                                            startLocation,
                                            filter)
        tiles = QList()
        id = tileset.tileCount()
        for file in files:
            image = QPixmap(file)
            if (not image.isNull()):
                tiles.append(Tile(image, file, id, tileset))
                id += 1
            else:
                warning = QMessageBox(QMessageBox.Warning,
                                    self.tr("Add Tiles"),
                                    self.tr("Could not load \"%s\"!"%file),
                                    QMessageBox.Ignore | QMessageBox.Cancel, self.window())
                warning.setDefaultButton(QMessageBox.Ignore)
                if (warning.exec() != QMessageBox.Ignore):
                    tiles.clear()
                    return

        if (tiles.isEmpty()):
            return
        prefs.setLastPath(preferences.Preferences.ImageFile, files.last())
        self.mMapDocument.undoStack().push(AddTiles(self.mMapDocument, tileset, tiles))

    def removeTiles(self):
        view = self.currentTilesetView()
        if (not view):
            return
        if (not view.selectionModel().hasSelection()):
            return
        indexes = view.selectionModel().selectedIndexes()
        model = view.tilesetModel()
        tileIds = RangeSet()
        tiles = QList()
        for index in indexes:
            tile = model.tileAt(index)
            if tile:
                tileIds.insert(tile.id())
                tiles.append(tile)

        def matchesAnyTile(cell):
            tile = cell.tile
            if tile:
                return tiles.contains(tile)
            return False

        inUse = self.hasTileReferences(self.mMapDocument, matchesAnyTile)
        # If the tileset is in use, warn the user and confirm removal
        if (inUse):
            warning = QMessageBox(QMessageBox.Warning,
                                self.tr("Remove Tiles"),
                                self.tr("One or more of the tiles to be removed are "
                                   "still in use by the map!"),
                                QMessageBox.Yes | QMessageBox.No, self)
            warning.setDefaultButton(QMessageBox.Yes)
            warning.setInformativeText(self.tr("Remove all references to these tiles?"))
            if (warning.exec() != QMessageBox.Yes):
                return

        undoStack = self.mMapDocument.undoStack()
        undoStack.beginMacro(self.tr("Remove Tiles"))
        removeTileReferences(self.mMapDocument, matchesAnyTile)
        # Iterate backwards over the ranges in order to keep the indexes valid
        firstRange = tileIds.begin()
        it = tileIds.end()
        if (it == firstRange): # no range
            return
        tileset = view.tilesetModel().tileset()
        while (it != firstRange):
            it -= 1
            undoStack.push(RemoveTiles(self.mMapDocument, tileset,
                                            it.first(), it.length()))

        undoStack.endMacro()
        # Clear the current tiles, will be referencing the removed tiles
        self.setCurrentTiles(None)
        self.setCurrentTile(None)

    def documentAboutToClose(self, mapDocument):
        self.mCurrentTilesets.remove(mapDocument)

    def refreshTilesetMenu(self):
        self.mTilesetMenu.clear()
        if (self.mTilesetMenuMapper):
            self.mTabBar.disconnect(self.mTilesetMenuMapper)
            del self.mTilesetMenuMapper

        self.mTilesetMenuMapper = QSignalMapper(self)
        self.mTilesetMenuMapper.mapped.connect(self.mTabBar.setCurrentIndex)
        currentIndex = self.mTabBar.currentIndex()
        for i in range(self.mTabBar.count()):
            action = QAction(self.mTabBar.tabText(i), self)
            action.setCheckable(True)
            self.mTilesetActionGroup.addAction(action)
            if (i == currentIndex):
                action.setChecked(True)
            self.mTilesetMenu.addAction(action)
            action.triggered.connect(self.mTilesetMenuMapper.map)
            self.mTilesetMenuMapper.setMapping(action, i)

    def setCurrentTile(self, tile):
        if (self.mCurrentTile == tile):
            return
        self.mCurrentTile = tile
        self.currentTileChanged.emit([tile])
        if (tile):
            self.mMapDocument.setCurrentObject(tile)

    def setCurrentTiles(self, tiles):
        if (self.mCurrentTiles == tiles):
            return
        del self.mCurrentTiles
        self.mCurrentTiles = tiles
        # Set the selected tiles on the map document
        if (tiles):
            selectedTiles = QList()
            for y in range(tiles.height()):
                for x in range(tiles.width()):
                    cell = tiles.cellAt(x, y)
                    if (not cell.isEmpty()):
                        selectedTiles.append(cell.tile)

            self.mMapDocument.setSelectedTiles(selectedTiles)
            
            # Create a tile stamp with these tiles
            map = self.mMapDocument.map()
            stamp = Map(map.orientation(),
                                 tiles.width(),
                                 tiles.height(),
                                 map.tileWidth(),
                                 map.tileHeight())
            stamp.addLayer(tiles.clone())
            stamp.addTilesets(tiles.usedTilesets())

            self.mEmittingStampCaptured = True
            self.stampCaptured.emit(TileStamp(stamp))
            self.mEmittingStampCaptured = False

    def retranslateUi(self):
        self.setWindowTitle(self.tr("Tilesets"))
        self.mNewTileset.setText(self.tr("New Tileset"))
        self.mImportTileset.setText(self.tr("Import Tileset"))
        self.mExportTileset.setText(self.tr("Export Tileset As..."))
        self.mPropertiesTileset.setText(self.tr("Tileset Properties"))
        self.mDeleteTileset.setText(self.tr("Remove Tileset"))
        self.mEditTerrain.setText(self.tr("Edit Terrain Information"))
        self.mAddTiles.setText(self.tr("Add Tiles"))
        self.mRemoveTiles.setText(self.tr("Remove Tiles"))

    def currentTileset(self):
        index = self.mTabBar.currentIndex()
        if (index == -1):
            return None
        return self.mTilesets.at(index)

    def currentTilesetView(self):
        return self.mViewStack.currentWidget()

    def tilesetViewAt(self, index):
        return self.mViewStack.widget(index)

    def setupTilesetModel(self, view, tileset):
        view.setModel(TilesetModel(tileset, view))

        s = view.selectionModel()
        s.selectionChanged.connect(self.selectionChanged)
        s.currentChanged.connect(self.currentChanged)
        view.pressed.connect(self.indexPressed)

##
# Used for exporting/importing tilesets.
#
# @warning Does not work for tilesets that are shared by multiple maps!
##
class SetTilesetFileName(QUndoCommand):

    def __init__(self, mapDocument, tileset, fileName):
        super().__init__()

        self.mMapDocument = mapDocument
        self.mTileset = tileset
        self.mFileName = fileName

        if (fileName.isEmpty()):
            self.setText(QCoreApplication.translate("Undo Commands", "Import Tileset"))
        else:
            self.setText(QCoreApplication.translate("Undo Commands", "Export Tileset"))

    def undo(self):
        self.swap()

    def redo(self):
        self.swap()

    def swap(self):
        previousFileName = self.mTileset.fileName()
        self.mMapDocument.setTilesetFileName(self.mTileset, self.mFileName)
        self.mFileName = previousFileName

class TilesetMenuButton(QToolButton):

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setArrowType(Qt.DownArrow)
        self.setIconSize(QSize(16, 16))
        self.setPopupMode(QToolButton.InstantPopup)
        self.setAutoRaise(True)
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(),
                      QSizePolicy.Ignored)

    def paintEvent(self, arg1):
        p = QStylePainter(self)
        opt = QStyleOptionToolButton()
        self.initStyleOption(opt)
        # Disable the menu arrow, since we already got a down arrow icon
        opt.features &= ~QStyleOptionToolButton.HasMenu
        p.drawComplexControl(QStyle.CC_ToolButton, opt)

def hasTileReferences(mapDocument, condition):
    for layer in mapDocument.map().layers():
        tileLayer = layer.asTileLayer()
        if tileLayer:
            if (tileLayer.hasCell(condition)):
                return True
        else:
            objectGroup = layer.asObjectGroup()
            if objectGroup:
                for object in objectGroup.objects():
                    if (condition(object.cell())):
                        return True

    return False

def removeTileReferences(mapDocument, condition):
    undoStack = mapDocument.undoStack()
    for layer in mapDocument.map().layers():
        tileLayer = layer.asTileLayer()
        if tileLayer:
            refs = tileLayer.region(condition)
            if (not refs.isEmpty()):
                undoStack.push(EraseTiles(mapDocument, tileLayer, refs))
        else:
            objectGroup = layer.asObjectGroup()
            if objectGroup:
                for object in objectGroup.objects():
                    if (condition(object.cell())):
                        undoStack.push(RemoveMapObject(mapDocument, object))
