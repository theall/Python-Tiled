##
# undodock.py
# Copyright 2009, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2010, Petr Viktorin
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

from PyQt5.QtGui import (
    QIcon
)
from PyQt5.QtCore import (
    Qt,
    QEvent
)
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QUndoView,
    QDockWidget
)
##
# A dock widget showing the undo stack. Mainly for debugging, but can also be
# useful for the user.
##
class UndoDock(QDockWidget):

    def __init__(self, undoGroup, parent = None):
        super().__init__(parent)

        self.setObjectName("undoViewDock")
        self.mUndoView = QUndoView(undoGroup, self)
        cleanIcon = QIcon(":images/16x16/drive-harddisk.png")
        self.mUndoView.setCleanIcon(cleanIcon)
        self.mUndoView.setUniformItemSizes(True)
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.addWidget(self.mUndoView)
        self.setWidget(widget)
        self.retranslateUi()

    def changeEvent(self, e):
        super().changeEvent(e)
        x = e.type()
        if x==QEvent.LanguageChange:
            self.retranslateUi()
        else:
            pass

    def retranslateUi(self):
        self.setWindowTitle(self.tr("History"))
        self.mUndoView.setEmptyLabel(self.tr("<empty>"))
