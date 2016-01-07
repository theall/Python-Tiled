##
# createpolygonobjecttool.py
# Copyright 2014, Martin Ziel
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

from mapobject import MapObject
from createmultipointobjecttool import CreateMultipointObjectTool
from PyQt5.QtGui import QIcon, QKeySequence

class CreatePolygonObjectTool(CreateMultipointObjectTool):
    def __init__(self, parent):
        super().__init__(parent)

        self.setIcon(QIcon(":images/24x24/insert-polygon.png"))
        self.languageChanged()

    def languageChanged(self):
        self.setName(self.tr("Insert Polygon"))
        self.setShortcut(QKeySequence(self.tr("P")))

    def createNewMapObject(self):
        newMapObject = MapObject()
        newMapObject.setShape(MapObject.Polygon)
        return newMapObject

    def finishNewMapObject(self):
        if (self.mNewMapObjectItem.mapObject().polygon().size() >= 3):
            super().finishNewMapObject()
        else:
            super().cancelNewMapObject()
