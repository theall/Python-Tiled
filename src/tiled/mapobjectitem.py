##
# mapobjectitem.py
# Copyright 2008, Roderic Morris <roderic@ccs.neu.edu>
# Copyright 2008-2011, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from objectgroup import ObjectGroup
import preferences
from PyQt5.QtCore import (
    Qt,
    QRectF,
    QCoreApplication
)
from PyQt5.QtGui import (
    QColor,
    QPolygonF
)
from PyQt5.QtWidgets import (
    QGraphicsItem
)
from pyqtcore import QString
##
# A graphics item displaying a map object.
##
class MapObjectItem(QGraphicsItem):
    _Type = QGraphicsItem.UserType + 1

    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('MapObjectItem', sourceText, disambiguation, n)

    def trUtf8(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('MapObjectItem', sourceText, disambiguation, n)

    ##
    # Constructor.
    #
    # @param object the object to be displayed
    # @param parent the item of the object group this object belongs to
    ##
    def __init__(self, object, mapDocument, parent = None):
        super().__init__(parent)
        
        self.mObject = object
        self.mMapDocument = mapDocument

        ## Bounding rect cached, for adapting to geometry change correctly. ##
        self.mBoundingRect = QRectF()
        self.mName = QString()
        self.mColor = QColor()
        self.mPolygon = QPolygonF()
        
        self.syncWithMapObject()
        
    def type(self):
        return MapObjectItem._Type

    def mapObject(self):
        return self.mObject

    ##
    # Should be called when the map object this item refers to was changed.
    ##
    def syncWithMapObject(self):
        color = MapObjectItem.objectColor(self.mObject)
        
        # Update the whole object when the name or polygon has changed
        if (self.mObject.name() != self.mName or self.mObject.polygon() != self.mPolygon or self.mColor != color):
            self.mName = self.mObject.name()
            self.mPolygon = self.mObject.polygon()
            self.mColor = color
            self.update()

        toolTip = self.mName
        tp = self.mObject.type()
        if tp != '':
            toolTip += " (" + tp + ""

        self.setToolTip(toolTip)
        renderer = self.mMapDocument.renderer()
        pixelPos = renderer.pixelToScreenCoords_(self.mObject.position())
        bounds = renderer.boundingRect(self.mObject)
        bounds.translate(-pixelPos)
        self.setPos(pixelPos)
        self.setRotation(self.mObject.rotation())
        objectGroup = self.mObject.objectGroup()
        if objectGroup:
            if (objectGroup.drawOrder() == ObjectGroup.DrawOrder.TopDownOrder):
                self.setZValue(pixelPos.y())

        if (self.mBoundingRect != bounds):
            # Notify the graphics scene about the geometry change in advance
            self.prepareGeometryChange()
            self.mBoundingRect = bounds

        self.setVisible(self.mObject.isVisible())

    # QGraphicsItem
    def boundingRect(self):
        return self.mBoundingRect

    def shape(self):
        path = self.mMapDocument.renderer().shape(self.mObject)
        path.translate(-self.pos())
        return path

    def paint(self, painter, option, widget = None):
        scale = widget.parent().zoomable().scale()
        painter.translate(-self.pos())
        self.mMapDocument.renderer().setPainterScale(scale)
        self.mMapDocument.renderer().drawMapObject(painter, self.mObject, self.mColor)

    ##
    # Resizes the associated map object. The \a size is given in tiles.
    ##
    def resizeObject(self, size):
        # Not using the MapObjectModel because it is also used during object
        # creation, when the object is not actually part of the map yet.
        self.mObject.setSize(size)
        self.syncWithMapObject()

    ##
    # Sets the rotation of the associated map object.
    ##
    def setObjectRotation(self, angle):
        self.mMapDocument.mapObjectModel().setObjectRotation(self.mObject, angle)

    ##
    # Sets a new polygon on the associated object.
    ##
    def setPolygon(self, polygon):
        # Not using the MapObjectModel because it is used during object creation,
        # when the object is not actually part of the map yet.
        self.mObject.setPolygon(polygon)
        self.syncWithMapObject()

    ##
    # A helper function to determine the color of a map object. The color is
    # determined first of all by the object type, and otherwise by the group
    # that the object is in. If still no color is defined, it defaults to
    # gray.
    ##
    def objectColor(object):
        # See if this object type has a color associated with it
        for _type in preferences.Preferences.instance().objectTypes():
            if _type.name.lower == object.type().lower():
                return type.color

        # If not, get color from object group
        objectGroup = object.objectGroup()
        if (objectGroup and objectGroup.color().isValid()):
            return objectGroup.color()
        # Fallback color
        return Qt.gray
