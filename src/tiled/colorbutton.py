##
# colorbutton.py
# Copyright 2009, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
    pyqtSignal,
    QSize
)
from PyQt5.QtGui import (
    QPainter,
    QColor,
    QPixmap,
    QIcon
)
from PyQt5.QtWidgets import (
    QColorDialog,
    QToolButton
)
##
# A tool button for letting the user pick a color. When clicked it shows a
# color dialog and it has an icon to represent the currently chosen color.
##
class ColorButton(QToolButton):
    colorChanged = pyqtSignal(QColor)

    def __init__(self, parent = None):
        super().__init__(parent)

        self.mColor = QColor()
        self.setColor(Qt.white)
        self.clicked.connect(self.pickColor)

    def color(self):
        return self.mColor
        
    def setColor(self, color):
        if type(color)!=QColor:
            color = QColor(color)
        if (self.mColor == color or not color.isValid()):
            return
        self.mColor = color
        size = QSize(self.iconSize())
        size.setWidth(size.width()-2)
        size.setHeight(size.height()-2)
        pixmap = QPixmap(size)
        pixmap.fill(self.mColor)
        painter = QPainter(pixmap)
        border = QColor(Qt.black)
        border.setAlpha(128)
        painter.setPen(border)
        painter.drawRect(0, 0, pixmap.width() - 1, pixmap.height() - 1)
        painter.end()
        self.setIcon(QIcon(pixmap))
        self.colorChanged.emit(color)

    def pickColor(self):
        newColor = QColorDialog.getColor(self.mColor, self)
        if (newColor.isValid()):
            self.setColor(newColor)
