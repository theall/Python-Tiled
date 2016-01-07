##
# resizedialog.py
# Copyright 2008-2009, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
from Ui_resizedialog import Ui_ResizeDialog
from PyQt5.QtCore import (
    Qt,
    QSize
)
from PyQt5.QtWidgets import (
    QDialog
)
class ResizeDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.mUi = Ui_ResizeDialog()

        self.mUi.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        # Initialize the new size of the resizeHelper to the default values of
        # the spin boxes. Otherwise, if the map width or height is default, then
        # setOldSize() will simply reset default values, causing callbacks in the
        # resize helper to not be called.
        self.mUi.resizeHelper.setNewSize(QSize(self.mUi.widthSpinBox.value(),
                                            self.mUi.heightSpinBox.value()))
        self.mUi.resizeHelper.offsetBoundsChanged.connect(self.updateOffsetBounds)
        Utils.restoreGeometry(self)

    def __del__(self):
        Utils.saveGeometry(self)
        del self.mUi

    def setOldSize(self, size):
        self.mUi.resizeHelper.setOldSize(size)
        # Reset the spin boxes to the old size
        self.mUi.widthSpinBox.setValue(size.width())
        self.mUi.heightSpinBox.setValue(size.height())

    def newSize(self):
        return self.mUi.resizeHelper.newSize()

    def offset(self):
        return self.mUi.resizeHelper.offset()

    def updateOffsetBounds(self, bounds):
        self.mUi.offsetXSpinBox.setRange(bounds.left(), bounds.right())
        self.mUi.offsetYSpinBox.setRange(bounds.top(), bounds.bottom())
