##
# movabletabwidget.py
# Copyright 2014, Sean Humeniuk
# Copyright 2014, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
    pyqtSignal
)
from PyQt5.QtWidgets import (
    QTabWidget
)
##
# A QTabWidget that has movable tabs by default and forwards its QTabBar's
# tabMoved signal.
##
class MovableTabWidget(QTabWidget):
    ##
    # Emitted when a tab is moved from index position \a from to
    # index position \a to.
    ##
    tabMoved = pyqtSignal(int, int)

    ##
    # Constructor
    ##
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setMovable(True)
        self.tabBar().tabMoved.connect(self.tabMoved)

    def moveTab(self, _from, to):
        self.tabBar().moveTab(_from, to)
