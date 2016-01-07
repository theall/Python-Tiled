##
# toolmanager.py
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

from pyqtcore import QString
from PyQt5.QtCore import (
    QObject,
    QVariant,
    pyqtSignal,
)
from PyQt5.QtWidgets import (
    QActionGroup,
    QAction
)

##
# The tool manager provides a central place to register editing tools.
#
# It creates actions for the tools that can be placed on a tool bar. All the
# actions are put into a QActionGroup to make sure only one tool can be
# selected at a time.
##
class ToolManager(QObject):
    selectEnabledToolSignal = pyqtSignal()
    selectedToolChanged = pyqtSignal(list)
    
    ##
    # Emitted when the status information of the current tool changed.
    # @see AbstractTool.setStatusInfo()
    ##
    statusInfoChanged = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.mActionGroup = QActionGroup(self)
        self.mSelectedTool = None
        self.mPreviouslyDisabledTool = None
        self.mMapDocument = None

        self.mActionGroup.setExclusive(True)
        self.mActionGroup.triggered.connect(self.actionTriggered)
        self.selectEnabledToolSignal.connect(self.selectEnabledTool)
        
    def __del__(self):
        pass

    ##
    # Sets the MapDocument on which the registered tools will operate.
    ##
    def setMapDocument(self, mapDocument):
        if (self.mMapDocument == mapDocument):
            return
        self.mMapDocument = mapDocument
        for action in self.mActionGroup.actions():
            tool = action.data()
            tool.setMapDocument(mapDocument)

    ##
    # Registers a new tool. The tool manager does not take ownership over the
    # tool.
    #
    # @return The action for activating the tool.
    ##
    def registerTool(self, tool):
        tool.setMapDocument(self.mMapDocument)
        toolAction = QAction(tool.icon, tool.name, self)
        toolAction.setShortcut(tool.shortcut)
        toolAction.setData(QVariant(tool))
        toolAction.setCheckable(True)
        toolAction.setToolTip("%s (%s)"%(tool.name, tool.shortcut.toString()))
        toolAction.setEnabled(tool.isEnabled())
        self.mActionGroup.addAction(toolAction)
        tool.enabledChanged.connect(self.toolEnabledChanged)
        # Select the first added tool
        if (not self.mSelectedTool and tool.isEnabled()):
            self.setSelectedTool(tool)
            toolAction.setChecked(True)
        return toolAction

    ##
    # Selects the given tool. It should be previously added using
    # registerTool().
    ##
    def selectTool(self, tool):
        if (tool and not tool.isEnabled()): # Refuse to select disabled tools
            return
        for action in self.mActionGroup.actions():
            if (action.data() == tool):
                action.trigger()
                return

        # The given tool was not found. Don't select any tool.
        for action in self.mActionGroup.actions():
            action.setChecked(False)
        self.setSelectedTool(None)

    ##
    # Returns the selected tool.
    ##
    def selectedTool(self):
        return self.mSelectedTool

    def retranslateTools(self):
        # Allow the tools to adapt to the new language
        for action in self.mActionGroup.actions():
            tool = action.data()
            tool.languageChanged()
            # Update the text, shortcut and tooltip of the action
            action.setText(tool.name)
            action.setShortcut(tool.shortcut)
            action.setToolTip("%s (%s)"%(tool.name, tool.shortcut.toString()))

    def actionTriggered(self, action):
        self.setSelectedTool(action.data())

    def toolEnabledChanged(self, enabled):
        tool = self.sender()
        for action in self.mActionGroup.actions():
            if (action.data() == tool):
                action.setEnabled(enabled)
                break

        # Switch to another tool when the current tool gets disabled. This is done
        # with a delayed call since we first want all the tools to update their
        # enabled state.
        if ((not enabled and tool == self.mSelectedTool) or (enabled and not self.mSelectedTool)):
            self.selectEnabledToolSignal.emit()

    def selectEnabledTool(self):
        # Avoid changing tools when it's no longer necessary
        if (self.mSelectedTool and self.mSelectedTool.isEnabled()):
            return
        currentTool = self.mSelectedTool
        # Prefer the tool we switched away from last time
        if (self.mPreviouslyDisabledTool and self.mPreviouslyDisabledTool.isEnabled()):
            self.selectTool(self.mPreviouslyDisabledTool)
        else:
            self.selectTool(self.firstEnabledTool())
        
        self.mPreviouslyDisabledTool = currentTool

    def firstEnabledTool(self):
        for action in self.mActionGroup.actions():
            tool = action.data()
            if tool:
                if (tool.isEnabled()):
                    return tool
        return None

    def setSelectedTool(self, tool):
        if (self.mSelectedTool == tool):
            return
        if (self.mSelectedTool):
            self.mSelectedTool.statusInfoChanged.disconnect(self.statusInfoChanged)

        self.mSelectedTool = tool
        self.selectedToolChanged.emit([self.mSelectedTool])
        if (self.mSelectedTool):
            self.statusInfoChanged.emit(self.mSelectedTool.statusInfo)
            self.mSelectedTool.statusInfoChanged.connect(self.statusInfoChanged)
