##
# mapdocument.py
# Copyright 2008-2014, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2009, Jeff Bland <jeff@teamphobic.com>
# Copyright 2011, Stefan Beller <stefanbeller@googlemail.com
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

from mapformat import MapFormat
from tmxmapformat import TmxMapFormat
from tileset import Tileset
from tilesetmanager import TilesetManager
from tilelayer import TileLayer
from tile import Tile
from terrainmodel import TerrainModel
from staggeredrenderer import StaggeredRenderer
from rotatemapobject import RotateMapObject
from resizetilelayer import ResizeTileLayer
from resizemap import ResizeMap
from pluginmanager import PluginManager
from orthogonalrenderer import OrthogonalRenderer
from offsetlayer import OffsetLayer
from objectgroup import ObjectGroup
from movemapobjecttogroup import MoveMapObjectToGroup
from movemapobject import MoveMapObject
from movelayer import MoveLayer
from map import Map
from mapobjectmodel import MapObjectModel
from layermodel import LayerModel
from isometricrenderer import IsometricRenderer
from imagelayer import ImageLayer
from hexagonalrenderer import HexagonalRenderer
from flipmapobjects import FlipMapObjects
from changeselectedarea import ChangeSelectedArea
from changeproperties import ChangeProperties
from addremovetileset import AddTileset
from addremovemapobject import RemoveMapObject, AddMapObject
from addremovelayer import AddLayer, RemoveLayer
from libtiled.tiled import RotateDirection
from layer import Layer
from object import Object
from pyqtcore import QString, QList
from PyQt5.QtCore import (
    QRect,
    QFileInfo,
    QObject,
    QPointF,
    QDateTime,
    pyqtSignal
)
from PyQt5.QtGui import (
    QRegion,
    QTransform
)
from PyQt5.QtWidgets import (
    QUndoStack
)

##
# Custom intersects check necessary because QRectF.intersects wants a
# non-empty area of overlap, but we should also consider overlap with empty
# area as intersection.
#
# Results for rectangles with negative size are undefined.
##
def intersects(a, b):
    return a.right() >= b.left() and a.bottom() >= b.top() and a.left() <= b.right() and a.top() <= b.bottom()

def visibleIn(area, object, renderer):
    boundingRect = renderer.boundingRect(object)
    if (object.rotation() != 0):
        # Rotate around object position
        pos = renderer.pixelToScreenCoords_(object.position())
        boundingRect.translate(-pos)
        transform = QTransform()
        transform.rotate(object.rotation())
        boundingRect = transform.mapRect(boundingRect)
        boundingRect.translate(pos)

    return intersects(area, boundingRect)

def isFromTileset(object, tileset):
    if (not object):
        return False
    if (object.typeId() == Object.TileType and tileset == object.tileset()):
        return True
    if (object.typeId() == Object.TerrainType and tileset == object.tileset()):
        return True
    return False

##
# Represents an editable map. The purpose of this class is to make sure that
# any editing operations will cause the appropriate signals to be emitted, in
# order to allow the GUI to update accordingly.
#
# At the moment the map document provides the layer model, keeps track of the
# the currently selected layer and provides an API for adding and removing
# map objects. It also owns the QUndoStack.
##
class MapDocument(QObject):
    fileNameChanged = pyqtSignal(str, str)
    modifiedChanged = pyqtSignal()
    saved = pyqtSignal()
    ##
    # Emitted when the selected tile region changes. Sends the currently
    # selected region and the previously selected region.
    ##
    selectedAreaChanged = pyqtSignal(QRegion, QRegion)
    ##
    # Emitted when the list of selected objects changes.
    ##
    selectedObjectsChanged = pyqtSignal()
    ##
    # Emitted when the list of selected tiles from the dock changes.
    ##
    selectedTilesChanged = pyqtSignal()
    currentObjectChanged = pyqtSignal(list)
    ##
    # Emitted when the map size or its tile size changes.
    ##
    mapChanged = pyqtSignal()
    layerAdded = pyqtSignal(int)
    layerAboutToBeRemoved = pyqtSignal(int)
    layerRenamed = pyqtSignal(int)
    layerRemoved = pyqtSignal(int)
    layerChanged = pyqtSignal(int)
    ##
    # Emitted after a new layer was added and the name should be edited.
    # Applies to the current layer.
    ##
    editLayerNameRequested = pyqtSignal()
    editCurrentObject = pyqtSignal()
    ##
    # Emitted when the current layer index changes.
    ##
    currentLayerIndexChanged = pyqtSignal(int)
    ##
    # Emitted when a certain region of the map changes. The region is given in
    # tile coordinates.
    ##
    regionChanged = pyqtSignal(QRegion, Layer)
    ##
    # Emitted when a certain region of the map was edited by user input.
    # The region is given in tile coordinates.
    # If multiple layers have been edited, multiple signals will be emitted.
    ##
    regionEdited = pyqtSignal(QRegion, Layer)
    tileLayerDrawMarginsChanged = pyqtSignal(TileLayer)
    tileTerrainChanged = pyqtSignal(QList)
    tileProbabilityChanged = pyqtSignal(Tile)
    tileObjectGroupChanged = pyqtSignal(Tile)
    tileAnimationChanged = pyqtSignal(Tile)
    objectGroupChanged = pyqtSignal(ObjectGroup)
    imageLayerChanged = pyqtSignal(ImageLayer)
    tilesetAboutToBeAdded = pyqtSignal(int)
    tilesetAdded = pyqtSignal(int, Tileset)
    tilesetAboutToBeRemoved = pyqtSignal(int)
    tilesetRemoved = pyqtSignal(Tileset)
    tilesetMoved = pyqtSignal(int, int)
    tilesetFileNameChanged = pyqtSignal(Tileset)
    tilesetNameChanged = pyqtSignal(Tileset)
    tilesetTileOffsetChanged = pyqtSignal(Tileset)
    tilesetChanged = pyqtSignal(Tileset)
    objectsAdded = pyqtSignal(QList)
    objectsInserted = pyqtSignal(ObjectGroup, int, int)
    objectsRemoved = pyqtSignal(QList)
    objectsChanged = pyqtSignal(QList)
    objectsIndexChanged = pyqtSignal(ObjectGroup, int, int)
    propertyAdded = pyqtSignal(Object, str)
    propertyRemoved = pyqtSignal(Object, str)
    propertyChanged = pyqtSignal(Object, str)
    propertiesChanged = pyqtSignal(Object)

    ##
    # Constructs a map document around the given map. The map document takes
    # ownership of the map.
    ##
    def __init__(self, map, fileName = QString()):
        super().__init__()

        ##
        # The filename of a plugin is unique. So it can be used to determine
        # the right plugin to be used for saving or reloading the map.
        # The nameFilter of a plugin can not be used, since it's translatable.
        # The filename of a plugin must not change while maps are open using this
        # plugin.
        ##
        self.mReaderFormat = None
        self.mWriterFormat = None
        self.mExportFormat = None
        self.mSelectedArea = QRegion()
        self.mSelectedObjects = QList()
        self.mSelectedTiles = QList()
        self.mCurrentLayerIndex = 0
        self.mLastSaved = QDateTime()
        self.mLastExportFileName = ''

        self.mFileName = fileName
        self.mMap = map
        self.mLayerModel = LayerModel(self)
        self.mCurrentObject = map ## Current properties object. ##
        self.mRenderer = None
        self.mMapObjectModel = MapObjectModel(self)
        self.mTerrainModel = TerrainModel(self, self)
        self.mUndoStack = QUndoStack(self)
        self.createRenderer()
        if (map.layerCount() == 0):
            _x = -1
        else:
            _x = 0
        self.mCurrentLayerIndex = _x
        self.mLayerModel.setMapDocument(self)
        # Forward signals emitted from the layer model
        self.mLayerModel.layerAdded.connect(self.onLayerAdded)
        self.mLayerModel.layerAboutToBeRemoved.connect(self.onLayerAboutToBeRemoved)
        self.mLayerModel.layerRemoved.connect(self.onLayerRemoved)
        self.mLayerModel.layerChanged.connect(self.layerChanged)
        # Forward signals emitted from the map object model
        self.mMapObjectModel.setMapDocument(self)
        self.mMapObjectModel.objectsAdded.connect(self.objectsAdded)
        self.mMapObjectModel.objectsChanged.connect(self.objectsChanged)
        self.mMapObjectModel.objectsRemoved.connect(self.onObjectsRemoved)
        self.mMapObjectModel.rowsInserted.connect(self.onMapObjectModelRowsInserted)
        self.mMapObjectModel.rowsRemoved.connect(self.onMapObjectModelRowsInsertedOrRemoved)
        self.mMapObjectModel.rowsMoved.connect(self.onObjectsMoved)
        self.mTerrainModel.terrainRemoved.connect(self.onTerrainRemoved)
        self.mUndoStack.cleanChanged.connect(self.modifiedChanged)
        # Register tileset references
        tilesetManager = TilesetManager.instance()
        tilesetManager.addReferences(self.mMap.tilesets())

    ##
    # Destructor.
    ##
    def __del__(self):
        # Unregister tileset references
        tilesetManager = TilesetManager.instance()
        tilesetManager.removeReferences(self.mMap.tilesets())
        del self.mRenderer
        del self.mMap

    ##
    # Saves the map to its current file name. Returns whether or not the file
    # was saved successfully. If not, <i>error</i> will be set to the error
    # message if it is not 0.
    ##
    def save(self, *args):
        l = len(args)
        if l==0:
            args = ('')
        if l==1:
            arg = args[0]
            file = QFileInfo(arg)
            if not file.isFile():
                fileName = self.fileName()
                error = args[0]
            else:
                fileName = arg
                error = ''
            return self.save(fileName, error)
        if l==2:
            ##
            # Saves the map to the file at \a fileName. Returns whether or not the
            # file was saved successfully. If not, <i>error</i> will be set to the
            # error message if it is not 0.
            #
            # If the save was successful, the file name of this document will be set
            # to \a fileName.
            #
            # The map format will be the same as this map was opened with.
            ##
            fileName, error = args
            mapFormat = self.mWriterFormat
            
            tmxMapFormat = TmxMapFormat()
            if (not mapFormat):
                mapFormat = tmxMapFormat
            if (not mapFormat.write(self.map(), fileName)):
                if (error):
                   error = mapFormat.errorString()
                return False

            self.undoStack().setClean()
            self.setFileName(fileName)
            self.mLastSaved = QFileInfo(fileName).lastModified()
            self.saved.emit()
            return True

    ##
    # Loads a map and returns a MapDocument instance on success. Returns 0
    # on error and sets the \a error message.
    ##
    def load(fileName, mapFormat = None):
        error = ''
        tmxMapFormat = TmxMapFormat()
        
        if (not mapFormat and not tmxMapFormat.supportsFile(fileName)):
            # Try to find a plugin that implements support for this format
            formats = PluginManager.objects(MapFormat)
            for format in formats:
                if (format.supportsFile(fileName)):
                    mapFormat = format
                    break

        map = None
        errorString = ''

        if mapFormat:
            map = mapFormat.read(fileName)
            errorString = mapFormat.errorString()
        else:
            map = tmxMapFormat.read(fileName)
            errorString = tmxMapFormat.errorString()

        if (not map):
            error = errorString
            return None, error

        mapDocument = MapDocument(map, fileName)
        if mapFormat:
            mapDocument.setReaderFormat(mapFormat)
            if mapFormat.hasCapabilities(MapFormat.Write):
                mapDocument.setWriterFormat(mapFormat)

        return mapDocument, error

    def fileName(self):
        return self.mFileName

    def lastExportFileName(self):
        return self.mLastExportFileName

    def setLastExportFileName(self, fileName):
        self.mLastExportFileName = fileName

    def readerFormat(self):
        return self.mReaderFormat

    def setReaderFormat(self, format):
        self.mReaderFormat = format

    def writerFormat(self):
        return self.mWriterFormat

    def setWriterFormat(self, format):
        self.mWriterFormat = format

    def exportFormat(self):
        return self.mExportFormat

    def setExportFormat(self, format):
        self.mExportFormat = format
        
    ##
    # Returns the name with which to display this map. It is the file name without
    # its path, or 'untitled.tmx' when the map has no file name.
    ##
    def displayName(self):
        displayName = QFileInfo(self.mFileName).fileName()
        if len(displayName)==0:
            displayName = self.tr("untitled.tmx")
        return displayName

    ##
    # Returns whether the map has unsaved changes.
    ##
    def isModified(self):
        return not self.mUndoStack.isClean()

    def lastSaved(self):
        return self.mLastSaved
        
    ##
    # Returns the map instance. Be aware that directly modifying the map will
    # not allow the GUI to update itself appropriately.
    ##
    def map(self):
        return self.mMap

    ##
    # Sets the current layer to the given index.
    ##
    def setCurrentLayerIndex(self, index):
        changed = self.mCurrentLayerIndex != index
        self.mCurrentLayerIndex = index
        ## This function always sends the following signal, even if the index
        # didn't actually change. This is because the selected index in the layer
        # table view might be out of date anyway, and would otherwise not be
        # properly updated.
        #
        # This problem happens due to the selection model not sending signals
        # about changes to its current index when it is due to insertion/removal
        # of other items. The selected item doesn't change in that case, but our
        # layer index does.
        ##
        self.currentLayerIndexChanged.emit(self.mCurrentLayerIndex)
        if (changed and self.mCurrentLayerIndex != -1):
            self.setCurrentObject(self.currentLayer())

    ##
    # Returns the index of the currently selected layer. Returns -1 if no
    # layer is currently selected.
    ##
    def currentLayerIndex(self):
        return self.mCurrentLayerIndex

    ##
    # Returns the currently selected layer, or 0 if no layer is currently
    # selected.
    ##
    def currentLayer(self):
        if (self.mCurrentLayerIndex == -1):
            return None
        return self.mMap.layerAt(self.mCurrentLayerIndex)

    ##
    # Resize this map to the given \a size, while at the same time shifting
    # the contents by \a offset.
    ##
    def resizeMap(self, size, offset):
        movedSelection = self.mSelectedArea.translated(offset)
        newArea = QRect(-offset, size)
        visibleArea = self.mRenderer.boundingRect(newArea)
        origin = self.mRenderer.tileToPixelCoords_(QPointF())
        newOrigin = self.mRenderer.tileToPixelCoords_(-offset)
        pixelOffset = origin - newOrigin
        # Resize the map and each layer
        self.mUndoStack.beginMacro(self.tr("Resize Map"))
        for i in range(self.mMap.layerCount()):
            layer = self.mMap.layerAt(i)
            x = layer.layerType()
            if x==Layer.TileLayerType:
                tileLayer = layer
                self.mUndoStack.push(ResizeTileLayer(self, tileLayer, size, offset))
            elif x==Layer.ObjectGroupType:
                objectGroup = layer
                # Remove objects that will fall outside of the map
                for o in objectGroup.objects():
                    if (not visibleIn(visibleArea, o, self.mRenderer)):
                        self.mUndoStack.push(RemoveMapObject(self, o))
                    else:
                        oldPos = o.position()
                        newPos = oldPos + pixelOffset
                        self.mUndoStack.push(MoveMapObject(self, newPos, oldPos))
            elif x==Layer.ImageLayerType:
                # Currently not adjusted when resizing the map
                break

        self.mUndoStack.push(ResizeMap(self, size))
        self.mUndoStack.push(ChangeSelectedArea(self, movedSelection))
        self.mUndoStack.endMacro()
        # TODO: Handle layers that don't match the map size correctly

    ##
    # Offsets the layers at \a layerIndexes by \a offset, within \a bounds,
    # and optionally wraps on the X or Y axis.
    ##
    def offsetMap(self, layerIndexes, offset, bounds, wrapX, wrapY):
        if (layerIndexes.empty()):
            return
        if (layerIndexes.size() == 1):
            self.mUndoStack.push(OffsetLayer(self, layerIndexes.first(), offset,
                                             bounds, wrapX, wrapY))
        else:
            self.mUndoStack.beginMacro(self.tr("Offset Map"))
            for layerIndex in layerIndexes:
                self.mUndoStack.push(OffsetLayer(self, layerIndex, offset,
                                                 bounds, wrapX, wrapY))

            self.mUndoStack.endMacro()

    ##
    # Flips the selected objects in the given \a direction.
    ##
    def flipSelectedObjects(self, direction):
        if (self.mSelectedObjects.isEmpty()):
            return
        self.mUndoStack.push(FlipMapObjects(self, self.mSelectedObjects, direction))

    ##
    # Rotates the selected objects.
    ##
    def rotateSelectedObjects(self, direction):
        if (self.mSelectedObjects.isEmpty()):
            return
        self.mUndoStack.beginMacro(self.tr("Rotate %n Object(s)", "", self.mSelectedObjects.size()))
        # TODO: Rotate them properly as a group
        for mapObject in self.mSelectedObjects:
            oldRotation = mapObject.rotation()
            newRotation = oldRotation
            if (direction == RotateDirection.RotateLeft):
                newRotation -= 90
                if (newRotation < -180):
                    newRotation += 360
            else:
                newRotation += 90
                if (newRotation > 180):
                    newRotation -= 360

            self.mUndoStack.push(RotateMapObject(self, mapObject, newRotation, oldRotation))

        self.mUndoStack.endMacro()

    ##
    # Adds a layer of the given type to the top of the layer stack. After adding
    # the new layer, emits editLayerNameRequested().
    ##
    def addLayer(self, layerType):
        layer = None
        name = QString()
        x = layerType
        if x==Layer.TileLayerType:
            name = self.tr("Tile Layer %d"%(self.mMap.tileLayerCount() + 1))
            layer = TileLayer(name, 0, 0, self.mMap.width(), self.mMap.height())
        elif x==Layer.ObjectGroupType:
            name = self.tr("Object Layer %d"%(self.mMap.objectGroupCount() + 1))
            layer = ObjectGroup(name, 0, 0, self.mMap.width(), self.mMap.height())
        elif x==Layer.ImageLayerType:
            name = self.tr("Image Layer %d"%(self.mMap.imageLayerCount() + 1))
            layer = ImageLayer(name, 0, 0, self.mMap.width(), self.mMap.height())

        index = self.mMap.layerCount()
        self.mUndoStack.push(AddLayer(self, index, layer))
        self.setCurrentLayerIndex(index)
        self.editLayerNameRequested.emit()

    ##
    # Duplicates the currently selected layer.
    ##
    def duplicateLayer(self):
        if (self.mCurrentLayerIndex == -1):
            return
        duplicate = self.mMap.layerAt(self.mCurrentLayerIndex).clone()
        duplicate.setName(self.tr("Copy of %s"%duplicate.name()))
        index = self.mCurrentLayerIndex + 1
        cmd = AddLayer(self, index, duplicate)
        cmd.setText(self.tr("Duplicate Layer"))
        self.mUndoStack.push(cmd)
        self.setCurrentLayerIndex(index)

    ##
    # Merges the currently selected layer with the layer below. This only works
    # when the layers can be merged.
    #
    # \see Layer.canMergeWith
    ##
    def mergeLayerDown(self):
        if (self.mCurrentLayerIndex < 1):
            return
        upperLayer = self.mMap.layerAt(self.mCurrentLayerIndex)
        lowerLayer = self.mMap.layerAt(self.mCurrentLayerIndex - 1)
        if (not lowerLayer.canMergeWith(upperLayer)):
            return
        merged = lowerLayer.mergedWith(upperLayer)
        self.mUndoStack.beginMacro(self.tr("Merge Layer Down"))
        self.mUndoStack.push(AddLayer(self, self.mCurrentLayerIndex - 1, merged))
        self.mUndoStack.push(RemoveLayer(self, self.mCurrentLayerIndex))
        self.mUndoStack.push(RemoveLayer(self, self.mCurrentLayerIndex))
        self.mUndoStack.endMacro()

    ##
    # Moves the given layer up. Does nothing when no valid layer index is
    # given.
    ##
    def moveLayerUp(self, index):
        if index<0 or index>=self.mMap.layerCount() - 1:
            return
        self.mUndoStack.push(MoveLayer(self, index, MoveLayer.Up))

    ##
    # Moves the given layer down. Does nothing when no valid layer index is
    # given.
    ##
    def moveLayerDown(self, index):
        if index<1 or index>=self.mMap.layerCount():
            return
        self.mUndoStack.push(MoveLayer(self, index, MoveLayer.Down))

    ##
    # Removes the given layer.
    ##
    def removeLayer(self, index):
        if index<0 or index>=self.mMap.layerCount():
            return
        self.mUndoStack.push(RemoveLayer(self, index))

    ##
    # Show or hide all other layers except the layer at the given index.
    # If any other layer is visible then all layers will be hidden, otherwise
    # the layers will be shown.
    ##
    def toggleOtherLayers(self, index):
        self.mLayerModel.toggleOtherLayers(index)

    ##
    # Adds a tileset to this map at the given \a index. Emits the appropriate
    # signal.
    ##
    def insertTileset(self, index, tileset):
        self.tilesetAboutToBeAdded.emit(index)
        self.mMap.insertTileset(index, tileset)
        tilesetManager = TilesetManager.instance()
        tilesetManager.addReference(tileset)
        self.tilesetAdded.emit(index, tileset)

    ##
    # Removes the tileset at the given \a index from this map. Emits the
    # appropriate signal.
    #
    # \warning Does not make sure that any references to tiles in the removed
    #          tileset are cleared.
    ##
    def removeTilesetAt(self, index):
        self.tilesetAboutToBeRemoved.emit(index)
        tileset = self.mMap.tilesets().at(index)
        if (tileset == self.mCurrentObject or isFromTileset(self.mCurrentObject, tileset)):
            self.setCurrentObject(None)
        self.mMap.removeTilesetAt(index)
        self.tilesetRemoved.emit(tileset)
        tilesetManager = TilesetManager.instance()
        tilesetManager.removeReference(tileset)

    def moveTileset(self, _from, to):
        if (_from == to):
            return
        tileset = self.mMap.tilesets().at(_from)
        self.mMap.removeTilesetAt(_from)
        self.mMap.insertTileset(to, tileset)
        self.tilesetMoved.emit(_from, to)

    def setTilesetFileName(self, tileset, fileName):
        tileset.setFileName(fileName)
        self.tilesetFileNameChanged.emit(tileset)

    def setTilesetName(self, tileset, name):
        tileset.setName(name)
        self.tilesetNameChanged.emit(tileset)

    def setTilesetTileOffset(self, tileset, tileOffset):
        tileset.setTileOffset(tileOffset)
        self.mMap.recomputeDrawMargins()
        self.tilesetTileOffsetChanged.emit(tileset)

    def duplicateObjects(self, objects):
        if (objects.isEmpty()):
            return
        self.mUndoStack.beginMacro(self.tr("Duplicate %n Object(s)", "", objects.size()))
        clones = QList()
        for mapObject in objects:
            clone = mapObject.clone()
            clones.append(clone)
            self.mUndoStack.push(AddMapObject(self,
                                              mapObject.objectGroup(),
                                              clone))

        self.mUndoStack.endMacro()
        self.setSelectedObjects(clones)

    def removeObjects(self, objects):
        if (objects.isEmpty()):
            return
        self.mUndoStack.beginMacro(self.tr("Remove %n Object(s)", "", objects.size()))
        for mapObject in objects:
            self.mUndoStack.push(RemoveMapObject(self, mapObject))
        self.mUndoStack.endMacro()

    def moveObjectsToGroup(self, objects, objectGroup):
        if (objects.isEmpty()):
            return
        self.mUndoStack.beginMacro(self.tr("Move %n Object(s) to Layer", "",
                                  objects.size()))
        for mapObject in objects:
            if (mapObject.objectGroup() == objectGroup):
                continue
            self.mUndoStack.push(MoveMapObjectToGroup(self,
                                                      mapObject,
                                                      objectGroup))

        self.mUndoStack.endMacro()

    def setProperty(self, object, name, value):
        hadProperty = object.hasProperty(name)
        object.setProperty(name, value)
        if (hadProperty):
            self.propertyChanged.emit(object, name)
        else:
            self.propertyAdded.emit(object, name)

    def setProperties(self, object, properties):
        object.setProperties(properties)
        self.propertiesChanged.emit(object)

    def removeProperty(self, object, name):
        object.removeProperty(name)
        self.propertyRemoved.emit(object, name)

    ##
    # Returns the layer model. Can be used to modify the layer stack of the
    # map, and to display the layer stack in a view.
    ##
    def layerModel(self):
        return self.mLayerModel

    def mapObjectModel(self):
        return self.mMapObjectModel

    def terrainModel(self):
        return self.mTerrainModel

    ##
    # Returns the map renderer.
    ##
    def renderer(self):
        return self.mRenderer

    ##
    # Creates the map renderer. Should be called after changing the map
    # orientation.
    ##
    def createRenderer(self):
        if (self.mRenderer):
            del self.mRenderer
        x = self.mMap.orientation()
        if x==Map.Orientation.Isometric:
            self.mRenderer = IsometricRenderer(self.mMap)
        elif x==Map.Orientation.Staggered:
            self.mRenderer = StaggeredRenderer(self.mMap)
        elif x==Map.Orientation.Hexagonal:
            self.mRenderer = HexagonalRenderer(self.mMap)
        else:
            self.mRenderer = OrthogonalRenderer(self.mMap)

    ##
    # Returns the undo stack of this map document. Should be used to push any
    # commands on that modify the map.
    ##
    def undoStack(self):
        return self.mUndoStack

    ##
    # Returns the selected area of tiles.
    ##
    def selectedArea(self):
        return QRegion(self.mSelectedArea)

    ##
    # Sets the selected area of tiles.
    ##
    def setSelectedArea(self, selection):
        if (self.mSelectedArea != selection):
            oldSelectedArea = self.mSelectedArea
            self.mSelectedArea = selection
            self.selectedAreaChanged.emit(self.mSelectedArea, oldSelectedArea)

    ##
    # Returns the list of selected objects.
    ##
    def selectedObjects(self):
        return self.mSelectedObjects

    ##
    # Sets the list of selected objects, emitting the selectedObjectsChanged
    # signal.
    ##
    def setSelectedObjects(self, selectedObjects):
        self.mSelectedObjects = selectedObjects
        self.selectedObjectsChanged.emit()
        if (selectedObjects.size() == 1):
            self.setCurrentObject(selectedObjects.first())

    ##
    # Returns the list of selected tiles.
    ##
    def selectedTiles(self):
        return self.mSelectedTiles

    def setSelectedTiles(self, selectedTiles):
        self.mSelectedTiles = selectedTiles
        self.selectedTilesChanged.emit()

    def currentObject(self):
        return self.mCurrentObject

    def setCurrentObject(self, object):
        if (object == self.mCurrentObject):
            return
        self.mCurrentObject = object
        self.currentObjectChanged.emit([object])

    def currentObjects(self):
        objects = QList()
        if (self.mCurrentObject):
            if (self.mCurrentObject.typeId() == Object.MapObjectType and not self.mSelectedObjects.isEmpty()):
                for mapObj in self.mSelectedObjects:
                    objects.append(mapObj)
            elif (self.mCurrentObject.typeId() == Object.TileType and not self.mSelectedTiles.isEmpty()):
                for tile in self.mSelectedTiles:
                    objects.append(tile)

            else:
                objects.append(self.mCurrentObject)

        return objects

    def unifyTilesets(self, *args):
        l = len(args)
        if l==1:
            ##
            # Makes sure the all tilesets which are used at the given \a map will be
            # present in the map document.
            #
            # To reach the aim, all similar tilesets will be replaced by the version
            # in the current map document and all missing tilesets will be added to
            # the current map document.
            #
            # \warning This method assumes that the tilesets in \a map are managed by
            #          the TilesetManager!
            ##
            map = args[0]
            undoCommands = QList()
            existingTilesets = self.mMap.tilesets()
            tilesetManager = TilesetManager.instance()
            # Add tilesets that are not yet part of this map
            for tileset in map.tilesets():
                if (existingTilesets.contains(tileset)):
                    continue
                replacement = tileset.findSimilarTileset(existingTilesets)
                if (not replacement):
                    undoCommands.append(AddTileset(self, tileset))
                    continue

                # Merge the tile properties
                sharedTileCount = min(tileset.tileCount(), replacement.tileCount())
                for i in range(sharedTileCount):
                    replacementTile = replacement.tileAt(i)
                    properties = replacementTile.properties()
                    properties.merge(tileset.tileAt(i).properties())
                    undoCommands.append(ChangeProperties(self,
                                                             self.tr("Tile"),
                                                             replacementTile,
                                                             properties))

                map.replaceTileset(tileset, replacement)
                tilesetManager.addReference(replacement)
                tilesetManager.removeReference(tileset)

            if (not undoCommands.isEmpty()):
                self.mUndoStack.beginMacro(self.tr("Tileset Changes"))
                for command in undoCommands:
                    self.mUndoStack.push(command)
                self.mUndoStack.endMacro()
        elif l==2:
            map, missingTilesets = args
            
            existingTilesets = self.mMap.tilesets()
            tilesetManager = TilesetManager.instance()

            for tileset in map.tilesets():
                # tileset already added
                if existingTilesets.contains(tileset):
                    continue

                replacement = tileset.findSimilarTileset(existingTilesets)

                # tileset not present and no replacement tileset found
                if not replacement:
                    if not missingTilesets.contains(tileset):
                        missingTilesets.append(tileset)
                    continue

                # replacement tileset found, change given map
                map.replaceTileset(tileset, replacement)

                tilesetManager.addReference(replacement)
                tilesetManager.removeReference(tileset)

    ##
    # Emits the map changed signal. This signal should be emitted after changing
    # the map size or its tile size.
    ##
    def emitMapChanged(self):
        self.mapChanged.emit()

    ##
    # Emits the region changed signal for the specified region. The region
    # should be in tile coordinates. This method is used by the TilePainter.
    ##
    def emitRegionChanged(self, region, layer):
        self.regionChanged.emit(region, layer)

    ##
    # Emits the region edited signal for the specified region and tile layer.
    # The region should be in tile coordinates. This should be called from
    # all map document changing classes which are triggered by user input.
    ##
    def emitRegionEdited(self, region, layer):
        self.regionEdited.emit(region, layer)

    def emitTileLayerDrawMarginsChanged(self, layer):
        self.tileLayerDrawMarginsChanged.emit(layer)

    ##
    # Emits the tileset changed signal. This signal is currently used when adding
    # or removing tiles from a tileset.
    #
    # @todo Emit more specific signals.
    ##
    def emitTilesetChanged(self, tileset):
        self.tilesetChanged.emit(tileset)

    ##
    # Emits the signal notifying about the terrain probability of a tile changing.
    ##
    def emitTileProbabilityChanged(self, tile):
        self.tileProbabilityChanged.emit(tile)

    ##
    # Emits the signal notifying tileset models about changes to tile terrain
    # information. All the \a tiles need to be from the same tileset.
    ##
    def emitTileTerrainChanged(self, tiles):
        if (not tiles.isEmpty()):
            self.tileTerrainChanged.emit(tiles)

    ##
    # Emits the signal notifying the TileCollisionEditor about the object group
    # of a tile changing.
    ##
    def emitTileObjectGroupChanged(self, tile):
        self.tileObjectGroupChanged.emit(tile)

    ##
    # Emits the signal notifying about the animation of a tile changing.
    ##
    def emitTileAnimationChanged(self, tile):
        self.tileAnimationChanged.emit(tile)

    ##
    # Emits the objectGroupChanged signal, should be called when changing the
    # color or drawing order of an object group.
    ##
    def emitObjectGroupChanged(self, objectGroup):
        self.objectGroupChanged.emit(objectGroup)

    ##
    # Emits the imageLayerChanged signal, should be called when changing the
    # image or the transparent color of an image layer.
    ##
    def emitImageLayerChanged(self, imageLayer):
        self.imageLayerChanged.emit(imageLayer)

    ##
    # Emits the editLayerNameRequested signal, to get renamed.
    ##
    def emitEditLayerNameRequested(self):
        self.editLayerNameRequested.emit()

    ##
    # Emits the editCurrentObject signal, which makes the Properties window become
    # visible and take focus.
    ##
    def emitEditCurrentObject(self):
        self.editCurrentObject.emit()

    ##
    # Before forwarding the signal, the objects are removed from the list of
    # selected objects, triggering a selectedObjectsChanged signal when
    # appropriate.
    ##
    def onObjectsRemoved(self, objects):
        self.deselectObjects(objects)
        self.objectsRemoved.emit(objects)

    def onMapObjectModelRowsInserted(self, parent, first, last):
        objectGroup = self.mMapObjectModel.toObjectGroup(parent)
        if (not objectGroup): # we're not dealing with insertion of objects
            return
        self.objectsInserted.emit(objectGroup, first, last)
        self.onMapObjectModelRowsInsertedOrRemoved(parent, first, last)

    def onMapObjectModelRowsInsertedOrRemoved(self, parent, first, last):
        objectGroup = self.mMapObjectModel.toObjectGroup(parent)
        if (not objectGroup):
            return
        # Inserting or removing objects changes the index of any that come after
        lastIndex = objectGroup.objectCount() - 1
        if (last < lastIndex):
            self.objectsIndexChanged.emit(objectGroup, last + 1, lastIndex)

    def onObjectsMoved(self, parent, start, end, destination, row):
        if (parent != destination):
            return
        objectGroup = self.mMapObjectModel.toObjectGroup(parent)
        # Determine the full range over which object indexes changed
        first = min(start, row)
        last = max(end, row - 1)
        self.objectsIndexChanged.emit(objectGroup, first, last)

    def onLayerAdded(self, index):
        self.layerAdded.emit(index)
        # Select the first layer that gets added to the map
        if (self.mMap.layerCount() == 1):
            self.setCurrentLayerIndex(0)

    def onLayerAboutToBeRemoved(self, index):
        layer = self.mMap.layerAt(index)
        if (layer == self.mCurrentObject):
            self.setCurrentObject(None)
        # Deselect any objects on this layer when necessary
        og = layer
        if type(og) == ObjectGroup:
            self.deselectObjects(og.objects())
        self.layerAboutToBeRemoved.emit(index)

    def onLayerRemoved(self, index):
        # Bring the current layer index to safety
        currentLayerRemoved = self.mCurrentLayerIndex == self.mMap.layerCount()
        if (currentLayerRemoved):
            self.mCurrentLayerIndex = self.mCurrentLayerIndex - 1
        self.layerRemoved.emit(index)
        # Emitted after the layerRemoved signal so that the MapScene has a chance
        # of synchronizing before adapting to the newly selected index
        if (currentLayerRemoved):
            self.currentLayerIndexChanged.emit(self.mCurrentLayerIndex)

    def onTerrainRemoved(self, terrain):
        if (terrain == self.mCurrentObject):
            self.setCurrentObject(None)

    def setFileName(self, fileName):
        if (self.mFileName == fileName):
            return
        oldFileName = self.mFileName
        self.mFileName = fileName
        self.fileNameChanged.emit(fileName, oldFileName)

    def deselectObjects(self, objects):
        # Unset the current object when it was part of this list of objects
        if (self.mCurrentObject and self.mCurrentObject.typeId() == Object.MapObjectType):
            if (objects.contains(self.mCurrentObject)):
                self.setCurrentObject(None)
        removedCount = 0
        for object in objects:
            removedCount += self.mSelectedObjects.removeAll(object)
        if (removedCount > 0):
            self.selectedObjectsChanged.emit()

    def disconnect(self):
        try:
            super().disconnect()
        except:
            pass
