##
# propertybrowser.py
# Copyright 2013, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from map import Map
from utils import Utils
from tilesetchanges import RenameTileset, ChangeTilesetTileOffset
from rotatemapobject import RotateMapObject
from renameterrain import RenameTerrain
from renamelayer import RenameLayer
from resizemapobject import ResizeMapObject
import preferences
from changelayer import SetLayerOffset
from movemapobject import MoveMapObject
from object import Object
from flipmapobjects import FlipMapObjects
from changetileprobability import ChangeTileProbability
from changeproperties import SetProperty
from changemapproperty import ChangeMapProperty
from changeobjectgroupproperties import ChangeObjectGroupProperties
from changemapobject import ChangeMapObject, SetMapObjectVisible
from changeimagelayerproperties import ChangeImageLayerProperties
from changeimagelayerposition import ChangeImageLayerPosition
from changelayer import SetLayerVisible, SetLayerOpacity
from libtiled.tiled import FlipDirection
from layer import Layer
from properties import Properties
from pyqtcore import QStringList, QHash, QList, dynamic_cast
from qttreepropertybrowser import QtTreePropertyBrowser
from variantpropertymanager import VariantPropertyManager
from qtpropertymanager import QtGroupPropertyManager
from varianteditorfactory import VariantEditorFactory
from qtvariantproperty import QtVariantPropertyManager
from PyQt5.QtCore import (
    Qt,
    QEvent, 
    QPoint, 
    QSizeF, 
    QPointF, 
    QVariant,
    QCoreApplication
)
from PyQt5.QtGui import (
    QColor
)

def objectTypeNames():
    names = QStringList()
    for _type in preferences.Preferences.instance().objectTypes():
        names.append(_type.name)
    return names

class PropertyId():
    NameProperty = 0
    TypeProperty = 1
    XProperty = 2
    YProperty = 3
    WidthProperty = 4
    HeightProperty = 5
    RotationProperty = 6
    VisibleProperty = 7
    OpacityProperty = 8
    OffsetXProperty = 9
    OffsetYProperty = 10
    ColorProperty = 11
    TileWidthProperty = 12
    TileHeightProperty = 13
    OrientationProperty = 14
    HexSideLengthProperty = 15
    StaggerAxisProperty = 16
    StaggerIndexProperty = 17
    RenderOrderProperty = 18
    LayerFormatProperty = 19
    ImageSourceProperty = 20
    FlippingProperty = 21
    DrawOrderProperty = 22
    TileOffsetProperty = 23
    SourceImageProperty = 24
    MarginProperty = 25
    SpacingProperty = 26
    TileProbabilityProperty = 27
    IdProperty = 28
    CustomProperty = 29

class PropertyBrowser(QtTreePropertyBrowser):
    def __init__(self, parent = None):
        super().__init__(parent)
        
        self.mUpdating = False
        self.mObject = None
        self.mMapDocument = None
        self.mVariantManager = VariantPropertyManager(self)
        self.mGroupManager = QtGroupPropertyManager(self)
        self.mCustomPropertiesGroup = None
        self.mCombinedProperties = Properties()
        self.mDrawOrderNames = QStringList()
        self.mPropertyToId = QHash()
        self.mOrientationNames = QStringList()
        self.mStaggerAxisNames = QStringList()
        self.mFlippingFlagNames = QStringList()
        self.mLayerFormatNames = QStringList()
        self.mRenderOrderNames = QStringList()
        self.mStaggerIndexNames = QStringList()
        self.mIdToProperty = QHash()
        self.mNameToProperty = QHash()

        self.setFactoryForManager(self.mVariantManager, VariantEditorFactory(self))
        self.setResizeMode(QtTreePropertyBrowser.ResizeToContents)
        self.setRootIsDecorated(False)
        self.setPropertiesWithoutValueMarked(True)
        self.mStaggerAxisNames.append(self.tr("X"))
        self.mStaggerAxisNames.append(self.tr("Y"))
        self.mStaggerIndexNames.append(self.tr("Odd"))
        self.mStaggerIndexNames.append(self.tr("Even"))
        self.mOrientationNames.append(QCoreApplication.translate("Tiled.Internal.NewMapDialog", "Orthogonal"))
        self.mOrientationNames.append(QCoreApplication.translate("Tiled.Internal.NewMapDialog", "Isometric"))
        self.mOrientationNames.append(QCoreApplication.translate("Tiled.Internal.NewMapDialog", "Isometric (Staggered)"))
        self.mOrientationNames.append(QCoreApplication.translate("Tiled.Internal.NewMapDialog", "Hexagonal (Staggered)"))
        self.mLayerFormatNames.append(QCoreApplication.translate("PreferencesDialog", "XML"))
        self.mLayerFormatNames.append(QCoreApplication.translate("PreferencesDialog", "Base64 (uncompressed)"))
        self.mLayerFormatNames.append(QCoreApplication.translate("PreferencesDialog", "Base64 (gzip compressed)"))
        self.mLayerFormatNames.append(QCoreApplication.translate("PreferencesDialog", "Base64 (zlib compressed)"))
        self.mLayerFormatNames.append(QCoreApplication.translate("PreferencesDialog", "CSV"))
        self.mRenderOrderNames.append(QCoreApplication.translate("PreferencesDialog", "Right Down"))
        self.mRenderOrderNames.append(QCoreApplication.translate("PreferencesDialog", "Right Up"))
        self.mRenderOrderNames.append(QCoreApplication.translate("PreferencesDialog", "Left Down"))
        self.mRenderOrderNames.append(QCoreApplication.translate("PreferencesDialog", "Left Up"))
        self.mFlippingFlagNames.append(self.tr("Horizontal"))
        self.mFlippingFlagNames.append(self.tr("Vertical"))
        self.mDrawOrderNames.append(self.tr("Top Down"))
        self.mDrawOrderNames.append(self.tr("Manual"))
        self.mVariantManager.valueChangedSignal.connect(self.valueChanged)

    def retranslateUi(self):
        self.removeProperties()
        self.addProperties()

    def addProperties(self):
        if (not self.mObject):
            return
        self.mUpdating = True
        # Add the built-in properties for each object type
        x = self.mObject.typeId()
        if x==Object.MapType:
            self.addMapProperties()
        elif x==Object.MapObjectType:
            self.addMapObjectProperties()
        elif x==Object.LayerType:
            x = self.mObject.layerType()
            if x==Layer.TileLayerType:
                self.addTileLayerProperties()
            elif x==Layer.ObjectGroupType:
                self.addObjectGroupProperties()
            elif x==Layer.ImageLayerType:
                self.addImageLayerProperties()
        elif x==Object.TilesetType:
            self.addTilesetProperties()
        elif x==Object.TileType:
            self.addTileProperties()
        elif x==Object.TerrainType:
            self.addTerrainProperties()

        # Add a node for the custom properties
        self.mCustomPropertiesGroup = self.mGroupManager.addProperty(self.tr("Custom Properties"))
        self.addProperty(self.mCustomPropertiesGroup)
        self.mUpdating = False
        self.updateProperties()
        self.updateCustomProperties()
        
    def removeProperties(self):
        # Destroy all previous properties
        self.mVariantManager.clear()
        self.mGroupManager.clear()
        self.mPropertyToId.clear()
        self.mIdToProperty.clear()
        self.mNameToProperty.clear()
        self.mCustomPropertiesGroup = None
        
    ##
    # Sets the \a object for which to display the properties.
    ##
    def setObject(self, object):
        if (self.mObject == object):
            return
        
        self.removeProperties()
        
        self.mObject = object
        
        self.addProperties()
        
    ##
    # Returns the object for which the properties are displayed.
    ##
    def object(self):
        return self.mObject

    ##
    # Sets the \a mapDocument, used for keeping track of changes and for
    # undo/redo support.
    ##
    def setMapDocument(self, mapDocument):
        if (self.mMapDocument == mapDocument):
            return
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
            self.mMapDocument.terrainModel().disconnect()

        self.mMapDocument = mapDocument
        if (mapDocument):
            mapDocument.mapChanged.connect(self.mapChanged)
            mapDocument.objectsChanged.connect(self.objectsChanged)
            mapDocument.layerChanged.connect(self.layerChanged)
            mapDocument.objectGroupChanged.connect(self.objectGroupChanged)
            mapDocument.imageLayerChanged.connect(self.imageLayerChanged)
            mapDocument.tilesetNameChanged.connect(self.tilesetChanged)
            mapDocument.tilesetTileOffsetChanged.connect(self.tilesetChanged)
            mapDocument.tileProbabilityChanged.connect(self.tileChanged)
            terrainModel = mapDocument.terrainModel()
            terrainModel.terrainChanged.connect(self.terrainChanged)
            # For custom properties:
            mapDocument.propertyAdded.connect(self.propertyAdded)
            mapDocument.propertyRemoved.connect(self.propertyRemoved)
            mapDocument.propertyChanged.connect(self.propertyChanged)
            mapDocument.propertiesChanged.connect(self.propertiesChanged)
            mapDocument.selectedObjectsChanged.connect(self.selectedObjectsChanged)
            mapDocument.selectedTilesChanged.connect(self.selectedTilesChanged)

    ##
    # Returns whether the given \a item displays a custom property.
    ##
    def isCustomPropertyItem(self, item):
        return item and self.mPropertyToId[item.property()] == PropertyId.CustomProperty

    ##
    # Makes the custom property with the \a name the currently edited one,
    # if it exists.
    ##
    def editCustomProperty(self, name):
        property = self.mNameToProperty.value(name)
        if (not property):
            return
        propertyItems = self.items(property)
        if (not propertyItems.isEmpty()):
            self.editItem(propertyItems.first())

    def event(self, event):
        if event.type() == QEvent.LanguageChange:
            self.retranslateUi()

        return super().event(event)

    def mapChanged(self):
        if (self.mObject == self.mMapDocument.map()):
            self.updateProperties()

    def objectsChanged(self, objects):
        if (self.mObject and self.mObject.typeId() == Object.MapObjectType):
            if (objects.contains(self.mObject)):
                self.updateProperties()

    def layerChanged(self, index):
        if (self.mObject == self.mMapDocument.map().layerAt(index)):
            self.updateProperties()

    def objectGroupChanged(self, objectGroup):
        if (self.mObject == objectGroup):
            self.updateProperties()

    def imageLayerChanged(self, imageLayer):
        if (self.mObject == imageLayer):
            self.updateProperties()

    def tilesetChanged(self, tileset):
        if (self.mObject == tileset):
            self.updateProperties()

    def tileChanged(self, tile):
        if (self.mObject == tile):
            self.updateProperties()

    def terrainChanged(self, tileset, index):
        if (self.mObject == tileset.terrain(index)):
            self.updateProperties()

    def propertyAdded(self, object, name):
        if (not self.mMapDocument.currentObjects().contains(object)):
            return
        if (self.mNameToProperty.contains(name)):
            if (self.mObject == object):
                self.mUpdating = True
                self.mNameToProperty[name].setValue(self.mObject.property(name))
                self.mUpdating = False

        else:
            # Determine the property preceding the new property, if any
            index = self.mObject.properties().keys().index(name)
            properties = self.mCustomPropertiesGroup.subProperties()
            if index > 0:
                precedingProperty = properties.at(index - 1)
            else:
                precedingProperty = None

            self.mUpdating = True
            property = self.mVariantManager.addProperty(QVariant.String, name)
            property.setValue(self.mObject.property(name))
            self.mCustomPropertiesGroup.insertSubProperty(property, precedingProperty)
            self.mPropertyToId.insert(property, PropertyId.CustomProperty)
            self.mNameToProperty.insert(name, property)
            self.mUpdating = False

        self.updatePropertyColor(name)

    def propertyRemoved(self, object, name):
        if (not self.mMapDocument.currentObjects().contains(object)):
            return
        if (self.mObject == object):
            deleteProperty = True
            for obj in self.mMapDocument.currentObjects():
                if (self.mObject == obj):
                    continue
                if (obj.properties().contains(name)):
                    # An other selected object still has this property, so just clear the value.
                    self.mUpdating = True
                    self.mNameToProperty[name].setValue(self.tr("<Invalid>"))
                    self.mUpdating = False
                    deleteProperty = False
                    break

            # No other selected objects have this property so delete it.
            if (deleteProperty):
                self.mNameToProperty.take(name).close()
        self.updatePropertyColor(name)

    def propertyChanged(self, object, name):
        if (self.mObject == object):
            self.mUpdating = True
            self.mNameToProperty[name].setValue(object.property(name))
            self.mUpdating = False

        if (self.mMapDocument.currentObjects().contains(object)):
            self.updatePropertyColor(name)

    def propertiesChanged(self, object):
        if (self.mMapDocument.currentObjects().contains(object)):
            self.updateCustomProperties()

    def selectedObjectsChanged(self):
        self.updateCustomProperties()

    def selectedTilesChanged(self):
        self.updateCustomProperties()

    def valueChanged(self, property, val):
        if (self.mUpdating):
            return
        if (not self.mObject or not self.mMapDocument):
            return
        if (not self.mPropertyToId.contains(property)):
            return
        id = self.mPropertyToId.value(property)
        if (id == PropertyId.CustomProperty):
            undoStack = self.mMapDocument.undoStack()
            undoStack.push(SetProperty(self.mMapDocument,
                                            self.mMapDocument.currentObjects(),
                                            property.propertyName(),
                                            val))
            return

        x = self.mObject.typeId()
        if x==Object.MapType:
            self.applyMapValue(id, val)
        elif x==Object.MapObjectType:
            self.applyMapObjectValue(id, val)
        elif x==Object.LayerType:
            self.applyLayerValue(id, val)
        elif x==Object.TilesetType:
            self.applyTilesetValue(id, val)
        elif x==Object.TileType:
            self.applyTileValue(id, val)
        elif x==Object.TerrainType:
            self.applyTerrainValue(id, val)

    def addMapProperties(self):
        
        groupProperty = self.mGroupManager.addProperty(self.tr("Map"))
        
        orientationProperty = self.createProperty(PropertyId.OrientationProperty,
                               QtVariantPropertyManager.enumTypeId(),
                               self.tr("Orientation"),
                               groupProperty)
        orientationProperty.setAttribute("enumNames", self.mOrientationNames)
        self.createProperty(PropertyId.WidthProperty, QVariant.Int, self.tr("Width"), groupProperty).setEnabled(False)
        self.createProperty(PropertyId.HeightProperty, QVariant.Int, self.tr("Height"), groupProperty).setEnabled(False)
        self.createProperty(PropertyId.TileWidthProperty, QVariant.Int, self.tr("Tile Width"), groupProperty)
        self.createProperty(PropertyId.TileHeightProperty, QVariant.Int, self.tr("Tile Height"), groupProperty)
        self.createProperty(PropertyId.HexSideLengthProperty, QVariant.Int, self.tr("Tile Side Length (Hex)"), groupProperty)
        staggerAxisProperty = self.createProperty(PropertyId.StaggerAxisProperty,
                               QtVariantPropertyManager.enumTypeId(),
                               self.tr("Stagger Axis"),
                               groupProperty)
        staggerAxisProperty.setAttribute("enumNames", self.mStaggerAxisNames)
        staggerIndexProperty = self.createProperty(PropertyId.StaggerIndexProperty,
                               QtVariantPropertyManager.enumTypeId(),
                               self.tr("Stagger Index"),
                               groupProperty)
        staggerIndexProperty.setAttribute("enumNames", self.mStaggerIndexNames)
        layerFormatProperty = self.createProperty(PropertyId.LayerFormatProperty,
                               QtVariantPropertyManager.enumTypeId(),
                               self.tr("Tile Layer Format"),
                               groupProperty)
        layerFormatProperty.setAttribute("enumNames", self.mLayerFormatNames)
        renderOrderProperty = self.createProperty(PropertyId.RenderOrderProperty,
                               QtVariantPropertyManager.enumTypeId(),
                               self.tr("Tile Render Order"),
                               groupProperty)
        renderOrderProperty.setAttribute("enumNames", self.mRenderOrderNames)
        self.createProperty(PropertyId.ColorProperty, QVariant.Color, self.tr("Background Color"), groupProperty)
        self.addProperty(groupProperty)

    def addMapObjectProperties(self):
        groupProperty = self.mGroupManager.addProperty(self.tr("Object"))
        self.createProperty(PropertyId.IdProperty, QVariant.Int, self.tr("ID"), groupProperty).setEnabled(False)
        self.createProperty(PropertyId.NameProperty, QVariant.String, self.tr("Name"), groupProperty)
        typeProperty = self.createProperty(PropertyId.TypeProperty, QVariant.String, self.tr("Type"), groupProperty)
        typeProperty.setAttribute("suggestions", objectTypeNames())
        self.createProperty(PropertyId.VisibleProperty, QVariant.Bool, self.tr("Visible"), groupProperty)
        self.createProperty(PropertyId.XProperty, QVariant.Double, self.tr("X"), groupProperty)
        self.createProperty(PropertyId.YProperty, QVariant.Double, self.tr("Y"), groupProperty)
        self.createProperty(PropertyId.WidthProperty, QVariant.Double, self.tr("Width"), groupProperty)
        self.createProperty(PropertyId.HeightProperty, QVariant.Double, self.tr("Height"), groupProperty)
        self.createProperty(PropertyId.RotationProperty, QVariant.Double, self.tr("Rotation"), groupProperty)
        if not self.mObject.cell().isEmpty():
            flippingProperty = self.createProperty(PropertyId.FlippingProperty, VariantPropertyManager.flagTypeId(), self.tr("Flipping"), groupProperty)
            flippingProperty.setAttribute("flagNames", self.mFlippingFlagNames)

        self.addProperty(groupProperty)

    def addLayerProperties(self, parent):
        self.createProperty(PropertyId.NameProperty, QVariant.String, self.tr("Name"), parent)
        self.createProperty(PropertyId.VisibleProperty, QVariant.Bool, self.tr("Visible"), parent)
        opacityProperty = self.createProperty(PropertyId.OpacityProperty, QVariant.Double, self.tr("Opacity"), parent)
        opacityProperty.setAttribute("minimum", 0.0)
        opacityProperty.setAttribute("maximum", 1.0)
        opacityProperty.setAttribute("singleStep", 0.1)

    def addTileLayerProperties(self):
        groupProperty = self.mGroupManager.addProperty(self.tr("Tile Layer"))
        self.addLayerProperties(groupProperty)
        self.createProperty(PropertyId.OffsetXProperty, QVariant.Double, self.tr("Horizontal Offset"), groupProperty)
        self.createProperty(PropertyId.OffsetYProperty, QVariant.Double, self.tr("Vertical Offset"), groupProperty)
        self.addProperty(groupProperty)

    def addObjectGroupProperties(self):
        groupProperty = self.mGroupManager.addProperty(self.tr("Object Layer"))
        self.addLayerProperties(groupProperty)
        
        self.createProperty(PropertyId.OffsetXProperty, QVariant.Double, self.tr("Horizontal Offset"), groupProperty)
        self.createProperty(PropertyId.OffsetYProperty, QVariant.Double, self.tr("Vertical Offset"), groupProperty)

        self.createProperty(PropertyId.ColorProperty, QVariant.Color, self.tr("Color"), groupProperty)
        drawOrderProperty = self.createProperty(PropertyId.DrawOrderProperty,
                               QtVariantPropertyManager.enumTypeId(),
                               self.tr("Drawing Order"),
                               groupProperty)
        drawOrderProperty.setAttribute("enumNames", self.mDrawOrderNames)
        self.addProperty(groupProperty)

    def addImageLayerProperties(self):
        groupProperty = self.mGroupManager.addProperty(self.tr("Image Layer"))
        self.addLayerProperties(groupProperty)
        imageSourceProperty = self.createProperty(PropertyId.ImageSourceProperty,
                                                                VariantPropertyManager.filePathTypeId(),
                                                                self.tr("Image"), groupProperty)
        imageSourceProperty.setAttribute("filter",
                                          Utils.readableImageFormatsFilter())
        self.createProperty(PropertyId.ColorProperty, QVariant.Color, self.tr("Transparent Color"), groupProperty)
        self.createProperty(PropertyId.XProperty, QVariant.Int, self.tr("X"), groupProperty)
        self.createProperty(PropertyId.YProperty, QVariant.Int, self.tr("Y"), groupProperty)
        self.addProperty(groupProperty)

    def addTilesetProperties(self):
        groupProperty = self.mGroupManager.addProperty(self.tr("Tileset"))
        self.createProperty(PropertyId.NameProperty, QVariant.String, self.tr("Name"), groupProperty)
        self.createProperty(PropertyId.TileOffsetProperty, QVariant.Point, self.tr("Drawing Offset"), groupProperty)
        
        # Next properties we should add only for non 'Collection of Images' tilesets
        currentTileset = dynamic_cast(self.mObject)
        if currentTileset.imageSource() != '':
            srcImgProperty = self.createProperty(PropertyId.SourceImageProperty, QVariant.String, self.tr("Source Image"), groupProperty)
            tileWidthProperty = self.createProperty(PropertyId.TileWidthProperty, QVariant.Int, self.tr("Tile Width"), groupProperty)
            tileHeightProperty = self.createProperty(PropertyId.TileHeightProperty, QVariant.Int, self.tr("Tile Height"), groupProperty)
            marginProperty = self.createProperty(PropertyId.MarginProperty, QVariant.Int, self.tr("Margin"), groupProperty)
            spacingProperty = self.createProperty(PropertyId.SpacingProperty, QVariant.Int, self.tr("Spacing"), groupProperty)
            # Make these properties read-only
            srcImgProperty.setEnabled(False)
            tileWidthProperty.setEnabled(False)
            tileHeightProperty.setEnabled(False)
            marginProperty.setEnabled(False)
            spacingProperty.setEnabled(False)
    
        self.addProperty(groupProperty)

    def addTileProperties(self):
        groupProperty = self.mGroupManager.addProperty(self.tr("Tile"))
        self.createProperty(PropertyId.IdProperty, QVariant.Int, self.tr("ID"), groupProperty).setEnabled(False)
        probabilityProperty = self.createProperty(PropertyId.TileProbabilityProperty,
                                                         QVariant.Double,
                                                         self.tr("Probability"),
                                                         groupProperty)
        probabilityProperty.setAttribute("decimals", 3)
        probabilityProperty.setToolTip(self.tr("Relative chance this tile will be picked"))
        self.addProperty(groupProperty)

    def addTerrainProperties(self):
        groupProperty = self.mGroupManager.addProperty(self.tr("Terrain"))
        self.createProperty(PropertyId.NameProperty, QVariant.String, self.tr("Name"), groupProperty)
        self.addProperty(groupProperty)

    def applyMapValue(self, id, val):
        command = None
        x = id
        if x==PropertyId.TileWidthProperty:
            command = ChangeMapProperty(self.mMapDocument, ChangeMapProperty.TileWidth, val)
        elif x==PropertyId.TileHeightProperty:
            command = ChangeMapProperty(self.mMapDocument, ChangeMapProperty.TileHeight, val)
        elif x==PropertyId.OrientationProperty:
            orientation = Map.Orientation((val + 1)%5)
            command = ChangeMapProperty(self.mMapDocument, orientation)
        elif x==PropertyId.HexSideLengthProperty:
            command = ChangeMapProperty(self.mMapDocument, ChangeMapProperty.HexSideLength, val)
        elif x==PropertyId.StaggerAxisProperty:
            staggerAxis = Map.StaggerAxis(val)
            command = ChangeMapProperty(self.mMapDocument, staggerAxis)
        elif x==PropertyId.StaggerIndexProperty:
            staggerIndex = Map.StaggerIndex(val)
            command = ChangeMapProperty(self.mMapDocument, staggerIndex)
        elif x==PropertyId.LayerFormatProperty:
            format = Map.LayerDataFormat(val)
            command = ChangeMapProperty(self.mMapDocument, format)
        elif x==PropertyId.RenderOrderProperty:
            renderOrder = Map.RenderOrder(val)
            command = ChangeMapProperty(self.mMapDocument, renderOrder)
        elif x==PropertyId.ColorProperty:
            command = ChangeMapProperty(self.mMapDocument, val)
        if (command):
            self.mMapDocument.undoStack().push(command)

    def applyMapObjectValue(self, id, val):
        mapObject = self.mObject
        command = self.applyMapObjectValueTo(id, val, mapObject)
        self.mMapDocument.undoStack().beginMacro(command.text())
        self.mMapDocument.undoStack().push(command)
        #Used to share non-custom properties.
        selectedObjects = self.mMapDocument.selectedObjects()
        if (selectedObjects.size() > 1):
            for obj in selectedObjects:
                if (obj != mapObject):
                    cmd = self.applyMapObjectValueTo(id, val, obj)
                    if cmd:
                        self.mMapDocument.undoStack().push(cmd)

        self.mMapDocument.undoStack().endMacro()

    def applyMapObjectValueTo(self, id, val, mapObject):
        command = None
        x = id
        if x==PropertyId.NameProperty or x==PropertyId.TypeProperty:
            command = ChangeMapObject(self.mMapDocument, mapObject,
                                          self.mIdToProperty[PropertyId.NameProperty],
                                          self.mIdToProperty[PropertyId.TypeProperty])
        elif x==PropertyId.VisibleProperty:
            command = SetMapObjectVisible(self.mMapDocument, mapObject, val)
        elif x==PropertyId.XProperty:
            oldPos = mapObject.position()
            newPos = QPointF(val, oldPos.y())
            command = MoveMapObject(self.mMapDocument, mapObject, newPos, oldPos)
        elif x==PropertyId.YProperty:
            oldPos = mapObject.position()
            newPos = QPointF(oldPos.x(), val)
            command = MoveMapObject(self.mMapDocument, mapObject, newPos, oldPos)
        elif x==PropertyId.WidthProperty:
            oldSize = mapObject.size()
            newSize = QSizeF(val, oldSize.height())
            command = ResizeMapObject(self.mMapDocument, mapObject, newSize, oldSize)
        elif x==PropertyId.HeightProperty:
            oldSize = mapObject.size()
            newSize = QSizeF(oldSize.width(), val)
            command = ResizeMapObject(self.mMapDocument, mapObject, newSize, oldSize)
        elif x==PropertyId.RotationProperty:
            newRotation = val
            oldRotation = mapObject.rotation()
            command = RotateMapObject(self.mMapDocument, mapObject, newRotation, oldRotation)
        elif x==PropertyId.FlippingProperty:
            flippingFlags = val
            flippedHorizontally = flippingFlags & 1
            flippedVertically = flippingFlags & 2
            # You can only change one checkbox at a time
            if (mapObject.cell().flippedHorizontally != flippedHorizontally):
                command = FlipMapObjects(self.mMapDocument,
                                             QList([mapObject]),
                                             FlipDirection.FlipHorizontally)
            elif (mapObject.cell().flippedVertically != flippedVertically):
                command = FlipMapObjects(self.mMapDocument,
                                             QList([mapObject]),
                                             FlipDirection.FlipVertically)
        else:
            pass

        return command

    def applyLayerValue(self, id, val):
        layer = self.mObject
        layerIndex = self.mMapDocument.map().layers().indexOf(layer)
        command = None
        x = id
        if x==PropertyId.NameProperty:
            command = RenameLayer(self.mMapDocument, layerIndex, val)
        elif x==PropertyId.VisibleProperty:
            command = SetLayerVisible(self.mMapDocument, layerIndex, val)
        elif x==PropertyId.OpacityProperty:
            command = SetLayerOpacity(self.mMapDocument, layerIndex, val)
        elif x==PropertyId.OffsetXProperty or x==PropertyId.OffsetYProperty:
            offset = QPointF(layer.offset())

            if id == PropertyId.OffsetXProperty:
                offset.setX(val)
            else:
                offset.setY(val)

            command = SetLayerOffset(self.mMapDocument, layerIndex, offset)
        else:
            x = layer.layerType()
            if x==Layer.TileLayerType:
                self.applyTileLayerValue(id, val)
            elif x==Layer.ObjectGroupType:
                self.applyObjectGroupValue(id, val)
            elif x==Layer.ImageLayerType:
                self.applyImageLayerValue(id, val)
        if (command):
            self.mMapDocument.undoStack().push(command)

    def applyTileLayerValue(self, id, val):
        pass

    def applyObjectGroupValue(self, id, val):
        objectGroup = self.mObject
        command = None
        x = id
        if x==PropertyId.ColorProperty:
            color = val.value()
            if (color == Qt.gray):
                color = QColor()
            command = ChangeObjectGroupProperties(self.mMapDocument,
                                                      objectGroup,
                                                      color,
                                                      objectGroup.drawOrder())
        elif x==PropertyId.DrawOrderProperty:
            drawOrder = val
            command = ChangeObjectGroupProperties(self.mMapDocument,
                                                      objectGroup,
                                                      objectGroup.color(),
                                                      drawOrder)

        else:
            pass

        if (command):
            self.mMapDocument.undoStack().push(command)

    def applyImageLayerValue(self, id, val):
        imageLayer = self.mObject
        undoStack = self.mMapDocument.undoStack()
        x = id
        if x==PropertyId.ImageSourceProperty:
            imageSource = val
            color = imageLayer.transparentColor()
            undoStack.push(ChangeImageLayerProperties(self.mMapDocument,
                                                           imageLayer,
                                                           color,
                                                           imageSource))
        elif x==PropertyId.ColorProperty:
            color = val
            if (color == Qt.gray):
                color = QColor()
            imageSource = imageLayer.imageSource()
            undoStack.push(ChangeImageLayerProperties(self.mMapDocument,
                                                           imageLayer,
                                                           color,
                                                           imageSource))
        elif x==PropertyId.XProperty:
            pos = QPoint(val, imageLayer.y())
            undoStack.push(ChangeImageLayerPosition(self.mMapDocument,
                                                         imageLayer,
                                                         pos))
        elif x==PropertyId.YProperty:
            pos = QPoint(imageLayer.x(), val)
            undoStack.push(ChangeImageLayerPosition(self.mMapDocument,
                                                         imageLayer,
                                                         pos))
        else:
            pass

    def applyTilesetValue(self, id, val):
        tileset = self.mObject
        undoStack = self.mMapDocument.undoStack()
        x = id
        if x==PropertyId.NameProperty:
            undoStack.push(RenameTileset(self.mMapDocument,
                                              tileset,
                                              val))
        elif x==PropertyId.TileOffsetProperty:
            undoStack.push(ChangeTilesetTileOffset(self.mMapDocument,
                                                        tileset,
                                                        val))
        else:
            pass

    def applyTileValue(self, id, val):
        tile = self.mObject
        if (id == PropertyId.TileProbabilityProperty):
            undoStack = self.mMapDocument.undoStack()
            undoStack.push(ChangeTileProbability(self.mMapDocument,
                                                      tile, val))

    def applyTerrainValue(self, id, val):
        terrain = self.mObject
        if (id == PropertyId.NameProperty):
            undoStack = self.mMapDocument.undoStack()
            undoStack.push(RenameTerrain(self.mMapDocument,
                                              terrain.tileset(),
                                              terrain.id(),
                                              val))

    def createProperty(self, id, type, name, parent):
        property = self.mVariantManager.addProperty(type, name)
        if (type == QVariant.Bool):
            property.setAttribute("textVisible", False)
        parent.addSubProperty(property)
        self.mPropertyToId.insert(property, id)
        if (id != PropertyId.CustomProperty):
            self.mIdToProperty.insert(id, property)
        else:
            self.mNameToProperty.insert(name, property)
        return property

    def updateProperties(self):
        self.mUpdating = True
        x = self.mObject.typeId()
        if x==Object.MapType:
            map = self.mObject
            self.mIdToProperty[PropertyId.WidthProperty].setValue(map.width())
            self.mIdToProperty[PropertyId.HeightProperty].setValue(map.height())
            self.mIdToProperty[PropertyId.TileWidthProperty].setValue(map.tileWidth())
            self.mIdToProperty[PropertyId.TileHeightProperty].setValue(map.tileHeight())
            self.mIdToProperty[PropertyId.OrientationProperty].setValue((map.orientation().value+4)%5)
            self.mIdToProperty[PropertyId.HexSideLengthProperty].setValue(map.hexSideLength())
            self.mIdToProperty[PropertyId.StaggerAxisProperty].setValue(map.staggerAxis().value)
            self.mIdToProperty[PropertyId.StaggerIndexProperty].setValue(map.staggerIndex().value)
            self.mIdToProperty[PropertyId.LayerFormatProperty].setValue(map.layerDataFormat().value)
            self.mIdToProperty[PropertyId.RenderOrderProperty].setValue(map.renderOrder().value)
            backgroundColor = map.backgroundColor()
            if (not backgroundColor.isValid()):
                backgroundColor = Qt.darkGray
            self.mIdToProperty[PropertyId.ColorProperty].setValue(backgroundColor)
        elif x==Object.MapObjectType:
            mapObject = self.mObject
            self.mIdToProperty[PropertyId.IdProperty].setValue(mapObject.id())
            self.mIdToProperty[PropertyId.NameProperty].setValue(mapObject.name())
            self.mIdToProperty[PropertyId.TypeProperty].setValue(mapObject.type())
            self.mIdToProperty[PropertyId.VisibleProperty].setValue(mapObject.isVisible())
            self.mIdToProperty[PropertyId.XProperty].setValue(mapObject.x())
            self.mIdToProperty[PropertyId.YProperty].setValue(mapObject.y())
            self.mIdToProperty[PropertyId.WidthProperty].setValue(mapObject.width())
            self.mIdToProperty[PropertyId.HeightProperty].setValue(mapObject.height())
            self.mIdToProperty[PropertyId.RotationProperty].setValue(mapObject.rotation())
            property = self.mIdToProperty[PropertyId.FlippingProperty]
            if property:
                flippingFlags = 0
                if (mapObject.cell().flippedHorizontally):
                    flippingFlags |= 1
                if (mapObject.cell().flippedVertically):
                    flippingFlags |= 2
                property.setValue(flippingFlags)
        elif x==Object.LayerType:
            layer = self.mObject
            self.mIdToProperty[PropertyId.NameProperty].setValue(layer.name())
            self.mIdToProperty[PropertyId.VisibleProperty].setValue(layer.isVisible())
            self.mIdToProperty[PropertyId.OpacityProperty].setValue(layer.opacity())
            x = layer.layerType()
            if x==Layer.TileLayerType:
                self.mIdToProperty[PropertyId.OffsetXProperty].setValue(layer.offset().x())
                self.mIdToProperty[PropertyId.OffsetYProperty].setValue(layer.offset().y())
            elif x==Layer.ObjectGroupType:
                self.mIdToProperty[PropertyId.OffsetXProperty].setValue(layer.offset().x())
                self.mIdToProperty[PropertyId.OffsetYProperty].setValue(layer.offset().y())
                objectGroup = layer
                color = objectGroup.color()
                if (not color.isValid()):
                    color = Qt.gray
                self.mIdToProperty[PropertyId.ColorProperty].setValue(color)
                self.mIdToProperty[PropertyId.DrawOrderProperty].setValue(objectGroup.drawOrder())
            elif x==Layer.ImageLayerType:
                imageLayer = layer
                self.mIdToProperty[PropertyId.ImageSourceProperty].setValue(imageLayer.imageSource())
                self.mIdToProperty[PropertyId.ColorProperty].setValue(imageLayer.transparentColor())
                self.mIdToProperty[PropertyId.XProperty].setValue(imageLayer.x())
                self.mIdToProperty[PropertyId.YProperty].setValue(imageLayer.y())
        elif x==Object.TilesetType:
            tileset = self.mObject
            self.mIdToProperty[PropertyId.NameProperty].setValue(tileset.name())
            self.mIdToProperty[PropertyId.TileOffsetProperty].setValue(tileset.tileOffset())
            if tileset.imageSource() != '':
                self.mIdToProperty[PropertyId.SourceImageProperty].setValue(tileset.imageSource())
                self.mIdToProperty[PropertyId.TileWidthProperty].setValue(tileset.tileWidth())
                self.mIdToProperty[PropertyId.TileHeightProperty].setValue(tileset.tileHeight())
                self.mIdToProperty[PropertyId.MarginProperty].setValue(tileset.margin())
                self.mIdToProperty[PropertyId.SpacingProperty].setValue(tileset.tileSpacing())
        elif x==Object.TileType:
            tile = self.mObject
            self.mIdToProperty[PropertyId.IdProperty].setValue(tile.id())
            self.mIdToProperty[PropertyId.TileProbabilityProperty].setValue(tile.probability())
        elif x==Object.TerrainType:
            terrain = self.mObject
            self.mIdToProperty[PropertyId.NameProperty].setValue(terrain.name())

        self.mUpdating = False

    def updateCustomProperties(self):
        if (not self.mObject):
            return
        self.mUpdating = True
        self.mNameToProperty.clear()
        self.mCombinedProperties = self.mObject.properties()
        # Add properties from selected objects which mObject does not contain to mCombinedProperties.
        for obj in self.mMapDocument.currentObjects():
            if (obj == self.mObject):
                continue
            for it in obj.properties():
                if (not self.mCombinedProperties.contains(it[0])):
                    self.mCombinedProperties.insert(it[0], self.tr("<Invalid>"))

        for it in self.mCombinedProperties:
            property = self.createProperty(PropertyId.CustomProperty,
                                                         QVariant.String,
                                                         it[0],
                                                         self.mCustomPropertiesGroup)
            property.setValue(it[1])
            self.updatePropertyColor(it[0])

        self.mUpdating = False

    # If there are other objects selected check if their properties are equal. If not give them a gray color.
    def updatePropertyColor(self, name):
        property = self.mNameToProperty.value(name)
        if (not property):
            return
        propertyName = property.propertyName()
        propertyValue = property.valueText()
        # If one of the objects doesn't have this property then gray out the name and value.
        for obj in self.mMapDocument.currentObjects():
            if (not obj.hasProperty(propertyName)):
                property.setNameColor(Qt.gray)
                property.setValueColor(Qt.gray)
                return

        # If one of the objects doesn't have the same property value then gray out the value.
        for obj in self.mMapDocument.currentObjects():
            if (obj == self.mObject):
                continue
            if (obj.property(propertyName) != propertyValue):
                property.setValueColor(Qt.gray)
                return

        property.setNameColor(Qt.black)
        property.setValueColor(Qt.black)
