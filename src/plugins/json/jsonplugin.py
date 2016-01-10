##
# JSON Tiled Plugin
# Copyright 2011, Porfírio José Pereira Ribeiro <porfirioribeiro@gmail.com>
# Copyright 2011, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

import json
from varianttomapconverter import VariantToMapConverter
from maptovariantconverter import MapToVariantConverter
from plugin import Plugin
from mapformat import MapFormat
from tilesetformat import TilesetFormat
from PyQt5.QtCore import (
    Qt,
    QIODevice,
    QSaveFile,
    QFileInfo,
    QTextStream,
    QFile, 
    QCoreApplication
)   
    
class JsonPlugin(Plugin):
    def __init__(self):
        super().__init__()
        
        self.mError = ''
        
    def initialize(self):
        Plugin.addObject(JsonMapFormat(JsonMapFormat.SubFormat.Json, self))
        Plugin.addObject(JsonMapFormat(JsonMapFormat.SubFormat.JavaScript, self))
        Plugin.addObject(JsonTilesetFormat(self))

    def errorString(self):
        return self.mError

class JsonMapFormat(MapFormat):
    class SubFormat():
        Json = 0
        JavaScript = 1
    
    def __init__(self, subFormat, parent=None):
        super().__init__(parent)
        
        self.mSubFormat = subFormat
        self.mError = ''
        
    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('JsonMapFormat', sourceText, disambiguation, n)
        
    # MapReaderInterface
    def read(self, fileName):
        file = QFile(fileName)
        if (not file.open(QIODevice.ReadOnly | QIODevice.Text)) :
            self.mError = self.tr("Could not open file for reading.")
            return None
        
        contents = file.readAll()
        contents = contents.data().decode()
        if (self.mSubFormat == JsonMapFormat.SubFormat.JavaScript and len(contents) > 0 and contents[0] != '{') :
            # Scan past JSONP prefix; look for an open curly at the start of the line
            i = contents.index("\n{")
            if (i > 0) :
                contents = contents[i:]
                contents = contents.strip() # potential trailing whitespace
                if (contents.endswith(';')):
                    contents = contents[:-1]
                if (contents.endswith(')')):
                    contents = contents[:-1]
        
        try:
            variant = json.loads(contents)
        except:
            self.mError = self.tr("Error parsing file.")
            return None
        
        converter = VariantToMapConverter()
        map = converter.toMap(variant, QFileInfo(fileName).dir())
        if (not map):
            self.mError = converter.errorString()
        return map

    # MapWriterInterface
    def write(self, map, fileName):
        file = QSaveFile(fileName)
        if (not file.open(QIODevice.WriteOnly | QIODevice.Text)) :
            self.mError = self.tr("Could not open file for writing.")
            return False
        
        converter = MapToVariantConverter()
        variant = converter.toVariant(map, QFileInfo(fileName).dir())
        
        writer = json
        try:
            result = writer.dumps(variant, indent=4)
        except:
            # This can only happen due to coding error
            self.mError = self.tr('Unknow error.')
            return False
        
        out = QTextStream(file)
        if self.mSubFormat == JsonMapFormat.SubFormat.JavaScript:
            # Trim and escape name
            nameWriter = json
            baseName = QFileInfo(fileName).baseName()
            baseNameResult = nameWriter.dumps(baseName)
            out << "(function(name,data){\n if(typeof onTileMapLoaded === 'undefined') {\n"
            out << "  if(typeof TileMaps === 'undefined') TileMaps = {};\n"
            out << "  TileMaps[name] = data;\n"
            out << " } else {\n"
            out << "  onTileMapLoaded(name,data);\n"
            out << " }})(" + baseNameResult + ",\n"
        
        out << result
        if self.mSubFormat == JsonMapFormat.SubFormat.JavaScript:
            out << ");"
        
        out.flush()
        if (file.error() != QFile.NoError) :
            self.mError = self.tr("Error while writing file:\n%1").arg(file.errorString())
            return False

        if (not file.commit()) :
            self.mError = file.errorString()
            return False
        
        return True
    
    # Both interfaces
    def nameFilter(self):
        if self.mSubFormat == JsonMapFormat.SubFormat.Json:
            return self.tr("Json map files (*.json)")
        else:
            return self.tr("JavaScript map files (*.js)")

    def supportsFile(self, fileName):
        if (self.mSubFormat == JsonMapFormat.SubFormat.Json):
            return fileName.endswith(".json", Qt.CaseInsensitive)
        else:
            return fileName.endswith(".js", Qt.CaseInsensitive)

    def errorString(self):
        return self.mError

class JsonTilesetFormat(TilesetFormat):
    def __init__(self, parent=None):
        super().__init__(parent)

    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('JsonTilesetFormat', sourceText, disambiguation, n)
        
    def read(self, fileName):
        file = QFile(fileName)
        if (not file.open(QIODevice.ReadOnly | QIODevice.Text)):
            self.mError = self.tr("Could not open file for reading.")
            return None
        
        reader = json
        contents = file.readAll()
        reader.loads(contents)
        variant = reader.result()
        if (not variant.isValid()):
            self.mError = self.tr("Error parsing file.")
            return None
        
        converter = VariantToMapConverter()
        tileset = converter.toTileset(variant, QFileInfo(fileName).dir())
        if (not tileset):
            self.mError = converter.errorString()
        else:
            tileset.setFileName(fileName)
        return tileset

    def supportsFile(self, fileName):
        return fileName.lower().endswith(".json")

    def write(self, tileset, fileName):
        file = QSaveFile(fileName)
        if (not file.open(QIODevice.WriteOnly | QIODevice.Text)):
            self.mError = self.tr("Could not open file for writing.")
            return False
        
        converter = MapToVariantConverter()
        variant = converter.toVariant(tileset, QFileInfo(fileName).dir())
        writer = json
        try:
            result = writer.dumps(variant, indent=4)
        except:
            # This can only happen due to coding error
            self.mError = self.tr('Unknow error.')
            return False
        
        out = QTextStream(file)
        out << result
        out.flush()
        if (file.error() != QFile.NoError):
            self.mError = self.tr("Error while writing file:\n%1").arg(file.errorString())
            return False
        
        if (not file.commit()):
            self.mError = file.errorString()
            return False
        
        return True

    def nameFilter(self):
        return self.tr("Json tileset files (*.json)")

    def errorString(self):
        return self.mError
