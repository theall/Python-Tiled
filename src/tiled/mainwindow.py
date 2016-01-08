##
# mainwindow.py
# Copyright 2008-2015, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2008, Roderic Morris <roderic@ccs.neu.edu>
# Copyright 2009-2010, Jeff Bland <jeff@teamphobic.com>
# Copyright 2010-2011, Stefan Beller, stefanbeller@googlemail.com
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


import re, sys
from utils import Utils
from tilelayer import TileLayer
from mapdocument import MapDocument
from tilesetformat import readTileset
from macsupport import MacSupport
from magicwandtool import MagicWandTool
from imagemovementtool import ImageMovementTool
from tilecollisioneditor import TileCollisionEditor
from tileanimationeditor import TileAnimationEditor
from consoledock import ConsoleDock
from minimapdock import MiniMapDock
from objectsdock import ObjectsDock
from commandbutton import CommandButton
from libtiled.tiled import FlipDirection, RotateDirection
from selectsametiletool import SelectSameTileTool
from undodock import UndoDock
from mapformat import FileFormat, FormatHelper
from toolmanager import ToolManager
from terraindock import TerrainDock
from tilesetmanager import TilesetManager
from tilesetdock import TilesetDock
from tileselectiontool import TileSelectionTool
from terrainbrush import TerrainBrush
from tmxmapformat import TsxTilesetFormat
from stampbrush import StampBrush
from propertiesdock import PropertiesDock
from preferencesdialog import PreferencesDialog
from preferences import Preferences, ObjectLabelVisiblity
from tmxmapformat import TmxMapFormat
from patreondialog import PatreonDialog
from offsetmapdialog import OffsetMapDialog
from objectselectiontool import ObjectSelectionTool
from resizedialog import ResizeDialog
from pluginmanager import PluginManager
from newtilesetdialog import NewTilesetDialog
from newmapdialog import NewMapDialog
from mapsdock import MapsDock
from mapdocumentactionhandler import MapDocumentActionHandler
from layerdock import LayerDock
from languagemanager import LanguageManager
from bucketfilltool import BucketFillTool
from exportasimagedialog import ExportAsImageDialog
from erasetiles import EraseTiles
from tilestamp import TileStamp
from eraser import Eraser
from tilestampsdock import TileStampsDock
from editpolygontool import EditPolygonTool
from documentmanager import DocumentManager
from createpolylineobjecttool import CreatePolylineObjectTool
from createpolygonobjecttool import CreatePolygonObjectTool
from createtileobjecttool import CreateTileObjectTool
from createellipseobjecttool import CreateEllipseObjectTool
from createrectangleobjecttool import CreateRectangleObjectTool
from clipboardmanager import ClipboardManager
from addremovetileset import AddTileset
from automappingmanager import AutomappingManager
from tilestampmanager import TileStampManager
from addremovemapobject import RemoveMapObject
from aboutdialog import AboutDialog
from Ui_mainwindow import Ui_MainWindow
from pyqtcore import QList, QString, QVector, QStringList
from PyQt5.QtCore import (
    Qt,
    QUrl, 
    QFile, 
    QEvent,
    QFileInfo,
    QSignalMapper,
    QByteArray,
    QSettings
)
from PyQt5.QtGui import (
    QIcon,
    QRegion,
    QKeySequence, 
    QDesktopServices
)
from PyQt5.QtWidgets import (
    QMenu,
    QLabel,
    QAction,
    QActionGroup, 
    QToolButton,
    QShortcut,
    QMessageBox,
    QFileDialog,
    QComboBox,
    QMainWindow
)

MaxRecentFiles = 8
QT_VERSION = 0x050401

##
# The main editor window.
#
# Represents the main user interface, including the menu bar. It keeps track
# of the current file and is also the entry point of all menu actions.
##
class MainWindow(QMainWindow):

    def __init__(self, parent = None):
        super().__init__(parent)

        self.mRecentFiles = []
        for i in range(MaxRecentFiles):
            self.mRecentFiles.append('')
        self.mSettings = QSettings()
        self.mUi = Ui_MainWindow()
        self.mMapDocument = None
        self.mActionHandler = MapDocumentActionHandler(self)
        self.mLayerDock = LayerDock(self)
        self.mMapsDock = MapsDock(self)
        self.mObjectsDock = ObjectsDock()
        self.mTilesetDock = TilesetDock(self)
        self.mTerrainDock = TerrainDock(self)
        self.mMiniMapDock = MiniMapDock(self)
        self.mConsoleDock = ConsoleDock(self)
        self.mTileAnimationEditor = TileAnimationEditor(self)
        self.mTileCollisionEditor = TileCollisionEditor(self)
        self.mCurrentLayerLabel = QLabel()
        self.mZoomable = None
        self.mZoomComboBox = QComboBox()
        self.mStatusInfoLabel = QLabel()
        self.mAutomappingManager = AutomappingManager(self)
        self.mDocumentManager = DocumentManager.instance()
        self.mToolManager = ToolManager(self)
        self.mTileStampManager = TileStampManager(self.mToolManager, self)
        
        self.mUi.setupUi(self)
        self.setCentralWidget(self.mDocumentManager.widget())
        if sys.platform=='darwin':
            MacSupport.addFullscreen(self)
        prefs = Preferences.instance()
        redoIcon = QIcon(":images/16x16/edit-redo.png")
        undoIcon = QIcon(":images/16x16/edit-undo.png")
        if sys.platform=='darwin':
            tiledIcon = QIcon(":images/16x16/tiled.png")
            tiledIcon.addFile(":images/32x32/tiled.png")
            self.setWindowIcon(tiledIcon)

        # Add larger icon versions for actions used in the tool bar
        newIcon = self.mUi.actionNew.icon()
        openIcon = self.mUi.actionOpen.icon()
        saveIcon = self.mUi.actionSave.icon()
        newIcon.addFile(":images/24x24/document-new.png")
        openIcon.addFile(":images/24x24/document-open.png")
        saveIcon.addFile(":images/24x24/document-save.png")
        redoIcon.addFile(":images/24x24/edit-redo.png")
        undoIcon.addFile(":images/24x24/edit-undo.png")
        self.mUi.actionNew.setIcon(newIcon)
        self.mUi.actionOpen.setIcon(openIcon)
        self.mUi.actionSave.setIcon(saveIcon)
        undoGroup = self.mDocumentManager.undoGroup()
        undoAction = undoGroup.createUndoAction(self, self.tr("Undo"))
        redoAction = undoGroup.createRedoAction(self, self.tr("Redo"))
        self.mUi.mainToolBar.setToolButtonStyle(Qt.ToolButtonFollowStyle)
        self.mUi.actionNew.setPriority(QAction.LowPriority)
        if QT_VERSION >= 0x050500:
            undoAction.setPriority(QAction.LowPriority)
        redoAction.setPriority(QAction.LowPriority)
        redoAction.setIcon(redoIcon)
        undoAction.setIcon(undoIcon)
        redoAction.setIconText(self.tr("Redo"))
        undoAction.setIconText(self.tr("Undo"))
        undoGroup.cleanChanged.connect(self.updateWindowTitle)
        undoDock = UndoDock(undoGroup, self)
        propertiesDock = PropertiesDock(self)
        tileStampsDock = TileStampsDock(self.mTileStampManager, self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.mLayerDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, propertiesDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, undoDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.mMapsDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.mObjectsDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.mMiniMapDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.mTerrainDock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.mTilesetDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.mConsoleDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, tileStampsDock)
        self.tabifyDockWidget(self.mMiniMapDock, self.mObjectsDock)
        self.tabifyDockWidget(self.mObjectsDock, self.mLayerDock)
        self.tabifyDockWidget(self.mTerrainDock, self.mTilesetDock)
        self.tabifyDockWidget(undoDock, self.mMapsDock)
        self.tabifyDockWidget(tileStampsDock, undoDock)
        
        # These dock widgets may not be immediately useful to many people, so
        # they are hidden by default.
        undoDock.setVisible(False)
        self.mMapsDock.setVisible(False)
        self.mConsoleDock.setVisible(False)
        tileStampsDock.setVisible(False)
        
        self.statusBar().addPermanentWidget(self.mZoomComboBox)
        self.mUi.actionNew.setShortcuts(QKeySequence.New)
        self.mUi.actionOpen.setShortcuts(QKeySequence.Open)
        self.mUi.actionSave.setShortcuts(QKeySequence.Save)
        self.mUi.actionSaveAs.setShortcuts(QKeySequence.SaveAs)
        self.mUi.actionClose.setShortcuts(QKeySequence.Close)
        self.mUi.actionQuit.setShortcuts(QKeySequence.Quit)
        self.mUi.actionCut.setShortcuts(QKeySequence.Cut)
        self.mUi.actionCopy.setShortcuts(QKeySequence.Copy)
        self.mUi.actionPaste.setShortcuts(QKeySequence.Paste)
        
        deleteKeys = QKeySequence.keyBindings(QKeySequence.Delete)
        if sys.platform == 'darwin':
            # Add the Backspace key as primary shortcut for Delete, which seems to be
            # the expected one for OS X.
            if not deleteKeys.contains(QKeySequence(Qt.Key_Backspace)):
                deleteKeys.prepend(QKeySequence(Qt.Key_Backspace))
        
        self.mUi.actionDelete.setShortcuts(deleteKeys)
        
        undoAction.setShortcuts(QKeySequence.Undo)
        redoAction.setShortcuts(QKeySequence.Redo)
        self.mUi.actionShowGrid.setChecked(prefs.showGrid())
        self.mUi.actionShowTileObjectOutlines.setChecked(prefs.showTileObjectOutlines())
        self.mUi.actionShowTileAnimations.setChecked(prefs.showTileAnimations())
        self.mUi.actionSnapToGrid.setChecked(prefs.snapToGrid())
        self.mUi.actionSnapToFineGrid.setChecked(prefs.snapToFineGrid())
        self.mUi.actionHighlightCurrentLayer.setChecked(prefs.highlightCurrentLayer())
        
        objectLabelVisibilityGroup = QActionGroup(self)
        self.mUi.actionNoLabels.setActionGroup(objectLabelVisibilityGroup)
        self.mUi.actionLabelsForSelectedObjects.setActionGroup(objectLabelVisibilityGroup)
        self.mUi.actionLabelsForAllObjects.setActionGroup(objectLabelVisibilityGroup)

        x = prefs.objectLabelVisibility()
        if x == ObjectLabelVisiblity.NoObjectLabels:
            self.mUi.actionNoLabels.setChecked(True)
        elif x == ObjectLabelVisiblity.SelectedObjectLabels:
            self.mUi.actionLabelsForSelectedObjects.setChecked(True)
        elif x == ObjectLabelVisiblity.AllObjectLabels:
            self.mUi.actionLabelsForAllObjects.setChecked(True)

        objectLabelVisibilityGroup.triggered.connect(self.labelVisibilityActionTriggered)
                
        reloadTilesetsShortcut = QShortcut(QKeySequence(self.tr("Ctrl+T")), self)
        reloadTilesetsShortcut.activated.connect(self.reloadTilesets)
        # Make sure Ctrl+= also works for zooming in
        keys = QKeySequence.keyBindings(QKeySequence.ZoomIn)
        keys += QKeySequence(self.tr("Ctrl+="))
        keys += QKeySequence(self.tr("+"))
        self.mUi.actionZoomIn.setShortcuts(keys)
        keys = QKeySequence.keyBindings(QKeySequence.ZoomOut)
        keys += QKeySequence(self.tr("-"))
        self.mUi.actionZoomOut.setShortcuts(keys)
        self.mUi.menuEdit.insertAction(self.mUi.actionCut, undoAction)
        self.mUi.menuEdit.insertAction(self.mUi.actionCut, redoAction)
        self.mUi.menuEdit.insertSeparator(self.mUi.actionCut)
        self.mUi.menuEdit.insertAction(self.mUi.actionPreferences, self.mActionHandler.actionSelectAll())
        self.mUi.menuEdit.insertAction(self.mUi.actionPreferences, self.mActionHandler.actionSelectNone())
        self.mUi.menuEdit.insertSeparator(self.mUi.actionPreferences)
        self.mUi.mainToolBar.addAction(undoAction)
        self.mUi.mainToolBar.addAction(redoAction)
        self.mUi.mainToolBar.addSeparator()
        self.mCommandButton = CommandButton(self)
        self.mUi.mainToolBar.addWidget(self.mCommandButton)
        self.mUi.menuMap.insertAction(self.mUi.actionOffsetMap, self.mActionHandler.actionCropToSelection())
        self.mRandomButton = QToolButton(self)
        self.mRandomButton.setToolTip(self.tr("Random Mode"))
        self.mRandomButton.setIcon(QIcon(":images/24x24/dice.png"))
        self.mRandomButton.setCheckable(True)
        self.mRandomButton.setShortcut(QKeySequence(self.tr("D")))
        self.mUi.mainToolBar.addWidget(self.mRandomButton)
        self.mLayerMenu = QMenu(self.tr("Layer"), self)
        self.mLayerMenu.addAction(self.mActionHandler.actionAddTileLayer())
        self.mLayerMenu.addAction(self.mActionHandler.actionAddObjectGroup())
        self.mLayerMenu.addAction(self.mActionHandler.actionAddImageLayer())
        self.mLayerMenu.addAction(self.mActionHandler.actionDuplicateLayer())
        self.mLayerMenu.addAction(self.mActionHandler.actionMergeLayerDown())
        self.mLayerMenu.addAction(self.mActionHandler.actionRemoveLayer())
        self.mLayerMenu.addSeparator()
        self.mLayerMenu.addAction(self.mActionHandler.actionSelectPreviousLayer())
        self.mLayerMenu.addAction(self.mActionHandler.actionSelectNextLayer())
        self.mLayerMenu.addAction(self.mActionHandler.actionMoveLayerUp())
        self.mLayerMenu.addAction(self.mActionHandler.actionMoveLayerDown())
        self.mLayerMenu.addSeparator()
        self.mLayerMenu.addAction(self.mActionHandler.actionToggleOtherLayers())
        self.mLayerMenu.addSeparator()
        self.mLayerMenu.addAction(self.mActionHandler.actionLayerProperties())
        self.menuBar().insertMenu(self.mUi.menuHelp.menuAction(), self.mLayerMenu)
        self.mUi.actionNew.triggered.connect(self.newMap)
        self.mUi.actionOpen.triggered.connect(self.openFile)
        self.mUi.actionClearRecentFiles.triggered.connect(self.clearRecentFiles)
        self.mUi.actionSave.triggered.connect(self.saveFile)
        self.mUi.actionSaveAs.triggered.connect(self.saveFileAs)
        self.mUi.actionSaveAll.triggered.connect(self.saveAll)
        self.mUi.actionExportAsImage.triggered.connect(self.exportAsImage)
        self.mUi.actionExport.triggered.connect(self.export_)
        self.mUi.actionExportAs.triggered.connect(self.exportAs)
        self.mUi.actionReload.triggered.connect(self.reload)
        self.mUi.actionClose.triggered.connect(self.closeFile)
        self.mUi.actionCloseAll.triggered.connect(self.closeAllFiles)
        self.mUi.actionQuit.triggered.connect(self.close)
        self.mUi.actionCut.triggered.connect(self.cut)
        self.mUi.actionCopy.triggered.connect(self.copy)
        self.mUi.actionPaste.triggered.connect(self.paste)
        self.mUi.actionDelete.triggered.connect(self.delete_)
        self.mUi.actionPreferences.triggered.connect(self.openPreferences)
        self.mUi.actionShowGrid.toggled.connect(prefs.setShowGrid)
        self.mUi.actionShowTileObjectOutlines.toggled.connect(prefs.setShowTileObjectOutlines)
        self.mUi.actionShowTileAnimations.toggled.connect(prefs.setShowTileAnimations)
        self.mUi.actionSnapToGrid.toggled.connect(prefs.setSnapToGrid)
        self.mUi.actionSnapToFineGrid.toggled.connect(prefs.setSnapToFineGrid)
        self.mUi.actionHighlightCurrentLayer.toggled.connect(prefs.setHighlightCurrentLayer)
        self.mUi.actionZoomIn.triggered.connect(self.zoomIn)
        self.mUi.actionZoomOut.triggered.connect(self.zoomOut)
        self.mUi.actionZoomNormal.triggered.connect(self.zoomNormal)
        self.mUi.actionNewTileset.triggered.connect(self.newTileset)
        self.mUi.actionAddExternalTileset.triggered.connect(self.addExternalTileset)
        self.mUi.actionResizeMap.triggered.connect(self.resizeMap)
        self.mUi.actionOffsetMap.triggered.connect(self.offsetMap)
        self.mUi.actionMapProperties.triggered.connect(self.editMapProperties)
        self.mUi.actionAutoMap.triggered.connect(self.mAutomappingManager.autoMap)
        self.mUi.actionDocumentation.triggered.connect(self.openDocumentation)
        self.mUi.actionBecomePatron.triggered.connect(self.becomePatron)
        self.mUi.actionAbout.triggered.connect(self.aboutTiled)
        self.mTilesetDock.tilesetsDropped.connect(self.newTilesets)
        # Add recent file actions to the recent files menu
        for i in range(MaxRecentFiles):
            self.mRecentFiles[i] = QAction(self)
            self.mUi.menuRecentFiles.insertAction(self.mUi.actionClearRecentFiles, self.mRecentFiles[i])
            self.mRecentFiles[i].setVisible(False)
            self.mRecentFiles[i].triggered.connect(self.openRecentFile)

        self.mUi.menuRecentFiles.insertSeparator(self.mUi.actionClearRecentFiles)
        Utils.setThemeIcon(self.mUi.actionNew, "document-new")
        Utils.setThemeIcon(self.mUi.actionOpen, "document-open")
        Utils.setThemeIcon(self.mUi.menuRecentFiles, "document-open-recent")
        Utils.setThemeIcon(self.mUi.actionClearRecentFiles, "edit-clear")
        Utils.setThemeIcon(self.mUi.actionSave, "document-save")
        Utils.setThemeIcon(self.mUi.actionSaveAs, "document-save-as")
        Utils.setThemeIcon(self.mUi.actionClose, "window-close")
        Utils.setThemeIcon(self.mUi.actionQuit, "application-exit")
        Utils.setThemeIcon(self.mUi.actionCut, "edit-cut")
        Utils.setThemeIcon(self.mUi.actionCopy, "edit-copy")
        Utils.setThemeIcon(self.mUi.actionPaste, "edit-paste")
        Utils.setThemeIcon(self.mUi.actionDelete, "edit-delete")
        Utils.setThemeIcon(redoAction, "edit-redo")
        Utils.setThemeIcon(undoAction, "edit-undo")
        Utils.setThemeIcon(self.mUi.actionZoomIn, "zoom-in")
        Utils.setThemeIcon(self.mUi.actionZoomOut, "zoom-out")
        Utils.setThemeIcon(self.mUi.actionZoomNormal, "zoom-original")
        Utils.setThemeIcon(self.mUi.actionNewTileset, "document-new")
        Utils.setThemeIcon(self.mUi.actionResizeMap, "document-page-setup")
        Utils.setThemeIcon(self.mUi.actionMapProperties, "document-properties")
        Utils.setThemeIcon(self.mUi.actionDocumentation, "help-contents")
        Utils.setThemeIcon(self.mUi.actionAbout, "help-about")
        self.mStampBrush = StampBrush(self)
        self.mTerrainBrush = TerrainBrush(self)
        self.mBucketFillTool = BucketFillTool(self)
        tileObjectsTool = CreateTileObjectTool(self)
        rectangleObjectsTool = CreateRectangleObjectTool(self)
        ellipseObjectsTool = CreateEllipseObjectTool(self)
        polygonObjectsTool = CreatePolygonObjectTool(self)
        polylineObjectsTool = CreatePolylineObjectTool(self)
        self.mTilesetDock.stampCaptured.connect(self.setStamp)
        self.mStampBrush.stampCaptured.connect(self.setStamp)
        self.mTilesetDock.currentTileChanged.connect(tileObjectsTool.setTile)
        self.mTilesetDock.currentTileChanged.connect(self.mTileAnimationEditor.setTile)
        self.mTilesetDock.currentTileChanged.connect(self.mTileCollisionEditor.setTile)
        self.mTilesetDock.newTileset.connect(self.newTileset)
        self.mTerrainDock.currentTerrainChanged.connect(self.setTerrainBrush)
        tileStampsDock.setStamp.connect(self.setStamp)
        
        self.mRandomButton.toggled.connect(self.mStampBrush.setRandom)
        self.mRandomButton.toggled.connect(self.mBucketFillTool.setRandom)
        toolBar = self.mUi.toolsToolBar
        toolBar.addAction(self.mToolManager.registerTool(self.mStampBrush))
        toolBar.addAction(self.mToolManager.registerTool(self.mTerrainBrush))
        toolBar.addAction(self.mToolManager.registerTool(self.mBucketFillTool))
        toolBar.addAction(self.mToolManager.registerTool(Eraser(self)))
        toolBar.addAction(self.mToolManager.registerTool(TileSelectionTool(self)))
        toolBar.addAction(self.mToolManager.registerTool(MagicWandTool(self)))
        toolBar.addAction(self.mToolManager.registerTool(SelectSameTileTool(self)))
        toolBar.addSeparator()
        toolBar.addAction(self.mToolManager.registerTool(ObjectSelectionTool(self)))
        toolBar.addAction(self.mToolManager.registerTool(EditPolygonTool(self)))
        toolBar.addAction(self.mToolManager.registerTool(rectangleObjectsTool))
        toolBar.addAction(self.mToolManager.registerTool(ellipseObjectsTool))
        toolBar.addAction(self.mToolManager.registerTool(polygonObjectsTool))
        toolBar.addAction(self.mToolManager.registerTool(polylineObjectsTool))
        toolBar.addAction(self.mToolManager.registerTool(tileObjectsTool))
        toolBar.addSeparator()
        toolBar.addAction(self.mToolManager.registerTool(ImageMovementTool(self)))
        self.mDocumentManager.setSelectedTool(self.mToolManager.selectedTool())
        self.mToolManager.selectedToolChanged.connect(self.mDocumentManager.setSelectedTool)
        self.statusBar().addWidget(self.mStatusInfoLabel)
        self.mToolManager.statusInfoChanged.connect(self.updateStatusInfoLabel)
        self.statusBar().addWidget(self.mCurrentLayerLabel)
        # Add the 'Views and Toolbars' submenu. This needs to happen after all
        # the dock widgets and toolbars have been added to the main window.
        self.mViewsAndToolbarsMenu = QAction(self.tr("Views and Toolbars"), self)
        self.mShowTileAnimationEditor = QAction(self.tr("Tile Animation Editor"), self)
        self.mShowTileAnimationEditor.setCheckable(True)
        self.mShowTileCollisionEditor = QAction(self.tr("Tile Collision Editor"), self)
        self.mShowTileCollisionEditor.setCheckable(True)
        self.mShowTileCollisionEditor.setShortcut(self.tr("Ctrl+Shift+O"))
        self.mShowTileCollisionEditor.setShortcutContext(Qt.ApplicationShortcut)
        popupMenu = self.createPopupMenu()
        popupMenu.setParent(self)
        self.mViewsAndToolbarsMenu.setMenu(popupMenu)
        self.mUi.menuView.insertAction(self.mUi.actionShowGrid, self.mViewsAndToolbarsMenu)
        self.mUi.menuView.insertAction(self.mUi.actionShowGrid, self.mShowTileAnimationEditor)
        self.mUi.menuView.insertAction(self.mUi.actionShowGrid, self.mShowTileCollisionEditor)
        self.mUi.menuView.insertSeparator(self.mUi.actionShowGrid)
        self.mShowTileAnimationEditor.toggled.connect(self.mTileAnimationEditor.setVisible)
        self.mTileAnimationEditor.closed.connect(self.onAnimationEditorClosed)
        self.mShowTileCollisionEditor.toggled.connect(self.mTileCollisionEditor.setVisible)
        self.mTileCollisionEditor.closed.connect(self.onCollisionEditorClosed)
        ClipboardManager.instance().hasMapChanged.connect(self.updateActions)
        self.mDocumentManager.currentDocumentChanged.connect(self.mapDocumentChanged)
        self.mDocumentManager.documentCloseRequested.connect(self.closeMapDocument)
        self.mDocumentManager.reloadError.connect(self.reloadError)
        switchToLeftDocument = QShortcut(self.tr("Alt+Left"), self)
        switchToLeftDocument.activated.connect(self.mDocumentManager.switchToLeftDocument)
        switchToLeftDocument1 = QShortcut(self.tr("Ctrl+Shift+Tab"), self)
        switchToLeftDocument1.activated.connect(self.mDocumentManager.switchToLeftDocument)
        switchToRightDocument = QShortcut(self.tr("Alt+Right"), self)
        switchToRightDocument.activated.connect(self.mDocumentManager.switchToRightDocument)
        switchToRightDocument1 = QShortcut(self.tr("Ctrl+Tab"), self)
        switchToRightDocument1.activated.connect(self.mDocumentManager.switchToRightDocument)
        QShortcut(self.tr("X"), self, self.flipHorizontally)
        QShortcut(self.tr("Y"), self, self.flipVertically)
        QShortcut(self.tr("Z"), self, self.rotateRight)
        QShortcut(self.tr("Shift+Z"), self, self.rotateLeft)
        copyPositionShortcut = QShortcut(self.tr("Alt+C"), self)
        copyPositionShortcut.activated.connect(self.mActionHandler.copyPosition)

        self.updateActions()
        self.readSettings()
        self.setupQuickStamps()
        self.mAutomappingManager.warningsOccurred.connect(self.autoMappingWarning)
        self.mAutomappingManager.errorsOccurred.connect(self.autoMappingError)

    def __del__(self):
        TilesetManager.deleteInstance()
        DocumentManager.deleteInstance()
        Preferences.deleteInstance()
        LanguageManager.deleteInstance()
        PluginManager.deleteInstance()
        ClipboardManager.deleteInstance()
        self.mStampBrush = None
        self.mBucketFillTool = None

    def commitData(self, manager):
        # Play nice with session management and cancel shutdown process when user
        # requests this
        if (manager.allowsInteraction()):
            if (not self.confirmAllSave()):
                manager.cancel()

    ##
    # Opens the given file. When opened succesfully, the file is added to the
    # list of recent files.
    #
    # When a \a format is given, it is used to open the file. Otherwise, a
    # format is searched using Mapformat.supportsFile.
    #
    # @return whether the file was succesfully opened
    ##
    def openFile(self, *args):
        l = len(args)
        if l==2:
            fileName, format = args
            if len(fileName)==0:
                return False
            # Select existing document if this file is already open
            documentIndex = self.mDocumentManager.findDocument(fileName)
            if (documentIndex != -1):
                self.mDocumentManager.switchToDocument(documentIndex)
                return True

            mapDocument, error = MapDocument.load(fileName, format)
            if (not mapDocument):
                QMessageBox.critical(self, self.tr("Error Opening Map"), error)
                return False

            self.mDocumentManager.addDocument(mapDocument)
            self.setRecentFile(fileName)
            return True
        elif l==1:
            fileName = args[0]
            tp = type(fileName)
            if tp==bool:
                return self.openFile()
            elif tp==QString or tp==str:
                return self.openFile(fileName, None)
        elif l==0:
            filter = self.tr("All Files (*)")
            selectedFilter = TmxMapFormat().nameFilter()
            filter += ";;"
            filter += selectedFilter
            helper = FormatHelper(FileFormat.Read, filter)
            selectedFilter = self.mSettings.value("lastUsedOpenFilter", selectedFilter)
            

            fileNames, _ = QFileDialog.getOpenFileNames(self, self.tr("Open Map"),
                                                            self.fileDialogStartLocation(),
                                                            helper.filter(), selectedFilter)
            if len(fileNames)<=0:
                return
            # When a particular filter was selected, use the associated reader
            mapFormat = helper.formatByNameFilter(selectedFilter)

            self.mSettings.setValue("lastUsedOpenFilter", selectedFilter)
            for fileName in fileNames:
                self.openFile(fileName, mapFormat)

    ##
    # Attempt to open the previously opened file.
    ##
    def openLastFiles(self):
        self.mSettings.beginGroup("recentFiles")
        lastOpenFiles = self.mSettings.value("lastOpenFiles")
        if lastOpenFiles is None:
            lastOpenFiles = []
        openCountVariant = self.mSettings.value("recentOpenedFiles")
        # Backwards compatibility mode
        if openCountVariant:
            recentFiles = self.mSettings.value(
                        "fileNames")
            openCount = min(openCountVariant, recentFiles.size())
            while(openCount>0):
                lastOpenFiles.append(recentFiles.at(openCount - 1))
                openCount -= 1
            self.mSettings.remove("recentOpenedFiles")

        mapScales = self.mSettings.value("mapScale")
        scrollX = self.mSettings.value("scrollX")
        scrollY = self.mSettings.value("scrollY")
        selectedLayer = self.mSettings.value("selectedLayer")
        for i in range(len(lastOpenFiles)):
            if not (i < len(mapScales)):
                continue
            if (not (i < len(scrollX))):
                continue
            if (not (i < len(scrollY))):
                continue
            if (not (i < len(selectedLayer))):
                continue
            if (self.openFile(lastOpenFiles[i])):
                mapView = self.mDocumentManager.currentMapView()
                # Restore camera to the previous position
                scale = float(mapScales[i])
                if (scale > 0):
                    mapView.zoomable().setScale(scale)
                hor = int(scrollX[i])
                ver = int(scrollY[i])
                mapView.horizontalScrollBar().setSliderPosition(hor)
                mapView.verticalScrollBar().setSliderPosition(ver)
                layer = int(selectedLayer[i])
                if (layer > 0 and layer < self.mMapDocument.map().layerCount()):
                    self.mMapDocument.setCurrentLayerIndex(layer)

        lastActiveDocument = self.mSettings.value("lastActive")
        documentIndex = self.mDocumentManager.findDocument(lastActiveDocument)
        if (documentIndex != -1):
            self.mDocumentManager.switchToDocument(documentIndex)
        self.mSettings.endGroup()

    def closeEvent(self, event):
        self.writeSettings()
        if (self.confirmAllSave()):
            self.mDocumentManager.closeAllDocuments()
            # This needs to happen before deleting the TilesetManager otherwise it may
            # hold references to tilesets.
            self.mTileAnimationEditor.setTile(0)
            self.mTileAnimationEditor.writeSettings()
            self.mTileCollisionEditor.setTile(0)
            self.mTileCollisionEditor.writeSettings()
            event.accept()
        else:
            event.ignore()

    def changeEvent(self, event):
        super().changeEvent(event)
        x = event.type()
        if x==QEvent.LanguageChange:
            self.mUi.retranslateUi(self)
            self.retranslateUi()
        else:
            pass

    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Space and not event.isAutoRepeat()):
            mapView = self.mDocumentManager.currentMapView()
            if mapView:
                mapView.setHandScrolling(True)

    def keyReleaseEvent(self, event):
        if (event.key() == Qt.Key_Space and not event.isAutoRepeat()):
            mapView = self.mDocumentManager.currentMapView()
            if mapView:
                mapView.setHandScrolling(False)

    def dragEnterEvent(self, e):
        urls = e.mimeData().urls()
        if len(urls)>0 and urls[0].toLocalFile() != '':
            e.accept()

    def dropEvent(self, e):
        for url in e.mimeData().urls():
            self.openFile(url.toLocalFile())

    def newMap(self):
        newMapDialog = NewMapDialog(self)
        mapDocument = newMapDialog.createMap()
        if (not mapDocument):
            return
        self.mDocumentManager.addDocument(mapDocument)

    def saveFileAs(self):
        tmxFilter = TmxMapFormat().nameFilter()

        helper = FormatHelper(FileFormat.ReadWrite, tmxFilter)

        selectedFilter = ''
        if (self.mMapDocument):
            format = self.mMapDocument.writerFormat()
            if format:
                selectedFilter = format.nameFilter()
        if selectedFilter == '':
            selectedFilter = tmxFilter
        suggestedFileName = QString()
        if (self.mMapDocument and self.mMapDocument.fileName()!=''):
            suggestedFileName = self.mMapDocument.fileName()
        else:
            suggestedFileName = self.fileDialogStartLocation()
            suggestedFileName += '/'
            suggestedFileName += self.tr("untitled.tmx")

        fileName, _ = QFileDialog.getSaveFileName(self, '', suggestedFileName, helper.filter(), selectedFilter)
        if fileName == '':
            return False
        
        format = helper.formatByNameFilter(selectedFilter)
        self.mMapDocument.setWriterFormat(format)
    
        return self.saveFile(fileName)

    def saveAll(self):
        for mapDoc in self.mDocumentManager.documents():
            if not mapDoc.isModified():
                continue

            fileName = mapDoc.fileName()
            error = ''

            if fileName == '':
                self.mDocumentManager.switchToDocument(mapDoc)
                if not self.saveFileAs():
                    return
            else:
                ok, error = mapDoc.save(fileName)
                if not ok:
                    self.mDocumentManager.switchToDocument(mapDoc)
                    QMessageBox.critical(self, self.tr("Error Saving Map"), error)
                return

            self.setRecentFile(fileName)

    # 'export' is a reserved word
    def export_(self):
        if (not self.mMapDocument):
            return
        exportFileName = self.mMapDocument.lastExportFileName()

        if exportFileName != '':
            exportFormat = self.mMapDocument.exportFormat()
            tmxFormat = TmxMapFormat()

            if not exportFormat:
                exportFormat = tmxFormat
                
            if exportFormat.write(self.mMapDocument.map(), exportFileName):
                self.statusBar().showMessage(self.tr("Exported to %s"%exportFileName), 3000)
                return

            QMessageBox.critical(self, self.tr("Error Exporting Map"), exportFormat.errorString())

        # fall back when no succesful export happened
        self.exportAs()

    def exportAs(self):
        if (not self.mMapDocument):
            return
        
        helper = FormatHelper(FileFormat.Write, self.tr("All Files (*)"))

        prefs = Preferences.instance()
        selectedFilter = self.mSettings.value("lastUsedExportFilter", '')
        suggestedFilename = self.mMapDocument.lastExportFileName()
        if suggestedFilename == '':
            baseNameInfo = QFileInfo(self.mMapDocument.fileName())
            baseName = baseNameInfo.baseName()
            extensionFinder = re.search("\(\*\.([^\)\s]*)", selectedFilter)
            if extensionFinder:
                extension = extensionFinder.group(1)
            else:
                extension = ''
            lastExportedFilePath = prefs.lastPath(Preferences.ExportedFile)
            suggestedFilename = lastExportedFilePath + "/" + baseName
            if extension != '':
                suggestedFilename += '.' + extension

        # No need to confirm overwrite here since it'll be prompted below
        fileName, selectedFilter = QFileDialog.getSaveFileName(self, self.tr("Export As..."),
                                                        suggestedFilename,
                                                        helper.filter(), selectedFilter, QFileDialog.DontConfirmOverwrite)
        if fileName == '':
            return

        # If a specific filter was selected, use that writer
        chosenFormat = helper.formatByNameFilter(selectedFilter)
        
        # If not, try to find the file extension among the name filters
        suffix = QFileInfo(fileName).completeSuffix()
        if (not chosenFormat and suffix!=''):
            suffix = "*." + suffix
            for format in helper.formats():
                if suffix.lower() in format.nameFilter().lower():
                    if chosenFormat:
                        QMessageBox.warning(self, self.tr("Non-unique file extension"),
                                             self.tr("Non-unique file extension.\n"
                                                "Please select specific format."))
                        return self.exportAs()
                    else:
                        chosenFormat = format

        # Also support exporting to the TMX map format when requested
        tmxMapFormat = TmxMapFormat()
        if (not chosenFormat and tmxMapFormat.supportsFile(fileName)):
            chosenFormat = tmxMapFormat
        if (not chosenFormat):
            QMessageBox.critical(self, self.tr("Unknown File Format"),
                                  self.tr("The given filename does not have any known "
                                     "file extension."))
            return
        
        # Check if writer will overwrite existing files here because some writers
        # could save to multiple files at the same time. For example CSV saves
        # each layer into a separate file.
        outputFiles = chosenFormat.outputFiles(self.mMapDocument.map(), fileName)
        if len(outputFiles) > 0:
            # Check if any output file already exists
            message = self.tr("Some export files already exist:") + "\n\n"

            overwriteHappens = False

            for outputFile in outputFiles:
                if (QFile.exists(outputFile)):
                    overwriteHappens = True
                    message += outputFile + '\n'

            message += '\n' + self.tr("Do you want to replace them?")

            # If overwrite happens, warn the user and get confirmation before exporting
            if (overwriteHappens):
                reply = QMessageBox.warning(
                    self,
                    self.tr("Overwrite Files"),
                    message,
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No)

                if reply != QMessageBox.Yes:
                    return

        prefs.setLastPath(Preferences.ExportedFile, QFileInfo(fileName).path())
        
        self.mSettings.setValue("lastUsedExportFilter", selectedFilter)
        if (not chosenFormat.write(self.mMapDocument.map(), fileName)):
            QMessageBox.critical(self, self.tr("Error Exporting Map"),
                                  chosenFormat.errorString())
        else:
            # Remember export parameters, so subsequent exports can be done faster
            self.mMapDocument.setLastExportFileName(fileName)
            if chosenFormat != tmxMapFormat:
                self.mMapDocument.setExportFormat(chosenFormat)

    def exportAsImage(self):
        if (not self.mMapDocument):
            return
        mapView = self.mDocumentManager.currentMapView()
        dialog = ExportAsImageDialog(self.mMapDocument,
                                   self.mMapDocument.fileName(),
                                   mapView.zoomable().scale(), self)
        dialog.exec()

    def reload(self):
        if (self.confirmSave(self.mDocumentManager.currentDocument())):
            self.mDocumentManager.reloadCurrentDocument()

    def closeFile(self):
        if (self.confirmSave(self.mDocumentManager.currentDocument())):
            self.mDocumentManager.closeCurrentDocument()

    def closeAllFiles(self):
        if (self.confirmAllSave()):
            self.mDocumentManager.closeAllDocuments()

    def cut(self):
        if (not self.mMapDocument):
            return
        currentLayer = self.mMapDocument.currentLayer()
        if (not currentLayer):
            return
        tileLayer = currentLayer
        selectedArea = self.mMapDocument.selectedArea()
        selectedObjects = self.mMapDocument.selectedObjects()
        self.copy()
        stack = self.mMapDocument.undoStack()
        stack.beginMacro(self.tr("Cut"))
        if (type(tileLayer)==TileLayer and not selectedArea.isEmpty()):
            stack.push(EraseTiles(self.mMapDocument, tileLayer, selectedArea))
        elif (not selectedObjects.isEmpty()):
            for mapObject in selectedObjects:
                stack.push(RemoveMapObject(self.mMapDocument, mapObject))

        self.mActionHandler.selectNone()
        stack.endMacro()

    def copy(self):
        if (not self.mMapDocument):
            return
        ClipboardManager.instance().copySelection(self.mMapDocument)

    def paste(self):
        if (not self.mMapDocument):
            return
        currentLayer = self.mMapDocument.currentLayer()
        if (not currentLayer):
            return
        clipboardManager = ClipboardManager.instance()
        map = clipboardManager.map()
        if (not map):
            return
        # We can currently only handle maps with a single layer
        if (map.layerCount() != 1):
            # Need to clean up the tilesets since they didn't get an owner
            return

        tilesetManager = TilesetManager.instance()
        tilesetManager.addReferences(map.tilesets())
        self.mMapDocument.unifyTilesets(map.data())
        layer = map.layerAt(0)
        
        if layer.isTileLayer():
            # Reset selection and paste into the stamp brush
            self.mActionHandler.selectNone()
            stamp = map.take() # TileStamp will take ownership
            self.setStamp(TileStamp(stamp))
            tilesetManager.removeReferences(stamp.tilesets())
            self.mToolManager.selectTool(self.mStampBrush)
        else:
            objectGroup = layer.asObjectGroup()
            if objectGroup:
                view = self.mDocumentManager.currentMapView()
                clipboardManager.pasteObjectGroup(objectGroup, self.mMapDocument, view)
        
        if map:
            tilesetManager.removeReferences(map.tilesets())

    def delete_(self): # delete is a reserved word
        if (not self.mMapDocument):
            return

        currentLayer = self.mMapDocument.currentLayer()
        if (not currentLayer):
            return

        tileLayer = currentLayer
        selectedArea = self.mMapDocument.selectedArea()
        selectedObjects = self.mMapDocument.selectedObjects()

        undoStack = self.mMapDocument.undoStack()
        undoStack.beginMacro(self.tr("Delete"))

        if (type(tileLayer)==TileLayer and not selectedArea.isEmpty()):
            undoStack.push(EraseTiles(self.mMapDocument, tileLayer, selectedArea))
        elif (not selectedObjects.isEmpty()):
            for mapObject in selectedObjects:
                undoStack.push(RemoveMapObject(self.mMapDocument, mapObject))

        self.mActionHandler.selectNone()
        undoStack.endMacro()

    def openPreferences(self):
        preferencesDialog = PreferencesDialog(self)
        preferencesDialog.exec()

    def labelVisibilityActionTriggered(self, action):
        visibility = ObjectLabelVisiblity.NoObjectLabels

        if action == self.mUi.actionLabelsForSelectedObjects:
            visibility = ObjectLabelVisiblity.SelectedObjectLabels
        elif action == self.mUi.actionLabelsForAllObjects:
            visibility = ObjectLabelVisiblity.AllObjectLabels

        Preferences.instance().setObjectLabelVisibility(visibility)

    def zoomIn(self):
        mapView = self.mDocumentManager.currentMapView()
        if mapView:
            mapView.zoomable().zoomIn()

    def zoomOut(self):
        mapView = self.mDocumentManager.currentMapView()
        if mapView:
            mapView.zoomable().zoomOut()

    def zoomNormal(self):
        mapView = self.mDocumentManager.currentMapView()
        if mapView:
            mapView.zoomable().resetZoom()

    def newTileset(self, path = QString()):
        if (not self.mMapDocument):
            return False
        map = self.mMapDocument.map()
        prefs = Preferences.instance()
        if path=='' or type(path)==bool:
            startLocation = QFileInfo(prefs.lastPath(Preferences.ImageFile)).absolutePath()
        else:
            startLocation = path

        newTileset = NewTilesetDialog(startLocation, self)
        newTileset.setTileWidth(map.tileWidth())
        newTileset.setTileHeight(map.tileHeight())
        tileset = newTileset.createTileset()
        if tileset:
            self.mMapDocument.undoStack().push(AddTileset(self.mMapDocument, tileset))
            prefs.setLastPath(Preferences.ImageFile, tileset.imageSource())
            return True

        return False

    def newTilesets(self, paths):
        for path in paths:
            if (not self.newTileset(path)):
                return

    def reloadTilesets(self):
        if not self.mMapDocument:
            return

        map = self.mMapDocument.map()
        tilesetManager = TilesetManager.instance()
        for tileset in map.tilesets():
            tilesetManager.forceTilesetReload(tileset)

    def addExternalTileset(self):
        if (not self.mMapDocument):
            return
            
        filter = self.tr("All Files (*)")

        selectedFilter = TsxTilesetFormat().nameFilter()
        
        filter += ";;"
        filter += selectedFilter

        helper = FormatHelper(FileFormat.Read, filter)

        selectedFilter = self.mSettings.value("lastUsedTilesetFilter", selectedFilter)
        
        prefs = Preferences.instance()
        start = prefs.lastPath(Preferences.ExternalTileset)
        fileNames, _ = QFileDialog.getOpenFileNames(self, self.tr("Add External Tileset(s)"),
                                              start,
                                              helper.filter(), 
                                              selectedFilter)
        if len(fileNames)==0:
            return
        prefs.setLastPath(Preferences.ExternalTileset, QFileInfo(fileNames[-1]).path())
        self.mSettings.setValue("lastUsedTilesetFilter", selectedFilter)
        
        tilesets = QVector()
        for fileName in fileNames:
            error = ''
            tileset, error = readTileset(fileName)
            if tileset:
                tilesets.append(tileset)
            elif (len(fileNames) == 1):
                QMessageBox.critical(self, self.tr("Error Reading Tileset"), error)
                return
            else:
                result = 0
                result = QMessageBox.warning(self, self.tr("Error Reading Tileset"),
                                              self.tr("%s: %s"%(fileName, error)),
                                              QMessageBox.Abort | QMessageBox.Ignore,
                                              QMessageBox.Ignore)
                if (result == QMessageBox.Abort):
                    # On abort, clean out any already loaded tilesets.
                    return

        undoStack = self.mMapDocument.undoStack()
        undoStack.beginMacro(self.tr("Add %n Tileset(s)", "", tilesets.size()))
        for tileset in tilesets:
            undoStack.push(AddTileset(self.mMapDocument, tileset))
        undoStack.endMacro()

    def resizeMap(self):
        if (not self.mMapDocument):
            return
        map = self.mMapDocument.map()
        resizeDialog = ResizeDialog(self)
        resizeDialog.setOldSize(map.size())
        if (resizeDialog.exec()):
            newSize = resizeDialog.newSize()
            offset = resizeDialog.offset()
            if (newSize != map.size() or not offset.isNull()):
                self.mMapDocument.resizeMap(newSize, offset)

    def offsetMap(self):
        if (not self.mMapDocument):
            return
        offsetDialog = OffsetMapDialog(self.mMapDocument, self)
        if (offsetDialog.exec()):
            layerIndexes = offsetDialog.affectedLayerIndexes()
            if (layerIndexes.empty()):
                return
            self.mMapDocument.offsetMap(layerIndexes,
                                    offsetDialog.offset(),
                                    offsetDialog.affectedBoundingRect(),
                                    offsetDialog.wrapX(),
                                    offsetDialog.wrapY())

    def editMapProperties(self):
        if (not self.mMapDocument):
            return
        self.mMapDocument.setCurrentObject(self.mMapDocument.map())
        self.mMapDocument.emitEditCurrentObject()

    def updateWindowTitle(self):
        if (self.mMapDocument):
            self.setWindowTitle(self.tr("[*]%s - Tiled"%self.mMapDocument.displayName()))
            self.setWindowFilePath(self.mMapDocument.fileName())
            self.setWindowModified(self.mMapDocument.isModified())
        else:
            self.setWindowTitle('')
            self.setWindowFilePath(QString())
            self.setWindowModified(False)

    def updateActions(self):
        map = None
        tileLayerSelected = False
        objectsSelected = False
        selection = QRegion()
        if (self.mMapDocument):
            currentLayer = self.mMapDocument.currentLayer()
            map = self.mMapDocument.map()
            tileLayerSelected = type(currentLayer)==TileLayer
            objectsSelected = not self.mMapDocument.selectedObjects().isEmpty()
            selection = self.mMapDocument.selectedArea()

        canCopy = (tileLayerSelected and not selection.isEmpty()) or objectsSelected
        self.mUi.actionSave.setEnabled(bool(map))
        self.mUi.actionSaveAs.setEnabled(bool(map))
        self.mUi.actionSaveAll.setEnabled(bool(map))
        self.mUi.actionExportAsImage.setEnabled(bool(map))
        self.mUi.actionExport.setEnabled(bool(map))
        self.mUi.actionExportAs.setEnabled(bool(map))
        self.mUi.actionReload.setEnabled(bool(map))
        self.mUi.actionClose.setEnabled(bool(map))
        self.mUi.actionCloseAll.setEnabled(bool(map))
        self.mUi.actionCut.setEnabled(canCopy)
        self.mUi.actionCopy.setEnabled(canCopy)
        self.mUi.actionPaste.setEnabled(ClipboardManager.instance().hasMap())
        self.mUi.actionDelete.setEnabled(canCopy)
        self.mUi.actionNewTileset.setEnabled(bool(map))
        self.mUi.actionAddExternalTileset.setEnabled(bool(map))
        self.mUi.actionResizeMap.setEnabled(bool(map))
        self.mUi.actionOffsetMap.setEnabled(bool(map))
        self.mUi.actionMapProperties.setEnabled(bool(map))
        self.mUi.actionAutoMap.setEnabled(bool(map))
        self.mCommandButton.setEnabled(bool(map))
        self.updateZoomLabel() # for the zoom actions
        if self.mMapDocument:
            _x = self.mMapDocument.currentLayer()
        else:
            _x = None
        layer = _x
        if layer:
            _x = layer.name()
        else:
            _x = self.tr("<none>")
        self.mCurrentLayerLabel.setText(self.tr("Current layer: %s"%_x))

    def updateZoomLabel(self):
        mapView = self.mDocumentManager.currentMapView()
        if mapView:
            _x = mapView.zoomable()
        else:
            _x = None
        zoomable = _x
        if zoomable:
            _x = zoomable.scale()
        else:
            _x = 1
        scale = _x
        self.mUi.actionZoomIn.setEnabled(bool(zoomable and zoomable.canZoomIn()))
        self.mUi.actionZoomOut.setEnabled(bool(zoomable and zoomable.canZoomOut()))
        self.mUi.actionZoomNormal.setEnabled(bool(scale != 1))
        if (zoomable):
            self.mZoomComboBox.setEnabled(True)
        else:
            index = self.mZoomComboBox.findData(1.0)
            self.mZoomComboBox.setCurrentIndex(index)
            self.mZoomComboBox.setEnabled(False)

    def becomePatron(self):
        patreonDialog = PatreonDialog(self)
        patreonDialog.exec()

    def aboutTiled(self):
        aboutDialog = AboutDialog(self)
        aboutDialog.exec()

    def openRecentFile(self):
        action = self.sender()
        if (action):
            self.openFile(action.data())

    def clearRecentFiles(self):
        self.mSettings.beginGroup("recentFiles")
        self.mSettings.setValue("fileNames", QStringList())
        self.mSettings.endGroup()
        self.updateRecentFiles()
        
    def flipHorizontally(self):
        self.flip(FlipDirection.FlipHorizontally)

    def flipVertically(self):
        self.flip(FlipDirection.FlipVertically)

    def rotateLeft(self):
        self.rotate(RotateDirection.RotateLeft)

    def rotateRight(self):
        self.rotate(RotateDirection.RotateRight)

    def openDocumentation(self):
        QDesktopServices.openUrl(QUrl("http://doc.mapeditor.org"))
        
    def flip(self, direction):
        if (self.mStampBrush.isEnabled()):
            stamp = self.mStampBrush.stamp()
            if not stamp.isEmpty():
                self.setStamp(stamp.flipped(direction))
        elif (self.mMapDocument):
            self.mMapDocument.flipSelectedObjects(direction)

    def rotate(self, direction):
        if (self.mStampBrush.isEnabled()):
            stamp = self.mStampBrush.stamp()
            if not stamp.isEmpty():
                self.setStamp(stamp.rotated(direction))
        elif (self.mMapDocument):
            self.mMapDocument.rotateSelectedObjects(direction)

    ##
    # Sets the current stamp, which is used by both the stamp brush and the bucket
    # fill tool.
    ##
    def setStamp(self, stamp):
        if type(stamp)==list and len(stamp)>0:
            stamp = stamp[0]
        if stamp.isEmpty():
            return
        self.mStampBrush.setStamp(stamp)
        self.mBucketFillTool.setStamp(stamp)
        # When selecting a new stamp, it makes sense to switch to a stamp tool
        selectedTool = self.mToolManager.selectedTool()
        if (selectedTool != self.mStampBrush and selectedTool != self.mBucketFillTool):
            self.mToolManager.selectTool(self.mStampBrush)
        self.mTilesetDock.selectTilesInStamp(stamp)
        
    ##
    # Sets the terrain brush.
    ##
    def setTerrainBrush(self, terrain):
        self.mTerrainBrush.setTerrain(terrain)
        # When selecting a new terrain, it makes sense to switch to a terrain brush tool
        selectedTool = self.mToolManager.selectedTool()
        if (selectedTool != self.mTerrainBrush):
            self.mToolManager.selectTool(self.mTerrainBrush)

    def updateStatusInfoLabel(self, statusInfo):
        self.mStatusInfoLabel.setText(statusInfo)

    def mapDocumentChanged(self, mapDocument):
        mapDocument = mapDocument[0]
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
        if (self.mZoomable):
            self.mZoomable.connectToComboBox(None)
            self.mZoomable.scaleChanged.disconnect(self.updateZoomLabel)

        self.mZoomable = None
        self.mMapDocument = mapDocument
        self.mActionHandler.setMapDocument(mapDocument)
        self.mLayerDock.setMapDocument(mapDocument)
        self.mObjectsDock.setMapDocument(mapDocument)
        self.mTilesetDock.setMapDocument(mapDocument)
        self.mTerrainDock.setMapDocument(mapDocument)
        self.mMiniMapDock.setMapDocument(mapDocument)
        self.mTileAnimationEditor.setMapDocument(mapDocument)
        self.mTileCollisionEditor.setMapDocument(mapDocument)
        self.mToolManager.setMapDocument(mapDocument)
        self.mAutomappingManager.setMapDocument(mapDocument)
        if (mapDocument):
            mapDocument.fileNameChanged.connect(self.updateWindowTitle)
            mapDocument.currentLayerIndexChanged.connect(self.updateActions)
            mapDocument.selectedAreaChanged.connect(self.updateActions)
            mapDocument.selectedObjectsChanged.connect(self.updateActions)
            mapView = self.mDocumentManager.currentMapView()
            if mapView:
                self.mZoomable = mapView.zoomable()
                self.mZoomable.connectToComboBox(self.mZoomComboBox)
                self.mZoomable.scaleChanged.connect(self.updateZoomLabel)

        self.updateWindowTitle()
        self.updateActions()

    def closeMapDocument(self, index):
        if (self.confirmSave(self.mDocumentManager.documents().at(index))):
            self.mDocumentManager.closeDocumentAt(index)

    def reloadError(self, error):
        QMessageBox.critical(self, self.tr("Error Reloading Map"), error)

    def autoMappingError(self, automatic):
        title = self.tr("Automatic Mapping Error")
        error = self.mAutomappingManager.errorString()
        if error != '':
            if (automatic):
                self.statusBar().showMessage(error, 3000)
            else:
                QMessageBox.critical(self, title, error)

    def autoMappingWarning(self, automatic):
        title = self.tr("Automatic Mapping Warning")
        warning = self.mAutomappingManager.warningString()
        if (not warning.isEmpty()):
            if (automatic):
                self.statusBar().showMessage(warning, 3000)
            else:
                QMessageBox.warning(self, title, warning)

    def onAnimationEditorClosed(self):
        self.mShowTileAnimationEditor.setChecked(False)

    def onCollisionEditorClosed(self):
        self.mShowTileCollisionEditor.setChecked(False)

    ##
    # Asks the user whether the given \a mapDocument should be saved, when
    # necessary. If it needs to ask, also makes sure that it is the current
    # document.
    #
    # @return <code>True</code> when any unsaved data is either discarded or
    #         saved, <code>False</code> when the user cancelled or saving
    #         failed.
    ##
    def confirmSave(self, mapDocument):
        if (not mapDocument or not mapDocument.isModified()):
            return True
        self.mDocumentManager.switchToDocument(mapDocument)
        ret = QMessageBox.warning(
                self, self.tr("Unsaved Changes"),
                self.tr("There are unsaved changes. Do you want to save now?"),
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        x = ret
        if x==QMessageBox.Save:
            return self.saveFile()
        elif x==QMessageBox.Discard:
            return True
        elif x==QMessageBox.Cancel:
            pass
        else:
            return False

    ##
    # Checks all maps for changes, if so, ask if to save these changes.
    #
    # @return <code>True</code> when any unsaved data is either discarded or
    #         saved, <code>False</code> when the user cancelled or saving
    #         failed.
    ##
    def confirmAllSave(self):
        for i in range(self.mDocumentManager.documentCount()):
            if (not self.confirmSave(self.mDocumentManager.documents().at(i))):
                return False

        return True

    ##
    # Save the current map to the given file name. When saved succesfully, the
    # file is added to the list of recent files.
    # @return <code>True</code> on success, <code>False</code> on failure
    ##
    def saveFile(self, *args):
        l = len(args)
        if l==1:
            arg1 = args[0]
            tp = type(arg1)
            if tp==bool:
                return self.saveFile()
            elif tp in [str, QString]:
                fileName = arg1
                if (not self.mMapDocument):
                    return False
                if fileName == '':
                    return False
                error = QString()
                if (not self.mMapDocument.save(fileName, error)):
                    QMessageBox.critical(self, self.tr("Error Saving Map"), error)
                    return False

                self.setRecentFile(fileName)
                return True
        elif l==0:
            if (not self.mMapDocument):
                return False
            currentFileName = self.mMapDocument.fileName()
            if currentFileName == '':
                return self.saveFileAs()
            else:
                return self.saveFile(currentFileName)

    def writeSettings(self):
        self.mSettings.beginGroup("mainwindow")
        self.mSettings.setValue("geometry", self.saveGeometry())
        self.mSettings.setValue("state", self.saveState())
        self.mSettings.endGroup()
        self.mSettings.beginGroup("recentFiles")
        document = self.mDocumentManager.currentDocument()
        if document:
            self.mSettings.setValue("lastActive", document.fileName())
        fileList = QStringList()
        mapScales = QStringList()
        scrollX = QStringList()
        scrollY = QStringList()
        selectedLayer = QStringList()
        for i in range(self.mDocumentManager.documentCount()):
            document = self.mDocumentManager.documents().at(i)
            mapView = self.mDocumentManager.viewForDocument(document)
            fileList.append(document.fileName())
            currentLayerIndex = document.currentLayerIndex()
            mapScales.append(str(mapView.zoomable().scale()))
            scrollX.append(str(mapView.horizontalScrollBar().sliderPosition()))
            scrollY.append(str(mapView.verticalScrollBar().sliderPosition()))
            selectedLayer.append(str(currentLayerIndex))

        self.mSettings.setValue("lastOpenFiles", fileList)
        self.mSettings.setValue("mapScale", mapScales)
        self.mSettings.setValue("scrollX", scrollX)
        self.mSettings.setValue("scrollY", scrollY)
        self.mSettings.setValue("selectedLayer", selectedLayer)
        self.mSettings.endGroup()

    def readSettings(self):
        self.mSettings.beginGroup("mainwindow")
        geom = self.mSettings.value("geometry", QByteArray())
        if not geom.isEmpty():
            self.restoreGeometry(geom)
        else:
            self.resize(1200, 700)
        self.restoreState(self.mSettings.value("state", QByteArray()))
        self.mSettings.endGroup()
        self.updateRecentFiles()

    def recentFiles(self):
        v = self.mSettings.value("recentFiles/fileNames")
        return QList(v)

    def fileDialogStartLocation(self):
        files = self.recentFiles()
        if (not files.isEmpty()):
            _x = QFileInfo(files.first()).path()
        else:
            _x = QString()
        return _x

    ##
    # Adds the given file to the recent files list.
    ##
    def setRecentFile(self, fileName):
        # Remember the file by its canonical file path
        canonicalFilePath = QFileInfo(fileName).canonicalFilePath()
        if (canonicalFilePath==''):
            return
        files = self.recentFiles()
        files.removeAll(canonicalFilePath)
        files.prepend(canonicalFilePath)
        while (files.size() > MaxRecentFiles):
            files.removeLast()
        self.mSettings.beginGroup("recentFiles")
        self.mSettings.setValue("fileNames", files)
        self.mSettings.endGroup()
        self.updateRecentFiles()

    ##
    # Updates the recent files menu.
    ##
    def updateRecentFiles(self):
        files = self.recentFiles()
        numRecentFiles = min(files.size(),  MaxRecentFiles)
        for i in range(numRecentFiles):

            self.mRecentFiles[i].setText(QFileInfo(files[i]).fileName())
            self.mRecentFiles[i].setData(files[i])
            self.mRecentFiles[i].setVisible(True)

        for j in range(numRecentFiles, MaxRecentFiles):

            self.mRecentFiles[j].setVisible(False)

        self.mUi.menuRecentFiles.setEnabled(numRecentFiles > 0)

    def retranslateUi(self):
        self.updateWindowTitle()
        self.mRandomButton.setToolTip(self.tr("Random Mode"))
        self.mLayerMenu.setTitle(self.tr("Layer"))
        self.mViewsAndToolbarsMenu.setText(self.tr("Views and Toolbars"))
        self.mShowTileAnimationEditor.setText(self.tr("Tile Animation Editor"))
        self.mShowTileCollisionEditor.setText(self.tr("Tile Collision Editor"))
        self.mActionHandler.retranslateUi()
        self.mToolManager.retranslateTools()

    def setupQuickStamps(self):
        keys = TileStampManager.quickStampKeys()
        selectMapper = QSignalMapper(self)
        createMapper = QSignalMapper(self)
        extendMapper = QSignalMapper(self)
        for i in range(keys.__len__()):
            key = keys[i]
            # Set up shortcut for selecting this quick stamp
            selectStamp = QShortcut(key, self)

            selectStamp.activated.connect(selectMapper.map)
            selectMapper.setMapping(selectStamp, i)
            # Set up shortcut for saving this quick stamp
            createStamp = QShortcut(Qt.CTRL + key, self)

            createStamp.activated.connect(createMapper.map)
            createMapper.setMapping(createStamp, i)
            
            # Set up shortcut for extending this quick stamp
            extendStamp = QShortcut(Qt.CTRL + Qt.SHIFT + key, self)
            extendStamp.activated.connect(extendMapper.map)
            extendMapper.setMapping(extendStamp, i)
            
        selectMapper.mapped.connect(self.mTileStampManager.selectQuickStamp)
        createMapper.mapped.connect(self.mTileStampManager.createQuickStamp)
        extendMapper.mapped.connect(self.mTileStampManager.extendQuickStamp)
        self.mTileStampManager.setStamp.connect(self.setStamp)
