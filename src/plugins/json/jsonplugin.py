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
from pyqtcore import (
    QStringList
)
from PyQt5.QtCore import (
    Qt,
    QIODevice,
    QSaveFile,
    QFileInfo,
    QTextStream,
    QFile
)   
    
class JsonPlugin(Plugin):
    def __init__(self):
        self.mError = ''

        # MapReaderInterface
    def read(self, fileName):
        file = QFile(fileName)
        if (not file.open(QIODevice.ReadOnly | QIODevice.Text)) :
            self.mError = self.tr("Could not open file for reading.")
            return 0
        
        contents = file.readAll()
        if (fileName.endsWith(".js") and contents.size() > 0 and contents[0] != '{') :
            # Scan past JSONP prefix; look for an open curly at the start of the line
            i = contents.indexOf("\n{")
            if (i > 0) :
                contents.remove(0, i)
                contents = contents.trimmed(); # potential trailing whitespace
                if (contents.endsWith(';')):
                    contents.chop(1)
                if (contents.endsWith(')')):
                    contents.chop(1)

        reader = json.decoder(contents)
        variant = reader.result()
        if (not variant.isValid()) :
            self.mError = self.tr("Error parsing file.")
            return 0
        
        converter = VariantToMapConverter()
        map = converter.toMap(variant, QFileInfo(fileName).dir())
        if (not map):
            self.mError = converter.errorString()
        return map
        
    def supportsFile(self, fileName):
        return fileName.endsWith(".json", Qt.CaseInsensitive) or fileName.endsWith(".js", Qt.CaseInsensitive)
    
    # MapWriterInterface
    def write(self, map, fileName):
        file = QSaveFile(fileName)
        if (not file.open(QIODevice.WriteOnly | QIODevice.Text)) :
            self.mError = self.tr("Could not open file for writing.")
            return False
        
        converter = MapToVariantConverter()
        variant = converter.toVariant(map, QFileInfo(fileName).dir())
        
        writer = json
        writer.setAutoFormatting(True)
        if (not writer.dumps(variant)) :
            # This can only happen due to coding error
            self.mError = writer.errorString()
            return False
        
        out = QTextStream(file)
        isJsFile = fileName.endsWith(".js")
        if (isJsFile) :
            # Trim and escape name
            nameWriter = json
            baseName = QFileInfo(fileName).baseName()
            nameWriter.stringify(baseName)
            out.write("(function(name,data){\n if(typeof onTileMapLoaded === 'undefined'):\n")
            out.write("  if(typeof TileMaps === 'undefined') TileMaps = {};\n")
            out.write("  TileMaps[name] = data;\n")
            out.write(" } else {\n")
            out.write("  onTileMapLoaded(name,data);\n")
            out.write(" }})(" + nameWriter.result() + ",\n")
        
        out.write(writer.result())
        if (isJsFile):
            out.write(");")
        
        out.flush()
        if (file.error() != QFile.NoError) :
            self.mError = self.tr("Error while writing file:\n%1").arg(file.errorString())
            return False

        if (not file.commit()) :
            self.mError = file.errorString()
            return False
        
        return True
    
    # Both interfaces
    def nameFilters(self):
        filters = QStringList()
        filters.append(self.tr("Json files (*.json)"))
        filters.append(self.tr("JavaScript files (*.js)"))
        return filters
    
    def errorString(self):
        return self.mError

