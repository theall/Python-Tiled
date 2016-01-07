##
# fileedit.py
# Copyright (C) 2006 Trolltech ASA. All rights reserved. (GPLv2)
# Copyright 2013, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from PyQt5.QtGui import QPalette
from PyQt5.QtCore import (
    Qt,
    QFile,
    pyqtSignal
)
from PyQt5.QtWidgets import (
    QSizePolicy,
    QToolButton,
    QLineEdit,
    QHBoxLayout,
    QFileDialog,
    QWidget
)
from pyqtcore import QString

##
# A widget that combines a line edit with a button to choose a file.
##
class FileEdit(QWidget):
    filePathChanged = pyqtSignal(QString)

    def __init__(self, parent = None):
        super().__init__(parent)

        self.mFilter = QString()
        self.mErrorTextColor = Qt.red

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.mLineEdit = QLineEdit(self)
        self.mLineEdit.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred))
        self.mOkTextColor = self.mLineEdit.palette().color(QPalette.Active, QPalette.Text)
        button = QToolButton(self)
        button.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred))
        button.setFixedWidth(20)
        button.setText("...")
        layout.addWidget(self.mLineEdit)
        layout.addWidget(button)
        self.setFocusProxy(self.mLineEdit)
        self.setFocusPolicy(Qt.StrongFocus)
        self.setAttribute(Qt.WA_InputMethodEnabled)
        self.mLineEdit.textEdited.connect(self.filePathChanged)
        self.mLineEdit.textChanged.connect(self.validate)
        button.clicked.connect(self.buttonClicked)

    def setFilePath(self, filePath):
         if (self.mLineEdit.text() != filePath):
             self.mLineEdit.setText(filePath)

    def filePath(self):
        return self.mLineEdit.text()

    def setFilter(self, filter):
        self.mFilter = filter

    def focusInEvent(self, e):
        self.mLineEdit.event(e)
        if (e.reason() == Qt.TabFocusReason or e.reason() == Qt.BacktabFocusReason):
            self.mLineEdit.selectAll()

        super().focusInEvent(e)

    def focusOutEvent(self, e):
        self.mLineEdit.event(e)
        super().focusOutEvent(e)

    def keyPressEvent(self, e):
        self.mLineEdit.event(e)

    def keyReleaseEvent(self, e):
        self.mLineEdit.event(e)

    def validate(self, text):
        if QFile.exists(text):
            textColor = self.mOkTextColor
        else:
            textColor = self.mErrorTextColor
        palette = self.mLineEdit.palette()
        palette.setColor(QPalette.Active, QPalette.Text, textColor)
        self.mLineEdit.setPalette(palette)

    def buttonClicked(self):
        filePath = QFileDialog.getOpenFileName(self.window(), self.tr("Choose a File"), self.mLineEdit.text(), self.mFilter)
        if (filePath.isNull()):
            return
        self.mLineEdit.setText(filePath)
        self.filePathChanged.emit(filePath)
