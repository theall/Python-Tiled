# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\src\tiled\exportasimagedialog.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ExportAsImageDialog(object):
    def setupUi(self, ExportAsImageDialog):
        ExportAsImageDialog.setObjectName("ExportAsImageDialog")
        ExportAsImageDialog.resize(337, 231)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(ExportAsImageDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupBox = QtWidgets.QGroupBox(ExportAsImageDialog)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.fileNameEdit = QtWidgets.QLineEdit(self.groupBox)
        self.fileNameEdit.setObjectName("fileNameEdit")
        self.horizontalLayout.addWidget(self.fileNameEdit)
        self.browseButton = QtWidgets.QPushButton(self.groupBox)
        self.browseButton.setObjectName("browseButton")
        self.horizontalLayout.addWidget(self.browseButton)
        self.verticalLayout_2.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(ExportAsImageDialog)
        self.groupBox_2.setObjectName("groupBox_2")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox_2)
        self.verticalLayout.setObjectName("verticalLayout")
        self.visibleLayersOnly = QtWidgets.QCheckBox(self.groupBox_2)
        self.visibleLayersOnly.setChecked(True)
        self.visibleLayersOnly.setObjectName("visibleLayersOnly")
        self.verticalLayout.addWidget(self.visibleLayersOnly)
        self.currentZoomLevel = QtWidgets.QCheckBox(self.groupBox_2)
        self.currentZoomLevel.setChecked(True)
        self.currentZoomLevel.setObjectName("currentZoomLevel")
        self.verticalLayout.addWidget(self.currentZoomLevel)
        self.drawTileGrid = QtWidgets.QCheckBox(self.groupBox_2)
        self.drawTileGrid.setObjectName("drawTileGrid")
        self.verticalLayout.addWidget(self.drawTileGrid)
        self.includeBackgroundColor = QtWidgets.QCheckBox(self.groupBox_2)
        self.includeBackgroundColor.setObjectName("includeBackgroundColor")
        self.verticalLayout.addWidget(self.includeBackgroundColor)
        self.verticalLayout_2.addWidget(self.groupBox_2)
        spacerItem = QtWidgets.QSpacerItem(20, 0, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(ExportAsImageDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Save)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.label.setBuddy(self.fileNameEdit)

        self.retranslateUi(ExportAsImageDialog)
        self.buttonBox.accepted.connect(ExportAsImageDialog.accept)
        self.buttonBox.rejected.connect(ExportAsImageDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(ExportAsImageDialog)

    def retranslateUi(self, ExportAsImageDialog):
        _translate = QtCore.QCoreApplication.translate
        ExportAsImageDialog.setWindowTitle(_translate("ExportAsImageDialog", "Export As Image"))
        self.groupBox.setTitle(_translate("ExportAsImageDialog", "Location"))
        self.label.setText(_translate("ExportAsImageDialog", "Name:"))
        self.browseButton.setText(_translate("ExportAsImageDialog", "&Browse..."))
        self.groupBox_2.setTitle(_translate("ExportAsImageDialog", "Settings"))
        self.visibleLayersOnly.setText(_translate("ExportAsImageDialog", "Only include &visible layers"))
        self.currentZoomLevel.setText(_translate("ExportAsImageDialog", "Use current &zoom level"))
        self.drawTileGrid.setText(_translate("ExportAsImageDialog", "&Draw tile grid"))
        self.includeBackgroundColor.setText(_translate("ExportAsImageDialog", "&Include background color"))

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ExportAsImageDialog = QtWidgets.QDialog()
    ui = Ui_ExportAsImageDialog()
    ui.setupUi(ExportAsImageDialog)
    ExportAsImageDialog.show()
    sys.exit(app.exec_())

