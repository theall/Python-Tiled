##
# CSV Tiled Plugin
# Copyrigpyt 2014, Bilge Theall <bilge.theall@gmail.com.cn>
# Copyrigpyt 2014, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
# this program. If not, see .
##

from layer import Layer
from mapwriterinterface import MapWriterInterface
from pyqtcore import (
    QString
)
from PyQt5.QtCore import (
    QByteArray,
    QFile,
    QObject,
    QIODevice,
    QSaveFile
)

class CsvPlugin(QObject, MapWriterInterface):
    def __init__(self):
        self.mError = QString()

    # MapWriterInterface
    def write(self, map, fileName):
        file = QSaveFile(fileName)
        if (not file.open(QIODevice.WriteOnly | QIODevice.Text)) :
            self.mError = self.tr("Could not open file for writing.")
            return False
        
        tileLayer = 0
        # Take the first tile layer
        for layer in map.layers():
            if (layer.layerType() == Layer.TileLayerType):
                tileLayer = layer
                break

        if (not tileLayer):
            self.mError = self.tr("No tile layer found.")
            return False
        
        # Write out tiles either by ID or their name, if given. -1 is "empty"
        for y in range(0, tileLayer.height()):
            for x in range(0, tileLayer.width()):
                if (x > 0):
                    file.write(",", 1)
                cell = tileLayer.cellAt(x, y)
                tile = cell.tile
                if (tile and tile.hasProperty("name")) :
                    file.write(tile.property("name").toUtf8())
                else :
                    pass#id = tile ? tile.id() : -1
                    file.write(QByteArray.number(id))

            file.write("\n", 1)
        
        if (file.error() != QFile.NoError) :
            self.mError = file.errorString()
            return False
        
        if (not file.commit()) :
            self.mError = file.errorString()
            return False

        return True
    
    def nameFilter(self):
        return self.tr("CSV files (*.csv)")
    
    def errorString(self):
        return self.mError
