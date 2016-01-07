##
# Lua Tiled Plugin
# Copyright 2011-2013, Thorbj?rn Lindeijer <thorbjorn@lindeijer.nl>
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
    QChar,
    QuotedKeyAndValue,
    QString,
    Quotes,
    QLatin
)
from PyQt5.QtCore import (
    QByteArray,
    QIODevice
)
##
# Makes it easy to produce a well formatted Lua table.
##
class LuaTableWriter():

    def __init__(self, device):
        super().__init__.m_device(device)
        self.m_indent(0)
        self.m_valueSeparator(',')
        self.m_suppressNewlines(False)
        self.m_newLine(True)
        self.m_valueWritten(False)
        self.m_error(False)

        self.m_valueWritten = False
        self.m_valueSeparator = char()
        self.m_device = None
        self.m_suppressNewlines = False
        self.m_indent = 0
        self.m_error = False
        self.m_newLine = False

    def writeStartDocument(self):
        pass
        
    def writeEndDocument(self):
        self.write('\n')
    
    def writeStartTable(self):
        self.prepareNewLine()
        self.write('{')
        self.m_indent += 1
        self.m_newLine = False
        self.m_valueWritten = False

        self.prepareNewLine()
        self.write(name + " = {")
        self.m_indent += 1
        self.m_newLine = False
        self.m_valueWritten = False
    
    def writeStartReturnTable(self):
        self.prepareNewLine()
        self.write("return {")
        self.m_indent += 1
        self.m_newLine = False
        self.m_valueWritten = False
    
    def writeStartTable(self, name):
        self.prepareNewLine()
        self.write('{')
        self.m_indent += 1
        self.m_newLine = False
        self.m_valueWritten = False

        self.prepareNewLine()
        self.write(name + " = {")
        self.m_indent += 1
        self.m_newLine = False
        self.m_valueWritten = False

    def writeEndTable(self):
        self.m_indent -= 1
        if (self.m_valueWritten):
            self.writeNewline()
        self.write('}')
        self.m_newLine = False
        self.m_valueWritten = True
    
    def writeValue(self, value):
        self.writeUnquotedValue(QByteArray.number(value))
    def writeValue(self, value):
        self.writeUnquotedValue(QByteArray.number(value))
    def writeValue(self,value):
        self.writeUnquotedValue(quote(value).toUtf8())
    def writeKeyAndValue(self, key, value):
        self.writeKeyAndUnquotedValue(key, QByteArray.number(value))
    def writeKeyAndValue(self, key, value):
        self.writeKeyAndUnquotedValue(key, QByteArray.number(value))
    def writeKeyAndValue(self, key, value):
        self.writeKeyAndUnquotedValue(key, QByteArray.number(value))
    def writeKeyAndValue(self, key, value):
        if value:
            v = "True"
        else:
            v = "False"
        self.writeKeyAndUnquotedValue(key, v)
        
    def writeKeyAndValue(self, key, value):
        self.writeKeyAndUnquotedValue(key, self.quote(value).toUtf8())
    def write(self, bytes):
        self.write(bytes, qstrlen(bytes))
    def write(self, bytes):
        self.write(bytes.constData(), bytes.length())
    def write(self, c):
        self.write(c, 1)

    ##
    # Sets whether newlines should be suppressed. While newlines are suppressed,
    # the writer will write out spaces instead of newlines.
    ##
    def setSuppressNewlines(self, suppressNewlines):
        self.m_suppressNewlines = suppressNewlines
        
    def suppressNewlines(self):
        return self.m_suppressNewlines

    def writeValue(self, value):
        self.prepareNewValue()
        self.write('"')
        self.write(value)
        self.write('"')
        self.m_newLine = False
        self.m_valueWritten = True
    
    def writeValue(self, value):
        self.writeUnquotedValue(QByteArray.number(value))
        
    def writeValue(self, value):
        self.writeUnquotedValue(QByteArray.number(value))
    def writeValue(self, value):
        self.writeUnquotedValue(quote(value).toUtf8())
    def writeKeyAndValue(self, key, value):
        self.writeKeyAndUnquotedValue(key, QByteArray.number(value))
    def writeKeyAndValue(self, key, value):
        self.writeKeyAndUnquotedValue(key, QByteArray.number(value))
    def writeKeyAndValue(self, key, value):
        self.writeKeyAndUnquotedValue(key, QByteArray.number(value))
    def writeKeyAndValue(self, key, value):
        if value:
            v = "True"
        else:
            v = "False"
        self.writeKeyAndUnquotedValue(key, v)
        
    def writeKeyAndValue(self, key, value):
        self.writeKeyAndUnquotedValue(key, self.quote(value).toUtf8())
    def write(self, bytes):
        self.write(bytes, qstrlen(bytes))
    def write(self, bytes):
        self.write(bytes.constData(), bytes.length())
    def write(self, c):
        self.write(c, 1)
