##
# automappingmanager.py
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
import preferences
from tmxmapformat import TmxMapFormat
from tilesetmanager import TilesetManager
from automapperwrapper import AutoMapperWrapper
from automapper import AutoMapper

from PyQt5.QtCore import (
    QTextStream,
    QFileInfo,
    QObject,
    pyqtSignal,
    QRect,
    QFile,
    QIODevice,
    Qt
)
from PyQt5.QtGui import (
    QRegion
)
from pyqtcore import QString, QVector
##
# This class is a superior class to the AutoMapper and AutoMapperWrapper class.
# It uses these classes to do the whole automapping process.
##
class AutomappingManager(QObject):
    ##
    # This signal is emited after automapping was done and an error occurred.
    ##
    errorsOccurred = pyqtSignal(bool)
    ##
    # This signal is emited after automapping was done and a warning occurred.
    ##
    warningsOccurred = pyqtSignal(bool)

    ##
    # Constructor.
    ##
    def __init__(self, parent = None):
        super().__init__(parent)

        ##
        # The current map document.
        ##
        self.mMapDocument = None
        ##
        # For each new file of rules a new AutoMapper is setup. In this vector we
        # can store all of the AutoMappers in order.
        ##
        self.mAutoMappers = QVector()
        ##
        # This tells you if the rules for the current map document were already
        # loaded.
        ##
        self.mLoaded = False
        ##
        # Contains all errors which occurred until canceling.
        # If mError is not empty, no serious result can be expected.
        ##
        self.mError = QString()
        ##
        # Contains all strings, which try to explain unusual and unexpected
        # behavior.
        ##
        self.mWarning = QString()

    def __del__(self):
        self.cleanUp()

    def setMapDocument(self, mapDocument):
        self.cleanUp()
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
        self.mMapDocument = mapDocument
        if (self.mMapDocument):
            self.mMapDocument.regionEdited.connect(self.autoMap)

        self.mLoaded = False

    def errorString(self):
        return self.mError

    def warningString(self):
        return self.mWarning
    
    ##
    # This triggers an automapping on the whole current map document.
    ##
    def autoMap(self, *args):
        l = len(args)
        if l == 0:
            if (not self.mMapDocument):
                return
            map = self.mMapDocument.Map()
            w = map.width()
            h = map.height()
            self.autoMapInternal(QRect(0, 0, w, h), None)
        elif l==2:
            where, touchedLayer = args
            if (preferences.Preferences.instance().automappingDrawing()):
                self.autoMapInternal(where, touchedLayer)

    ##
    # This function parses a rules file.
    # For each path which is a rule, (fileextension is tmx) an AutoMapper
    # object is setup.
    #
    # If a fileextension is txt, this file will be opened and searched for
    # rules again.
    #
    # @return if the loading was successful: return True if it suceeded.
    ##
    def loadFile(self, filePath):
        ret = True
        absPath = QFileInfo(filePath).path()
        rulesFile = QFile(filePath)
        if (not rulesFile.exists()):
            self.mError += self.tr("No rules file found at:\n%s\n"%filePath)
            return False

        if (not rulesFile.open(QIODevice.ReadOnly | QIODevice.Text)):
            self.mError += self.tr("Error opening rules file:\n%s\n"%filePath)
            return False

        i = QTextStream(rulesFile)
        line = ' '
        while line != '':
            line = i.readLine()
            rulePath = line.strip()
            if (rulePath=='' or rulePath.startswith('#') or rulePath.startswith("//")):
                continue
            if (QFileInfo(rulePath).isRelative()):
                rulePath = absPath + '/' + rulePath
            if (not QFileInfo(rulePath).exists()):
                self.mError += self.tr("File not found:\n%s"%rulePath) + '\n'
                ret = False
                continue

            if (rulePath.endsWith(".tmx", Qt.CaseInsensitive)):
                tmxFormat = TmxMapFormat()
                rules = tmxFormat.read(rulePath)
                if (not rules):
                    self.mError += self.tr("Opening rules map failed:\n%s"%tmxFormat.errorString()) + '\n'
                    ret = False
                    continue

                tilesetManager = TilesetManager.instance()
                tilesetManager.addReferences(rules.tilesets())
                autoMapper = None
                autoMapper = AutoMapper(self.mMapDocument, rules, rulePath)
                self.mWarning += autoMapper.warningString()
                error = autoMapper.errorString()
                if error != '':
                    self.mAutoMappers.append(autoMapper)
                else:
                    self.mError += error
                    del autoMapper

            if (rulePath.endsWith(".txt", Qt.CaseInsensitive)):
                if (not self.loadFile(rulePath)):
                    ret = False
        return ret

    ##
    # Applies automapping to the Region \a where, considering only layer
    # \a touchedLayer has changed.
    # There will only those Automappers be used which have a rule layer
    # touching the \a touchedLayer
    # If layer is 0, all Automappers are used.
    ##
    def autoMapInternal(self, where, touchedLayer):
        self.mError = ''
        self.mWarning = ''
        if (not self.mMapDocument):
            return
        automatic = touchedLayer != None
        if (not self.mLoaded):
            mapPath = QFileInfo(self.mMapDocument.fileName()).path()
            rulesFileName = mapPath + "/rules.txt"
            if (self.loadFile(rulesFileName)):
                self.mLoaded = True
            else:
                self.errorsOccurred.emit(automatic)
                return
                
        passedAutoMappers = QVector()
        if (touchedLayer):
            for a in self.mAutoMappers:
                if (a.ruleLayerNameUsed(touchedLayer.name())):
                    passedAutoMappers.append(a)
        else:
            passedAutoMappers = self.mAutoMappers

        if (not passedAutoMappers.isEmpty()):
            # use a pointer to the region, so each automapper can manipulate it and the
            # following automappers do see the impact
            region = QRegion(where)
        
            undoStack = self.mMapDocument.undoStack()
            undoStack.beginMacro(self.tr("Apply AutoMap rules"))
            aw = AutoMapperWrapper(self.mMapDocument, passedAutoMappers, region)
            undoStack.push(aw)
            undoStack.endMacro()

        for automapper in self.mAutoMappers:
            self.mWarning += automapper.warningString()
            self.mError += automapper.errorString()

        if self.mWarning != '':
            self.warningsOccurred.emit(automatic)
        if self.mError != '':
            self.errorsOccurred.emit(automatic)

    ##
    # deletes all its data structures
    ##
    def cleanUp(self):
        self.mAutoMappers.clear()

