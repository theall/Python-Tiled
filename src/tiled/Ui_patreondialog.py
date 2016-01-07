# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'F:\opensource\tiled\src\tiled\patreondialog.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PatreonDialog(object):
    def setupUi(self, PatreonDialog):
        PatreonDialog.setObjectName("PatreonDialog")
        PatreonDialog.resize(407, 360)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(PatreonDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.textBrowser = QtWidgets.QTextBrowser(PatreonDialog)
        self.textBrowser.setStyleSheet("")
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout_2.addWidget(self.textBrowser)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gotoPatreon = QtWidgets.QCommandLinkButton(PatreonDialog)
        self.gotoPatreon.setObjectName("gotoPatreon")
        self.verticalLayout.addWidget(self.gotoPatreon)
        self.alreadyPatron = QtWidgets.QCommandLinkButton(PatreonDialog)
        self.alreadyPatron.setObjectName("alreadyPatron")
        self.verticalLayout.addWidget(self.alreadyPatron)
        self.maybeLaterButton = QtWidgets.QCommandLinkButton(PatreonDialog)
        self.maybeLaterButton.setObjectName("maybeLaterButton")
        self.verticalLayout.addWidget(self.maybeLaterButton)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(PatreonDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)

        self.retranslateUi(PatreonDialog)
        self.buttonBox.accepted.connect(PatreonDialog.accept)
        self.buttonBox.rejected.connect(PatreonDialog.reject)
        self.maybeLaterButton.clicked.connect(PatreonDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(PatreonDialog)

    def retranslateUi(self, PatreonDialog):
        _translate = QtCore.QCoreApplication.translate
        PatreonDialog.setWindowTitle(_translate("PatreonDialog", "Become a Patron"))
        self.gotoPatreon.setText(_translate("PatreonDialog", "Visit https://www.patreon.com/bjorn"))
        self.alreadyPatron.setText(_translate("PatreonDialog", "I\'m already a patron!"))
        self.maybeLaterButton.setText(_translate("PatreonDialog", "Maybe later"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    PatreonDialog = QtWidgets.QDialog()
    ui = Ui_PatreonDialog()
    ui.setupUi(PatreonDialog)
    PatreonDialog.show()
    sys.exit(app.exec_())

