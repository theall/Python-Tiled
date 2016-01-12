##
# convertercontrol.py
# Copyright 2012, Stefan Beller, stefanbeller@googlemail.com
#
# This file is part of the AutomappingConverter, which converts old rulemaps
# of Tiled to work with the latest version of Tiled.
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

from mapreader import MapReader
from mapwriter import MapWriter
from pyqtcore import QString
from PyQt5.QtCore import (
    qWarning, 
    QCoreApplication
)
class ConverterControl():

    def __init__(self):
        pass
        
    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('MapReader', sourceText, disambiguation, n)
        
    def version1(self):
        return self.tr("v0.8 and before")

    def version2(self):
        return self.tr("v0.9 and later")

    def versionUnknown(self):
        return self.tr("unknown")

    def versionNotAMap(self):
        return self.tr("not a map")

    def automappingRuleFileVersion(self, fileName):
        reader = MapReader()
        map = reader.readMap(fileName)
        if (not map):
            return self.versionNotAMap()
        # version 1 check
        hasonlyruleprefix = True
        for layer in map.layers():
            if (not layer.name().lower().startswith("rule")):
                hasonlyruleprefix = False

        if (hasonlyruleprefix):
            return self.version1()
        # version 2 check
        hasrule = False
        hasoutput = False
        hasregion = False
        allused = True
        for layer in map.layers():
            isunused = True
            if (layer.name().lower().startswith("input")):
                hasrule = True
                isunused = False

            if (layer.name().lower().startswith("output")):
                hasoutput = True
                isunused = False

            if (layer.name().lower() == "regions"):
                hasregion = True
                isunused = False

            if (isunused):
                allused = False

        if (allused and hasoutput and hasregion and hasrule):
            return self.version2()
        return self.versionUnknown()

    def convertV1toV2(self, fileName):
        reader = MapReader()
        map = reader.readMap(fileName)
        if (not map):
            qWarning("Error at conversion of "+fileName+":\n"+reader.errorString())
            return

        for layer in map.layers():
            if (layer.name().lower().startswith("ruleset")):
                layer.setName("Input_set")
            elif (layer.name().lower().startswith("rulenotset")):
                layer.setName("InputNot_set")
            elif (layer.name().lower().startswith("ruleregions")):
                layer.setName("Regions")
            elif (layer.name().lower().startswith("rule")):
                newname = layer.name().right(layer.name().length() - 4)
                layer.setName("Output" + newname)
            else:
                qWarning(QString("Warning at conversion of")+fileName+QString("unused layers found"))

        writer = MapWriter()
        writer.writeMap(map.data(), fileName)
        map.tilesets().clear()
