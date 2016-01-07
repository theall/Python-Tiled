##
# mapreader.py
# Copyright 2008-2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from tiled_global import Int, Int2, Float, Float2
from properties import Properties
from tile import Frame
from tileset import Tileset
from tilelayer import TileLayer
import tilesetformat
from map import (
    Map, 
    orientationFromString, 
    staggerAxisFromString, 
    staggerIndexFromString, 
    renderOrderFromString
)
from gidmapper import GidMapper, DecodeError
from mapobject import MapObject
from objectgroup import ObjectGroup, drawOrderFromString
from imagelayer import ImageLayer
from pyqtcore import QString, QVector
from PyQt5.QtCore import (
    QXmlStreamReader,
    QFileInfo,
    QDir,
    QFile,
    QSizeF,
    QByteArray,
    qDebug,
    QPoint,
    QPointF,
    QIODevice,
    QCoreApplication
)
from PyQt5.QtGui import (
    QColor,
    QImage,
    QPolygonF,
    QPixmap
)

def readLayerAttributes(layer, atts):
    opacityRef = atts.value("opacity")
    visibleRef = atts.value("visible")
    opacity, ok = Float2(opacityRef)
    if (ok):
        layer.setOpacity(opacity)
    visible, ok = Int2(visibleRef)
    if (ok):
        layer.setVisible(visible)
    offset = QPointF(Float(atts.value("offsetx")),
                         Float(atts.value("offsety")))

    layer.setOffset(offset)
    
##
# A fast QXmlStreamReader based reader for the TMX and TSX formats.
#
# Can be subclassed when special handling of external images and tilesets is
# needed.
##
class MapReader():
    
    def __init__(self):
        self.d = MapReaderPrivate(self)

    def __del__(self):
        del self.d

    ##
    # Reads a TMX map from the given \a device. Optionally a \a path can
    # be given, which will be used to resolve relative references to external
    # images and tilesets.
    #
    # Returns 0 and sets errorString() when reading failed.
    #
    # The caller takes ownership over the newly created map.
    ##
    def readMap(self, *args):
        l = len(args)
        if l==2:
            device, path = args
            return self.d.readMap(device, path)
        elif l==1:
            tp = type(args[0])
            if tp==QIODevice:
                return self.d.readMap(device, QString())
            elif tp in [QString, str]:
                ##
                # Reads a TMX map from the given \a fileName.
                # \overload
                ##
                fileName = args[0]
                file = QFile(fileName)
                if (not self.d.openFile(file)):
                    return None
                return self.readMap(file, QFileInfo(fileName).absolutePath())

    ##
    # Reads a TSX tileset from the given \a device. Optionally a \a path can
    # be given, which will be used to resolve relative references to external
    # images.
    #
    # Returns 0 and sets errorString() when reading failed.
    #
    # The caller takes ownership over the newly created tileset.
    ##
    def readTileset(self, *args):
        l = len(args)
        if l==2:
            device, path = args
            return self.d.readTileset(device, path)
        elif l==1:
            tp = type(args[0])
            if tp==QIODevice:
                return self.d.readTileset(device, QString())
            elif tp in [QString, str]:
                fileName = args[0]
                ##
                # Reads a TSX tileset from the given \a fileName.
                # \overload
                ##
                file = QFile(fileName)
                if (not self.d.openFile(file)):
                    return None
                tileset = self.readTileset(file, QFileInfo(fileName).absolutePath())
                if (tileset):
                    tileset.setFileName(fileName)
                return tileset

    ##
    # Returns the error message for the last occurred error.
    ##
    def errorString(self):
        return self.d.errorString()

    ##
    # Called for each \a reference to an external file. Should return the path
    # to be used when loading this file. \a mapPath contains the path to the
    # map or tileset that is currently being loaded.
    ##
    def resolveReference(self, reference, mapPath):
        if (QDir.isRelativePath(reference)):
            return mapPath + '/' + reference
        else:
            return reference

    ##
    # Called when an external image is encountered while a tileset is loaded.
    ##
    def readExternalImage(self, source):
        return QImage(source)

    ##
    # Called when an external tileset is encountered while a map is loaded.
    # The default implementation just calls __readTileset() on a new MapReader.
    #
    # If an error occurred, the \a error parameter should be set to the error
    # message.
    ##
    def readExternalTileset(self, source):
        return tilesetformat.readTileset(source)

class MapReaderPrivate():
    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('MapReader', sourceText, disambiguation, n)

    def trUtf8(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('MapReader', sourceText, disambiguation, n)

    def __init__(self, mapReader):
        self.p = mapReader
        self.mMap = None
        self.mError = QString('')
        self.mReadingExternalTileset = False
        self.xml = QXmlStreamReader()
        self.mGidMapper = GidMapper()

    def readMap(self, device, path):
        self.mError = QString('')
        self.mPath = path
        map = None
        self.xml.setDevice(device)
        if (self.xml.readNextStartElement() and self.xml.name() == "map"):
            map = self.__readMap()
        else:
            self.xml.raiseError(self.tr("Not a map file."))

        self.mGidMapper.clear()
        return map

    def readTileset(self, device, path):
        self.mError = ''
        self.mPath = path
        tileset = None
        self.mReadingExternalTileset = True
        self.xml.setDevice(device)
        if (self.xml.readNextStartElement() and self.xml.name() == "tileset"):
            tileset = self.__readTileset()
        else:
            self.xml.raiseError(self.tr("Not a tileset file."))
        self.mReadingExternalTileset = False
        return tileset

    def openFile(self, file):
        if (not file.exists()):
            self.mError = self.tr("File not found: %s"%file.fileName())
            return False
        elif (not file.open(QFile.ReadOnly | QFile.Text)):
            self.mError = self.tr("Unable to read file: %s"%file.fileName())
            return False

        return True

    def errorString(self):
        if self.mError != '':
            return self.mError
        else:
            return self.tr("%d\n\nLine %d, column %s"%(self.xml.lineNumber(), self.xml.columnNumber(), self.xml.errorString()))

    def __readUnknownElement(self):
        qDebug("Unknown element (fixme): "+self.xml.name()+" at line "+self.xml.lineNumber()+", column "+self.xml.columnNumber())
        self.xml.skipCurrentElement()

    def __readMap(self):
        atts = self.xml.attributes()
        mapWidth = Int(atts.value("width"))
        mapHeight = Int(atts.value("height"))
        tileWidth = Int(atts.value("tilewidth"))
        tileHeight = Int(atts.value("tileheight"))
        hexSideLength = Int(atts.value("hexsidelength"))
        orientationString = atts.value("orientation")
        orientation = orientationFromString(orientationString)
        if (orientation == Map.Orientation.Unknown):
            self.xml.raiseError(self.tr("Unsupported map orientation: \"%s\""%orientationString))

        staggerAxisString = atts.value("staggeraxis")
        staggerAxis = staggerAxisFromString(staggerAxisString)
        staggerIndexString = atts.value("staggerindex")
        staggerIndex = staggerIndexFromString(staggerIndexString)
        renderOrderString = atts.value("renderorder")
        renderOrder = renderOrderFromString(renderOrderString)
        nextObjectId = Int(atts.value("nextobjectid"))
        self.mMap = Map(orientation, mapWidth, mapHeight, tileWidth, tileHeight)
        self.mMap.setHexSideLength(hexSideLength)
        self.mMap.setStaggerAxis(staggerAxis)
        self.mMap.setStaggerIndex(staggerIndex)
        self.mMap.setRenderOrder(renderOrder)
        if (nextObjectId):
            self.mMap.setNextObjectId(nextObjectId)

        bgColorString = atts.value("backgroundcolor")
        if len(bgColorString)>0:
            self.mMap.setBackgroundColor(QColor(bgColorString))
        while (self.xml.readNextStartElement()):
            if (self.xml.name() == "properties"):
                self.mMap.mergeProperties(self.__readProperties())
            elif (self.xml.name() == "tileset"):
                self.mMap.addTileset(self.__readTileset())
            elif (self.xml.name() == "layer"):
                self.mMap.addLayer(self.__readLayer())
            elif (self.xml.name() == "objectgroup"):
                self.mMap.addLayer(self.__readObjectGroup())
            elif (self.xml.name() == "imagelayer"):
                self.mMap.addLayer(self.__readImageLayer())
            else:
                self.__readUnknownElement()

        # Clean up in case of error
        if (self.xml.hasError()):
            self.mMap = None

        return self.mMap

    def __readTileset(self):
        atts = self.xml.attributes()
        source = atts.value("source")
        firstGid = Int(atts.value("firstgid"))
        tileset = None
        if source == '': # Not an external tileset
            name = atts.value("name")
            tileWidth = Int(atts.value("tilewidth"))
            tileHeight = Int(atts.value("tileheight"))
            tileSpacing = Int(atts.value("spacing"))
            margin = Int(atts.value("margin"))
            if (tileWidth < 0 or tileHeight < 0
                or (firstGid == 0 and not self.mReadingExternalTileset)):
                self.xml.raiseError(self.tr("Invalid tileset parameters for tileset '%s'"%name))
            else:
                tileset = Tileset.create(name, tileWidth, tileHeight, tileSpacing, margin)

                while (self.xml.readNextStartElement()):
                    if (self.xml.name() == "tile"):
                        self.__readTilesetTile(tileset)
                    elif (self.xml.name() == "tileoffset"):
                        oa = self.xml.attributes()
                        x = Int(oa.value("x"))
                        y = Int(oa.value("y"))
                        tileset.setTileOffset(QPoint(x, y))
                        self.xml.skipCurrentElement()
                    elif (self.xml.name() == "properties"):
                        tileset.mergeProperties(self.__readProperties())
                    elif (self.xml.name() == "image"):
                        if (tileWidth == 0 or tileHeight == 0):
                            self.xml.raiseError(self.tr("Invalid tileset parameters for tileset '%s'"%name))
                            
                            tileset.clear()
                            break
                        else:
                            self.__readTilesetImage(tileset)
                    elif (self.xml.name() == "terraintypes"):
                        self.__readTilesetTerrainTypes(tileset)
                    else:
                        self.__readUnknownElement()
        else: # External tileset
            absoluteSource = self.p.resolveReference(source, self.mPath)
            tileset, error = self.p.readExternalTileset(absoluteSource)
            if (not tileset):
                self.xml.raiseError(self.tr("Error while loading tileset '%s': %s"%(absoluteSource, error)))

            self.xml.skipCurrentElement()

        if (tileset and not self.mReadingExternalTileset):
            self.mGidMapper.insert(firstGid, tileset)
        return tileset

    def __readTilesetTile(self, tileset):
        atts = self.xml.attributes()
        id = Int(atts.value("id"))
        if (id < 0):
            self.xml.raiseError(self.tr("Invalid tile ID: %d"%id))
            return

        hasImage = tileset.imageSource()!=''
        if (hasImage and id >= tileset.tileCount()):
            self.xml.raiseError(self.tr("Tile ID does not exist in tileset image: %d"%id))
            return

        if (id > tileset.tileCount()):
            self.xml.raiseError(self.tr("Invalid (nonconsecutive) tile ID: %d"%id))
            return

        # For tilesets without image source, consecutive tile IDs are allowed (for
        # tiles with individual images)
        if (id == tileset.tileCount()):
            tileset.addTile(QPixmap())
        tile = tileset.tileAt(id)
        # Read tile quadrant terrain ids
        terrain = atts.value("terrain")
        if terrain != '':
            quadrants = terrain.split(",")
            if (len(quadrants) == 4):
                for i in range(4):
                    if quadrants[i]=='':
                        t = -1
                    else:
                        t = Int(quadrants[i])
                    tile.setCornerTerrainId(i, t)

        # Read tile probability
        probability = atts.value("probability")
        if probability != '':
            tile.setProbability(Float(probability))
        while (self.xml.readNextStartElement()):
            if (self.xml.name() == "properties"):
                tile.mergeProperties(self.__readProperties())
            elif (self.xml.name() == "image"):
                source = self.xml.attributes().value("source")
                if source != '':
                    source = self.p.resolveReference(source, self.mPath)
                tileset.setTileImage(id, QPixmap.fromImage(self.__readImage()), source)
            elif (self.xml.name() == "objectgroup"):
                tile.setObjectGroup(self.__readObjectGroup())
            elif (self.xml.name() == "animation"):
                tile.setFrames(self.__readAnimationFrames())
            else:
                self.__readUnknownElement()

        # Temporary code to support TMW-style animation frame properties
        if (not tile.isAnimated() and tile.hasProperty("animation-frame0")):
            frames = QVector()
            i = 0
            while(i>=0):
                frameName = "animation-frame" + str(i)
                delayName = "animation-delay" + str(i)
                if (tile.hasProperty(frameName) and tile.hasProperty(delayName)):
                    frame = Frame()
                    frame.tileId = tile.property(frameName)
                    frame.duration = tile.property(delayName) * 10
                    frames.append(frame)
                else:
                    break
                i += 1

            tile.setFrames(frames)

    def __readTilesetImage(self, tileset):
        atts = self.xml.attributes()
        source = atts.value("source")
        trans = atts.value("trans")
        if len(trans)>0:
            if (not trans.startswith('#')):
                trans = '#' + trans
            tileset.setTransparentColor(QColor(trans))

        if len(source)>0:
            source = self.p.resolveReference(source, self.mPath)
        # Set the width that the tileset had when the map was saved
        width = Int(atts.value("width"))
        self.mGidMapper.setTilesetWidth(tileset, width)
        if (not tileset.loadFromImage(self.__readImage(), source)):
            self.xml.raiseError(self.tr("Error loading tileset image:\n'%s'"%source))

    def __readTilesetTerrainTypes(self, tileset):
        while (self.xml.readNextStartElement()):
            if (self.xml.name() == "terrain"):
                atts = self.xml.attributes()
                name = atts.value("name")
                tile = atts.value("tile")
                terrain = tileset.addTerrain(name, tile)
                while (self.xml.readNextStartElement()):
                    if (self.xml.name() == "properties"):
                        terrain.mergeProperties(self.__readProperties())
                    else:
                        self.__readUnknownElement()

            else:
                self.__readUnknownElement()

    def __readImage(self):
        atts = self.xml.attributes()
        source = atts.value("source")
        format = atts.value("format")
        if len(source)==0:
            while (self.xml.readNextStartElement()):
                if (self.xml.name() == "data"):
                    atts = self.xml.attributes()
                    encoding = atts.value("encoding")
                    data = self.xml.readElementText().toLatin1()
                    if (encoding == "base64"):
                        data = QByteArray.fromBase64(data)

                    self.xml.skipCurrentElement()
                    return QImage.fromData(data, format.toLatin1())
                else:
                    self.__readUnknownElement()

        else:
            self.xml.skipCurrentElement()
            source = self.p.resolveReference(source, self.mPath)
            image = self.p.readExternalImage(source)
            if (image.isNull()):
                self.xml.raiseError(self.tr("Error loading image:\n'%s'"%source))
            return image

        return QImage()

    def __readLayer(self):
        atts = self.xml.attributes()
        name = atts.value("name")
        x = Int(atts.value("x"))
        y = Int(atts.value("y"))
        width = Int(atts.value("width"))
        height = Int(atts.value("height"))
        tileLayer = TileLayer(name, x, y, width, height)
        readLayerAttributes(tileLayer, atts)
        while (self.xml.readNextStartElement()):
            if (self.xml.name() == "properties"):
                tileLayer.mergeProperties(self.__readProperties())
            elif (self.xml.name() == "data"):
                self.__readLayerData(tileLayer)
            else:
                self.__readUnknownElement()

        return tileLayer

    def __readLayerData(self, tileLayer):
        atts = self.xml.attributes()
        encoding = atts.value("encoding")
        compression = atts.value("compression")
        layerDataFormat = 0
        if (encoding == ''):
            layerDataFormat = Map.LayerDataFormat.XML
        elif (encoding == "csv"):
            layerDataFormat = Map.LayerDataFormat.CSV
        elif (encoding == "base64"):
            if (compression == ''):
                layerDataFormat = Map.LayerDataFormat.Base64
            elif (compression == "gzip"):
                layerDataFormat = Map.LayerDataFormat.Base64Gzip
            elif (compression == "zlib"):
                layerDataFormat = Map.LayerDataFormat.Base64Zlib
            else:
                self.xml.raiseError(self.tr("Compression method '%s' not supported"%compression))
                return
        else:
            self.xml.raiseError(self.tr("Unknown encoding: %s"%encoding))
            return
        
        self.mMap.setLayerDataFormat(layerDataFormat)
        
        x = 0
        y = 0
        while (self.xml.readNext() != QXmlStreamReader.Invalid):
            if (self.xml.isEndElement()):
                break
            elif (self.xml.isStartElement()):
                if (self.xml.name() == "tile"):
                    if (y >= tileLayer.height()):
                        self.xml.raiseError(self.tr("Too many <tile> elements"))
                        continue

                    atts = self.xml.attributes()
                    gid = Int(atts.value("gid"))
                    tileLayer.setCell(x, y, self.__cellForGid(gid))
                    x += 1
                    if (x >= tileLayer.width()):
                        x = 0
                        y += 1

                    self.xml.skipCurrentElement()
                else:
                    self.__readUnknownElement()
            elif (self.xml.isCharacters() and not self.xml.isWhitespace()):
                if (encoding == "base64"):
                    self.__decodeBinaryLayerData(tileLayer,
                                          self.xml.text(),
                                          layerDataFormat)
                elif (encoding == "csv"):
                    self.__decodeCSVLayerData(tileLayer, self.xml.text())

    def __decodeBinaryLayerData(self, tileLayer, data, format):
        error = self.mGidMapper.decodeLayerData(tileLayer, data, format)

        if error==DecodeError.CorruptLayerData:
            self.xml.raiseError(self.tr("Corrupt layer data for layer '%s'"%tileLayer.name()))
            return
        elif error==DecodeError.TileButNoTilesets:
            self.xml.raiseError(self.tr("Tile used but no tilesets specified"))
            return
        elif error==DecodeError.InvalidTile:
            self.xml.raiseError(self.tr("Invalid tile: %d"%self.mGidMapper.invalidTile()))
            return
        elif error==DecodeError.NoError:
            pass

    def __decodeCSVLayerData(self, tileLayer, text):
        trimText = text.strip()
        tiles = trimText.split(',')
        if (len(tiles) != tileLayer.width() * tileLayer.height()):
            self.xml.raiseError(self.tr("Corrupt layer data for layer '%s'"%tileLayer.name()))
            return

        for y in range(tileLayer.height()):
            for x in range(tileLayer.width()):
                conversionOk = False
                gid, conversionOk = Int2(tiles[y * tileLayer.width() + x])
                if (not conversionOk):
                    self.xml.raiseError(self.tr("Unable to parse tile at (%d,%d) on layer '%s'"%(x + 1, y + 1, tileLayer.name())))
                    return

                tileLayer.setCell(x, y, self.__cellForGid(gid))

    ##
    # Returns the cell for the given global tile ID. Errors are raised with
    # the QXmlStreamReader.
    #
    # @param gid the global tile ID
    # @return the cell data associated with the given global tile ID, or an
    #         empty cell if not found
    ##
    def __cellForGid(self, gid):
        ok = False
        result, ok = self.mGidMapper.gidToCell(gid)
        if (not ok):
            if (self.mGidMapper.isEmpty()):
                self.xml.raiseError(self.tr("Tile used but no tilesets specified"))
            else:
                self.xml.raiseError(self.tr("Invalid tile: %d"%gid))

        return result

    def __readImageLayer(self):
        atts = self.xml.attributes()
        name = atts.value("name")
        x = Int(atts.value("x"))
        y = Int(atts.value("y"))
        width = Int(atts.value("width"))
        height = Int(atts.value("height"))
        imageLayer = ImageLayer(name, x, y, width, height)
        readLayerAttributes(imageLayer, atts)
        while (self.xml.readNextStartElement()):
            if (self.xml.name() == "image"):
                self.__readImageLayerImage(imageLayer)
            elif (self.xml.name() == "properties"):
                imageLayer.mergeProperties(self.__readProperties())
            else:
                self.__readUnknownElement()

        return imageLayer

    def __readImageLayerImage(self, imageLayer):
        atts = self.xml.attributes()
        source = atts.value("source")
        trans = atts.value("trans")
        if trans != '':
            if (not trans.startswith('#')):
                trans = '#' + trans
            imageLayer.setTransparentColor(QColor(trans))

        source = self.p.resolveReference(source, self.mPath)
        imageLayerImage = self.p.readExternalImage(source)
        if (not imageLayer.loadFromImage(imageLayerImage, source)):
            self.xml.raiseError(self.tr("Error loading image layer image:\n'%s'"%source))
        self.xml.skipCurrentElement()

    def __readObjectGroup(self):
        atts = self.xml.attributes()
        name = atts.value("name")
        x = Int(atts.value("x"))
        y = Int(atts.value("y"))
        width = Int(atts.value("width"))
        height = Int(atts.value("height"))
        objectGroup = ObjectGroup(name, x, y, width, height)
        readLayerAttributes(objectGroup, atts)
        color = atts.value("color")
        if color != '':
            objectGroup.setColor(color)
        if (atts.hasAttribute("draworder")):
            value = atts.value("draworder")
            drawOrder = drawOrderFromString(value)
            if (drawOrder == ObjectGroup.DrawOrder.UnknownOrder):
                #del objectGroup
                self.xml.raiseError(self.tr("Invalid draw order: %s"%value))
                return None

            objectGroup.setDrawOrder(drawOrder)

        while (self.xml.readNextStartElement()):
            if (self.xml.name() == "object"):
                objectGroup.addObject(self.__readObject())
            elif (self.xml.name() == "properties"):
                objectGroup.mergeProperties(self.__readProperties())
            else:
                self.__readUnknownElement()

        return objectGroup

    def __readObject(self):
        atts = self.xml.attributes()
        id = Int(atts.value("id"))
        name = atts.value("name")
        gid = Int(atts.value("gid"))
        x = Float(atts.value("x"))
        y = Float(atts.value("y"))
        width = Float(atts.value("width"))
        height = Float(atts.value("height"))
        type = atts.value("type")
        visibleRef = atts.value("visible")
        pos = QPointF(x, y)
        size = QSizeF(width, height)
        object = MapObject(name, type, pos, size)
        object.setId(id)

        try:
            rotation = Float(atts.value("rotation"))
            ok = True
        except:
            ok = False
        if (ok):
            object.setRotation(rotation)
        if (gid):
            object.setCell(self.__cellForGid(gid))
            if (not object.cell().isEmpty()):
                tileSize = object.cell().tile.size()
                if (width == 0):
                    object.setWidth(tileSize.width())
                if (height == 0):
                    object.setHeight(tileSize.height())
        
        try:
            visible = int(visibleRef)
            ok = True
        except:
            ok = False
        if ok:
            object.setVisible(visible)
        while (self.xml.readNextStartElement()):
            if (self.xml.name() == "properties"):
                object.mergeProperties(self.__readProperties())
            elif (self.xml.name() == "polygon"):
                object.setPolygon(self.__readPolygon())
                object.setShape(MapObject.Polygon)
            elif (self.xml.name() == "polyline"):
                object.setPolygon(self.__readPolygon())
                object.setShape(MapObject.Polyline)
            elif (self.xml.name() == "ellipse"):
                self.xml.skipCurrentElement()
                object.setShape(MapObject.Ellipse)
            else:
                self.__readUnknownElement()

        return object

    def __readPolygon(self):
        atts = self.xml.attributes()
        points = atts.value("points")
        pointsList = points.split(' ', QString.SkipEmptyParts)
        polygon = QPolygonF()
        ok = True
        for point in pointsList:
            commaPos = point.indexOf(',')
            if (commaPos == -1):
                ok = False
                break
            
            try:
                x = Float(point.left(commaPos))
                ok = True
            except:
                ok = False
            if (not ok):
                break
            try:
                y = point[commaPos + 1]
                ok = True
            except:
                ok = False
            if (not ok):
                break
            polygon.append(QPointF(x, y))

        if (not ok):
            self.xml.raiseError(self.tr("Invalid points data for polygon"))
        self.xml.skipCurrentElement()
        return polygon

    def __readAnimationFrames(self):
        frames = QVector()
        while (self.xml.readNextStartElement()):
            if (self.xml.name() == "frame"):
                atts = self.xml.attributes()
                frame = Frame()
                frame.tileId = Int(atts.value("tileid"))
                frame.duration = atts.value("duration")
                frames.append(frame)
                self.xml.skipCurrentElement()
            else:
                self.__readUnknownElement()

        return frames

    def __readProperties(self):
        properties = Properties()
        while (self.xml.readNextStartElement()):
            if (self.xml.name() == "property"):
                self.__readProperty(properties)
            else:
                self.__readUnknownElement()

        return properties

    def __readProperty(self, properties):
        atts = self.xml.attributes()
        propertyName = atts.value("name")
        propertyValue = atts.value("value")
        while (self.xml.readNext() != QXmlStreamReader.Invalid):
            if (self.xml.isEndElement()):
                break
            elif (self.xml.isCharacters() and not self.xml.isWhitespace()):
                if (propertyValue.isEmpty()):
                    propertyValue = self.xml.text()
            elif (self.xml.isStartElement()):
                self.__readUnknownElement()

        properties.insert(propertyName, propertyValue)
