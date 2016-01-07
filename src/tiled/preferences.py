##
# preferences.py
# Copyright 2009-2011, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from tilesetmanager import TilesetManager
import languagemanager
from tiled_global import Int, Float
from documentmanager import DocumentManager
from objecttypes import ObjectType
from map import Map
from pyqtcore import QStringList, QVector
from PyQt5.QtCore import (
    Qt,
    QSettings,
    QFileInfo,
    pyqtSignal,
    QStandardPaths,
    QObject,
    QDate
)
from PyQt5.QtGui import (
    QColor
)

def lastPathKey(fileType):
    key = "LastPaths/"
    x = fileType
    if x==Preferences.ObjectTypesFile:
        key += "ObjectTypes"
    elif x==Preferences.ImageFile:
        key += "Images"
    elif x==Preferences.ExportedFile:
        key += "ExportedFile"
    elif x==Preferences.ExternalTileset:
        key += "ExternalTileset"
    else:
        pass # Getting here means invalid file type

    return key

class ObjectLabelVisiblity():
    NoObjectLabels = 0
    SelectedObjectLabels = 1
    AllObjectLabels = 2
    
##
# This class holds user preferences and provides a convenient interface to
# access them.
##
class Preferences(QObject):
    showGridChanged = pyqtSignal(bool)
    showTileObjectOutlinesChanged = pyqtSignal(bool)
    showTileAnimationsChanged = pyqtSignal(bool)
    snapToGridChanged = pyqtSignal(bool)
    snapToFineGridChanged = pyqtSignal(bool)
    gridColorChanged = pyqtSignal(QColor)
    gridFineChanged = pyqtSignal(int)
    objectLineWidthChanged = pyqtSignal(float)
    highlightCurrentLayerChanged = pyqtSignal(bool)
    showTilesetGridChanged = pyqtSignal(bool)
    objectLabelVisibilityChanged = pyqtSignal(int)
    useOpenGLChanged = pyqtSignal(bool)
    objectTypesChanged = pyqtSignal()
    mapsDirectoryChanged = pyqtSignal()
    stampsDirectoryChanged = pyqtSignal(str)
    isPatronChanged = pyqtSignal()

    mInstance = None

    ObjectTypesFile, ImageFile, ExportedFile, ExternalTileset = range(4)

    def __init__(self):
        super().__init__()

        self.mSettings = QSettings(self)

        self.mObjectTypes = QVector()

        # Retrieve storage settings
        self.mSettings.beginGroup("Storage")
        self.mLayerDataFormat = Map.LayerDataFormat(self.intValue("LayerDataFormat", Map.LayerDataFormat.Base64Zlib.value))
        self.mMapRenderOrder = Map.RenderOrder(self.intValue("MapRenderOrder", Map.RenderOrder.RightDown.value))
        self.mDtdEnabled = self.boolValue("DtdEnabled")
        self.mReloadTilesetsOnChange = self.boolValue("ReloadTilesets", True)
        self.mStampsDirectory = self.stringValue("StampsDirectory")
        self.mSettings.endGroup()
        # Retrieve interface settings
        self.mSettings.beginGroup("Interface")
        self.mShowGrid = self.boolValue("ShowGrid")
        self.mShowTileObjectOutlines = self.boolValue("ShowTileObjectOutlines")
        self.mShowTileAnimations = self.boolValue("ShowTileAnimations", True)
        self.mSnapToGrid = self.boolValue("SnapToGrid")
        self.mSnapToFineGrid = self.boolValue("SnapToFineGrid")
        self.mGridColor = self.colorValue("GridColor", Qt.black)
        self.mGridFine = self.intValue("GridFine", 4)
        self.mObjectLineWidth = self.realValue("ObjectLineWidth", 2)
        self.mHighlightCurrentLayer = self.boolValue("HighlightCurrentLayer")
        self.mShowTilesetGrid = self.boolValue("ShowTilesetGrid", True)
        self.mLanguage = self.stringValue("Language")
        self.mUseOpenGL = self.boolValue("OpenGL")
        self.mObjectLabelVisibility = self.intValue("ObjectLabelVisibility", ObjectLabelVisiblity.AllObjectLabels)
        self.mSettings.endGroup()
        # Retrieve defined object types
        self.mSettings.beginGroup("ObjectTypes")
        names = self.mSettings.value("Names", QStringList())
        colors = self.mSettings.value("Colors", QStringList())
        self.mSettings.endGroup()
        count = min(len(names), len(colors))
        for i in range(count):
            self.mObjectTypes.append(ObjectType(names[i], QColor(colors[i])))
        self.mSettings.beginGroup("Automapping")
        self.mAutoMapDrawing = self.boolValue("WhileDrawing")
        self.mSettings.endGroup()
        self.mSettings.beginGroup("MapsDirectory")
        self.mMapsDirectory = self.stringValue("Current")
        self.mSettings.endGroup()
        tilesetManager = TilesetManager.instance()
        tilesetManager.setReloadTilesetsOnChange(self.mReloadTilesetsOnChange)
        tilesetManager.setAnimateTiles(self.mShowTileAnimations)
        # Keeping track of some usage information
        self.mSettings.beginGroup("Install")
        self.mFirstRun = QDate.fromString(self.mSettings.value("FirstRun"))
        self.mRunCount = self.intValue("RunCount", 0) + 1
        self.mIsPatron = self.boolValue("IsPatron")
        if (not self.mFirstRun.isValid()):
            self.mFirstRun = QDate.currentDate()
            self.mSettings.setValue("FirstRun", self.mFirstRun.toString(Qt.ISODate))

        self.mSettings.setValue("RunCount", self.mRunCount)
        self.mSettings.endGroup()
        
        # Retrieve startup settings
        self.mSettings.beginGroup("Startup")
        self.mOpenLastFilesOnStartup = self.boolValue("OpenLastFiles", True)
        self.mSettings.endGroup()

    def __del__(self):
        pass

    def setObjectLabelVisibility(self, visibility):
        if self.mObjectLabelVisibility == visibility:
            return

        self.mObjectLabelVisibility = visibility
        self.mSettings.setValue("Interface/ObjectLabelVisibility", visibility)
        self.objectLabelVisibilityChanged.emit(visibility)
        
    def instance():
        if (not Preferences.mInstance):
            Preferences.mInstance = Preferences()
        return Preferences.mInstance

    def deleteInstance():
        del Preferences.mInstance
        Preferences.mInstance = None

    def showGrid(self):
        return self.mShowGrid

    def showTileObjectOutlines(self):
        return self.mShowTileObjectOutlines

    def showTileAnimations(self):
        return self.mShowTileAnimations

    def snapToGrid(self):
        return self.mSnapToGrid

    def snapToFineGrid(self):
        return self.mSnapToFineGrid

    def gridColor(self):
        return self.mGridColor

    def gridFine(self):
        return self.mGridFine

    def objectLineWidth(self):
        return self.mObjectLineWidth

    def highlightCurrentLayer(self):
        return self.mHighlightCurrentLayer

    def showTilesetGrid(self):
        return self.mShowTilesetGrid

    def useOpenGL(self):
        return self.mUseOpenGL

    def objectTypes(self):
        return self.mObjectTypes

    def automappingDrawing(self):
        return self.mAutoMapDrawing

    ##
    # Provides access to the QSettings instance to allow storing/retrieving
    # arbitrary values. The naming style for groups and keys is CamelCase.
    ##
    def settings(self):
        return self.mSettings

    def layerDataFormat(self):
        return self.mLayerDataFormat

    def setLayerDataFormat(self, layerDataFormat):
        if (self.mLayerDataFormat == layerDataFormat):
            return
        self.mLayerDataFormat = layerDataFormat
        self.mSettings.setValue("Storage/LayerDataFormat",
                            self.mLayerDataFormat)

    def mapRenderOrder(self):
        return self.mMapRenderOrder

    def setMapRenderOrder(self, mapRenderOrder):
        if (self.mMapRenderOrder == mapRenderOrder):
            return
        self.mMapRenderOrder = mapRenderOrder
        self.mSettings.setValue("Storage/MapRenderOrder",
                            self.mMapRenderOrder)

    def dtdEnabled(self):
        return self.mDtdEnabled

    def setDtdEnabled(self, enabled):
        self.mDtdEnabled = enabled
        self.mSettings.setValue("Storage/DtdEnabled", enabled)

    def language(self):
        return self.mLanguage

    def setLanguage(self, language):
        if (self.mLanguage == language):
            return
        self.mLanguage = language
        self.mSettings.setValue("Interface/Language", self.mLanguage)
        languagemanager.LanguageManager.instance().installTranslators()

    def reloadTilesetsOnChange(self):
        return self.mReloadTilesetsOnChange

    def setReloadTilesetsOnChanged(self, value):
        if (self.mReloadTilesetsOnChange == value):
            return
        self.mReloadTilesetsOnChange = value
        self.mSettings.setValue("Storage/ReloadTilesets",
                            self.mReloadTilesetsOnChange)
        tilesetManager = TilesetManager.instance()
        tilesetManager.setReloadTilesetsOnChange(self.mReloadTilesetsOnChange)

    def setUseOpenGL(self, useOpenGL):
        if (self.mUseOpenGL == useOpenGL):
            return
        self.mUseOpenGL = useOpenGL
        self.mSettings.setValue("Interface/OpenGL", self.mUseOpenGL)
        self.useOpenGLChanged.emit(self.mUseOpenGL)

    def setObjectTypes(self, objectTypes):
        self.mObjectTypes = objectTypes
        names = QStringList()
        colors = QStringList()
        for objectType in objectTypes:
            names.append(objectType.name)
            colors.append(objectType.color.name())

        self.mSettings.beginGroup("ObjectTypes")
        self.mSettings.setValue("Names", names)
        self.mSettings.setValue("Colors", colors)
        self.mSettings.endGroup()
        self.objectTypesChanged.emit()

    def lastPath(self, fileType):
        path = self.mSettings.value(lastPathKey(fileType))
        if path==None or path=='':
            documentManager = DocumentManager.instance()
            mapDocument = documentManager.currentDocument()
            if mapDocument:
                path = QFileInfo(mapDocument.fileName()).path()

        if path==None or path=='':
            path = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)

        return path

    ##
    # \see lastPath()
    ##
    def setLastPath(self, fileType, path):
        self.mSettings.setValue(lastPathKey(fileType), path)

    def setAutomappingDrawing(self, enabled):
        self.mAutoMapDrawing = enabled
        self.mSettings.setValue("Automapping/WhileDrawing", enabled)

    def mapsDirectory(self):
        return self.mMapsDirectory

    def setMapsDirectory(self, path):
        if (self.mMapsDirectory == path):
            return
        self.mMapsDirectory = path
        self.mSettings.setValue("MapsDirectory/Current", path)
        self.mapsDirectoryChanged.emit()

    def objectLabelVisibility(self):
        return self.mObjectLabelVisibility

    def firstRun(self):
        return self.mFirstRun

    def runCount(self):
        return self.mRunCount

    def isPatron(self):
        return self.mIsPatron

    def openLastFilesOnStartup(self):
        return self.mOpenLastFilesOnStartup
        
    def setPatron(self, isPatron):
        if (self.mIsPatron == isPatron):
            return
        self.mIsPatron = isPatron
        self.mSettings.setValue("Install/IsPatron", isPatron)
        self.isPatronChanged.emit()

    def setShowGrid(self, showGrid):
        if (self.mShowGrid == showGrid):
            return
        self.mShowGrid = showGrid
        self.mSettings.setValue("Interface/ShowGrid", self.mShowGrid)
        self.showGridChanged.emit(self.mShowGrid)

    def setShowTileObjectOutlines(self, enabled):
        if (self.mShowTileObjectOutlines == enabled):
            return
        self.mShowTileObjectOutlines = enabled
        self.mSettings.setValue("Interface/ShowTileObjectOutlines",
                            self.mShowTileObjectOutlines)
        self.showTileObjectOutlinesChanged.emit(self.mShowTileObjectOutlines)

    def setShowTileAnimations(self, enabled):
        if (self.mShowTileAnimations == enabled):
            return
        self.mShowTileAnimations = enabled
        self.mSettings.setValue("Interface/ShowTileAnimations",
                            self.mShowTileAnimations)
        tilesetManager = TilesetManager.instance()
        tilesetManager.setAnimateTiles(self.mShowTileAnimations)
        self.showTileAnimationsChanged.emit(self.mShowTileAnimations)

    def setSnapToGrid(self, snapToGrid):
        if (self.mSnapToGrid == snapToGrid):
            return
        self.mSnapToGrid = snapToGrid
        self.mSettings.setValue("Interface/SnapToGrid", self.mSnapToGrid)
        self.snapToGridChanged.emit(self.mSnapToGrid)

    def setSnapToFineGrid(self, snapToFineGrid):
        if (self.mSnapToFineGrid == snapToFineGrid):
            return
        self.mSnapToFineGrid = snapToFineGrid
        self.mSettings.setValue("Interface/SnapToFineGrid", self.mSnapToFineGrid)
        self.snapToFineGridChanged.emit(self.mSnapToFineGrid)

    def setGridColor(self, gridColor):
        if (self.mGridColor == gridColor):
            return
        self.mGridColor = gridColor
        self.mSettings.setValue("Interface/GridColor", self.mGridColor.name())
        self.gridColorChanged.emit(self.mGridColor)

    def setGridFine(self, gridFine):
        if (self.mGridFine == gridFine):
            return
        self.mGridFine = gridFine
        self.mSettings.setValue("Interface/GridFine", self.mGridFine)
        self.gridFineChanged.emit(self.mGridFine)

    def setObjectLineWidth(self, lineWidth):
        if (self.mObjectLineWidth == lineWidth):
            return
        self.mObjectLineWidth = lineWidth
        self.mSettings.setValue("Interface/ObjectLineWidth", self.mObjectLineWidth)
        self.objectLineWidthChanged.emit(self.mObjectLineWidth)

    def setHighlightCurrentLayer(self, highlight):
        if (self.mHighlightCurrentLayer == highlight):
            return
        self.mHighlightCurrentLayer = highlight
        self.mSettings.setValue("Interface/HighlightCurrentLayer",
                            self.mHighlightCurrentLayer)
        self.highlightCurrentLayerChanged.emit(self.mHighlightCurrentLayer)

    def setShowTilesetGrid(self, showTilesetGrid):
        if (self.mShowTilesetGrid == showTilesetGrid):
            return
        self.mShowTilesetGrid = showTilesetGrid
        self.mSettings.setValue("Interface/ShowTilesetGrid",
                            self.mShowTilesetGrid)
        self.showTilesetGridChanged.emit(self.mShowTilesetGrid)

    def setOpenLastFilesOnStartup(self, open):
        if self.mOpenLastFilesOnStartup == open:
            return

        self.mOpenLastFilesOnStartup = open
        self.mSettings.setValue("Startup/OpenLastFiles", open)

    def boolValue(self, key, defaultValue = False):
        b = self.mSettings.value(key, defaultValue)
        tp = type(b)
        if tp==bool:
            return b
        elif tp==str:
            return b.lower()=='true'
        return bool(b)

    def colorValue(self, key, default = QColor()):
        if type(default) != QColor:
            default = QColor(default)
        name = self.mSettings.value(key, default.name())
        if (not QColor.isValidColor(name)):
            return QColor()
        return QColor(name)

    def stringValue(self, key, default = ''):
        return self.mSettings.value(key, default)

    def intValue(self, key, defaultValue):
        return Int(self.mSettings.value(key, defaultValue))

    def realValue(self, key, defaultValue):
        return Float(self.mSettings.value(key, defaultValue))

    def stampsDirectory(self):
        if self.mStampsDirectory == '':
            appData = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
            return appData + "/stamps"
        return self.mStampsDirectory

    def setStampsDirectory(self, stampsDirectory):
        if self.mStampsDirectory == stampsDirectory:
            return

        self.mStampsDirectory = stampsDirectory
        self.mSettings.setValue("Storage/StampsDirectory", stampsDirectory)

        self.stampsDirectoryChanged.emit(stampsDirectory)
