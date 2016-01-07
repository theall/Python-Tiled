##
# tileanimationdriver.py
# Copyright 2014, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
    QAbstractAnimation
)
class TileAnimationDriver(QAbstractAnimation):
    ##
    # Emitted every time a logic update should be made. \a deltaTime is in
    # milliseconds.
    ##
    update = pyqtSignal(int)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.mLastTime = 0

        self.setLoopCount(-1) # loop forever

    def duration(self):
        return 1000

    def updateCurrentTime(self, currentTime):
        elapsed = currentTime - self.mLastTime
        if (elapsed < 0):
            elapsed += 1000
        self.mLastTime = currentTime
        self.update.emit(elapsed)

    def updateState(self, newState, oldState):
        if (newState == QAbstractAnimation.Stopped):
            self.mLastTime = 0
