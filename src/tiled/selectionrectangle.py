##
# selectionrectangle.py
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
    Qt,
    QRectF
)
from PyQt5.QtGui import (
    QPen,
    QColor
)
from PyQt5.QtWidgets import (
    QApplication,
    QGraphicsItem
)
##
# The rectangle used for indicating the dragged area when selecting items.
##
class SelectionRectangle(QGraphicsItem):

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setZValue(10000)

        self.mRectangle = QRectF()

    def setRectangle(self, rectangle):
        self.prepareGeometryChange()
        self.mRectangle = rectangle

    def boundingRect(self):
        return self.mRectangle.adjusted(-1, -1, 2, 2)

    def paint(self, painter, option, widget = None):
        if (self.mRectangle.isNull()):
            return
        # Draw a shadow
        black = QColor(Qt.black)
        black.setAlpha(128)
        pen = QPen(black, 2, Qt.DotLine)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawRect(self.mRectangle.translated(1, 1))
        # Draw a rectangle in the highlight color
        highlight = QApplication.palette().highlight().color()
        pen.setColor(highlight)
        highlight.setAlpha(32)
        painter.setPen(pen)
        painter.setBrush(highlight)
        painter.drawRect(self.mRectangle)
