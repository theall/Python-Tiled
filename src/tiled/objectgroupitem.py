##
# objectgroupitem.py
# Copyright 2009, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from PyQt5.QtCore import QRectF
from PyQt5.QtWidgets import (
    QGraphicsItem
)
##
# A graphics item representing an object group in a QGraphicsView. It only
# serves to group together the objects belonging to the same object group.
#
# @see MapObjectItem
##
class ObjectGroupItem(QGraphicsItem):

    def __init__(self, objectGroup):
        super().__init__()

        # Since we don't do any painting, we can spare us the call to paint()
        self.mObjectGroup = objectGroup
        self.setFlag(QGraphicsItem.ItemHasNoContents)
        
        self.setOpacity(objectGroup.opacity())
        self.setPos(objectGroup.offset())
        
    def objectGroup(self):
        return self.mObjectGroup

    ##
    # Changes the object group represented by this item. Currently only expected
    # to be used by the CreateObjectTool.
    ##
    def setObjectGroup(self, objectGroup):
        if self.mObjectGroup == objectGroup:
            return

        self.mObjectGroup = objectGroup
        self.setOpacity(self.mObjectGroup.opacity())
        self.setPos(self.mObjectGroup.offset())

    # QGraphicsItem
    def boundingRect(self):
        return QRectF()

    def paint(self, painter, option, widget = None):
        pass
