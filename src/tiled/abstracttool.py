# -*- coding: utf-8 -*-
##
# abstracttool.py
# Copyright 2009-2013, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2010, Jeff Bland <jksb@member.fsf.org>
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

from PyQt5.QtGui import (
    QIcon, 
    QCursor, 
    QKeySequence
)
from PyQt5.QtCore import (
    QObject,
    pyqtSignal, 
    pyqtProperty
)

###
# An abstraction of any kind of tool used to edit the map.
#
# Events that hit the MapScene are forwarded to the current tool, which can
# handle them as appropriate for that tool.
#
# A tool will usually add one or more QGraphicsItems to the scene in order to
# represent it to the user.
##
class AbstractTool(QObject):
    statusInfoChanged = pyqtSignal(str)
    cursorChanged = pyqtSignal(QCursor)
    enabledChanged = pyqtSignal(bool)

    ###
    # Constructs an abstract tool with the given \a name and \a icon.
    ##
    def __init__(self, name, icon, shortcut, parent = None):
        super().__init__(parent)
        
        self.mName = name
        self.mIcon = icon
        self.mShortcut = shortcut
        self.mStatusInfo = ''
        self.mEnabled = False
        self.mMapDocument = None
        self.mCursor = QCursor()
        
    def __del__(self):
        pass

    def name(self):
        return self.mName

    def setName(self, name):
        self.mName = name

    def icon(self):
        return self.mIcon

    def setIcon(self, icon):
        self.mIcon = icon

    def shortcut(self):
        return self.mShortcut

    def setShortcut(self, shortcut):
        self.mShortcut = shortcut

    def statusInfo(self):
        return self.mStatusInfo

    def setStatusInfo(self, statusInfo):
        if (self.mStatusInfo != statusInfo):
            self.mStatusInfo = statusInfo
            self.statusInfoChanged.emit(self.mStatusInfo)

    def cursor(self):
        return self.mCursor
    
    ##
    # Sets the cursor used by this tool. This will be the cursor set on the
    # viewport of the MapView while the tool is active.
    ##
    def setCursor(self, cursor):
        if type(cursor)!= QCursor:
            cursor = QCursor(cursor)
        self.mCursor = cursor
        self.cursorChanged.emit(cursor)

    def isEnabled(self):
        return self.mEnabled

    def setEnabled(self, enabled):
        if (self.mEnabled == enabled):
            return
        self.mEnabled = enabled
        self.enabledChanged.emit(self.mEnabled)

    ###
    # Activates this tool. If the tool plans to add any items to the scene, it
    # probably wants to do it here.
    ##
    def activate(self, scene):
        pass

    ###
    # Deactivates this tool. Should do any necessary cleanup to make sure the
    # tool is no longer active.
    ##
    def deactivate(self, scene):
        pass

    def keyPressed(self, event):
        event.ignore()

    ###
    # Called when the mouse entered the scene. This is usually an appropriate
    # time to make a hover item visible.
    ##
    def mouseEntered(self):
        pass

    ###
    # Called when the mouse left the scene.
    ##
    def mouseLeft(self):
        pass

    ###
    # Called when the mouse cursor moves in the scene.
    ##
    def mouseMoved(self, pos, modifiers):
        pass

    ###
    # Called when a mouse button is pressed on the scene.
    ##
    def mousePressed(self, event):
        pass

    ###
    # Called when a mouse button is released on the scene.
    ##
    def mouseReleased(self, event):
        pass

    ###
    # Called when the user presses or releases a modifier key resulting
    # in a change of modifier status, and when the tool is enabled with
    # a modifier key pressed.
    ##
    def modifiersChanged(self, modifiers):
        pass

    ###
    # Called when the application language changed.
    ##
    def languageChanged(self):
        pass

    def setMapDocument(self, mapDocument):
        if (self.mMapDocument == mapDocument):
            return
        if (self.mMapDocument):
            try:
                self.mMapDocument.layerChanged.disconnect(self.updateEnabledState)
                self.mMapDocument.currentLayerIndexChanged.disconnect(self.updateEnabledState)
            except:
                pass
        
        oldDocument = self.mMapDocument
        self.mMapDocument = mapDocument
        self.mapDocumentChanged(oldDocument, self.mMapDocument)

        if self.mMapDocument:
            self.mMapDocument.layerChanged.connect(self.updateEnabledState)
            self.mMapDocument.currentLayerIndexChanged.connect(self.updateEnabledState)
        self.updateEnabledState()
        
    ###
    # Can be used to respond to the map document changing.
    ##
    def mapDocumentChanged(self, oldDocument, newDocument):
        pass

    def mapDocument(self):
        return self.mMapDocument

    ###
    # By default, this function is called after the current map has changed
    # and when the current layer changes. It can be overridden to implement
    # custom logic for when the tool should be enabled.
    #
    # The default implementation enables tools when a map document is set.
    ##
    def updateEnabledState(self):
        self.setEnabled(self.mMapDocument != None)

    name = pyqtProperty(str, name, setName)
    icon = pyqtProperty(QIcon, icon, setIcon)
    shortcut = pyqtProperty(QKeySequence, shortcut, setShortcut)
    statusInfo = pyqtProperty(str, statusInfo, setStatusInfo, notify=statusInfoChanged)
    cursor = pyqtProperty(QCursor, cursor, setCursor, notify=cursorChanged)
    enabled = pyqtProperty(bool, isEnabled, setEnabled, notify=enabledChanged)
