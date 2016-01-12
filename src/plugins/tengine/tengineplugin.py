##
# The T-Engine 4 Tiled Plugin
# Copyright 2010, Mikolai Fajer <mfajer@gmail.com>
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

import math
from properties import Properties
from mapformat import WritableMapFormat
from pyqtcore import (
    QList,
    QString,
    QMap,
    QHash
)
from PyQt5.QtCore import (
    QSaveFile,
    Qt,
    QIODevice,
    QTextStream
)
# ASCII characters between decimals 32 and 126 should be ok
ASCII_MIN = 32
ASCII_MAX = 126

class TenginePlugin(WritableMapFormat):
    def __init__(self):
        super().__init__()
        
        self.mError = ''

    # MapWriterInterface
    def write(self, map, fileName):
        file = QSaveFile(fileName)
        if (not file.open(QIODevice.WriteOnly | QIODevice.Text)) :
            self.mError = self.tr("Could not open file for writing.")
            return False
        
        out = QTextStream(file)
        # Write the header
        header = map.property("header")
        for line in header.split("\\n"):
            out << line << '\n'
        
        width = map.width()
        height = map.height()
        asciiMap = QList()
        cachedTiles = QHash()
        propertyOrder = QList()
        propertyOrder.append("terrain")
        propertyOrder.append("object")
        propertyOrder.append("actor")
        propertyOrder.append("trap")
        propertyOrder.append("status")
        propertyOrder.append("spot")
        # Ability to handle overflow and strings for display
        outputLists = False
        asciiDisplay = ASCII_MIN
        overflowDisplay = 1
        # Add the empty tile
        numEmptyTiles = 0
        emptyTile = Properties()
        emptyTile["display"] = "?"
        cachedTiles["?"] = emptyTile
        # Process the map, collecting used display strings as we go
        for y in range(0, height):
            for x in range(0, width):
                currentTile = cachedTiles["?"]
                for layer in map.layers():
                    # If the layer name does not start with one of the tile properties, skip it
                    layerKey = ''
                    for currentProperty in propertyOrder:
                        if (layer.name().lower().startswith(currentProperty.lower())) :
                            layerKey = currentProperty
                            break

                    if layerKey == '':
                        continue
                    
                    tileLayer = layer.asTileLayer()
                    objectLayer = layer.asObjectGroup()
                    # Process the Tile Layer
                    if (tileLayer) :
                        tile = tileLayer.cellAt(x, y).tile
                        if (tile) :
                            currentTile["display"] = tile.property("display")
                            currentTile[layerKey] = tile.property("value")
                        
                    # Process the Object Layer
                    elif (objectLayer) :
                        for obj in objectLayer.objects():
                            if (math.floor(obj.y()) <= y and y <= math.floor(obj.y() + obj.height())) :
                                if (math.floor(obj.x()) <= x and x <= math.floor(obj.x() + obj.width())) :
                                    # Check the Object Layer properties if either display or value was missing
                                    if (not obj.property("display").isEmpty()) :
                                        currentTile["display"] = obj.property("display")
                                    elif (not objectLayer.property("display").isEmpty()) :
                                        currentTile["display"] = objectLayer.property("display")
                                    
                                    if (not obj.property("value").isEmpty()) :
                                        currentTile[layerKey] = obj.property("value")
                                    elif (not objectLayer.property("value").isEmpty()) :
                                        currentTile[layerKey] = objectLayer.property("value")



                # If the currentTile does not exist in the cache, add it
                if (not cachedTiles.contains(currentTile["display"])) :
                    cachedTiles[currentTile["display"]] = currentTile
                # Otherwise check that it EXACTLY matches the cached one
                # and if not...
                elif (currentTile != cachedTiles[currentTile["display"]]) :
                    # Search the cached tiles for a match
                    foundInCache = False
                    displayString = QString()
                    for i in cachedTiles.items():
                        displayString = i[0]
                        currentTile["display"] = displayString
                        if (currentTile == i[1]) :
                            foundInCache = True
                            break

                    # If we haven't found a match then find a random display string
                    # and cache it
                    if (not foundInCache) :
                        while (True) :
                            # First try to use the ASCII characters
                            if (asciiDisplay < ASCII_MAX) :
                                displayString = asciiDisplay
                                asciiDisplay += 1
                            # Then fall back onto integers
                            else :
                                displayString = QString.number(overflowDisplay)
                                overflowDisplay += 1
                            
                            currentTile["display"] = displayString
                            if (not cachedTiles.contains(displayString)) :
                                cachedTiles[displayString] = currentTile
                                break
                            elif (currentTile == cachedTiles[currentTile["display"]]) :
                                break


                # Check the output type
                if len(currentTile["display"]) > 1:
                    outputLists = True
                
                # Check if we are still the emptyTile
                if (currentTile == emptyTile) :
                    numEmptyTiles += 1
                
                # Finally add the character to the asciiMap
                asciiMap.append(currentTile["display"])

        # Write the definitions to the file
        out << "-- defineTile section\n"
        for i in cachedTiles.items():
            displayString = i[0]
            # Only print the emptyTile definition if there were empty tiles
            if (displayString == "?" and numEmptyTiles == 0) :
                continue
            
            # Need to escape " and \ characters
            displayString.replace('\\', "\\\\")
            displayString.replace('"', "\\\"")
            args = self.constructArgs(i[1], propertyOrder)
            if (not args.isEmpty()) :
                args = QString(", %1").arg(args)
            
            out << "defineTile(\"%s\"%s)\n"%(displayString, args)
        
        # Check for an ObjectGroup named AddSpot
        out << "\n-- addSpot section\n"
        for layer in map.layers():
            objectLayer = layer.asObjectGroup()
            if (objectLayer and objectLayer.name().lower().startsWith("addspot")):
                for obj in objectLayer.objects():
                    propertyOrder = QList()
                    propertyOrder.append("type")
                    propertyOrder.append("subtype")
                    propertyOrder.append("additional")
                    args = self.constructArgs(obj.properties(), propertyOrder)
                    if (not args.isEmpty()) :
                        args = QString(", %1").arg(args)
                    
                    for y in range(math.floor(obj.y()), math.floor(obj.y() + obj.height())):
                        for y in range(math.floor(obj.x()), math.floor(obj.x() + obj.width())):
                            out << "addSpot({%s, %s}%s)\n"%(x, y, args)
        
        # Check for an ObjectGroup named AddZone
        out << "\n-- addZone section\n"
        for layer in map.layers():
            objectLayer = layer.asObjectGroup()
            if (objectLayer and objectLayer.name().lower().startsWith("addzone")):
                for obj in objectLayer.objects():
                    propertyOrder = QList()
                    propertyOrder.append("type")
                    propertyOrder.append("subtype")
                    propertyOrder.append("additional")
                    args = self.constructArgs(obj.properties(), propertyOrder)
                    if (not args.isEmpty()) :
                        args = QString(", %1").arg(args)
                    
                    top_left_x = math.floor(obj.x())
                    top_left_y = math.floor(obj.y())
                    bottom_right_x = math.floor(obj.x() + obj.width())
                    bottom_right_y = math.floor(obj.y() + obj.height())
                    out << "addZone({%s, %s, %s, %s}%s)"%(top_left_x, top_left_y, bottom_right_x, bottom_right_y, args)

        
        # Write the map
        returnStart = QString()
        returnStop = QString()
        lineStart = QString()
        lineStop = QString()
        itemStart = QString()
        itemStop = QString()
        seperator = QString()
        if (outputLists) :
            returnStart = "{"
            returnStop = "}"
            lineStart = "{"
            lineStop = "},"
            itemStart = "[["
            itemStop = "]]"
            seperator = ","
        else :
            returnStart = "[["
            returnStop = "]]"
            lineStart = ""
            lineStop = ""
            itemStart = ""
            itemStop = ""
            seperator = ""
        
        out << "\n-- ASCII map section\n"
        out << "return " << returnStart << '\n'
        for y in range(0, height):
            out << lineStart
            for x in range(0, width):
                out << itemStart << asciiMap[x + (y * width)] << itemStop << seperator
            
            if (y == height - 1):
                out << lineStop << returnStop
            else :
                out << lineStop << '\n'

        if not file.commit():
            self.mError = file.errorString()
            return False

        return True
    
    def nameFilter(self):
        return self.tr("T-Engine4 map files (*.lua)")
    
    def errorString(self):
        return self.mError


    def constructArgs(self, props, propOrder):
        argString = QString()
        # We work backwards so we don't have to include a bunch of nils
        for i in range(propOrder.size() - 1, -1, -1):
            currentValue = props.get(propOrder[i], '')
            # Special handling of the "additional" property
            if ((propOrder[i] == "additional") and currentValue.isEmpty()) :
                currentValue = self.constructAdditionalTable(props, propOrder)
            
            if (not argString.isEmpty()) :
                if (currentValue.isEmpty()) :
                    currentValue = "nil"
                
                argString = "%s, %s"%(currentValue, argString)
            elif currentValue != '':
                argString = currentValue

        return argString
    
    # Finds unhandled properties and bundles them into a Lua table
    def constructAdditionalTable(self, props, propOrder):
        tableString = QString()
        unhandledProps = QMap(props)
        # Remove handled properties
        for i in range(0, propOrder.size()):
            unhandledProps.remove(propOrder[i])
        
        # Construct the Lua string
        if (unhandledProps.size() > 0) :
            tableString = "{"
            for i in unhandledProps:
                tableString = "%s%s=%s,"%tableString, i[0], i[1]
            
            tableString = "%s}"%tableString
        
        return tableString
