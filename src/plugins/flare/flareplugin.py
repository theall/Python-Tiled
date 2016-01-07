##
# Flare Tiled Plugin
# Copyright 2015, Bilge Theall <bilge.theall@gmail.com.cn> 
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

from objectgroup import ObjectGroup
from tileset import Tileset
from tilelayer import TileLayer
from mapobject import MapObject
from map import Map, orientationFromString, orientationToString
from gidmapper import GidMapper
from mapreaderinterface import MapReaderInterface
from mapwriterinterface import MapWriterInterface
from pyqtcore import (
    QString
)
from PyQt5.QtCore import (
    QPoint,
    QObject,
    QDir,
    QPointF,
    QFileInfo,
    QTextStream,
    QFile,
    QIODevice
)
class FlarePlugin(QObject, MapWriterInterface, MapReaderInterface):
    def __init__(self):
        self.mError = QString()

    # MapReaderInterface
    def read(self, fileName):
        file = QFile(fileName)
        if (not file.open (QIODevice.ReadOnly)):
            self.mError = self.tr("Could not open file for reading.")
            return 0
        
        # default to values of the original flare alpha game.
        map = Map(Map.Isometric, 256, 256, 64, 32)
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
            if (not line.length()):
                continue
            startsWith = line.at(0)
            if (startsWith == '['):
                sectionName = line.mid(1, line.indexOf(']') - 1)
                newsection = True
                continue
            
            if (sectionName == "header"):
                headerSectionFound = True
                #get map properties
                epos = line.indexOf('=')
                if (epos != -1):
                    key = line.left(epos).trimmed()
                    value = line.mid(epos + 1, -1).trimmed()
                    if (key == "width"):
                        map.setWidth(value.toInt())
                    elif (key == "height"):
                        map.setHeight(value.toInt())
                    elif (key == "tilewidth"):
                        map.setTileWidth(value.toInt())
                    elif (key == "tileheight"):
                        map.setTileHeight(value.toInt())
                    elif (key == "orientation"):
                        map.setOrientation(orientationFromString(value))
                    else:
                        map.setProperty(key, value)
                
            elif (sectionName == "tilesets"):
                tilesetsSectionFound = True
                epos = line.indexOf('=')
                key = line.left(epos).trimmed()
                value = line.mid(epos + 1, -1).trimmed()
                if (key == "tileset"):
                    _list = value.split(',')
                    absoluteSource = QString(_list.first())
                    if (QDir.isRelativePath(absoluteSource)):
                        absoluteSource = path + '/' + absoluteSource
                    tilesetwidth = 0
                    tilesetheight = 0
                    if (_list.size() > 2):
                        tilesetwidth = _list[1].toInt()
                        tilesetheight = _list[2].toInt()
                    
                    tileset = Tileset(QFileInfo(absoluteSource).fileName(), tilesetwidth, tilesetheight)
                    ok = tileset.loadFromImage(absoluteSource)
                    if not ok:
                        self.mError = self.tr("Error loading tileset %s, which expands to %s. Path not found!"%(_list[0], absoluteSource))
                        del map
                        return 0
                    else :
                        if (_list.size() > 4):
                            tileset.setTileOffset(QPoint(_list[3].toInt(),_list[4].toInt()))
                        gidMapper.insert(gid, tileset)
                        if (_list.size() > 5):
                            gid += _list[5].toInt()
                        else :
                            gid += tileset.tileCount()
                        
                        map.addTileset(tileset)

            elif (sectionName == "layer"):
                if (not tilesetsSectionFound):
                    self.mError = self.tr("No tilesets section found before layer section.")
                    #del map
                    return 0
                
                tilelayerSectionFound = True
                epos = line.indexOf('=')
                if (epos != -1):
                    key = line.left(epos).trimmed()
                    value = line.mid(epos + 1, -1).trimmed()
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
                            for x in range(min(map.width(), l.size())):
                                ok = False
                                tileid = l[x].toInt(0, base)
                                c = gidMapper.gidToCell(tileid, ok)
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
                    name = line.mid(1).trimmed()
                    mapobject.setName(name)
                
                epos = line.indexOf('=')
                if (epos != -1):
                    key = line.left(epos).trimmed()
                    value = line.mid(epos + 1, -1).trimmed()
                    if (key == "type"):
                        mapobject.setType(value)
                    elif (key == "location"):
                        loc = value.split(',')
                        x,y = 0.0, 0.0
                        w,h = 0, 0
                        if (map.orientation() == Map.Orthogonal):
                            x = loc[0].toFloat()*map.tileWidth()
                            y = loc[1].toFloat()*map.tileHeight()
                            if (loc.size() > 3):
                                w = loc[2].toInt()*map.tileWidth()
                                h = loc[3].toInt()*map.tileHeight()
                            else :
                                w = map.tileWidth()
                                h = map.tileHeight()
                            
                        else :
                            x = loc[0].toFloat()*map.tileHeight()
                            y = loc[1].toFloat()*map.tileHeight()
                            if (loc.size() > 3):
                                w = loc[2].toInt()*map.tileHeight()
                                h = loc[3].toInt()*map.tileHeight()
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
        out.write("[header]\n")
        out.write("width=%d" + str(mapWidth) + "\n")
        out.write("height=" + str(mapHeight) + "\n")
        out.write("tilewidth=" + str(map.tileWidth()) + "\n")
        out.write("tileheight=" + str(map.tileHeight()) + "\n")
        out.write("orientation=" + str(orientationToString(map.orientation())) + "\n")
        # write all properties for this map
        for it in map.properties().__iter__():
            out.write(it[0] + "=" + it[1] + "\n")
        
        out.write("\n")
        mapDir = QFileInfo(fileName).absoluteDir()
        out.write("[tilesets]\n")
        for ts in map.tilesets():
            imageSource = ts.imageSource()
            source = mapDir.relativeFilePath(imageSource)
            out.write("tileset=" + source
                + "," + str(ts.tileWidth())
                + "," + str(ts.tileHeight())
                + "," + str(ts.tileOffset().x())
                + "," + str(ts.tileOffset().y())
                + "\n")
        
        out.write("\n")
        gidMapper = GidMapper(map.tilesets())
        # write layers
        for layer in map.layers():
            tileLayer = layer.asTileLayer()
            if tileLayer:
                out.write("[layer]\n")
                out.write("type=" + layer.name() + "\n")
                out.write("data=\n")
                for y in range(0, mapHeight):
                    for x in range(0, mapWidth):
                        t = tileLayer.cellAt(x, y)
                        id = 0
                        if (t.tile):
                            id = gidMapper.cellToGid(t)
                        out.write(id)
                        if (x < mapWidth - 1):
                            out.write(",")
                    
                    if (y < mapHeight - 1):
                        out.write(",")
                    out.write("\n")
                
                out.write("\n")
            
            group = layer.asObjectGroup()
            if group:
                for o in group.objects():
                    if ((not o.type().isEmpty())):
                        out.write("[" + group.name() + "]\n")
                        # display object name as comment
                        if o.name() != '':
                            out.write("# " + o.name() + "\n")
                        
                        out.write("type=" + o.type() + "\n")
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
                        
                        out.write("location=" + x + "," + y)
                        out.write("," + w + "," + h + "\n")
                        # write all properties for this object
                        for it in o.properties().__iter__():
                            out.write(it[0] + "=" + it[1] + "\n")
                        
                        out.write("\n")


        file.close()
        return True
    
    def nameFilter(self):
        return self.tr("Flare map files (*.txt)")
    
    def errorString(self):
        return self.mError
