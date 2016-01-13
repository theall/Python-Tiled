##
# tileanimationeditor.py
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
from zoomable import Zoomable
from tile import Frame
from utils import Utils
from object import Object
from libtiled.tiled import TILES_MIMETYPE, FRAMES_MIMETYPE
from rangeset import RangeSet
from tilesetmodel import TilesetModel
from tileanimationdriver import TileAnimationDriver
from changetileanimation import ChangeTileAnimation
from Ui_tileanimationeditor import Ui_TileAnimationEditor
from pyqtcore import QList, QVector, QStringList
from PyQt5.QtCore import (
    Qt,
    QEvent,
    QVariant,
    QIODevice,
    QMimeData,
    QByteArray,
    pyqtSignal,
    QDataStream,
    QAbstractListModel,
    QModelIndex
)
from PyQt5.QtGui import (
    QKeySequence
)
from PyQt5.QtWidgets import (
    QShortcut,
    QWidget,
    QApplication
)

class TileAnimationEditor(QWidget):
    closed = pyqtSignal()

    def __init__(self, parent = None):
        super().__init__(parent, Qt.Window)
        self.mUi = Ui_TileAnimationEditor()
        self.mMapDocument = None
        self.mTile = None
        self.mFrameListModel = FrameListModel(self)
        self.mApplyingChanges = False
        self.mPreviewAnimationDriver = TileAnimationDriver(self)
        self.mPreviewFrameIndex = 0
        self.mPreviewUnusedTime = 0

        self.mUi.setupUi(self)
        zoomable = Zoomable(self)
        zoomable.connectToComboBox(self.mUi.zoomComboBox)
        self.mUi.frameList.setModel(self.mFrameListModel)
        self.mUi.tilesetView.setMarkAnimatedTiles(False)
        self.mUi.tilesetView.setZoomable(zoomable)
        self.mUi.tilesetView.doubleClicked.connect(self.addFrameForTileAt)
        self.mFrameListModel.dataChanged.connect(self.framesEdited)
        self.mFrameListModel.rowsInserted.connect(self.framesEdited)
        self.mFrameListModel.rowsRemoved.connect(self.framesEdited)
        self.mFrameListModel.rowsMoved.connect(self.framesEdited)
        self.mPreviewAnimationDriver.update.connect(self.advancePreviewAnimation)
        undoShortcut = QShortcut(QKeySequence.Undo, self)
        redoShortcut = QShortcut(QKeySequence.Redo, self)
        deleteShortcut = QShortcut(QKeySequence.Delete, self)
        deleteShortcut2 = QShortcut(QKeySequence.Back, self)
        undoShortcut.activated.connect(self.undo)
        redoShortcut.activated.connect(self.redo)
        deleteShortcut.activated.connect(self.delete_)
        deleteShortcut2.activated.connect(self.delete_)
        Utils.restoreGeometry(self)
        self.mUi.horizontalSplitter.setSizes(QList([128, 512]))

    def __del__(self):
        del self.mUi

    def setMapDocument(self, mapDocument):
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
        self.mMapDocument = mapDocument
        self.mUi.tilesetView.setMapDocument(mapDocument)
        if (self.mMapDocument):
            self.mMapDocument.tileAnimationChanged.connect(self.tileAnimationChanged)
            self.mMapDocument.tilesetFileNameChanged.connect(self.tilesetFileNameChanged)

    def writeSettings(self):
        Utils.saveGeometry(self)

    def setTile(self, tile):
        if type(tile)==list:
            tile = tile[0]
            
        self.mTile = tile
        #self.mUi.tilesetView.model().close()
        if (tile):
            self.mFrameListModel.setFrames(tile.tileset(), tile.frames())
            tilesetModel = TilesetModel(tile.tileset(), self.mUi.tilesetView)
            self.mUi.tilesetView.setModel(tilesetModel)
        else:
            self.mFrameListModel.setFrames(None, QVector())

        self.mUi.frameList.setEnabled(bool(tile and not tile.tileset().isExternal()))
        self.resetPreview()

    def closeEvent(self, event):
        super().closeEvent(event)
        if (event.isAccepted()):
            self.closed.emit()

    def changeEvent(self, e):
        super().changeEvent(e)
        x = e.type()
        if x==QEvent.LanguageChange:
            self.mUi.retranslateUi(self)
        else:
            pass

    def showEvent(self, arg1):
        self.mPreviewAnimationDriver.start()

    def hideEvent(self, arg1):
        self.mPreviewAnimationDriver.stop()

    def framesEdited(self):
        undoStack = self.mMapDocument.undoStack()
        self.mApplyingChanges = True
        undoStack.push(ChangeTileAnimation(self.mMapDocument,
                                                self.mTile,
                                                self.mFrameListModel.frames()))
        self.mApplyingChanges = False

    def tileAnimationChanged(self, tile):
        if (self.mTile != tile):
            return
        self.resetPreview()
        if (self.mApplyingChanges):
            return
        self.mFrameListModel.setFrames(tile.tileset(), tile.frames())

    def tilesetFileNameChanged(self, tileset):
        if (self.mTile and self.mTile.tileset() == tileset):
            self.mUi.frameList.setEnabled(not tileset.isExternal())

    def currentObjectChanged(self, object):
        # If a tile object is selected, edit the animation frames for that tile
        if object and object.typeId() == Object.MapObjectType:
            cell = object.cell()
            if cell.tile:
                self.setTile(cell.tile)

    def addFrameForTileAt(self, index):
        if (self.mTile.tileset().isExternal()):
            return
        tile = self.mUi.tilesetView.tilesetModel().tileAt(index)
        self.mFrameListModel.addTileIdAsFrame(tile.id())

    def undo(self):
        if (self.mMapDocument):
            self.mMapDocument.undoStack().undo()

    def redo(self):
        if (self.mMapDocument):
            self.mMapDocument.undoStack().redo()

    def delete_(self):
        if (not self.mMapDocument or not self.mTile):
            return
        if (self.mTile.tileset().isExternal()):
            return
        selectionModel = self.mUi.frameList.selectionModel()
        indexes = selectionModel.selectedIndexes()
        if len(indexes)==0:
            return
        undoStack = self.mMapDocument.undoStack()
        undoStack.beginMacro(self.tr("Delete Frames"))
        ranges = RangeSet()
        for index in indexes:
            ranges.insert(index.row())
        # Iterate backwards over the ranges in order to keep the indexes valid
        firstRange = ranges.begin()
        it = ranges.end()
        while (it != firstRange):
            it -= 1
            item = ranges.item(it)
            length = item[1] - item[0] + 1
            self.mFrameListModel.removeRows(item[0], length, QModelIndex())

        undoStack.endMacro()

    def advancePreviewAnimation(self, ms):
        if (not self.mTile or not self.mTile.isAnimated()):
            return
        self.mPreviewUnusedTime += ms
        frames = self.mTile.frames()
        frame = frames.at(self.mPreviewFrameIndex)
        previousTileId = frame.tileId
        while (frame.duration > 0 and self.mPreviewUnusedTime > frame.duration):
            self.mPreviewUnusedTime -= frame.duration
            self.mPreviewFrameIndex = (self.mPreviewFrameIndex + 1) % frames.size()
            frame = frames.at(self.mPreviewFrameIndex)

        if (previousTileId != frame.tileId):
            tile = self.mTile.tileset().tileAt(frame.tileId)
            if tile:
                self.mUi.preview.setPixmap(tile.image())

    def resetPreview(self):
        self.mPreviewFrameIndex = 0
        self.mPreviewUnusedTime = 0
        if (self.mTile and self.mTile.isAnimated()):
            tileId = self.mTile.frames().first().tileId
            tile = self.mTile.tileset().tileAt(tileId)
            if tile:
                self.mUi.preview.setPixmap(tile.image())
                return

        self.mUi.preview.setText(QApplication.translate("TileAnimationEditor", "Preview"))

class FrameListModel(QAbstractListModel):
    DEFAULT_DURATION = 100

    def __init__(self, parent):
        super().__init__(parent)
        
        self.mFrames = QVector()
        self.mTileset = None

    def rowCount(self, parent):
        if parent.isValid():
            _x = 0
        else:
            _x = self.mFrames.size()
        return _x

    def data(self, index, role):
        x = role
        if x==Qt.EditRole or x==Qt.DisplayRole:
            return self.mFrames.at(index.row()).duration
        elif x==Qt.DecorationRole:
            tileId = self.mFrames.at(index.row()).tileId
            tile = self.mTileset.tileAt(tileId)
            if tile:
                return tile.image()

        return QVariant()

    def setData(self, index, value, role):
        if (role == Qt.EditRole):
            duration = value
            if (duration >= 0):
                self.mFrames[index.row()].duration = duration
                self.dataChanged.emit(index, index)
                return True

        return False

    def flags(self, index):
        defaultFlags = super().flags(index)
        if (index.isValid()):
            return Qt.ItemIsDragEnabled | Qt.ItemIsEditable | defaultFlags
        else:
            return Qt.ItemIsDropEnabled | defaultFlags

    def removeRows(self, row, count, parent):
        if (not parent.isValid()):
            if (count > 0):
                self.beginRemoveRows(parent, row, row + count - 1)
                self.mFrames.remove(row, count)
                self.endRemoveRows()

            return True

        return False

    def mimeTypes(self):
        types = QStringList()
        types.append(TILES_MIMETYPE)
        types.append(FRAMES_MIMETYPE)
        return types

    def mimeData(self, indexes):
        mimeData = QMimeData()
        encodedData = QByteArray()
        stream = QDataStream(encodedData, QIODevice.WriteOnly)
        for index in indexes:
            if (index.isValid()):
                frame = self.mFrames.at(index.row())
                stream.writeInt(frame.tileId)
                stream.writeInt(frame.duration)

        mimeData.setData(FRAMES_MIMETYPE, encodedData)
        return mimeData

    def dropMimeData(self, data, action, row, column, parent):
        if (action == Qt.IgnoreAction):
            return True
        if (column > 0):
            return False
        beginRow = 0
        if (row != -1):
            beginRow = row
        elif parent.isValid():
            beginRow = parent.row()
        else:
            beginRow = self.mFrames.size()
        newFrames = QVector()
        if (data.hasFormat(FRAMES_MIMETYPE)):
            encodedData = data.data(FRAMES_MIMETYPE)
            stream = QDataStream(encodedData, QIODevice.ReadOnly)
            while (not stream.atEnd()):
                frame = Frame()
                frame.tileId = stream.readInt()
                frame.duration = stream.readInt()
                newFrames.append(frame)
        elif (data.hasFormat(TILES_MIMETYPE)):
            encodedData = data.data(TILES_MIMETYPE)
            stream = QDataStream(encodedData, QIODevice.ReadOnly)
            while (not stream.atEnd()):
                frame = Frame()
                frame.tileId = stream.readInt()
                frame.duration = FrameListModel.DEFAULT_DURATION
                newFrames.append(frame)

        if (newFrames.isEmpty()):
            return False
        self.beginInsertRows(QModelIndex(), beginRow, beginRow + newFrames.size() - 1)
        self.mFrames.insert(beginRow, newFrames.size(), Frame())
        for i in range(newFrames.size()):
            self.mFrames[i + beginRow] = newFrames[i]
        self.endInsertRows()
        return True

    def supportedDropActions(self):
        return Qt.CopyAction | Qt.MoveAction

    def setFrames(self, tileset, frames):
        self.beginResetModel()
        self.mTileset = tileset
        self.mFrames = frames
        self.endResetModel()

    def addTileIdAsFrame(self, id):
        frame = Frame()
        frame.tileId = id
        frame.duration = FrameListModel.DEFAULT_DURATION
        self.addFrame(frame)

    def frames(self):
        return self.mFrames

    def addFrame(self, frame):
        self.beginInsertRows(QModelIndex(), self.mFrames.size(), self.mFrames.size())
        self.mFrames.append(frame)
        self.endInsertRows()
