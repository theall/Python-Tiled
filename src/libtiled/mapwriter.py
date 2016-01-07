##
# mapwriter.py
# Copyright 2008-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2010, Dennis Honeyman <arcticuno@gmail.com>
#
# This file is part of libtiled.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.
#
#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE CONTRIBUTORS ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL THE CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
##

from layer import Layer
from gidmapper import GidMapper
from mapobject import MapObject
from objectgroup import ObjectGroup, drawOrderToString
from map import (
    Map,
    orientationToString,
    renderOrderToString,
    staggerAxisToString,
    staggerIndexToString
)
from pyqtcore import QString
from PyQt5.QtCore import (
    QSaveFile,
    QIODevice,
    QXmlStreamWriter,
    QDir,
    QFile,
    QFileInfo,
    QBuffer,
    QCoreApplication
)

def createWriter(device):
    writer = QXmlStreamWriter(device)
    writer.setAutoFormatting(True)
    writer.setAutoFormattingIndent(1)
    return writer

def makeTerrainAttribute(tile):
    terrain = QString()
    for i in range(4):
        if (i > 0):
            terrain += ","
        t = tile.cornerTerrainId(i)
        if (t > -1):
            terrain += str(t)

    return terrain
    
##
# A QXmlStreamWriter based writer for the TMX and TSX formats.
##
class MapWriter():
    def __init__(self):
        self.d = MapWriterPrivate()

    def __del__(self):
        del self.d

    ##
    # Writes a TMX map to the given \a device. Optionally a \a path can
    # be given, which will be used to create relative references to external
    # images and tilesets.
    #
    # Error checking will need to be done on the \a device after calling this
    # function.
    ##
    def writeMap(self, *args):
        l = len(args)
        if l==3:
            map, device, path = args
            self.d.writeMap(map, device, path)
        elif l==2:
            tp = type(args[1])
            if tp==QIODevice:
                map, device, path = args, QString()
                self.d.writeMap(map, device, path)
            elif tp in [QString, str]:
                ##
                # Writes a TMX map to the given \a fileName.
                #
                # Returns False and sets errorString() when reading failed.
                # \overload
                ##
                map, fileName = args
                file = QSaveFile(fileName)
                if (not self.d.openFile(file)):
                    return False
                self.writeMap(map, file, QFileInfo(fileName).absolutePath())
                if (file.error() != QFile.NoError):
                    self.d.mError = file.errorString()
                    return False

                if (not file.commit()):
                    self.d.mError = file.errorString()
                    return False

                return True

    ##
    # Writes a TSX tileset to the given \a device. Optionally a \a path can
    # be given, which will be used to create relative references to external
    # images.
    #
    # Error checking will need to be done on the \a device after calling this
    # function.
    ##
    def writeTileset(self, *args):
        l = len(args)
        if l==3:
            tileset, device, path = args
            self.d.writeTileset(tileset, device, path)
        elif l==2:
            tp = type(args[1])
            if tp==QIODevice:
                tileset, device, path = args, QString()
                self.d.writeTileset(tileset, device, path)
            elif tp in [QString, str]:
                ##
                # Writes a TSX tileset to the given \a fileName.
                #
                # Returns False and sets errorString() when reading failed.
                # \overload
                ##
                tileset, fileName = args
                file = QFile(fileName)
                if (not self.d.openFile(file)):
                    return False
                self.writeTileset(tileset, file, QFileInfo(fileName).absolutePath())
                if (file.error() != QFile.NoError):
                    self.d.mError = file.errorString()
                    return False

                return True

    ##
    # Returns the error message for the last occurred error.
    ##
    def errorString(self):
        return self.d.mError

    ##
    # Sets whether the DTD reference is written when saving the map.
    ##
    def setDtdEnabled(self, enabled):
        self.d.mDtdEnabled = enabled

    def isDtdEnabled(self):
        return self.d.mDtdEnabled

class MapWriterPrivate():

    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('MapWriter', sourceText, disambiguation, n)

    def trUtf8(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('MapWriter', sourceText, disambiguation, n)

    def __init__(self):
        self.mLayerDataFormat = Map.LayerDataFormat.Base64Zlib
        self.mDtdEnabled = False
        self.mUseAbsolutePaths = False

        self.mMapDir = QDir()
        self.mGidMapper = GidMapper()
        self.mError = QString()

    def writeMap(self, map, device, path):
        self.mMapDir = QDir(path)
        self.mUseAbsolutePaths = path==''
        self.mLayerDataFormat = map.layerDataFormat()
        writer = createWriter(device)
        writer.writeStartDocument()
        if (self.mDtdEnabled):
            writer.writeDTD("<not DOCTYPE map SYSTEM \"http://mapeditor.org/dtd/1.0/map.dtd\">")

        self.__writeMap(writer, map)
        writer.writeEndDocument()
        del writer

    def writeTileset(self, tileset, device, path):
        self.mMapDir = QDir(path)
        self.mUseAbsolutePaths = path==''
        writer = createWriter(device)
        writer.writeStartDocument()
        if (self.mDtdEnabled):
            writer.writeDTD("<not DOCTYPE tileset SYSTEM \"http://mapeditor.org/dtd/1.0/map.dtd\">")

        self.__writeTileset(writer, tileset, 0)
        writer.writeEndDocument()
        del writer

    def openFile(self, file):
        if (not file.open(QIODevice.WriteOnly | QIODevice.Text)):
            self.mError = self.tr("Could not open file for writing.")
            return False

        return True

    def __writeMap(self, w, map):
        w.writeStartElement("map")
        orientation = orientationToString(map.orientation())
        renderOrder = renderOrderToString(map.renderOrder())
        w.writeAttribute("version", "1.0")
        w.writeAttribute("orientation", orientation)
        w.writeAttribute("renderorder", renderOrder)
        w.writeAttribute("width", str(map.width()))
        w.writeAttribute("height", str(map.height()))
        w.writeAttribute("tilewidth", str(map.tileWidth()))
        w.writeAttribute("tileheight", str(map.tileHeight()))
        if (map.orientation() == Map.Orientation.Hexagonal):
            w.writeAttribute("hexsidelength", str(map.hexSideLength()))

        if (map.orientation() == Map.Orientation.Staggered or map.orientation() == Map.Orientation.Hexagonal):
            w.writeAttribute("staggeraxis", staggerAxisToString(map.staggerAxis()))
            w.writeAttribute("staggerindex", staggerIndexToString(map.staggerIndex()))

        if (map.backgroundColor().isValid()):
            w.writeAttribute("backgroundcolor", map.backgroundColor().name())

        w.writeAttribute("nextobjectid", str(map.nextObjectId()))
        self.__writeProperties(w, map.properties())
        self.mGidMapper.clear()
        firstGid = 1
        for tileset in map.tilesets():
            self.__writeTileset(w, tileset, firstGid)
            self.mGidMapper.insert(firstGid, tileset)
            firstGid += tileset.tileCount()

        for layer in map.layers():
            type = layer.layerType()
            if (type == Layer.TileLayerType):
                self.__writeTileLayer(w, layer)
            elif (type == Layer.ObjectGroupType):
                self.__writeObjectGroup(w, layer)
            elif (type == Layer.ImageLayerType):
                self.__writeImageLayer(w, layer)

        w.writeEndElement()

    def __writeTileset(self, w, tileset, firstGid):
        w.writeStartElement("tileset")
        if (firstGid > 0):
            w.writeAttribute("firstgid", str(firstGid))
        fileName = tileset.fileName()
        if fileName != '':
            source = fileName
            if (not self.mUseAbsolutePaths):
                source = self.mMapDir.relativeFilePath(source)
            w.writeAttribute("source", source)
            # Tileset is external, so no need to write any of the stuff below
            w.writeEndElement()
            return

        w.writeAttribute("name", tileset.name())
        w.writeAttribute("tilewidth", str(tileset.tileWidth()))
        w.writeAttribute("tileheight", str(tileset.tileHeight()))
        tileSpacing = tileset.tileSpacing()
        margin = tileset.margin()
        if (tileSpacing != 0):
            w.writeAttribute("spacing",
                             str(tileSpacing))
        if (margin != 0):
            w.writeAttribute("margin", str(margin))
        
        w.writeAttribute("tilecount", str(tileset.tileCount()))
                     
        offset = tileset.tileOffset()
        if (not offset.isNull()):
            w.writeStartElement("tileoffset")
            w.writeAttribute("x", str(offset.x()))
            w.writeAttribute("y", str(offset.y()))
            w.writeEndElement()

        # Write the tileset properties
        self.__writeProperties(w, tileset.properties())
        # Write the image element
        imageSource = tileset.imageSource()
        if imageSource != '':
            w.writeStartElement("image")
            source = imageSource
            if (not self.mUseAbsolutePaths):
                source = self.mMapDir.relativeFilePath(source)
            w.writeAttribute("source", source)
            transColor = tileset.transparentColor()
            if (transColor.isValid()):
                w.writeAttribute("trans", transColor.name()[1])
            if (tileset.imageWidth() > 0):
                w.writeAttribute("width",
                                 str(tileset.imageWidth()))
            if (tileset.imageHeight() > 0):
                w.writeAttribute("height",
                                 str(tileset.imageHeight()))
            w.writeEndElement()

        # Write the terrain types
        if (tileset.terrainCount() > 0):
            w.writeStartElement("terraintypes")
            for i in range(tileset.terrainCount()):
                t = tileset.terrain(i)
                w.writeStartElement("terrain")
                w.writeAttribute("name", t.name())
                w.writeAttribute("tile", str(t.imageTileId()))
                self.__writeProperties(w, t.properties())
                w.writeEndElement()

            w.writeEndElement()

        # Write the properties for those tiles that have them
        for i in range(tileset.tileCount()):
            tile = tileset.tileAt(i)
            properties = tile.properties()
            terrain = tile.terrain()
            probability = tile.probability()
            objectGroup = tile.objectGroup()
            if (not properties.isEmpty() or terrain != 0xFFFFFFFF or probability != 1.0 or imageSource=='' or objectGroup or tile.isAnimated()):
                w.writeStartElement("tile")
                w.writeAttribute("id", str(i))
                if (terrain != 0xFFFFFFFF):
                    w.writeAttribute("terrain", makeTerrainAttribute(tile))
                if (probability != 1.0):
                    w.writeAttribute("probability", str(probability))
                if (not properties.isEmpty()):
                    self.__writeProperties(w, properties)
                if imageSource=='':
                    w.writeStartElement("image")
                    tileSize = tile.size()
                    if (not tileSize.isNull()):
                        w.writeAttribute("width",
                                         str(tileSize.width()))
                        w.writeAttribute("height",
                                         str(tileSize.height()))

                    if (tile.imageSource()==''):
                        w.writeAttribute("format",
                                         "png")
                        w.writeStartElement("data")
                        w.writeAttribute("encoding",
                                         "base64")
                        buffer = QBuffer()
                        tile.image().save(buffer, "png")
                        w.writeCharacters(buffer.data().toBase64())
                        w.writeEndElement() #
                    else:
                        source = tile.imageSource()
                        if (not self.mUseAbsolutePaths):
                            source = self.mMapDir.relativeFilePath(source)
                        w.writeAttribute("source", source)

                    w.writeEndElement() #

                if (objectGroup):
                    self.__writeObjectGroup(w, objectGroup)
                if (tile.isAnimated()):
                    frames = tile.frames()
                    w.writeStartElement("animation")
                    for frame in frames:
                        w.writeStartElement("frame")
                        w.writeAttribute("tileid", str(frame.tileId))
                        w.writeAttribute("duration", str(frame.duration))
                        w.writeEndElement() #

                    w.writeEndElement() #

                w.writeEndElement() #

        w.writeEndElement()

    def __writeTileLayer(self, w, tileLayer):
        w.writeStartElement("layer")
        self.__writeLayerAttributes(w, tileLayer)
        self.__writeProperties(w, tileLayer.properties())
        encoding = QString()
        compression = QString()
        if (self.mLayerDataFormat == Map.LayerDataFormat.Base64
                or self.mLayerDataFormat == Map.LayerDataFormat.Base64Gzip
                or self.mLayerDataFormat == Map.LayerDataFormat.Base64Zlib):
            encoding = "base64"
            if (self.mLayerDataFormat == Map.LayerDataFormat.Base64Gzip):
                compression = "gzip"
            elif (self.mLayerDataFormat == Map.LayerDataFormat.Base64Zlib):
                compression = "zlib"
        elif (self.mLayerDataFormat == Map.LayerDataFormat.CSV):
            encoding = "csv"
        w.writeStartElement("data")
        if encoding != '':
            w.writeAttribute("encoding", encoding)
        if compression != '':
            w.writeAttribute("compression", compression)
        if (self.mLayerDataFormat == Map.LayerDataFormat.XML):
            for y in range(tileLayer.height()):
                for x in range(tileLayer.width()):
                    gid = self.mGidMapper.cellToGid(tileLayer.cellAt(x, y))
                    w.writeStartElement("tile")
                    w.writeAttribute("gid", str(gid))
                    w.writeEndElement()
        elif (self.mLayerDataFormat == Map.LayerDataFormat.CSV):
            tileData = ''
            for y in range(tileLayer.height()):
                for x in range(tileLayer.width()):
                    gid = self.mGidMapper.cellToGid(tileLayer.cellAt(x, y))
                    tileData += str(gid)
                    if (x != tileLayer.width() - 1 or y != tileLayer.height() - 1):
                        tileData += ","

                tileData += "\n"

            w.writeCharacters("\n")
            w.writeCharacters(tileData)
        else:
            tileData = self.mGidMapper.encodeLayerData(tileLayer, self.mLayerDataFormat)
            
            w.writeCharacters("\n   ")
            w.writeCharacters(tileData.data().decode())
            w.writeCharacters("\n  ")

        w.writeEndElement() # </data>
        w.writeEndElement() # </layer>

    def __writeLayerAttributes(self, w, layer):
        if layer.name() != '':
            w.writeAttribute("name", layer.name())

        x = layer.x()
        y = layer.y()
        opacity = layer.opacity()
        if (x != 0):
            w.writeAttribute("x", str(x))
        if (y != 0):
            w.writeAttribute("y", str(y))
            
        if (layer.layerType() == Layer.TileLayerType):
            w.writeAttribute("width", str(layer.width()))
            w.writeAttribute("height", str(layer.height()))
            
        if (not layer.isVisible()):
            w.writeAttribute("visible"), "0"
        if (opacity != 1.0):
            w.writeAttribute("opacity", str(opacity))
        
        offset = layer.offset()
        if (not offset.isNull()):
            w.writeAttribute("offsetx", str(offset.x()))
            w.writeAttribute("offsety", str(offset.y()))

    def __writeObjectGroup(self, w, objectGroup):
        w.writeStartElement("objectgroup")
        if (objectGroup.color().isValid()):
            w.writeAttribute("color", objectGroup.color().name())
        if (objectGroup.drawOrder() != ObjectGroup.DrawOrder.TopDownOrder):
            w.writeAttribute("draworder", drawOrderToString(objectGroup.drawOrder()))

        self.__writeLayerAttributes(w, objectGroup)
        self.__writeProperties(w, objectGroup.properties())
        for mapObject in objectGroup.objects():
            self.__writeObject(w, mapObject)
        w.writeEndElement()

    def __writeObject(self, w, mapObject):
        w.writeStartElement("object")
        w.writeAttribute("id", str(mapObject.id()))
        name = mapObject.name()
        type = mapObject.type()
        if name != '':
            w.writeAttribute("name", name)
        if type != '':
            w.writeAttribute("type", type)
        if (not mapObject.cell().isEmpty()):
            gid = self.mGidMapper.cellToGid(mapObject.cell())
            w.writeAttribute("gid", str(gid))

        pos = mapObject.position()
        size = mapObject.size()
        
        w.writeAttribute("x", str(pos.x()))
        w.writeAttribute("y", str(pos.y()))
        if (size.width() != 0):
            w.writeAttribute("width", str(size.width()))
        if (size.height() != 0):
            w.writeAttribute("height", str(size.height()))
        rotation = mapObject.rotation()
        if (rotation != 0.0):
            w.writeAttribute("rotation", str(rotation))
        if (not mapObject.isVisible()):
            w.writeAttribute("visible"), "0"
        self.__writeProperties(w, mapObject.properties())
        polygon = mapObject.polygon()
        if (not polygon.isEmpty()):
            if (mapObject.shape() == MapObject.Polygon):
                w.writeStartElement("polygon")
            else:
                w.writeStartElement("polyline")
            points = ''
            for point in polygon:
                points += str(point.x()) + ',' + str(point.y()) + ' '

            points = points[:-1]
            w.writeAttribute("points", points)
            w.writeEndElement()

        if (mapObject.shape() == MapObject.Ellipse):
            w.writeEmptyElement("ellipse")
        w.writeEndElement()

    def __writeImageLayer(self, w, imageLayer):
        w.writeStartElement("imagelayer")
        self.__writeLayerAttributes(w, imageLayer)
        # Write the image element
        imageSource = imageLayer.imageSource()
        if imageSource != '':
            w.writeStartElement("image")
            source = imageSource
            if (not self.mUseAbsolutePaths):
                source = self.mMapDir.relativeFilePath(source)
            w.writeAttribute("source", source)
            transColor = imageLayer.transparentColor()
            if (transColor.isValid()):
                w.writeAttribute("trans", transColor.name()[1])
            w.writeEndElement()

        self.__writeProperties(w, imageLayer.properties())
        w.writeEndElement()

    def __writeProperties(self, w, properties):
        if (properties.isEmpty()):
            return
        w.writeStartElement("properties")
        for it in properties:
            w.writeStartElement("property")
            w.writeAttribute("name", it[0])
            value = str(it[1])
            if value.__contains__('\n'):
                w.writeCharacters(value)
            else:
                w.writeAttribute("value", value)

            w.writeEndElement()

        w.writeEndElement()
