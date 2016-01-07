##
# changeobjectgroupproperties.py
# Copyright 2010, Jeff Bland <jeff@teamphobic.com>
# Copyright 2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)
class ChangeObjectGroupProperties(QUndoCommand):

    ##
    # Constructs a new 'Change Object Layer Properties' command.
    #
    # @param mapDocument     the map document of the object group's map
    # @param objectGroup     the object group in to modify
    # @param newColor        the new color to apply
    ##
    def __init__(self, mapDocument, objectGroup, newColor, newDrawOrder):
        super().__init__(QCoreApplication.translate("Undo Commands", "Change Object Layer Properties"))
        
        self.mMapDocument = mapDocument
        self.mObjectGroup = objectGroup
        self.mUndoColor = objectGroup.color()
        self.mRedoColor = newColor
        self.mUndoDrawOrder = objectGroup.drawOrder()
        self.mRedoDrawOrder = newDrawOrder

    def undo(self):
        self.mObjectGroup.setColor(self.mUndoColor)
        self.mObjectGroup.setDrawOrder(self.mUndoDrawOrder)
        self.mMapDocument.emitObjectGroupChanged(self.mObjectGroup)

    def redo(self):
        self.mObjectGroup.setColor(self.mRedoColor)
        self.mObjectGroup.setDrawOrder(self.mRedoDrawOrder)
        self.mMapDocument.emitObjectGroupChanged(self.mObjectGroup)
