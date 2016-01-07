##
# zoomable.py
# Copyright 2009-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from tiled_global import Float
from PyQt5.QtCore import (
    Qt,
    qAbs,
    QRegExp, 
    QObject,
    pyqtSignal
)
from PyQt5.QtGui import (
    QRegExpValidator
)
from PyQt5.QtWidgets import (
    QPinchGesture,
    QComboBox
)
import math
from pyqtcore import QVector, qBound
zoomFactors = [
    0.015625,
    0.03125,
    0.0625,
    0.125,
    0.25,
    0.33,
    0.5,
    0.75,
    1.0,
    1.5,
    2.0,
    3.0,
    4.0,
    5.5,
    8.0,
    11.0,
    16.0,
    23.0,
    32.0,
    45.0,
    64.0,
    90.0,
    128.0,
    180.0,
    256.0
]
zoomFactorCount = len(zoomFactors)

def scaleToString(scale):
    return "%d %%"%int(scale * 100)

##
# This class represents something zoomable. Is has a zoom factor and methods
# to change this factor in several ways.
#
# A class that wants to be zoomable would aggregate this class, and connect
# to the scaleChanged() signal in order to adapt to the new zoom factor.
##
class Zoomable(QObject):
    scaleChanged = pyqtSignal(float)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.mScale = 1
        self.mZoomFactors = QVector()
        self.mGestureStartScale = 0
        self.mComboBox = None
        self.mComboRegExp = QRegExp("^\\s*(\\d+)\\s*%?\\s*$")
        self.mComboValidator = None

        for i in range(zoomFactorCount):
            self.mZoomFactors.append(zoomFactors[i])

    def setScale(self, scale):
        if (scale == self.mScale):
            return
        self.mScale = scale
        self.syncComboBox()
        self.scaleChanged.emit(self.mScale)

    def scale(self):
        return self.mScale

    def canZoomIn(self):
        return self.mScale < self.mZoomFactors.last()

    def canZoomOut(self):
        return self.mScale > self.mZoomFactors.first()

    ##
    # Changes the current scale based on the given mouse wheel \a delta.
    #
    # For convenience, the delta is assumed to be in the same units as
    # QWheelEvent.delta, which is the distance that the wheel is rotated,
    # in eighths of a degree.
    ##
    def handleWheelDelta(self, delta):
        if (delta <= -120):
            self.zoomOut()
        elif (delta >= 120):
            self.zoomIn()
        else:
            # We're dealing with a finer-resolution mouse. Allow it to have finer
            # control over the zoom level.
            factor = 1 + 0.3 * qAbs(delta / 8 / 15)
            if (delta < 0):
                factor = 1 / factor
            scale = qBound(self.mZoomFactors.first(),
                                 self.mScale * factor,
                                 self.mZoomFactors.back())
            # Round to at most four digits after the decimal point
            self.setScale(math.floor(scale * 10000 + 0.5) / 10000)

    ##
    # Changes the current scale based on the given pinch gesture.
    ##
    def handlePinchGesture(self, pinch):
        if (not (pinch.changeFlags() & QPinchGesture.ScaleFactorChanged)):
            return
        x = pinch.state()
        if x==Qt.NoGesture:
            pass
        elif x==Qt.GestureStarted:
            self.mGestureStartScale = self.mScale
            # fall through
        elif x==Qt.GestureUpdated:
            factor = pinch.scaleFactor()
            scale = qBound(self.mZoomFactors.first(),
                                 self.mGestureStartScale * factor,
                                 self.mZoomFactors.back())
            self.setScale(math.floor(scale * 10000 + 0.5) / 10000)
        elif x==Qt.GestureFinished:
            pass
        elif x==Qt.GestureCanceled:
            pass

    ##
    # Returns whether images should be smoothly transformed when drawn at the
    # current scale. This is the case when the scale is not 1 and smaller than
    # 2.
    ##
    def smoothTransform(self):
        return self.mScale != 1.0 and self.mScale < 2.0

    def setZoomFactors(self, factors):
        self.mZoomFactors = factors

    def connectToComboBox(self, comboBox):
        if (self.mComboBox):
            self.mComboBox.disconnect()
            if (self.mComboBox.lineEdit()):
                self.mComboBox.lineEdit().disconnect()
            self.mComboBox.setValidator(None)

        self.mComboBox = comboBox
        if type(comboBox) is QComboBox:
            self.mComboBox.clear()
            for scale in self.mZoomFactors:
                self.mComboBox.addItem(scaleToString(scale), scale)
            self.syncComboBox()
            self.mComboBox.activated.connect(self.comboActivated)
            self.mComboBox.setEditable(True)
            self.mComboBox.setInsertPolicy(QComboBox.NoInsert)
            self.mComboBox.lineEdit().editingFinished.connect(self.comboEdited)
            if (not self.mComboValidator):
                self.mComboValidator = QRegExpValidator(self.mComboRegExp, self)
            self.mComboBox.setValidator(self.mComboValidator)

    def zoomIn(self):
        for scale in self.mZoomFactors:
            if (scale > self.mScale):
                self.setScale(scale)
                break

    def zoomOut(self):
        for i in range(self.mZoomFactors.count() - 1, -1, -1):
            if (self.mZoomFactors[i] < self.mScale):
                self.setScale(self.mZoomFactors[i])
                break

    def resetZoom(self):
        self.setScale(1)

    def comboActivated(self, index):
        self.setScale(self.mComboBox.itemData(index))

    def comboEdited(self):
        pos = self.mComboRegExp.indexIn(self.mComboBox.currentText())
        pos != -1
        scale = qBound(self.mZoomFactors.first(), Float(self.mComboRegExp.cap(1)) / 100.0, self.mZoomFactors.last())
        self.setScale(scale)

    def syncComboBox(self):
        if (not self.mComboBox):
            return
        index = self.mComboBox.findData(self.mScale)
        # For a custom scale, the current index must be set to -1
        self.mComboBox.setCurrentIndex(index)
        self.mComboBox.setEditText(scaleToString(self.mScale))
