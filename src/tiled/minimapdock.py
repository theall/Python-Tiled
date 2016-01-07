##
# minimapdock.py
# Copyright 2012, Christoph Schnackenberg
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
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
##

from minimap import MiniMap
from PyQt5.QtCore import (
    QEvent
)
from PyQt5.QtWidgets import (
    QDockWidget
)
##
# Shows a mini-map.
##
class MiniMapDock(QDockWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setObjectName("miniMapDock")
        self.mMiniMap = MiniMap(self)
        self.setWidget(self.mMiniMap)
        self.retranslateUi()

    def setMapDocument(self, map):
        self.mMiniMap.setMapDocument(map)

    def changeEvent(self, e):
        super().changeEvent(e)
        x = e.type()
        if x==QEvent.LanguageChange:
            self.retranslateUi()
        else:
            pass

    def retranslateUi(self):
        self.setWindowTitle(self.tr("Mini-map"))
