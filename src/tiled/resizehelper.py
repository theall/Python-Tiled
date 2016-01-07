##
# resizehelper.py
# Copyright 2008-2009, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
    QSize,
    QRect,
    pyqtSignal,
    QPoint
)
from PyQt5.QtGui import (
    QPen,
    QPainter
)
from PyQt5.QtWidgets import (
    QWidget
)
##
# A special widget designed as an aid for resizing a canvas. Based on a
# similar widget used by the GIMP.
##
class ResizeHelper(QWidget):
    offsetChanged = pyqtSignal(QPoint)
    offsetXChanged = pyqtSignal(int)
    offsetYChanged = pyqtSignal(int)
    offsetBoundsChanged = pyqtSignal(QRect)

    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.mMouseAnchorPoint = QPoint()
        self.mOffset = QPoint()
        self.mOldSize = QSize()
        self.mDragging = False
        self.mOffsetBounds = QRect()
        self.mScale = 0.0
        self.mNewSize = QSize()
        self.mOrigOffset = QPoint()
        
        self.setMinimumSize(20, 20)
        self.setOldSize(QSize(1, 1))

    def oldSize(self):
        return self.mOldSize

    def newSize(self):
        return self.mNewSize

    def offset(self):
        return self.mOffset

    def offsetBounds(self):
        return self.mOffsetBounds

    def setOldSize(self, size):
        self.mOldSize = size
        self.recalculateMinMaxOffset()
        self.recalculateScale()

    def setNewSize(self, size):
        self.mNewSize = size
        self.recalculateMinMaxOffset()
        self.recalculateScale()

    def setOffset(self, offset):
        # Clamp the offset within the offset bounds
        newOffset = QPoint(min(self.mOffsetBounds.right(),
                            max(self.mOffsetBounds.left(), offset.x())),
                                min(self.mOffsetBounds.bottom(),
                                    max(self.mOffsetBounds.top(), offset.y())))
        if (self.mOffset != newOffset):
            xChanged = self.mOffset.x() != newOffset.x()
            yChanged = self.mOffset.y() != newOffset.y()
            self.mOffset = newOffset
            if (xChanged):
                self.offsetXChanged.emit(self.mOffset.x())
            if (yChanged):
                self.offsetYChanged.emit(self.mOffset.y())
            self.offsetChanged.emit(self.mOffset)
            self.update()

    ## Method to set only the X offset, provided for convenience. */
    def setOffsetX(self, x):
        self.setOffset(QPoint(x, self.mOffset.y()))

    ## Method to set only the Y offset, provided for convenience. */
    def setOffsetY(self, y):
        self.setOffset(QPoint(self.mOffset.x(), y))

    ## Method to set only new width, provided for convenience. */
    def setNewWidth(self, width):
        self.mNewSize.setWidth(width)
        self.recalculateMinMaxOffset()
        self.recalculateScale()

    ## Method to set only new height, provided for convenience. */
    def setNewHeight(self, height):
        self.mNewSize.setHeight(height)
        self.recalculateMinMaxOffset()
        self.recalculateScale()

    def paintEvent(self, event):
        _size = self.size() - QSize(2, 2)
        if (_size.isEmpty()):
            return
        origX = (_size.width() - self.mNewSize.width() * self.mScale) / 2 + 0.5
        origY = (_size.height() - self.mNewSize.height() * self.mScale) / 2 + 0.5
        oldRect = QRect(self.mOffset, self.mOldSize)
        painter = QPainter(self)
        painter.translate(origX, origY)
        painter.scale(self.mScale, self.mScale)
        pen = QPen(Qt.black)
        pen.setCosmetic(True)
        painter.setPen(pen)
        painter.drawRect(QRect(QPoint(0, 0), self.mNewSize))
        pen.setColor(Qt.white)
        painter.setPen(pen)
        painter.setBrush(Qt.white)
        painter.setOpacity(0.5)
        painter.drawRect(oldRect)
        pen.setColor(Qt.black)
        pen.setStyle(Qt.DashLine)
        painter.setOpacity(1.0)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(pen)
        painter.drawRect(oldRect)
        painter.end()

    def mousePressEvent(self, event):
        self.mMouseAnchorPoint = event.pos()
        self.mOrigOffset = self.mOffset
        self.mDragging = event.button() == Qt.LeftButton

    def mouseMoveEvent(self, event):
        if (not self.mDragging):
            return
        pos = event.pos()
        if (pos != self.mMouseAnchorPoint):
            self.setOffset(self.mOrigOffset + (pos - self.mMouseAnchorPoint) / self.mScale)
            self.offsetChanged.emit(self.mOffset)

    def resizeEvent(self, event):
        self.recalculateScale()

    def recalculateScale(self):
        _size = self.size() - QSize(2, 2)
        if (_size.isEmpty()):
            return
        if self.mOldSize.width() < self.mNewSize.width():
            width = self.mNewSize.width()
        else:
            width = 2 * self.mOldSize.width() - self.mNewSize.width()
        if self.mOldSize.height() < self.mNewSize.height():
            height = self.mNewSize.height()
        else:
            height = 2 * self.mOldSize.height() - self.mNewSize.height()

        # Pick the smallest scale
        scaleW = _size.width() / width
        scaleH = _size.height() / height
        if scaleW < scaleH:
            self.mScale = scaleW
        else:
            self.mScale = scaleH

        self.update()

    def recalculateMinMaxOffset(self):
        offsetBounds = self.mOffsetBounds
        if (self.mOldSize.width() <= self.mNewSize.width()):
            offsetBounds.setLeft(0)
            offsetBounds.setRight(self.mNewSize.width() - self.mOldSize.width())
        else:
            offsetBounds.setLeft(self.mNewSize.width() - self.mOldSize.width())
            offsetBounds.setRight(0)

        if (self.mOldSize.height() <= self.mNewSize.height()):
            offsetBounds.setTop(0)
            offsetBounds.setBottom(self.mNewSize.height() - self.mOldSize.height())
        else:
            offsetBounds.setTop(self.mNewSize.height() - self.mOldSize.height())
            offsetBounds.setBottom(0)

        if (self.mOffsetBounds != offsetBounds):
            self.mOffsetBounds = offsetBounds
            self.offsetBoundsChanged.emit(self.mOffsetBounds)
