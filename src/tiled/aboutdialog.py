# -*- coding: utf-8 -*-
##
# aboutdialog.py
# Copyright 2008-2009, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2009, Dennis Honeyman <arcticuno@gmail.com>
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

from PyQt5.QtCore import (
    Qt,
    QUrl,
    QCoreApplication
)
from PyQt5.QtGui import (
    QDesktopServices
)
from PyQt5.QtWidgets import (
    QDialog, 
    QApplication
)
from Ui_aboutdialog import Ui_AboutDialog

class AboutDialog(QDialog, Ui_AboutDialog):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setupUi(self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMaximumSize(432, 460)
        html = QCoreApplication.translate(
                "AboutDialog",
                "<p align=\"center\"><font size=\"+2\"><b>Tiled Map Editor</b></font><br><i>Version %s</i></p>\n"
                "<p align=\"center\">Copyright 2008-2015 Thorbj&oslash;rn Lindeijer<br>(see the AUTHORS file for a full list of contributors)</p>\n"
                "<p align=\"center\">You may modify and redistribute this program under the terms of the GPL (version 2 or later). "
                "A copy of the GPL is contained in the 'COPYING' file distributed with Tiled.</p>\n"
                "<p align=\"center\"><a href=\"http://www.mapeditor.org/\">http://www.mapeditor.org/</a></p>\n"%QApplication.applicationVersion())
        self.textBrowser.setHtml(html)
        self.donateButton.clicked.connect(self.donate)

    def donate(self):
        QDesktopServices.openUrl(QUrl("http://www.mapeditor.org/donate"))
