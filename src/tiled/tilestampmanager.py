##
# tilestampmanager.py
# Copyright 2010-2011, Stefan Beller <stefanbeller@googlemail.com>
# Copyright 2014-2015, Thorbjørn Lindeijer <bjorn@lindeijer.nl>
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

from tilestampmodel import TileStampModel
import preferences
from map import Map
from documentmanager import DocumentManager
from bucketfilltool import BucketFillTool
from tilestamp import TileStamp
from pyqtcore import (
    QString,
    QMap,
    QVector, 
    dynamic_cast
)
from PyQt5.QtCore import (
    QIODevice,
    QSaveFile,
    Qt,
    qDebug, 
    pyqtSignal, 
    QDirIterator,
    QFile,
    QDir,
    QJsonDocument,
    QObject,
    QFileInfo, 
    QJsonParseError, 
    QRegularExpression
)

def stampFilePath(name):
    prefs = preferences.Preferences.instance()
    stampsDir = QDir(prefs.stampsDirectory())
    return stampsDir.filePath(name)

def findStampFileName(name, currentFileName=''):
    invalidChars = QRegularExpression("[^\\w -]+")
    prefs = preferences.Preferences.instance()
    stampsDir = QDir(prefs.stampsDirectory())
    suggestedFileName = name.toLower().remove(invalidChars)
    fileName = suggestedFileName + ".stamp"
    if (fileName == currentFileName or not stampsDir.exists(fileName)):
        return fileName
    n = 2
    while (fileName != currentFileName and stampsDir.exists(fileName)):
        fileName = suggestedFileName + QString.number(n) + ".stamp"
        n += 1
    
    return fileName

def stampFromContext(selectedTool):
    stamp = TileStamp()
    stampBrush = dynamic_cast(selectedTool)
    if stampBrush:
        # take the stamp from the stamp brush
        stamp = stampBrush.stamp()
    else:
        fillTool = dynamic_cast(selectedTool, BucketFillTool)
        if fillTool:
            # take the stamp from the fill tool
            stamp = fillTool.stamp()
        else:
            mapDocument = DocumentManager.instance().currentDocument()
            if mapDocument:
                # try making a stamp from the current tile selection
                tileLayer = dynamic_cast(mapDocument.currentLayer())
                if (not tileLayer):
                    return stamp
                selection = mapDocument.selectedArea()
                if (selection.isEmpty()):
                    return stamp
                selection.translate(-tileLayer.position())
                copy = tileLayer.copy(selection)
                if (copy.size().isEmpty()):
                    return stamp
                map = mapDocument.map()
                copyMap = Map(map.orientation(),
                                       copy.width(), copy.height(),
                                       map.tileWidth(), map.tileHeight())
                # Add tileset references to map
                for tileset in copy.usedTilesets():
                    copyMap.addTileset(tileset)
                copyMap.setRenderOrder(map.renderOrder())
                copyMap.addLayer(copy.take())
                stamp.addVariation(copyMap)
    
    return stamp

##
# Implements a manager which handles lots of copy&paste slots.
# Ctrl + <1..9> will store tile layers, and just <1..9> will recall these
# tile layers.
##
class TileStampManager(QObject):
    setStamp = pyqtSignal(TileStamp)

    def __init__(self, toolManager, parent = None):
        super().__init__(parent)
        
        self.mStampsByName = QMap()
        self.mQuickStamps = QVector()
        for i in range(TileStampManager.quickStampKeys().__len__()):
            self.mQuickStamps.append(0)
        
        self.mTileStampModel = TileStampModel(self)
        self.mToolManager = toolManager

        prefs = preferences.Preferences.instance()
        prefs.stampsDirectoryChanged.connect(self.stampsDirectoryChanged)
        self.mTileStampModel.stampAdded.connect(self.stampAdded)
        self.mTileStampModel.stampRenamed.connect(self.stampRenamed)
        self.mTileStampModel.stampChanged.connect(self.saveStamp)
        self.mTileStampModel.stampRemoved.connect(self.deleteStamp)
        self.loadStamps()

    def __del__(self):
        # needs to be over here where the TileStamp type is complete
        pass
        
    ##
    # Returns the keys used for quickly accessible tile stamps.
    # Note: To store a tile layer <Ctrl> is added. The given keys will work
    # for recalling the stored values.
    ##
    def quickStampKeys():
        keys=[Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5, Qt.Key_6, Qt.Key_7, Qt.Key_8, Qt.Key_9]
        return keys
        
    def tileStampModel(self):
        return self.mTileStampModel
        
    def createStamp(self):
        stamp = self.tampFromContext(self.mToolManager.selectedTool())
        if (not stamp.isEmpty()):
            self.mTileStampModel.addStamp(stamp)
        return stamp
    
    def addVariation(self, targetStamp):
        stamp = stampFromContext(self.mToolManager.selectedTool())
        if (stamp.isEmpty()):
            return
        if (stamp == targetStamp): # avoid easy mistake of adding duplicates
            return
        for variation in stamp.variations():
            self.mTileStampModel.addVariation(targetStamp, variation)

    def selectQuickStamp(self, index):
        stamp = self.mQuickStamps.at(index)
        if (not stamp.isEmpty()):
            self.setStamp.emit(stamp)
    
    def createQuickStamp(self, index):
        stamp = stampFromContext(self.mToolManager.selectedTool())
        if (stamp.isEmpty()):
            return
        self.setQuickStamp(index, stamp)
    
    def extendQuickStamp(self, index):
        quickStamp = self.mQuickStamps[index]
        if (quickStamp.isEmpty()):
            self.createQuickStamp(index)
        else:
            self.addVariation(quickStamp)
    
    def stampsDirectoryChanged(self):
        # erase current stamps
        self.mQuickStamps.fill(TileStamp())
        self.mStampsByName.clear()
        self.mTileStampModel.clear()
        self.loadStamps()

    def eraseQuickStamp(self, index):
        stamp = self.mQuickStamps.at(index)
        if (not stamp.isEmpty()):
            self.mQuickStamps[index] = TileStamp()
            if (not self.mQuickStamps.contains(stamp)):
                self.mTileStampModel.removeStamp(stamp)

    def setQuickStamp(self, index, stamp):
        stamp.setQuickStampIndex(index)
        # make sure existing quickstamp is removed from stamp model
        self.eraseQuickStamp(index)
        self.mTileStampModel.addStamp(stamp)
        self.mQuickStamps[index] = stamp
    
    def loadStamps(self):
        prefs = preferences.Preferences.instance()
        stampsDirectory = prefs.stampsDirectory()
        stampsDir = QDir(stampsDirectory)
        iterator = QDirIterator(stampsDirectory,
                              ["*.stamp"],
                              QDir.Files | QDir.Readable)
        while (iterator.hasNext()):
            stampFileName = iterator.next()
            stampFile = QFile(stampFileName)
            if (not stampFile.open(QIODevice.ReadOnly)):
                continue
            data = stampFile.readAll()
            document = QJsonDocument.fromBinaryData(data)
            if (document.isNull()):
                # document not valid binary data, maybe it's an JSON text file
                error = QJsonParseError()
                document, error = QJsonDocument.fromJson(data)
                if (error.error != QJsonParseError.NoError):
                    qDebug("Failed to parse stamp file:" + error.errorString())
                    continue

            stamp = TileStamp.fromJson(document.object(), stampsDir)
            if (stamp.isEmpty()):
                continue
            stamp.setFileName(iterator.fileInfo().fileName())
            self.mTileStampModel.addStamp(stamp)
            index = stamp.quickStampIndex()
            if (index >= 0 and index < self.mQuickStamps.size()):
                self.mQuickStamps[index] = stamp


    def stampAdded(self, stamp):
        if (stamp.name().isEmpty() or self.mStampsByName.contains(stamp.name())):
            # pick the first available stamp name
            name = QString()
            index = self.mTileStampModel.stamps().size()
            while(self.mStampsByName.contains(name)):
                name = str(index)
                index += 1
            
            stamp.setName(name)
        
        self.mStampsByName.insert(stamp.name(), stamp)
        if (stamp.fileName().isEmpty()):
            stamp.setFileName(findStampFileName(stamp.name()))
            self.saveStamp(stamp)

    def stampRenamed(self, stamp):
        existingName = self.mStampsByName.key(stamp)
        self.mStampsByName.remove(existingName)
        self.mStampsByName.insert(stamp.name(), stamp)
        existingFileName = stamp.fileName()
        newFileName = findStampFileName(stamp.name(), existingFileName)
        if (existingFileName != newFileName):
            if (QFile.rename(stampFilePath(existingFileName),
                              stampFilePath(newFileName))):
                stamp.setFileName(newFileName)

    
    def saveStamp(self, stamp):
        # make sure we have a stamps directory
        prefs = preferences.Preferences.instance()
        stampsDirectory = prefs.stampsDirectory()
        stampsDir = QDir(stampsDirectory)
        if (not stampsDir.exists() and not stampsDir.mkpath(".")):
            qDebug("Failed to create stamps directory" + stampsDirectory)
            return
        
        filePath = stampsDir.filePath(stamp.fileName())
        file = QSaveFile(filePath)
        if (not file.open(QIODevice.WriteOnly)):
            qDebug("Failed to open stamp file for writing" + filePath)
            return
        
        stampJson = stamp.toJson(QFileInfo(filePath).dir())
        file.write(QJsonDocument(stampJson).toJson(QJsonDocument.Compact))
        if (not file.commit()):
            qDebug() << "Failed to write stamp" << filePath
    
    def deleteStamp(self, stamp):
        self.mStampsByName.remove(stamp.name())
        QFile.remove(stampFilePath(stamp.fileName()))
