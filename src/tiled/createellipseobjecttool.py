##
# createellipseobjecttool.py
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
from utils import Utils
from mapobject import MapObject
from createscalableobjecttool import CreateScalableObjectTool
from PyQt5.QtGui import (
    QIcon,
    QKeySequence
)
class CreateEllipseObjectTool(CreateScalableObjectTool):
    def __init__(self, parent):
        super().__init__(parent)

        self.setIcon(QIcon(":images/24x24/insert-ellipse.png"))
        Utils.setThemeIcon(self, "insert-ellipse")
        self.languageChanged()

    def languageChanged(self):
        self.setName(self.tr("Insert Ellipse"))
        self.setShortcut(QKeySequence(self.tr("C")))

    def createNewMapObject(self):
        newMapObject = MapObject()
        newMapObject.setShape(MapObject.Ellipse)
        return newMapObject
