# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\src\tiled\commanddialog.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CommandDialog(object):
    def setupUi(self, CommandDialog):
        CommandDialog.setObjectName("CommandDialog")
        CommandDialog.resize(479, 258)
        self.verticalLayout = QtWidgets.QVBoxLayout(CommandDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.treeView = CommandTreeView(CommandDialog)
        self.treeView.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.treeView.setAlternatingRowColors(True)
        self.treeView.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.treeView.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.treeView.setObjectName("treeView")
        self.verticalLayout.addWidget(self.treeView)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.saveBox = QtWidgets.QCheckBox(CommandDialog)
        self.saveBox.setObjectName("saveBox")
        self.horizontalLayout.addWidget(self.saveBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(CommandDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(CommandDialog)
        self.buttonBox.accepted.connect(CommandDialog.accept)
        self.buttonBox.rejected.connect(CommandDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(CommandDialog)

    def retranslateUi(self, CommandDialog):
        _translate = QtCore.QCoreApplication.translate
        CommandDialog.setWindowTitle(_translate("CommandDialog", "Properties"))
        self.saveBox.setText(_translate("CommandDialog", "&Save map before executing"))

from tiled.commanddialog import CommandTreeView

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    CommandDialog = QtWidgets.QDialog()
    ui = Ui_CommandDialog()
    ui.setupUi(CommandDialog)
    CommandDialog.show()
    sys.exit(app.exec_())

