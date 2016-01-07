##
# automapperwrapper.py
# Copyright 2010-2011, Stefan Beller, stefanbeller@googlemail.com
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

from pyqtcore import (
    QVector,
    QSet,
)
from PyQt5.QtWidgets import (
    QUndoCommand
)
##
# This is a wrapper class for the AutoMapper class.
# Here in this class only undo/redo functionality all rulemaps
# is provided.
# This class will take a snapshot of the layers before and after the
# automapping is done. In between instances of AutoMapper are doing the work.
##
class AutoMapperWrapper(QUndoCommand):
    def __init__(self, mapDocument, autoMapper, where):
        super().__init__()
        
        self.mLayersAfter = QVector()
        self.mLayersBefore = QVector()
        self.mMapDocument = mapDocument
        map = self.mMapDocument.Map()
        touchedLayers = QSet()
        index = 0
        while (index < autoMapper.size()):
            a = autoMapper.at(index)
            if (a.prepareAutoMap()):
                touchedLayers|= a.getTouchedTileLayers()
                index += 1
            else:
                autoMapper.remove(index)

        for layerName in touchedLayers:
            layerindex = map.indexOfLayer(layerName)
            self.mLayersBefore (map.layerAt(layerindex).clone())

        for a in autoMapper:
            a.autoMap(where)
        for layerName in touchedLayers:
            layerindex = map.indexOfLayer(layerName)
            # layerindex exists, because AutoMapper is still alive, dont check
            self.mLayersAfter (map.layerAt(layerindex).clone())

        # reduce memory usage by saving only diffs
        for i in range(self.mLayersAfter.size()):
            before = self.mLayersBefore.at(i)
            after = self.mLayersAfter.at(i)
            diffRegion = before.computeDiffRegion(after).boundingRect()
            before1 = before.copy(diffRegion)
            after1 = after.copy(diffRegion)
            before1.setPosition(diffRegion.topLeft())
            after1.setPosition(diffRegion.topLeft())
            before1.setName(before.name())
            after1.setName(after.name())
            self.mLayersBefore.replace(i, before1)
            self.mLayersAfter.replace(i, after1)
            del before
            del after

        for a in autoMapper:
            a.cleanAll()

    def __del__(self):
        for i in self.mLayersAfter:
            del i
        for i in self.mLayersBefore:
            del i

    def undo(self):
        map = self.mMapDocument.Map()
        for layer in self.mLayersBefore:
            layerindex = map.indexOfLayer(layer.name())
            if (layerindex != -1):
                self.patchLayer(layerindex, layer)

    def redo(self):
        map = self.mMapDocument.Map()
        for layer in self.mLayersAfter:
            layerindex = (map.indexOfLayer(layer.name()))
            if (layerindex != -1):
                self.patchLayer(layerindex, layer)

    def patchLayer(self, layerIndex, layer):
        map = self.mMapDocument.Map()
        b = layer.bounds()
        t = map.layerAt(layerIndex)
        t.setCells(b.left() - t.x(), b.top() - t.y(), layer,
                    b.translated(-t.position()))
        self.mMapDocument.emitRegionChanged(b, t)
