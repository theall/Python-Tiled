##
# command.py
# Copyright 2011, Jeff Bland <jeff@teamphobic.com>
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
from mapobject import MapObject
from pyqtcore import QString, QHash
from documentmanager import DocumentManager
from PyQt5.QtCore import (
    QSettings,
    QProcess
)
from PyQt5.QtWidgets import (
    QMessageBox
)

class Command():
    def __init__(self, isEnabled = True, name = QString(), command = QString()):
        self.isEnabled = isEnabled
        self.name = name
        self.command = command

    ##
    # Returns the final command with replaced tokens.
    ##
    def finalCommand(self):
        finalCommand = self.command
        # Perform variable replacement
        mapDocument = DocumentManager.instance().currentDocument()
        if (mapDocument):
            fileName = mapDocument.fileName()
            finalCommand.replace("%mapfile", "\"%s\""%(fileName))
            
            currentObject = mapDocument.currentObject()
            if type(currentObject) == MapObject:
                finalCommand.replace("%objecttype", "\"%s\""%currentObject.type())

        return finalCommand

    ##
    # Executes the command in the operating system shell or terminal
    # application.
    ##
    def execute(self, inTerminal = False):
        # Save if save option is unset or True
        settings = QSettings()
        variant = settings.value("saveBeforeExecute", True)
        if variant.lower()=='true':
            document = DocumentManager.instance().currentDocument()
            if (document):
                document.save()

        # Start the process
        CommandProcess(self, inTerminal)

    ##
    # Stores this command in a QVariant.
    ##
    def toQVariant(self):
        hash = QHash()
        hash["Enabled"] = self.isEnabled
        hash["Name"] = self.name
        hash["Command"] = self.command
        return hash

    ##
    # Generates a command from a QVariant.
    ##
    def fromQVariant(variant):
        hash = variant
        namePref = "Name"
        commandPref = "Command"
        enablePref = "Enabled"
        command = Command()
        if (hash.__contains__(enablePref)):
            command.isEnabled = hash[enablePref]
        if (hash.__contains__(namePref)):
            command.name = hash[namePref]
        if (hash.__contains__(commandPref)):
            command.command = hash[commandPref]
        return command

class CommandProcess(QProcess):
    def __init__(self, command, inTerminal = False):
        super().__init__(DocumentManager.instance())
        self.mName = command.name
        self.mFinalCommand = command.finalCommand()
        if sys.platform == 'darwin':
            self.mFile = "tiledXXXXXX.command"

        # Give an error if the command is empty or just whitespace
        if (self.mFinalCommand.strip()==''):
            self.handleError(QProcess.FailedToStart)
            return

        # Modify the command to run in a terminal
        if (inTerminal):
            if sys.platform == 'linux':
                hasGnomeTerminal = super().execute("which gnome-terminal") == 0
                if (hasGnomeTerminal):
                    self.mFinalCommand = "gnome-terminal -x " + self.mFinalCommand
                else:
                    self.mFinalCommand = "xterm -e " + self.mFinalCommand
            elif sys.platform == 'darwin':
                # The only way I know to launch a Terminal with a command on mac is
                # to make a .command file and open it. The client command invoke the
                # exectuable directly (rather than using open) in order to get std
                # output in the terminal. Otherwise, you can use the Console
                # application to see the output.
                # Create and write the command to a .command file
                if (not self.mFile.open()):
                    self.handleError(self.tr("Unable to create/open %s"%self.mFile.fileName()))
                    return

                self.mFile.write(self.mFinalCommand.toStdString().c_str())
                self.mFile.close()
                # Add execute permission to the file
                chmodRet = super().execute("chmod +x \"%s\""%self.mFile.fileName())
                if (chmodRet != 0):
                    self.handleError(self.tr("Unable to add executable permissions to %s"%self.mFile.fileName()))
                    return

                # Use open command to launch the command in the terminal
                # -W makes it not return immediately
                # -n makes it open a new instance of terminal if it is open already
                self.mFinalCommand = "open -W -n \"%s\""%self.mFile.fileName()

        self.error.connect(self.handleError)
        self.finished.connect(self.deleteLater)
        self.start(self.mFinalCommand)

    def handleError(self, arg):
        tp = type(arg)
        if tp==QProcess.ProcessError:
            error = arg
            errorStr = QString()
            x = error
            if x==super().FailedToStart:
                errorStr = self.tr("The command failed to start.")
            elif x==super().Crashed:
                errorStr = self.tr("The command crashed.")
            elif x==super().Timedout:
                errorStr = self.tr("The command timed out.")
            else:
                errorStr = self.tr("An unknown error occurred.")

            self.handleError(errorStr)
        elif tp in [QString, str]:
            error = arg
            title = self.tr("Error Executing %s"%self.mName)
            message = error + "\n\n" + self.mFinalCommand
            parent = DocumentManager.instance().widget()
            QMessageBox.warning(parent, title, message)
            # Make sure this object gets deleted if the process failed to start
            self.deleteLater()
