##
# Flare Tiled Plugin
# Copyright 2010, Jaderamiso <jaderamiso@gmail.com>
# Copyright 2011, Stefan Beller <stefanbeller@googlemail.com>
# Copyright 2011, Clint Bellanger <clintbellanger@gmail.com>
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
# this program. If not, see .
##

from tiled_global import Int
from objectgroup import ObjectGroup
from tileset import Tileset
from tilelayer import TileLayer
from mapobject import MapObject
from map import Map, orientationFromString, orientationToString
from gidmapper import GidMapper
from mapformat import MapFormat
from pyqtcore import (
    QString
)
from PyQt5.QtCore import (
    QPoint,
    QDir,
    QPointF,
    QFileInfo,
    QTextStream,
    QFile,
    QIODevice
)
class FlarePlugin(MapFormat):
    def __init__(self):
        super().__init__()
        
        self.mError = ''

    # MapReaderInterface
    def read(self, fileName):
        file = QFile(fileName)
        if (not file.open (QIODevice.ReadOnly)):
            self.mError = self.tr("Could not open file for reading.")
            return 0
        
        # default to values of the original flare alpha game.
        map = Map(Map.Orientation.Isometric, 256, 256, 64, 32)
        stream = QTextStream(file)
        line = QString()
        sectionName = QString()
        newsection = False
        path = QFileInfo(file).absolutePath()
        base = 10
        gidMapper = GidMapper()
        gid = 1
        tilelayer = 0
        objectgroup = 0
        mapobject = 0
        tilesetsSectionFound = False
        headerSectionFound = False
        tilelayerSectionFound = False; # tile layer or objects
        while (not stream.atEnd()):
            line = stream.readLine()
            if line == '':
                continue
            startsWith = line[0]
            if (startsWith == '['):
                sectionName = line[1:line.index(']')]
                newsection = True
                continue
            
            if (sectionName == "header"):
                headerSectionFound = True
                #get map properties
                epos = line.index('=')
                if (epos != -1):
                    key = line[:epos].strip()
                    value = line[epos + 1:].strip()
                    if (key == "width"):
                        map.setWidth(Int(value))
                    elif (key == "height"):
                        map.setHeight(Int(value))
                    elif (key == "tilewidth"):
                        map.setTileWidth(Int(value))
                    elif (key == "tileheight"):
                        map.setTileHeight(Int(value))
                    elif (key == "orientation"):
                        map.setOrientation(orientationFromString(value))
                    else:
                        map.setProperty(key, value)
                
            elif (sectionName == "tilesets"):
                tilesetsSectionFound = True
                epos = line.index('=')
                key = line[:epos].strip()
                value = line[epos + 1:].strip()
                if (key == "tileset"):
                    _list = value.split(',')
                    absoluteSource = _list[0]
                    if (QDir.isRelativePath(absoluteSource)):
                        absoluteSource = path + '/' + absoluteSource
                    tilesetwidth = 0
                    tilesetheight = 0
                    if len(_list) > 2:
                        tilesetwidth = Int(_list[1])
                        tilesetheight = Int(_list[2])
                    
                    tileset = Tileset(QFileInfo(absoluteSource).fileName(), tilesetwidth, tilesetheight)
                    ok = tileset.loadFromImage(absoluteSource)
                    if not ok:
                        self.mError = self.tr("Error loading tileset %s, which expands to %s. Path not found!"%(_list[0], absoluteSource))
                        del map
                        return 0
                    else :
                        if len(_list) > 4:
                            tileset.setTileOffset(QPoint(Int(_list[3]),Int(_list[4])))
                        gidMapper.insert(gid, tileset)
                        if len(_list) > 5:
                            gid += Int(_list[5])
                        else :
                            gid += tileset.tileCount()
                        
                        map.addTileset(tileset)

            elif (sectionName == "layer"):
                if (not tilesetsSectionFound):
                    self.mError = self.tr("No tilesets section found before layer section.")
                    #del map
                    return 0
                
                tilelayerSectionFound = True
                epos = line.index('=')
                if (epos != -1):
                    key = line[:epos].strip()
                    value = line[epos + 1:].strip()
                    if (key == "type"):
                        tilelayer = TileLayer(value, 0, 0, map.width(),map.height())
                        map.addLayer(tilelayer)
                    elif (key == "format"):
                        if (value == "dec"):
                            base = 10
                        elif (value == "hex"):
                            base = 16
                        
                    elif (key == "data"):
                        for y in range(map.height()):
                            line = stream.readLine()
                            l = line.split(',')
                            for x in range(min(map.width(), len(l))):
                                ok = False
                                tileid = int(l[x], base)
                                c, ok = gidMapper.gidToCell(tileid)
                                if (not ok):
                                    self.mError += self.tr("Error mapping tile id %1.").arg(tileid)
                                    #del map
                                    return 0
                                
                                tilelayer.setCell(x, y, c)

                    else :
                        tilelayer.setProperty(key, value)

            else :
                if (newsection):
                    if (map.indexOfLayer(sectionName) == -1):
                        objectgroup = ObjectGroup(sectionName, 0,0,map.width(), map.height())
                        map.addLayer(objectgroup)
                    else :
                        objectgroup = map.layerAt(map.indexOfLayer(sectionName))
                    
                    mapobject = MapObject()
                    objectgroup.addObject(mapobject)
                    newsection = False
                
                if (not mapobject):
                    continue
                if (startsWith == '#'):
                    name = line[1].strip()
                    mapobject.setName(name)
                
                epos = line.index('=')
                if (epos != -1):
                    key = line[:epos].strip()
                    value = line[epos + 1:].strip()
                    if (key == "type"):
                        mapobject.setType(value)
                    elif (key == "location"):
                        loc = value.split(',')
                        x,y = 0.0, 0.0
                        w,h = 0, 0
                        if (map.orientation() == Map.Orthogonal):
                            x = loc[0].toFloat()*map.tileWidth()
                            y = loc[1].toFloat()*map.tileHeight()
                            if len(loc) > 3:
                                w = Int(loc[2])*map.tileWidth()
                                h = Int(loc[3])*map.tileHeight()
                            else :
                                w = map.tileWidth()
                                h = map.tileHeight()
                            
                        else :
                            x = loc[0].toFloat()*map.tileHeight()
                            y = loc[1].toFloat()*map.tileHeight()
                            if len(loc) > 3:
                                w = Int(loc[2])*map.tileHeight()
                                h = Int(loc[3])*map.tileHeight()
                            else :
                                w = h = map.tileHeight()

                        mapobject.setPosition(QPointF(x, y))
                        mapobject.setSize(w, h)
                    else :
                        mapobject.setProperty(key, value)


        if (not headerSectionFound or not tilesetsSectionFound or not tilelayerSectionFound):
            self.mError = self.tr("This seems to be no valid flare map. "
                        "A Flare map consists of at least a header "
                        "section, a tileset section and one tile layer.")
            #del map
            return 0
        
        return map
    def supportsFile(self, fileName):
        return QFileInfo(fileName).suffix() == "txt"
    
    # MapWriterInterface
    def write(self, map, fileName):
        file = QFile(fileName)
        if (not file.open(QFile.WriteOnly | QFile.Text)):
            self.mError = self.tr("Could not open file for writing.")
            return False
        
        out = QTextStream(file)
        out.setCodec("UTF-8")
        mapWidth = map.width()
        mapHeight = map.height()
        # write [header]
        out << "[header]\n"
        out << "width=" << str(mapWidth) << "\n"
        out << "height=" << str(mapHeight) << "\n"
        out << "tilewidth=" << str(map.tileWidth()) << "\n"
        out << "tileheight=" << str(map.tileHeight()) << "\n"
        out << "orientation=" << str(orientationToString(map.orientation())) << "\n"
        # write all properties for this map
        for it in map.properties().__iter__():
            out << it[0] << "=" << it[1] << "\n"
        
        out << "\n"
        mapDir = QFileInfo(fileName).absoluteDir()
        out << "[tilesets]\n"
        for ts in map.tilesets():
            imageSource = ts.imageSource()
            source = mapDir.relativeFilePath(imageSource)
            out << "tileset=" << source \
                << "," << str(ts.tileWidth()) \
                << "," << str(ts.tileHeight()) \
                << "," << str(ts.tileOffset().x()) \
                << "," << str(ts.tileOffset().y()) \
                << "\n"
        
        out << "\n"
        gidMapper = GidMapper(map.tilesets())
        # write layers
        for layer in map.layers():
            tileLayer = layer.asTileLayer()
            if tileLayer:
                out << "[layer]\n"
                out << "type=" << layer.name() << "\n"
                out << "data=\n"
                for y in range(0, mapHeight):
                    for x in range(0, mapWidth):
                        t = tileLayer.cellAt(x, y)
                        id = 0
                        if (t.tile):
                            id = gidMapper.cellToGid(t)
                        out << id
                        if (x < mapWidth - 1):
                            out << ","
                    
                    if (y < mapHeight - 1):
                        out << ","
                    out << "\n"
                
                out << "\n"
            
            group = layer.asObjectGroup()
            if group:
                for o in group.objects():
                    if ((not o.type().isEmpty())):
                        out << "[" << group.name() << "]\n"
                        # display object name as comment
                        if o.name() != '':
                            out << "# " << o.name() << "\n"
                        
                        out << "type=" << o.type() << "\n"
                        x,y,w,h = 0
                        if (map.orientation() == Map.Orthogonal):
                            x = o.x()/map.tileWidth()
                            y = o.y()/map.tileHeight()
                            w = o.width()/map.tileWidth()
                            h = o.height()/map.tileHeight()
                        else :
                            x = o.x()/map.tileHeight()
                            y = o.y()/map.tileHeight()
                            w = o.width()/map.tileHeight()
                            h = o.height()/map.tileHeight()
                        
                        out << "location=" << x << "," << y
                        out << "," << w << "," << h << "\n"
                        # write all properties for this object
                        for it in o.properties().__iter__():
                            out << it[0] << "=" << it[1] << "\n"
                        
                        out << "\n"


        file.close()
        return True
    
    def nameFilter(self):
        return self.tr("Flare map files (*.txt)")
    
    def errorString(self):
        return self.mError
