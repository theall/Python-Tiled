##
# consoledock.py
# Copyright 2013, Samuli Tuomola
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

from logginginterface import LoggingInterface
from pluginmanager import PluginManager
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPlainTextEdit,
    QDockWidget
)
from pyqtcore import QString

class ConsoleDock(QDockWidget):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.setObjectName("ConsoleDock")
        self.setWindowTitle(self.tr("Debug Console"))
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        self.plainTextEdit = QPlainTextEdit()
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setStyleSheet(QString(
                                "QAbstractScrollArea {"
                                " background-color: black;"
                                " color:green;"
                                "}"
                                ))
        layout.addWidget(self.plainTextEdit)
        
        for output in PluginManager.objects():
            self.registerOutput(output)

        PluginManager.instance().objectAdded.connect(self.onObjectAdded)

        self.setWidget(widget)

    def __del__(self):
        pass

    def appendInfo(self, s):
        self.plainTextEdit.appendHtml('<pre>'+s+'</pre>')

    def appendError(self, s):
        self.plainTextEdit.appendHtml("<pre style='color:red'>"+s+"</pre>")


    def onObjectAdded(self, object):
        if type(object) == LoggingInterface:
            self.registerOutput(object)

    def registerOutput(self, output):
        output.info.connect(self.appendInfo)
        output.error.connect(self.appendError)
