##
# commanddatamodel.py
# Copyright 2010, Jeff Bland <jeff@teamphobic.com>
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

from PyQt5.QtCore import (
    Qt,
    QVariant,
    QByteArray,
    QMimeData,
    QModelIndex,
    QSignalMapper,
    QSettings,
    QAbstractTableModel
)
from PyQt5.QtWidgets import (
    QMenu
)
from command import Command
from pyqtcore import QList, QString, QStringList
commandMimeType = "application/x-tiled-commandptr"

class CommandDataModel(QAbstractTableModel):
    NameColumn, CommandColumn, EnabledColumn = range(3)

    ##
    # Constructs the object and parses the users settings to allow easy
    # programmatic access to the command list.
    ##
    def __init__(self, parent):
        super().__init__(parent)
        
        self.mSettings = QSettings()
        self.mSaveBeforeExecute = False
        self.mCommands = QList()
        
        # Load saveBeforeExecute option
        s = self.mSettings.value("saveBeforeExecute", True)
        self.mSaveBeforeExecute = bool(s)
        # Load command list
        variant = self.mSettings.value("commandList")
        commands = variant
        if commands is None:
            commands = []
        for commandVariant in commands:
            self.mCommands.append(Command.fromQVariant(commandVariant))
        # Add default commands the first time the app has booted up.
        # This is useful on it's own and helps demonstrate how to use the commands.
        addPrefStr = "addedDefaultCommands"
        addedCommands = self.mSettings.value(addPrefStr, False)
        if (not addedCommands):
            # Disable default commands by default so user gets an informative
            # warning when clicking the command button for the first time
            command = Command(False)
            if sys.platform == 'linux':
                command.command = "gedit %mapfile"
            elif sys.platform == 'darwin':
                command.command = "open -t %mapfile"
            if (not command.command.isEmpty()):
                command.name = self.tr("Open in text editor")
                self.mCommands.push_back(command)

            self.commit()
            self.mSettings.setValue(addPrefStr, True)
            
    ##
    # Saves the data to the users preferences.
    ##
    def commit(self):
        # Save saveBeforeExecute option
        self.mSettings.setValue("saveBeforeExecute", self.mSaveBeforeExecute)
        # Save command list
        commands = QList()
        for command in self.mCommands:
            commands.append(command.toQVariant())
        self.mSettings.setValue("commandList", commands)

    ##
    # Returns whether saving before executing commands is enabled.
    ##
    def saveBeforeExecute(self):
        return self.mSaveBeforeExecute

    ##
    # Enables or disables saving before executing commands.
    ##
    def setSaveBeforeExecute(self, enabled):
        self.mSaveBeforeExecute = enabled

    ##
    # Returns the first enabled command in the list, or an empty
    # disabled command if there are no enabled commands.
    ##
    def firstEnabledCommand(self):
        for command in self.mCommands:
            if (command.isEnabled):
                return command
        return Command(False)

    ##
    # Returns a list of all the commands.
    ##
    def allCommands(self):
        return QList(self.mCommands)

    ##
    # Remove the given row or rows from the model.
    ##
    def removeRows(self, *args):
        l = len(args)
        if l>1 and l<4:
            row = args[0]
            count = args[1]
            if l==2:
                parent = QModelIndex()
            elif l==3:
                parent = args[2]

            if (row < 0 or row + count > self.mCommands.size()):
                return False
            self.beginRemoveRows(parent, row, row + count)
            self.mCommands.erase(self.mCommands.begin() + row, self.mCommands.begin() + row + count)
            self.endRemoveRows()
            return True
        elif l==1:
            indices = args[0]
            ##
             # Deletes the commands associated with the given row <i>indices</i>.
            ##
            while (not indices.empty()):
                row = indices.takeFirst().row()
                if (row >= self.mCommands.size()):
                    continue
                self.beginRemoveRows(QModelIndex(), row, row)
                self.mCommands.removeAt(row)
                # Decrement later indices since we removed a row
                for i in indices:
                    if (i.row() > row):
                       i = i.sibling(i.row() - 1, i.column())
                self.endRemoveRows()

    ##
    # Returns the number of rows (this includes the <New Command> row).
    ##
    def rowCount(self, parent):
        if parent.isValid():
            return 0
        else:
            return self.mCommands.size() + 1

    ##
    # Returns the number of columns.
    ##
    def columnCount(self, parent):
        if parent.isValid():
            return 0
        else:
            return 3

    ##
    # Returns the data at <i>index</i> for the given <i>role</i>.
    ##
    def data(self, index, role = Qt.DisplayRole):
        isNormalRow = index.row() < self.mCommands.size()
        command = Command()
        if (isNormalRow):
            command = self.mCommands[index.row()]
        x = role
        if x==Qt.DisplayRole or x==Qt.EditRole:
            if (isNormalRow):
                if (index.column() == CommandDataModel.NameColumn):
                    return command.name
                if (index.column() == CommandDataModel.CommandColumn):
                    return command.command
            else:
                if (index.column() == CommandDataModel.NameColumn):
                    if (role == Qt.EditRole):
                        return QString()
                    else:
                        return self.tr("<new command>")
        elif x==Qt.ToolTipRole:
            if (isNormalRow):
                if (index.column() == CommandDataModel.NameColumn):
                    return self.tr("Set a name for this command")
                if (index.column() == CommandDataModel.CommandColumn):
                    return self.tr("Set the shell command to execute")
                if (index.column() == CommandDataModel.EnabledColumn):
                    return self.tr("Show or hide this command in the command list")
            else:
                if (index.column() == CommandDataModel.NameColumn):
                    return self.tr("Add a new command")
        elif x==Qt.CheckStateRole:
            if (isNormalRow and index.column() == CommandDataModel.EnabledColumn):
                if command.isEnabled:
                    _x = 2
                else:
                    _x = 0
                return _x

        return QVariant()

    ##
    # Sets the data at <i>index</i> to the given <i>value</i>.
    # for the given <i>role</i>
    ##
    def setData(self, index, value, role):
        isNormalRow = index.row() < self.mCommands.size()
        isModified = False
        shouldAppend = False
        command = Command()
        if (isNormalRow):
            # Get the command as it exists already
            command = self.mCommands[index.row()]
            # Modify the command based on the passed date
            x = role
            if x==Qt.EditRole:
                text = value
                if text != '':
                    if (index.column() == CommandDataModel.NameColumn):
                        command.name = value
                        isModified = True
                    elif (index.column() == CommandDataModel.CommandColumn):
                        command.command = value
                        isModified = True
            elif x==Qt.CheckStateRole:
                if (index.column() == CommandDataModel.EnabledColumn):
                    command.isEnabled = value > 0
                    isModified = True

        else:
            # If final row was edited, insert the new command
            if (role == Qt.EditRole and index.column() == CommandDataModel.NameColumn):
                command.name = value
                if (command.name!='' and command.name!=self.tr("<new command>")):
                    isModified = True
                    shouldAppend = True

        if (isModified):
            # Write the modified command to our cache
            if (shouldAppend):
                self.mCommands.append(command)
            else:
                self.mCommands[index.row()] = command
            # Reset if there could be new rows or reordering, else emit dataChanged
            if (shouldAppend or index.column() == CommandDataModel.NameColumn):
                self.beginResetModel()
                self.endResetModel()
            else:
                self.dataChanged.emit(index, index)

        return isModified

    ##
    # Returns flags for the item at <i>index</i>.
    ##
    def flags(self, index):
        isNormalRow = index.row() < self.mCommands.size()
        f = super().flags(index)
        if (isNormalRow):
            f |= Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
            if (index.column() == CommandDataModel.EnabledColumn):
                f |= Qt.ItemIsUserCheckable
            else:
                f |= Qt.ItemIsEditable
        else:
            f |= Qt.ItemIsDropEnabled
            if (index.column() == CommandDataModel.NameColumn):
                f |= Qt.ItemIsEditable

        return f
    ##
    # Returns the header data for the given <i>section</i> and <i>role</i>.
    # <i>orientation</i> should be Qt.Horizontal.
    ##
    def headerData(self, section, orientation, role = Qt.EditRole):
        if (role != Qt.DisplayRole or orientation != Qt.Horizontal):
            return QVariant()
        sectionLabels = ["Name", "Command", "Enable"]
        return self.tr(sectionLabels[section])

    ##
    # Returns a menu containing a list of appropriate actions for the item at
    # <i>index</i>, or 0 if there are no actions for the index.
    ##
    def contextMenu(self, parent, index):
        menu = None
        row = index.row()
        if (row >= 0 and row < self.mCommands.size()):
            menu = QMenu(parent)
            if (row > 0):
                action = menu.addAction(self.tr("Move Up"))
                mapper = QSignalMapper(action)
                mapper.setMapping(action, row)
                action.triggered.connect(mapper.map)
                mapper.mapped.connect(self.moveUp)

            if (row+1 < self.mCommands.size()):
                action = menu.addAction(self.tr("Move Down"))
                mapper = QSignalMapper(action)
                mapper.setMapping(action, row + 1)
                action.triggered.connect(mapper.map)
                mapper.mapped.connect(self.moveUp)

            menu.addSeparator()

            action = menu.addAction(self.tr("Execute"))
            mapper = QSignalMapper(action)
            mapper.setMapping(action, row)
            action.triggered.connect(mapper.map)
            mapper.mapped.connect(self.execute)

            if sys.platform in ['linux', 'darwin']:
                action = menu.addAction(self.tr("Execute in Terminal"))
                mapper = QSignalMapper(action)
                mapper.setMapping(action, row)
                action.triggered.connect(mapper.map)
                mapper.mapped.connect(self.executeInTerminal)

            menu.addSeparator()

            action = menu.addAction(self.tr("Delete"))
            mapper = QSignalMapper(action)
            mapper.setMapping(action, row)
            action.triggered.connect(mapper.map)
            mapper.mapped.connect(self.remove)

        return menu
    ##
    # Returns mime data for the first index in <i>indexes</i>.
    ##
    def mimeData(self, indices):
        row = -1
        for index in indices:
            # Only generate mime data on command rows
            if (index.row() < 0 or index.row() >= self.mCommands.size()):
                return None
            # Currently only one row at a time is supported for drags
            # Note: we can get multiple indexes in the same row (different columns)
            if (row != -1 and index.row() != row):
                return None
            row = index.row()

        command = self.mCommands[row]
        mimeData = QMimeData()
        # Text data is used if command is dragged to a text editor or terminal
        mimeData.setText(command.finalCommand())
        # Ptr is used if command is dragged onto another command
        # We could store the index instead, the only difference would be that if
        # the item is moved or deleted shomehow during the drag, the ptr approach
        # will result in a no-op instead of moving the wrong thing.
        addr = command
        mimeData.setData(commandMimeType, QByteArray(addr, 4))
        return mimeData

    ##
    # Returns a list of mime types that can represent a command.
    ##
    def mimeTypes(self):
        result = QStringList("text/plain")
        result.append(commandMimeType)
        return result

    ##
    # Returns the drop actions that can be performed.
    ##
    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    ##
    # Handles dropping of mime data onto <i>parent</i>.
    ##
    def dropMimeData(self, data, action, row, column, parent):
        if (not parent.isValid()):
            return False
        dstRow = parent.row()
        if (data.hasFormat(commandMimeType)):
            # Get the ptr to the command that was being dragged
            byteData = data.data(commandMimeType)
            addr = byteData.data()
            # Find the command in the command list so we can move/copy it
            for srcRow in range(self.mCommands.size()):
                if (addr == self.mCommands[srcRow]):
                    # If a command is dropped on another command,
                    # move the src command into the positon of the dst command.
                    if (dstRow < self.mCommands.size()):
                        return self.move(srcRow, dstRow)
                    # If a command is dropped elsewhere, create a copy of it
                    if (dstRow == self.mCommands.size()):
                        self.append(Command(addr.isEnabled,
                                       self.tr("%s (copy)"%addr.name),
                                       addr.command))
                        return True

        if (data.hasText()):
            # If text is dropped on a valid command, just replace the data
            if (dstRow < self.mCommands.size()):
                return self.setData(parent, data.text(), Qt.EditRole)
            # If text is dropped elsewhere, create a new command
            # Assume the dropped text is the command, not the name
            if (dstRow == self.mCommands.size()):
                self.append(Command(True, self.tr("New command"), data.text()))
                return True

        return False

    ##
    # Moves the command at <i>commandIndex</i> to <i>newIndex></i>.
    ##
    def move(self, commandIndex, newIndex):
        commandIndex = self.mCommands.size()
        newIndex = self.mCommands.size()
        if (commandIndex or newIndex or newIndex == commandIndex):
            return False
        tmp = newIndex
        if newIndex > commandIndex:
            tmp += 1

        if (not self.beginMoveRows(QModelIndex(), commandIndex, commandIndex, QModelIndex(), tmp)):
            return False
        if (commandIndex - newIndex == 1 or newIndex - commandIndex == 1):
            # Swapping is probably more efficient than removing/inserting
            self.mCommands.swap(commandIndex, newIndex)
        else:
            command = self.mCommands.at(commandIndex)
            self.mCommands.removeAt(commandIndex)
            self.mCommands.insert(newIndex, command)

        self.endMoveRows()
        return True

    ##
    # Appends <i>command</i> to the command list.
    ##
    def append(self, command):
        self.beginInsertRows(QModelIndex(), self.mCommands.size(), self.mCommands.size())
        self.mCommands.append(command)
        self.endInsertRows()

    ##
    # Moves the command at <i>commandIndex</i> up one index, if possible.
    ##
    def moveUp(self, commandIndex):
        self.move(commandIndex, commandIndex - 1)

    ##
    # Executes the command at<i>commandIndex</i>.
    ##
    def execute(self, commandIndex):
        self.mCommands.at(commandIndex).execute()

    ##
    # Executes the command at <i>commandIndex</i> within the systems native
    # terminal if available.
    ##
    def executeInTerminal(self, commandIndex):
        self.mCommands.at(commandIndex).execute(True)

    ##
    # Deletes the command at <i>commandIndex</i>.
    ##
    def remove(self, commandIndex):
        self.removeRow(commandIndex)

