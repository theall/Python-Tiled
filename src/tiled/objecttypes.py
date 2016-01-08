##
# objecttypes.py
# Copyright 2011, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from PyQt5.QtCore import (
    Qt,
    QIODevice,
    QXmlStreamWriter,
    QXmlStreamReader,
    QFile,
    QCoreApplication
)
from PyQt5.QtGui import (
    QColor
)
from pyqtcore import QVector, QString
##
# Quick definition of an object type. It has a name and a color.
##
class ObjectType():
    def __init__(self, *args):
        l = len(args)
        if l == 0:
            self.name, self.color = '', QColor(Qt.gray)
        elif l==2:
            self.name, self.color = args

class ObjectTypesWriter():
    def __init__(self):
        self.mError = ''

    def writeObjectTypes(self, fileName, objectTypes):
        self.mError = ''
        file = QFile(fileName)
        if (not file.open(QIODevice.WriteOnly | QIODevice.Text)):
            self.mError = QCoreApplication.translate(
                        "ObjectTypes", "Could not open file for writing.")
            return False

        writer = QXmlStreamWriter(file)
        writer.setAutoFormatting(True)
        writer.setAutoFormattingIndent(1)
        writer.writeStartDocument()
        writer.writeStartElement("objecttypes")
        for objectType in objectTypes:
            writer.writeStartElement("objecttype")
            writer.writeAttribute("name", objectType.name)
            writer.writeAttribute("color", objectType.color.name())
            writer.writeEndElement()

        writer.writeEndElement()
        writer.writeEndDocument()
        if (file.error() != QFile.NoError):
            self.mError = file.errorString()
            return False

        return True

    def errorString(self):
        return self.mError

class ObjectTypesReader():
    def __init__(self):
        self.mError = ''

    def readObjectTypes(self, fileName):
        self.mError = ''
        objectTypes = QVector()
        file = QFile(fileName)
        if (not file.open(QIODevice.ReadOnly | QIODevice.Text)):
            self.mError = QCoreApplication.translate(
                        "ObjectTypes", "Could not open file.")
            return objectTypes

        reader = QXmlStreamReader(file)
        if (not reader.readNextStartElement() or reader.name() != "objecttypes"):
            self.mError = QCoreApplication.translate(
                        "ObjectTypes", "File doesn't contain object types.")
            return objectTypes

        while (reader.readNextStartElement()):
            if (reader.name() == "objecttype"):
                atts = reader.attributes()
                name = QString(atts.value("name"))
                color = QColor(atts.value("color"))
                objectTypes.append(ObjectType(name, color))

            reader.skipCurrentElement()

        if (reader.hasError()):
            self.mError = QCoreApplication.translate("ObjectTypes", "%s\n\nLine %d, column %d"%(reader.errorString(), reader.lineNumber(), reader.columnNumber()))
            return objectTypes

        return objectTypes

    def errorString(self):
        return self.mError
