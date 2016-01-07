##
# objecttypesmodel.py
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

from pyqtcore import QVector
from objecttypes import ObjectType
from PyQt5.QtCore import (
    Qt,
    QVariant, 
    QModelIndex,
    QAbstractTableModel
)
class ObjectTypesModel(QAbstractTableModel):
    ColorRole = Qt.UserRole

    def __init__(self, parent):
        super().__init__(parent)
        
        self.mObjectTypes = QVector()
        
    def setObjectTypes(self, objectTypes):
        self.beginResetModel()
        self.mObjectTypes = objectTypes
        self.endResetModel()

    def objectTypes(self):
        return self.mObjectTypes
        
    def rowCount(self, parent):
        if parent.isValid():
            _x = 0
        else:
            _x = self.mObjectTypes.size()
        return _x

    def columnCount(self, parent):
        if parent.isValid():
            _x = 0
        else:
            _x = 2
        return _x

    def headerData(self, section, orientation, role):
        if (orientation == Qt.Horizontal):
            if (role == Qt.DisplayRole):
                x = section
                if x==0:
                    return self.tr("Type")
                elif x==1:
                    return self.tr("Color")
            elif (role == Qt.TextAlignmentRole):
                return Qt.AlignLeft

        return QVariant()

    def data(self, index, role):
        # QComboBox requests data for an invalid index when the model is empty
        if (not index.isValid()):
            return QVariant()
        objectType = self.mObjectTypes.at(index.row())
        if (role == Qt.DisplayRole or role == Qt.EditRole):
            if (index.column() == 0):
                return objectType.name
        if (role == ObjectTypesModel.ColorRole and index.column() == 1):
            return objectType.color
        return QVariant()

    def setData(self, index, value, role):
        if (role == Qt.EditRole and index.column() == 0):
            self.mObjectTypes[index.row()].name = value.strip()
            self.dataChanged.emit(index, index)
            return True

        return False

    def flags(self, index):
        f = super().flags(index)
        if (index.column() == 0):
            f |= Qt.ItemIsEditable
        return f

    def setObjectTypeColor(self, objectIndex, color):
        self.mObjectTypes[objectIndex].color = color
        mi = self.index(objectIndex, 1)
        self.dataChanged.emit(mi, mi)

    def removeObjectTypes(self, indexes):
        rows = QVector()
        for index in indexes:
            rows.append(index.row())
        rows = sorted(rows)
        for i in range(len(rows) - 1, -1, -1):
            row = rows[i]
            self.beginRemoveRows(QModelIndex(), row, row)
            self.mObjectTypes.remove(row)
            self.endRemoveRows()

    def appendNewObjectType(self):
        self.beginInsertRows(QModelIndex(), self.mObjectTypes.size(), self.mObjectTypes.size())
        self.mObjectTypes.append(ObjectType())
        self.endInsertRows()
