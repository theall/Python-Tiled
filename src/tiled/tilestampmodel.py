##
# tilestampmodel.py
# Copyright 2015, Thorbjørn Lindeijer <bjorn@lindeijer.nl>
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


from thumbnailrenderer import ThumbnailRenderer
from tilestamp import TileStamp
from pyqtcore import (
    QList
)
from PyQt5.QtCore import (
    QAbstractItemModel,
    Qt,
    QVariant,
    pyqtSignal, 
    QSize, 
    QModelIndex
)
from PyQt5.QtGui import (
    QPixmap
)

def renderThumbnail(renderer):
    return QPixmap.fromImage(renderer.render(QSize(64, 64))
                              .scaled(32, 32,
                                      Qt.IgnoreAspectRatio,
                                      Qt.SmoothTransformation))
                                      
class TileStampModel(QAbstractItemModel):
    stampAdded = pyqtSignal(TileStamp)
    stampRenamed = pyqtSignal(TileStamp)
    stampChanged = pyqtSignal(TileStamp)
    stampRemoved = pyqtSignal(TileStamp)

    def __init__(self, parent = None):
        super().__init__(parent)

        self.mStamps = QList()

    def index(self, *args):
        l = len(args)
        if l==1:
            stamp = args[0]
            i = self.mStamps.indexOf(stamp)
            if i == -1:
                return QModelIndex()
            else:
                return TileStampModel.index(i, 0)
        elif l==2 or l==3:
            if l==2:
                row, column = args
            elif l==3:
                row, column, parent = args
                
            if (not self.hasIndex(row, column, parent)):
                return QModelIndex()
            if (not parent.isValid()):
                return self.createIndex(row, column)
            elif (self.isStamp(parent)):
                return self.createIndex(row, column, parent.row() + 1)
            return QModelIndex()
    
    def parent(self, index):
        id = index.internalId()
        if id:
            return self.createIndex(id - 1, 0)
        return QModelIndex()
    
    def rowCount(self, parent = QModelIndex()):
        if (not parent.isValid()):
            return self.mStamps.size()
        elif (self.isStamp(parent)):
            stamp = self.mStamps.at(parent.row())
            count = stamp.variations().size()
            # it does not make much sense to expand single variations
            if count==1:
                return 0
            else:
                return count        
        return 0
    
    def columnCount(self, parent = QModelIndex()):
        return 2 # stamp | probability
    
    def headerData(self, section, orientation, role = Qt.DisplayRole):
        if (role == Qt.DisplayRole and orientation == Qt.Horizontal):
            x = section
            if False:
                pass
            elif x==0:
                return self.tr("Stamp")
            elif x==1:
                return self.tr("Probability")

        return QVariant()
    
    def setData(self, index, value, role = Qt.EditRole):
        if self.isStamp(index):
            stamp = self.mStamps[index.row()]
            if (index.column() == 0):      # stamp name
                x = role
                if x==Qt.EditRole:
                    stamp.setName(value.toString())
                    self.dataChanged.emit(index, index)
                    self.stampRenamed.emit(stamp)
                    self.stampChanged.emit(stamp)
                    return True
                else:
                    pass
        elif (index.column() == 1):   # variation probability
            parent = index.parent()
            if self.isStamp(parent):
                stamp = self.mStamps[parent.row()]
                stamp.setProbability(index.row(), value.toReal())
                self.dataChanged.emit(index, index)
                probabilitySumIndex = TileStampModel.index(parent.row(), 1)
                self.dataChanged.emit(probabilitySumIndex, probabilitySumIndex)
                self.stampChanged.emit(stamp)
                return True

        return False
    
    def data(self, index, role = Qt.DisplayRole):
        if (self.isStamp(index)):
            stamp = self.mStamps.at(index.row())
            if (index.column() == 0):          # preview and name
                x = role
                if x==Qt.DisplayRole or x==Qt.EditRole:
                    return stamp.name()
                elif x==Qt.DecorationRole:
                    map = stamp.variations().first().map
                    thumbnail = self.mThumbnailCache.value(map)
                    if (thumbnail.isNull()):
                        renderer = ThumbnailRenderer(map)
                        thumbnail = renderThumbnail(renderer)
                        self.mThumbnailCache.insert(map, thumbnail)
                    
                    return thumbnail

            elif (index.column() == 1):   # sum of probabilities
                x = role
                if False:
                    pass
                elif x==Qt.DisplayRole:
                    if (stamp.variations().size() > 1):
                        sum = 0
                        for variation in stamp.variations():
                            sum += variation.probability
                        return sum
        else:
            variation = self.variationAt(index)
            if variation:
                if (index.column() == 0):
                    x = role
                    if x==Qt.DecorationRole:
                        map = variation.map
                        thumbnail = self.mThumbnailCache.value(map)
                        if (thumbnail.isNull()):
                            renderer = ThumbnailRenderer(map)
                            thumbnail = renderThumbnail(renderer)
                            self.mThumbnailCache.insert(map, thumbnail)
                        
                        return thumbnail

                elif (index.column() == 1):
                    x = role
                    if x==Qt.DisplayRole or x==Qt.EditRole:
                        return variation.probability
        
        return QVariant()
    
    def flags(self, index):
        rc = QAbstractItemModel.flags(index)
        validParent = index.parent().isValid()
        if ((not validParent and index.column() == 0) or    # can edit stamp names
                (validParent and index.column() == 1)):  # and variation probability
            rc |= Qt.ItemIsEditable
        return rc
        
    def removeRows(self, row, count, parent):
        if (parent.isValid()):
            # removing variations
            stamp = self.mStamps[parent.row()]
            # if only one variation is left, we make all variation rows disappear
            if (stamp.variations().size() - count == 1):
                self.beginRemoveRows(parent, 0, count)
            else:
                self.beginRemoveRows(parent, row, row + count - 1)
            
            for x in range(count, 0, -1):
                self.mThumbnailCache.remove(stamp.variations().at(row).map)
                stamp.deleteVariation(row)
            
            self.endRemoveRows()
            if (stamp.variations().isEmpty()):
                # remove stamp since all its variations were removed
                self.beginRemoveRows(QModelIndex(), parent.row(), parent.row())
                self.stampRemoved.emit(stamp)
                self.mStamps.removeAt(parent.row())
                self.endRemoveRows()
            else :
                if (row == 0):
                    # preview on stamp and probability sum need update
                    # (while technically I think this is correct, it triggers a
                    # repainting issue in QTreeView)
                    #emit dataChanged(index(parent.row(), 0),
                    #                 self.index(parent.row(), 1))
                    pass
                self.stampChanged.emit(stamp)
            
        else :
            # removing stamps
            self.beginRemoveRows(parent, row, row + count - 1)
            for x in range(count, 0, -1):
                for variation in self.mStamps.at(row).variations():
                    self.mThumbnailCache.remove(variation.map)
                self.stampRemoved.emit(self.mStamps.at(row))
                self.mStamps.removeAt(row)
            
            self.endRemoveRows()
        
        return True
    
    ##
    # Returns the stamp at the given \a index.
    ##
    def stampAt(self, index):
        return self.mStamps.at(index.row())

    def isStamp(self, index):
        return index.isValid() \
                and not index.parent().isValid() \
                and index.row() < self.mStamps.size()
    
    def variationAt(self, index):
        if (not index.isValid()):
            return None
        parent = index.parent()
        if (self.isStamp(parent)):
            stamp = self.mStamps.at(parent.row())
            return stamp.variations().at(index.row())
        
        return None
        
    def stamps(self):
        return self.mStamps

    def addStamp(self, stamp):
        if (self.mStamps.contains(stamp)):
            return
        self.beginInsertRows(QModelIndex(), self.mStamps.size(), self.mStamps.size())
        self.mStamps.append(stamp)
        self.stampAdded.emit(stamp)
        self.endInsertRows()
    
    def removeStamp(self, stamp):
        index = self.mStamps.indexOf(stamp)
        if (index == -1):
            return
        self.beginRemoveRows(QModelIndex(), index, index)
        self.mStamps.removeAt(index)
        self.endRemoveRows()
        for variation in stamp.variations():
            self.mThumbnailCache.remove(variation.map)
        self.stampRemoved.emit(stamp)
    
    def addVariation(self, stamp, variation):
        index = self.mStamps.indexOf(stamp)
        if (index == -1):
            return
        variationCount = stamp.variations().size()
        if (variationCount == 1):
            self.beginInsertRows(TileStampModel.index(index, 0), 0, 1)
        else:
            self.beginInsertRows(TileStampModel.index(index, 0),
                            variationCount, variationCount)
        self.mStamps[index].addVariation(variation)
        self.endInsertRows()
        probabilitySumIndex = TileStampModel.index(index, 1)
        self.dataChanged.emit(probabilitySumIndex, probabilitySumIndex)
        self.stampChanged.emit(stamp)
    
    def clear(self):
        self.beginResetModel()
        self.mStamps.clear()
        self.mThumbnailCache.clear()
        self.endResetModel()
