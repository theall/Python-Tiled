##
# painttilelayer.py
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

from tilepainter import TilePainter
from undocommands import UndoCommands
from PyQt5.QtGui import QRegion
from PyQt5.QtCore import (
    QRect,
    QPoint,
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QUndoCommand
)
##
# A command that paints one tile layer on top of another tile layer.
##
class PaintTileLayer(QUndoCommand):

    ##
    # Constructor.
    #
    # @param mapDocument the map document that's being edited
    # @param target      the target layer to paint on
    # @param x           the x position of the paint location
    # @param y           the y position of the paint location
    # @param source      the source layer to paint on the target layer
    ##
    def __init__(self, mapDocument, target, x, y, source):
        super().__init__()
        
        self.mMapDocument = mapDocument
        self.mTarget = target
        self.mSource = source.clone()
        self.mX = x
        self.mY = y
        self.mPaintedRegion = QRegion(x, y, source.width(), source.height())
        self.mMergeable = False

        self.mErased = self.mTarget.copy(self.mX - self.mTarget.x(),
                                self.mY - self.mTarget.y(),
                                self.mSource.width(), self.mSource.height())
        self.setText(QCoreApplication.translate("Undo Commands", "Paint"))

    def __del__(self):
        del self.mSource
        del self.mErased

    ##
    # Sets whether this undo command can be merged with an existing command.
    ##
    def setMergeable(self, mergeable):
        self.mMergeable = mergeable

    def undo(self):
        painter = TilePainter(self.mMapDocument, self.mTarget)
        painter.setCells(self.mX, self.mY, self.mErased, self.mPaintedRegion)
        
        super().undo() # undo child commands

    def redo(self):
        super().redo() # redo child commands
        
        painter = TilePainter(self.mMapDocument, self.mTarget)
        painter.drawCells(self.mX, self.mY, self.mSource)

    def id(self):
        return UndoCommands.Cmd_PaintTileLayer

    def mergeWith(self, other):
        o = other
        if (not (self.mMapDocument == o.mMapDocument and self.mTarget == o.mTarget and o.mMergeable)):
            return False
        newRegion = o.mPaintedRegion.subtracted(self.mPaintedRegion)
        combinedRegion = self.mPaintedRegion.united(o.mPaintedRegion)
        bounds = QRect(self.mX, self.mY, self.mSource.width(), self.mSource.height())
        combinedBounds = combinedRegion.boundingRect()
        # Resize the erased tiles and source layers when necessary
        if (bounds != combinedBounds):
            shift = bounds.topLeft() - combinedBounds.topLeft()
            self.mErased.resize(combinedBounds.size(), shift)
            self.mSource.resize(combinedBounds.size(), shift)

        mX = combinedBounds.left()
        self.mY = combinedBounds.top()
        self.mPaintedRegion = combinedRegion
        # Copy the painted tiles from the other command over
        pos = QPoint(o.mX, o.mY) - combinedBounds.topLeft()
        self.mSource.merge(pos, o.mSource)
        # Copy the newly erased tiles from the other command over
        for rect in newRegion.rects():
            for y in range(rect.top(), rect.bottom()+1):
                for x in range(rect.left(), rect.right()+1):
                    self.mErased.setCell(x - mX,
                                     y - self.mY,
                                     o.mErased.cellAt(x - o.mX, y - o.mY))
        return True
