##
# terrainview.py
# Copyright 2008-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2012, Manu Evans
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

from zoomable import Zoomable
from utils import Utils
from terrainmodel import TerrainModel
from PyQt5.QtCore import (
    Qt
)
from PyQt5.QtGui import (
    QIcon
)
from PyQt5.QtWidgets import (
    QMenu,
    QAbstractItemView,
    QTreeView
)
##
# The terrain view. Is expected to be used with the TerrainModel, but will
# also work when it is wrapped by a proxy model.
##
class TerrainView(QTreeView):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.mZoomable = Zoomable(self)
        self.mMapDocument = None

        self.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.setRootIsDecorated(False)
        self.setIndentation(0)
        self.setItemsExpandable(False)
        self.setHeaderHidden(True)
        self.mZoomable.scaleChanged.connect(self.adjustScale)

    def setMapDocument(self, mapDocument):
        self.mMapDocument = mapDocument

    ##
    # Convenience method to get the terrain at a given \a index.
    ##
    def terrainAt(self, index):
        data = self.model().data(index, TerrainModel.UserRoles.TerrainRole)
        return data

    ##
    # Override to support zooming in and out using the mouse wheel.
    ##
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if (event.modifiers()&Qt.ControlModifier and delta!=0):
            self.mZoomable.handleWheelDelta(delta)
            return

        super().wheelEvent(event)

    ##
    # Allow changing terrain properties through a context menu.
    ##
    def contextMenuEvent(self, event):
        terrain = self.terrainAt(self.indexAt(event.pos()))
        if (not terrain):
            return
        isExternal = terrain.tileset().isExternal()
        menu = QMenu()
        propIcon = QIcon(":images/16x16/document-properties.png")
        terrainProperties = menu.addAction(propIcon,
                                                 self.tr("Terrain Properties..."))
        terrainProperties.setEnabled(not isExternal)
        Utils.setThemeIcon(terrainProperties, "document-properties")
        menu.addSeparator()
        terrainProperties.triggered.connect(self.editTerrainProperties)
        menu.exec(event.globalPos())

    def editTerrainProperties(self):
        terrain = self.terrainAt(self.selectionModel().currentIndex())
        if (not terrain):
            return
        self.mMapDocument.setCurrentObject(terrain)
        self.mMapDocument.emitEditCurrentObject()

    def adjustScale(self):
        #terrainModel().tilesetChanged()
        pass
