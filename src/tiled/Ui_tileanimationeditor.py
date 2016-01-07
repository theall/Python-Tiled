# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Z:\src\tiled\tileanimationeditor.ui'
#
# Created by: PyQt5 UI code generator 5.4.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TileAnimationEditor(object):
    def setupUi(self, TileAnimationEditor):
        TileAnimationEditor.setObjectName("TileAnimationEditor")
        TileAnimationEditor.resize(669, 410)
        self.verticalLayout = QtWidgets.QVBoxLayout(TileAnimationEditor)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.zoomComboBox = QtWidgets.QComboBox(TileAnimationEditor)
        self.zoomComboBox.setObjectName("zoomComboBox")
        self.horizontalLayout.addWidget(self.zoomComboBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalSplitter = QtWidgets.QSplitter(TileAnimationEditor)
        self.horizontalSplitter.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSplitter.setChildrenCollapsible(False)
        self.horizontalSplitter.setObjectName("horizontalSplitter")
        self.verticalSplitter = QtWidgets.QSplitter(self.horizontalSplitter)
        self.verticalSplitter.setOrientation(QtCore.Qt.Vertical)
        self.verticalSplitter.setObjectName("verticalSplitter")
        self.frameList = QtWidgets.QListView(self.verticalSplitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.frameList.sizePolicy().hasHeightForWidth())
        self.frameList.setSizePolicy(sizePolicy)
        self.frameList.setMinimumSize(QtCore.QSize(128, 0))
        self.frameList.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.frameList.setAcceptDrops(True)
        self.frameList.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.frameList.setDragEnabled(True)
        self.frameList.setDragDropMode(QtWidgets.QAbstractItemView.DragDrop)
        self.frameList.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.frameList.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.frameList.setHorizontalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.frameList.setViewMode(QtWidgets.QListView.ListMode)
        self.frameList.setObjectName("frameList")
        self.preview = QtWidgets.QLabel(self.verticalSplitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.preview.sizePolicy().hasHeightForWidth())
        self.preview.setSizePolicy(sizePolicy)
        self.preview.setMinimumSize(QtCore.QSize(0, 64))
        self.preview.setFrameShape(QtWidgets.QFrame.Box)
        self.preview.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.preview.setAlignment(QtCore.Qt.AlignCenter)
        self.preview.setObjectName("preview")
        self.tilesetView = TilesetView(self.horizontalSplitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tilesetView.sizePolicy().hasHeightForWidth())
        self.tilesetView.setSizePolicy(sizePolicy)
        self.tilesetView.setMinimumSize(QtCore.QSize(128, 0))
        self.tilesetView.setDragEnabled(True)
        self.tilesetView.setDragDropMode(QtWidgets.QAbstractItemView.DragOnly)
        self.tilesetView.setObjectName("tilesetView")
        self.verticalLayout.addWidget(self.horizontalSplitter)
        self.buttonBox = QtWidgets.QDialogButtonBox(TileAnimationEditor)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Close)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(TileAnimationEditor)
        self.buttonBox.rejected.connect(TileAnimationEditor.close)
        QtCore.QMetaObject.connectSlotsByName(TileAnimationEditor)

    def retranslateUi(self, TileAnimationEditor):
        _translate = QtCore.QCoreApplication.translate
        TileAnimationEditor.setWindowTitle(_translate("TileAnimationEditor", "Tile Animation Editor"))
        self.preview.setText(_translate("TileAnimationEditor", "Preview"))

from tilesetview import TilesetView

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    TileAnimationEditor = QtWidgets.QWidget()
    ui = Ui_TileAnimationEditor()
    ui.setupUi(TileAnimationEditor)
    TileAnimationEditor.show()
    sys.exit(app.exec_())

