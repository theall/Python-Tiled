##
# changepolygon.py
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
from PyQt5.QtCore import (
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)
##
# Changes the polygon of a MapObject.
#
# This class expects the polygon to be already changed, and takes the previous
# polygon in the constructor.
##
class ChangePolygon(QUndoCommand):
    def __init__(self, *args):
        super().__init__()
        
        l = len(args)
        if l==3:
            mapDocument, mapObject, oldPolygon = args
            newPolygon = mapObject.polygon()
        elif l==4:
            mapDocument, mapObject, newPolygon, oldPolygon = args
            
        self.mMapDocument = mapDocument
        self.mMapObject = mapObject
        self.mOldPolygon = oldPolygon
        self.mNewPolygon = newPolygon
        self.setText(QCoreApplication.translate("Undo Commands", "Change Polygon"))
        
    def undo(self):
        self.mMapDocument.mapObjectModel().setObjectPolygon(self.mMapObject, self.mOldPolygon)

    def redo(self):
        self.mMapDocument.mapObjectModel().setObjectPolygon(self.mMapObject, self.mNewPolygon)
