##
# tmxmapformat.py
# Copyright 2008-2015, Thorbjørn Lindeijer <bjorn@lindeijer.nl>
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
import preferences
from mapwriter import MapWriter
from mapreader import MapReader
from tilesetformat import TilesetFormat
from mapformat import MapFormat
from PyQt5.QtCore import (
    QBuffer,
    QIODevice,
    QDir, 
    Qt
)

##
# A reader and writer for Tiled's .tmx map format.
##
class TmxMapFormat(MapFormat):

    def __init__(self):
        super().__init__()
        self.mError = ''
        
    def read(self, fileName):
        self.mError = ''
        reader = EditorMapReader()
        map = reader.readMap(fileName)
        if (not map):
            self.mError = reader.errorString()
        return map
        
    def write(self, map, fileName):
        prefs = preferences.Preferences.instance()
        writer = MapWriter()
        writer.setDtdEnabled(prefs.dtdEnabled())
        result = writer.writeMap(map, fileName)
        if (not result):
            self.mError = writer.errorString()
        else:
            self.mError = ''
        return result
    
    ##
    # Converts the given map to a utf8 byte array (in .tmx format). This is
    # for storing a map in the clipboard. References to other files (like
    # tileset images) will be saved as absolute paths.
    #
    # @see fromByteArray
    ##
    def toByteArray(self, map):
        buffer = QBuffer()
        buffer.open(QIODevice.WriteOnly)
        writer = MapWriter()
        writer.writeMap(map, buffer)
        return buffer.data()
    
    ##
    # Reads the map given from \a data. This is for retrieving a map from the
    # clipboard. Returns null on failure.
    #
    # @see toByteArray
    ##
    def fromByteArray(self, data):
        self.mError = ''
        buffer = QBuffer()
        buffer.setData(data)
        buffer.open(QBuffer.ReadOnly)
        reader = EditorMapReader()
        map = reader.readMap(buffer)
        if (not map):
            self.mError = reader.errorString()
        return map
        
    def nameFilter(self):
        return self.tr("Tiled map files (*.tmx)")
        
    def supportsFile(self, fileName):
        return fileName.lower().endswith(".tmx")
        
    def errorString(self):
        return self.mError


##
# A reader and writer for Tiled's .tsx tileset format.
##
class TsxTilesetFormat(TilesetFormat):

    def __init__(self):
        super().__init__()
        
    def read(self, fileName):
        self.mError = ''
        reader = EditorMapReader()
        tileset = reader.readTileset(fileName)
        if (not tileset):
            self.mError = reader.errorString()
        return tileset
    
    def write(self, tileset, fileName):
        prefs = preferences.Preferences.instance()
        writer = MapWriter()
        writer.setDtdEnabled(prefs.dtdEnabled())
        result = writer.writeTileset(tileset, fileName)
        if (not result):
            self.mError = writer.errorString()
        else:
            self.mError = ''
        return result
    
    def nameFilter(self):
        return self.tr("Tiled tileset files (*.tsx)")
        
    def supportsFile(fileName):
        return fileName.lower().endswith(".tsx")
        
    def errorString(self):
        return self.mError
        
class EditorMapReader(MapReader):

    def __init__(self):
        super().__init__()
        
    ##
    # Overridden to make sure the resolved reference is a clean path.
    ##
    def resolveReference(self, reference, mapPath):
        resolved = super().resolveReference(reference, mapPath)
        return QDir.cleanPath(resolved)
    
    ##
    # Overridden in order to check with the TilesetManager whether the tileset
    # is already loaded.
    ##
    def readExternalTileset(self, source):
        error = ''
        # Check if this tileset is already loaded
        manager = TilesetManager.instance()
        tileset = manager.findTileset(source)
        # If not, try to load it
        if (not tileset):
            tileset, error = super().readExternalTileset(source)
        return tileset, error
    
