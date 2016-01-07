# -*- coding: utf-8 -*-
##
# abstractimagetool.py
# Copyright 2014, Mattia Basaglia
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
###

from abstracttool import AbstractTool
from imagelayer import ImageLayer

###
# A convenient base class for tools that work on image layers.
##
class AbstractImageTool(AbstractTool):
    ###
    # Constructs an abstract image tool with the given \a name and \a icon.
    ##
    def __init__(self, name, icon, shortcut, parent = None):
        super(AbstractImageTool, self).__init__(name, icon, shortcut, parent)

        self.mMapScene = None

    def activate(self, scene):
        self.mMapScene = scene

    def deactivate(self, scene):
        self.mMapScene = None

    def keyPressed(self, event):
        event.ignore()

    def mouseLeft(self):
        self.setStatusInfo('')

    def mouseMoved(self, pos, modifiers):
        tilePosF = self.mapDocument().renderer().screenToTileCoords_(pos)
        self.setStatusInfo("%d, %d"%(int(tilePosF.x()), int(tilePosF.y())))

    def updateEnabledState(self):
        self.setEnabled(bool(self.currentImageLayer()))

    def mapScene(self):
        return self.mMapScene

    def currentImageLayer(self):
        if (not self.mapDocument()):
            return None
        currentLayer = self.mapDocument().currentLayer()
        if type(currentLayer)==ImageLayer:
            return currentLayer
        return None

