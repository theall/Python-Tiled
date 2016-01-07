##
# filesystemwatcher.py
# Copyright 2011, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
    pyqtSignal,
    QFile,
    qWarning,
    QObject, 
    QFileSystemWatcher
)
from pyqtcore import QMap
##
# A wrapper around QFileSystemWatcher that deals gracefully with files being
# watched multiple times. It also doesn't start complaining when a file
# doesn't exist.
#
# It's meant to be used as drop-in replacement for QFileSystemWatcher.
##
class FileSystemWatcher(QObject):
    fileChanged = pyqtSignal(str)
    directoryChanged = pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__(parent)

        self.mWatchCount = QMap()
        self.mWatcher = QFileSystemWatcher(self)
        self.mWatcher.fileChanged.connect(self.onFileChanged)
        self.mWatcher.directoryChanged.connect(self.onDirectoryChanged)

    def addPath(self, path):
        # Just silently ignore the request when the file doesn't exist
        if (not QFile.exists(path)):
            return
        entry = self.mWatchCount.find(path)
        if not entry:
            self.mWatcher.addPath(path)
            self.mWatchCount.insert(path, 1)
        else:
            # Path is already being watched, increment watch count
            self.mWatchCount[path] += 1

    def removePath(self, path):
        entry = self.mWatchCount.find(path)
        if (entry == self.mWatchCount.end()):
            if (QFile.exists(path)):
                qWarning("FileSystemWatcher: Path was never added:\n"+path)
            return

        # Decrement watch count
        entry -= 1
        self.mWatchCount[path] = entry
        if (entry == 0):
            self.mWatchCount.erase(path)
            self.mWatcher.removePath(path)

    def onFileChanged(self, path):
        # If the file was replaced, the watcher is automatically removed and needs
        # to be re-added to keep watching it for changes. This happens commonly
        # with applications that do atomic saving.
        if (not self.mWatcher.files().__contains__(path)):
            if (QFile.exists(path)):
                self.mWatcher.addPath(path)
        self.fileChanged.emit(path)

    def onDirectoryChanged(self, path):
        self.directoryChanged.emit(path)
