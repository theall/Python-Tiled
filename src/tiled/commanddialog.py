##
# commanddialog.py
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
from commanddatamodel import CommandDataModel
from PyQt5.QtCore import (
    Qt,
    QItemSelectionModel
)
from PyQt5.QtGui import (
    QKeySequence
)
from PyQt5.QtWidgets import (
    QShortcut,
    QTreeView,
    QDialog,
    QHeaderView
)
from Ui_commanddialog import Ui_CommandDialog

class CommandDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.mUi = Ui_CommandDialog()

        self.mUi.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.mUi.saveBox.setChecked(self.mUi.treeView.model().saveBeforeExecute())
        self.setWindowTitle(self.tr("Edit Commands"))
        Utils.restoreGeometry(self)

    def __del__(self):
        Utils.saveGeometry(self)
        del self.mUi

    ##
    # Saves the changes to the users preferences.
    # Automatically called when the dialog is accepted.
    ##
    def accept(self):
        super().accept()
        self.mUi.treeView.model().setSaveBeforeExecute(self.mUi.saveBox.isChecked())
        self.mUi.treeView.model().commit()

class CommandTreeView(QTreeView):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.mModel = CommandDataModel(self)

        self.setModel(self.mModel)
        self.setRootIsDecorated(False)
        # Setup resizing so the command column stretches
        self.setColumnWidth(0, 200)
        h = self.header()
        h.setStretchLastSection(False)

        h.setSectionResizeMode(CommandDataModel.NameColumn, QHeaderView.Interactive)
        h.setSectionResizeMode(CommandDataModel.CommandColumn, QHeaderView.Stretch)
        h.setSectionResizeMode(CommandDataModel.EnabledColumn,
                                QHeaderView.ResizeToContents)

        # Allow deletion via keyboard
        d = QShortcut(QKeySequence.Delete, self)
        d.setContext(Qt.WidgetShortcut)
        d.activated.connect(self.removeSelectedCommands)
        self.mModel.rowsRemoved.connect(self.handleRowsRemoved)

    def __del__(self):
        del self.mModel

    ##
    # Returns the model used by this view in CommandDataMode form.
    ##
    def model(self):
        return self.mModel

    ##
    # Displays a context menu for the item at <i>event</i>'s position.
    ##
    def contextMenuEvent(self, event):
        index = self.indexAt(event.pos())
        # Generate a run a menu for the index
        menu = self.mModel.contextMenu(self, index)
        if (menu):
            menu.exec(event.globalPos())

    ##
    # Fixes the selection after rows have been removed.
    ##
    def handleRowsRemoved(self, parent, start, end):
        if (parent.isValid()):
            return
        # Reselect the same row index of the removed row
        sModel = self.selectionModel()
        index = sModel.currentIndex()
        sModel.select(index.sibling(index.row() + 1,index.column()),
                       QItemSelectionModel.ClearAndSelect |
                       QItemSelectionModel.Rows)

    ##
    # Gets the currently selected rows and tells the model to delete them.
    ##
    def removeSelectedCommands(self):
        selection = self.selectionModel()
        indices = selection.selectedRows()
        self.mModel.removeRows(indices)
