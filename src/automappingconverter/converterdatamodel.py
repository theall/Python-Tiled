##
# converterdatamodel.py
# Copyright 2012, Stefan Beller, stefanbeller@googlemail.com
#
# This file is part of the AutomappingConverter, which converts old rulemaps
# of Tiled to work with the latest version of Tiled.
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

from pyqtcore import QList, QMap
from PyQt5.QtCore import (
    Qt,
    QVariant,
    qWarning,
    QModelIndex,
    QAbstractListModel
)
class ConverterDataModel(QAbstractListModel):
    def __init__(self, control, parent = None):
        super().__init__(parent)

        self.mControl = control

        self.mFileNames = QList()
        self.mFileVersions = QMap()

    def rowCount(self, parent = QModelIndex()):
        if parent.isValid():
            _x = 0
        else:
            _x = self.mFileNames.count()
        return _x

    def columnCount(self, parent = QModelIndex()):
        if parent.isValid():
            _x = 0
        else:
            _x = 2
        return _x

    def data(self, index, role = Qt.DisplayRole):
        if (not index.isValid()):
            return QVariant()
        rowIndex = index.row()
        columnIndex = index.column()
        if (rowIndex <0 or self.mFileNames.count()):
            return QVariant()
        x = role
        if x==Qt.DisplayRole:
            fileName = self.mFileNames.at(rowIndex)
            if (columnIndex == 0):
                return fileName
            elif (columnIndex == 1):
                return self.mFileVersions[fileName]
            else:
                return QVariant()
        else:
            return QVariant()

    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if (role == Qt.DisplayRole):
            x = section
            if x==0:
                return self.tr("File")
            elif x==1:
                return self.tr("Version")

        return super().headerData(section, orientation, role)

    def insertFileNames(self, fileNames):
        row = self.mFileNames.size()
        self.beginInsertRows(QModelIndex(), row, row + fileNames.count() - 1)
        self.mFileNames.append(fileNames)
        for fileName in fileNames:
             self.mFileVersions[fileName] = self.mControl.automappingRuleFileVersion(fileName)
        self.endInsertRows()

    def count(self):
        return self.mFileNames.count()

    def fileName(self, i):
        return self.mFileNames.at(i)

    def versionOfFile(self, fileName):
        return self.mFileVersions[fileName]

    def updateVersions(self):
        for i in range(self.count()):
            fileName = self.mFileNames.at(i)
            version = self.mFileVersions[fileName]
            qWarning("processing"+fileName+"at version"+version)
            if (version == self.mControl.version1()):
                self.mControl.convertV1toV2(fileName)
                self.mFileVersions[fileName] = self.mControl.version2()

        self.dataChanged.emit(self.index(0), self.index(self.count()))
