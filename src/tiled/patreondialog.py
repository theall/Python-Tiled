##
# patreondialog.py
# Copyright 2015, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

import preferences
from Ui_patreondialog import Ui_PatreonDialog
from PyQt5.QtCore import (
    QUrl
)
from PyQt5.QtGui import (
    QDesktopServices
)
from PyQt5.QtWidgets import (
    QDialog
)
class PatreonDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.ui = Ui_PatreonDialog()

        self.ui.setupUi(self)
        self.ui.maybeLaterButton.setVisible(False)
        self.ui.gotoPatreon.clicked.connect(self.openPatreonPage)
        self.ui.alreadyPatron.clicked.connect(self.togglePatreonStatus)
        prefs = preferences.Preferences.instance()
        prefs.isPatronChanged.connect(self.updatePatreonStatus)
        self.updatePatreonStatus()

    def __del__(self):
        del self.ui

    def openPatreonPage(self):
        QDesktopServices.openUrl(QUrl("https://www.patreon.com/bjorn"))

    def togglePatreonStatus(self):
        prefs = preferences.Preferences.instance()
        prefs.setPatron(not prefs.isPatron())
        self.setFocus()

    def updatePatreonStatus(self):
        if (preferences.Preferences.instance().isPatron()):
            self.ui.textBrowser.setHtml(self.tr(
                "\n"
                "\n"
                "Your support as a patron makes a big difference to me as the "
                "main developer and maintainer of Tiled. It allows me to spend "
                "less time working for money elsewhere and spend more time working "
                "on Tiled instead.\n"
                "Keep an eye out for exclusive updates in the Activity feed on "
                "my Patreon page to find out what I've been up to in the time I "
                "could spend on Tiled thanks to your support!\n"
                ""))
            self.ui.alreadyPatron.setText(self.tr("I'm no longer a patron"))
        else:
            self.ui.textBrowser.setHtml(self.tr(
                "\n"
                "\n"
                "Please consider supporting me as a patron. Your support would "
                "make a big difference to me, the main developer and maintainer of "
                "Tiled. I could spend less time working for money elsewhere and "
                "spend more time working on Tiled instead.\n"
                "Every little bit helps. Tiled has a lot of users and if each "
                "would contribute a small donation each month I will have time to "
                "make sure Tiled keeps getting better.\n"
                ""))
            self.ui.alreadyPatron.setText(self.tr("I'm already a patron!"))
