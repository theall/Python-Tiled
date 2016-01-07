# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\src\tiled\aboutdialog.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(432, 452)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(AboutDialog)
        self.verticalLayout_3.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.logoLayout = QtWidgets.QHBoxLayout()
        self.logoLayout.setObjectName("logoLayout")
        spacerItem = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.logoLayout.addItem(spacerItem)
        self.logo = QtWidgets.QLabel(AboutDialog)
        self.logo.setMinimumSize(QtCore.QSize(400, 200))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap(":/images/about-tiled-logo.png"))
        self.logo.setObjectName("logo")
        self.logoLayout.addWidget(self.logo)
        spacerItem1 = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.logoLayout.addItem(spacerItem1)
        self.verticalLayout_3.addLayout(self.logoLayout)
        self.textBrowser = QtWidgets.QTextBrowser(AboutDialog)
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_3.addWidget(self.textBrowser)
        self.buttonLayout = QtWidgets.QHBoxLayout()
        self.buttonLayout.setSizeConstraint(QtWidgets.QLayout.SetDefaultConstraint)
        self.buttonLayout.setObjectName("buttonLayout")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.buttonLayout.addItem(spacerItem2)
        self.donateButton = QtWidgets.QPushButton(AboutDialog)
        self.donateButton.setObjectName("donateButton")
        self.buttonLayout.addWidget(self.donateButton)
        self.pushButton = QtWidgets.QPushButton(AboutDialog)
        self.pushButton.setDefault(True)
        self.pushButton.setObjectName("pushButton")
        self.buttonLayout.addWidget(self.pushButton)
        self.verticalLayout_3.addLayout(self.buttonLayout)

        self.retranslateUi(AboutDialog)
        self.pushButton.clicked.connect(AboutDialog.close)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutDialog.setWindowTitle(_translate("AboutDialog", "About Tiled"))
        self.donateButton.setText(_translate("AboutDialog", "Donate"))
        self.pushButton.setText(_translate("AboutDialog", "OK"))

import tiled_rc

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    AboutDialog = QtWidgets.QDialog()
    ui = Ui_AboutDialog()
    ui.setupUi(AboutDialog)
    AboutDialog.show()
    sys.exit(app.exec_())

