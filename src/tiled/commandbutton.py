##
# commandbutton.py
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

from utils import Utils
from commanddialog import CommandDialog
from commanddatamodel import CommandDataModel
from command import Command
from PyQt5.QtCore import (
    QEvent
)
from PyQt5.QtGui import (
    QIcon,
    QKeySequence
)
from PyQt5.QtWidgets import (
    QMessageBox,
    QMenu,
    QAction, 
    QToolButton
)
class CommandButton(QToolButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.mMenu = QMenu(self)

        self.setIcon(QIcon(":images/24x24/system-run.png"))
        Utils.setThemeIcon(self, "system-run")
        self.retranslateUi()
        self.setPopupMode(QToolButton.MenuButtonPopup)
        self.setMenu(self.mMenu)
        self.mMenu.aboutToShow.connect(self.populateMenu)
        self.clicked.connect(self.runCommand)

    def changeEvent(self, event):
        super().changeEvent(event)
        x = event.type()
        if x==QEvent.LanguageChange:
            self.retranslateUi()
        else:
            pass

    def runCommand(self):
        command = Command()
        action = self.sender()
        if (type(action)==QAction and action.data()):
            #run the command passed by the action
            command = Command.fromQVariant(action.data())
        else:
            #run the default command
            command = CommandDataModel(self).firstEnabledCommand()
            if (not command.isEnabled):
                msgBox = QMessageBox(self.window())
                msgBox.setIcon(QMessageBox.Warning)
                msgBox.setWindowTitle(self.tr("Error Executing Command"))
                msgBox.setText(self.tr("You do not have any commands setup."))
                msgBox.addButton(QMessageBox.Ok)
                msgBox.addButton(self.tr("Edit commands..."), QMessageBox.ActionRole)
                msgBox.setDefaultButton(QMessageBox.Ok)
                msgBox.setEscapeButton(QMessageBox.Ok)
                button = msgBox.buttons()[-1]
                button.clicked.connect(self.showDialog)
                msgBox.exec()
                return

        command.execute()

    def showDialog(self):
        dialog = CommandDialog(self.window())
        dialog.exec()

    def populateMenu(self):
        self.mMenu.clear()
        # Use a data model for getting the command list to avoid having to
        # manually parse the settings
        model = CommandDataModel(self)
        commands = model.allCommands()
        for command in commands:
            if (not command.isEnabled):
                continue
            action = self.mMenu.addAction(command.name)
            action.setStatusTip(command.command)
            action.setData(command.toQVariant())
            action.triggered.connect(self.runCommand)

        if (not self.mMenu.isEmpty()):
            self.mMenu.addSeparator()
        # Add "Edit Commands..." action
        action = self.mMenu.addAction(self.tr("Edit Commands..."))
        action.triggered.connect(self.showDialog)

    def retranslateUi(self):
        self.setToolTip(self.tr("Execute Command"))
        self.setShortcut(QKeySequence(self.tr("F5")))
