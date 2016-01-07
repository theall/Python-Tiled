##
# snaphelper.py
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
from PyQt5.QtCore import Qt

class SnapHelper():
    def __init__(self, renderer, modifiers = 0):
        self.mRenderer = renderer

        prefs = preferences.Preferences.instance()
        self.mSnapToGrid = prefs.snapToGrid()
        self.mSnapToFineGrid = prefs.snapToFineGrid()
        if (modifiers & Qt.ControlModifier):
            self.toggleSnap()

    def toggleSnap(self):
        self.mSnapToGrid = not self.mSnapToGrid
        self.mSnapToFineGrid = False

    def snaps(self):
        return self.mSnapToGrid or self.mSnapToFineGrid

    def snap(self, pixelPos):
        if (self.mSnapToFineGrid or self.mSnapToGrid):
            tileCoords = self.mRenderer.pixelToTileCoords_(pixelPos)
            if (self.mSnapToFineGrid):
                gridFine = preferences.Preferences.instance().gridFine()
                tileCoords = (tileCoords * gridFine).toPoint()
                tileCoords /= gridFine
            else:
                tileCoords = tileCoords.toPoint()

            pixelPos = self.mRenderer.tileToPixelCoords_(tileCoords)
