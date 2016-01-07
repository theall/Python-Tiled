##
# mapview.py
# Copyright 2008-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

import sys
from zoomable import Zoomable
import preferences
from PyQt5.QtCore import (
    Qt,
    QPoint,
    QEvent,
    QPointF
)
from PyQt5.QtGui import (
    QCursor,
    QPainter,
    QTransform
)
from PyQt5.QtWidgets import (
    QFrame,
    QApplication,
    QPinchGesture,
    QGraphicsView
)
from PyQt5.QtOpenGL import QGLFormat, QGLWidget
QT_NO_OPENGL = False

##
# Using Qt.WA_StaticContents gives a performance boost in certain
# resizing operations. There is however a problem with it when used in
# child windows, so this option allows it to be turned off in that case.
#
# See https://codereview.qt-project.org/#change,74595 for my attempt at
# fixing the problem in Qt.
##
class MapViewMode():
    StaticContents = 0
    NoStaticContents = 1

##
# The map view shows the map scene. This class sets some MapScene specific
# properties on the viewport and implements zooming. It also allows the view
# to be scrolled with the middle mouse button.
#
# @see MapScene
##
class MapView(QGraphicsView):

    def __init__(self, parent = None, mode = MapViewMode.StaticContents):
        super().__init__(parent)
        self.mHandScrolling = False
        self.mMode = mode
        self.mZoomable = Zoomable(self)
        self.mLastMousePos = QPoint()
        self.mLastMouseScenePos = QPointF()

        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
        if sys.platform == 'darwin':
            self.setFrameStyle(QFrame.NoFrame)
        if not QT_NO_OPENGL:
            prefs = preferences.Preferences.instance()
            self.setUseOpenGL(prefs.useOpenGL())
            prefs.useOpenGLChanged.connect(self.setUseOpenGL)

        v = self.viewport()
        ## Since Qt 4.5, setting this attribute yields significant repaint
        # reduction when the view is being resized. */
        if (self.mMode == MapViewMode.StaticContents):
            v.setAttribute(Qt.WA_StaticContents)
        ## Since Qt 4.6, mouse tracking is disabled when no graphics item uses
        # hover events. We need to set it since our scene wants the events. */
        v.setMouseTracking(True)
        # Adjustment for antialiasing is done by the items that need it
        self.setOptimizationFlags(QGraphicsView.DontAdjustForAntialiasing)
        self.grabGesture(Qt.PinchGesture)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.mZoomable.scaleChanged.connect(self.adjustScale)

    def __del__(self):
        self.setHandScrolling(False) # Just in case we didn't get a hide event

    def mapScene(self):
        return self.scene()

    def zoomable(self):
        return self.mZoomable

    def handScrolling(self):
        return self.mHandScrolling

    def setHandScrolling(self, handScrolling):
        if (self.mHandScrolling == handScrolling):
            return
        self.mHandScrolling = handScrolling
        self.setInteractive(not self.mHandScrolling)
        if (self.mHandScrolling):
            self.mLastMousePos = QCursor.pos()
            QApplication.setOverrideCursor(QCursor(Qt.ClosedHandCursor))
            self.viewport().grabMouse()
        else:
            self.viewport().releaseMouse()
            QApplication.restoreOverrideCursor()

    def event(self, e):
        # Ignore space bar events since they're handled by the MainWindow
        if (e.type() == QEvent.KeyPress or e.type() == QEvent.KeyRelease):
            if (e).key() == Qt.Key_Space:
                e.ignore()
                return False
        elif (e.type() == QEvent.Gesture):
            gestureEvent = e
            gesture = gestureEvent.gesture(Qt.PinchGesture)
            if gesture:
                pinch = gesture
                if (pinch.changeFlags() & QPinchGesture.ScaleFactorChanged):
                    self.handlePinchGesture(pinch)

        return super().event(e)

    def hideEvent(self, event):
        # Disable hand scrolling when the view gets hidden in any way
        self.setHandScrolling(False)
        super().hideEvent(event)

    ##
    # Override to support zooming in and out using the mouse wheel.
    ##
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if (event.modifiers()&Qt.ControlModifier and delta!=0):

            # No automatic anchoring since we'll do it manually
            self.setTransformationAnchor(QGraphicsView.NoAnchor)
            self.mZoomable.handleWheelDelta(delta)
            self.adjustCenterFromMousePosition(self.mLastMousePos)
            # Restore the centering anchor
            self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
            return

        super().wheelEvent(event)
        # When scrolling the mouse does not move, but the view below it does.
        # This affects the mouse scene position, which needs to be updated.
        self.mLastMouseScenePos = self.mapToScene(self.viewport().mapFromGlobal(self.mLastMousePos))

    ##
    # Activates hand scrolling when the middle mouse button is pressed.
    ##
    def mousePressEvent(self, event):
        if (event.button() == Qt.MidButton and self.isActiveWindow()):
            self.setHandScrolling(True)
            return

        super().mousePressEvent(event)

    ##
    # Deactivates hand scrolling when the middle mouse button is released.
    ##
    def mouseReleaseEvent(self, event):
        if (event.button() == Qt.MidButton):
            self.setHandScrolling(False)
            return

        super().mouseReleaseEvent(event)

    ##
    # Moves the view with the mouse while hand scrolling.
    ##
    def mouseMoveEvent(self, event):
        if (self.mHandScrolling):
            hBar = self.horizontalScrollBar()
            vBar = self.verticalScrollBar()
            d = event.globalPos() - self.mLastMousePos
            if (self.isRightToLeft()):
                _x = d.x()
            else:
                _x = -d.x()
            hBar.setValue(hBar.value() + _x)
            vBar.setValue(vBar.value() - d.y())
            self.mLastMousePos = event.globalPos()
            return

        super().mouseMoveEvent(event)
        self.mLastMousePos = event.globalPos()
        self.mLastMouseScenePos = self.mapToScene(self.viewport().mapFromGlobal(self.mLastMousePos))

    def handlePinchGesture(self, pinch):
        self.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.mZoomable.handlePinchGesture(pinch)
        centerPoint = pinch.hotSpot().toPoint()
        self.adjustCenterFromMousePosition(centerPoint)
        self.setTransformationAnchor(QGraphicsView.AnchorViewCenter)

    def adjustCenterFromMousePosition(self, mousePos):
        # Place the last known mouse scene pos below the mouse again
        view = self.viewport()
        viewCenterScenePos = self.mapToScene(view.rect().center())
        mouseScenePos = self.mapToScene(view.mapFromGlobal(mousePos))
        diff = viewCenterScenePos - mouseScenePos
        self.centerOn(self.mLastMouseScenePos + diff)

    def adjustScale(self, scale):
        self.setTransform(QTransform.fromScale(scale, scale))
        self.setRenderHint(QPainter.SmoothPixmapTransform, self.mZoomable.smoothTransform())

    def setUseOpenGL(self, useOpenGL):
        if not QT_NO_OPENGL:
            if (useOpenGL and QGLFormat.hasOpenGL()):
                if (not self.viewport()):
                    format = QGLFormat.defaultFormat()
                    format.setDepth(False) # No need for a depth buffer
                    format.setSampleBuffers(True) # Enable anti-aliasing
                    self.setViewport(QGLWidget(format))

            else:
                if self.viewport():
                    self.setViewport(None)

            v = self.viewport()
            if (self.mMode == MapViewMode.StaticContents):
                v.setAttribute(Qt.WA_StaticContents)
            v.setMouseTracking(True)
        else:
            pass
