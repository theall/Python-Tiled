##
# The Mana World Tiled Plugin
# Copyright 2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from mapformat import WritableMapFormat
from PyQt5.QtCore import (
    QDataStream,
    QSaveFile,
    QIODevice
)
class TmwPlugin(WritableMapFormat):
    def __init__(self):
        super().__init__()
        
        self.mError = ''

    # MapWriterInterface
    def write(self, map, fileName):
        collisionLayer = None
        for layer in map.layers():
            if layer.name().lower() == "collision":
                tileLayer = layer.asTileLayer()
                if tileLayer:
                    if (collisionLayer) :
                        self.mError = self.tr("Multiple collision layers found!")
                        return False
                    
                    collisionLayer = tileLayer

        
        if (not collisionLayer) :
            self.mError = self.tr("No collision layer found!")
            return False
        
        file = QSaveFile(fileName)
        if (not file.open(QIODevice.WriteOnly)) :
            self.mError = self.tr("Could not open file for writing.")
            return False
        
        width = collisionLayer.width()
        height = collisionLayer.height()
        stream = QDataStream(file)
        stream.setByteOrder(QDataStream.LittleEndian)
        stream.writeInt16(width&0xffff)
        stream.writeInt16(height&0xffff)
        for y in range(0, height):
            for x in range(0, width):
                tile = collisionLayer.cellAt(x, y).tile
                stream.writeInt8(int(tile and tile.id()> 0)&0xff)

        if not file.commit():
            self.mError = file.errorString()
            return False

        return True
    
    def nameFilter(self):
        return self.tr("TMW-eAthena collision files (*.wlk)")
    
    def errorString(self):
        return self.mError
