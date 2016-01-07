##
# automappingutils.py
# Copyright 2012, Stefan Beller, stefanbeller@googlemail.com
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
from pyqtcore import QList
from PyQt5.QtGui import QRegion
from PyQt5.QtCore import QRectF
from addremovemapobject import RemoveMapObject

def eraseRegionObjectGroup(mapDocument, layer, where):
    undo = mapDocument.undoStack()
    for obj in layer.objects():
        # TODO: we are checking bounds, which is only correct for rectangles and 
        # tile objects. polygons and polylines are not covered correctly by this
        # erase method (we are in fact deleting too many objects)
        # TODO2: toAlignedRect may even break rects.
        # Convert the boundary of the object into tile space
        objBounds = obj.boundsUseTile()
        tl = mapDocument.renderer().pixelToTileCoords_(objBounds.topLeft())
        tr = mapDocument.renderer().pixelToTileCoords_(objBounds.topRight())
        br = mapDocument.renderer().pixelToTileCoords_(objBounds.bottomRight())
        bl = mapDocument.renderer().pixelToTileCoords_(objBounds.bottomLeft())
        objInTileSpace = QRectF()
        objInTileSpace.setTopLeft(tl)
        objInTileSpace.setTopRight(tr)
        objInTileSpace.setBottomRight(br)
        objInTileSpace.setBottomLeft(bl)
        objAlignedRect = objInTileSpace.toAlignedRect()
        if (where.intersects(objAlignedRect)):
            undo.push(RemoveMapObject(mapDocument, obj))

def tileRegionOfObjectGroup(layer):
    ret = QRegion()
    for obj in layer.objects():
        # TODO: we are using bounds, which is only correct for rectangles and 
        # tile objects. polygons and polylines are not probably covering less
        # tiles.
        ret += obj.bounds().toAlignedRect()

    return ret

def objectsInRegion(layer, where):
    ret = QList()
    for obj in layer.objects():
        # TODO: we are checking bounds, which is only correct for rectangles and 
        # tile objects. polygons and polylines are not covered correctly by this
        # erase method (we are in fact deleting too many objects)
        # TODO2: toAlignedRect may even break rects.
        rect = obj.boundsUseTile().toAlignedRect()
        # QRegion.intersects() returns False for empty regions even if they are
        # contained within the region, so we also check for containment of the
        # top left to include the case of zero size objects.
        if (where.intersects(rect) or where.contains(rect.topLeft())):
            ret += obj

    return ret

