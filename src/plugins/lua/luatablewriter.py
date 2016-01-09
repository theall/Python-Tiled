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

from PyQt5.QtCore import (
    QByteArray
)
##
# Makes it easy to produce a well formatted Lua table.
##
class LuaTableWriter():
    def __init__(self, device):
        self.m_valueWritten = False
        self.m_valueSeparator = ','
        self.m_device = device
        self.m_suppressNewlines = False
        self.m_indent = 0
        self.m_error = False
        self.m_newLine = True

    def writeStartDocument(self):
        pass
        
    def writeEndDocument(self):
        self.write('\n')
    
    def writeStartTable(self, *args):
        l = len(args)
        if l==0:
            self.prepareNewLine()
            self.write('{')
            self.m_indent += 1
            self.m_newLine = False
            self.m_valueWritten = False
        elif l==1:
            name = args[0]
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

    def writeEndTable(self):
        self.m_indent -= 1
        if (self.m_valueWritten):
            self.writeNewline()
        self.write('}')
        self.m_newLine = False
        self.m_valueWritten = True
    
    def writeValue(self, value):
        tp = type(value)
        if tp==int:
            self.writeUnquotedValue(QByteArray.number(value))
        elif tp==str:
            self.writeUnquotedValue(self.quote(value).encode())
        elif tp==QByteArray:
            self.prepareNewValue()
            self.write('"')
            self.write(value)
            self.write('"')
            self.m_newLine = False
            self.m_valueWritten = True

    def writeUnquotedValue(self, value):
        self.prepareNewValue()
        self.write(value)
        self.m_newLine = False
        self.m_valueWritten = True

    def writeKeyAndValue(self, key, value):
        tp = type(value)
        if tp==int or tp==float:
            self.writeKeyAndUnquotedValue(key, QByteArray.number(value))
        elif tp==bool:
            if value:
                v = "True"
            else:
                v = "False"
            self.writeKeyAndUnquotedValue(key, v)
        elif tp==str:
            self.writeKeyAndUnquotedValue(key, self.quote(value).encode())

    def writeQuotedKeyAndValue(self, key, value):
        self.prepareNewLine()
        self.write('[')
        self.write(self.quote(key).encode())
        self.write("] = ")
        self.write(self.quote(value).encode())
        self.m_newLine = False
        self.m_valueWritten = True

    def writeKeyAndUnquotedValue(self, key, value):
        self.prepareNewLine()
        self.write(key)
        self.write(" = ")
        self.write(value)
        self.m_newLine = False
        self.m_valueWritten = True

    def write(self, *args):
        l = len(args)
        if l==1:
            arg1 = args[0]
            tp = type(arg1)
            if tp==str or tp==bytes:
                self.write(arg1, len(arg1))
            elif tp==QByteArray:
                self.write(arg1.data(), arg1.length())
        elif l==2:
            _bytes, length = args
            if self.m_device.write(_bytes) != length:
                self.m_error = True

    ##
    # Sets whether newlines should be suppressed. While newlines are suppressed,
    # the writer will write out spaces instead of newlines.
    ##
    def setSuppressNewlines(self, suppressNewlines):
        self.m_suppressNewlines = suppressNewlines
        
    def suppressNewlines(self):
        return self.m_suppressNewlines

    ##
    # Quotes the given string, escaping special characters as necessary.
    ##
    def quote(self, s):

        quoted = "\""
        for i in range(len(s)):
            c = s[i]
            x = c.encode()
            if x=='\\':
                quoted += "\\\\"
                break
            elif x=='"':
                quoted += "\\\""
                break
            elif x=='\n':
                quoted += "\\n"
                break
            else:
                quoted += c

        quoted += '"'
        return quoted

    def prepareNewLine(self):
        if self.m_valueWritten:
            self.write(self.m_valueSeparator)
            self.m_valueWritten = False
        
        self.writeNewline()

    def prepareNewValue(self):
        if (not self.m_valueWritten):
            self.writeNewline()
        else:
            self.write(self.m_valueSeparator)
            self.write(' ')

    def writeIndent(self):
        for level in range(self.m_indent, -1, -1):
            self.write("  ")

    def writeNewline(self):
        if (not  self.m_newLine):
            if ( self.m_suppressNewlines):
                 self.write(' ')
            else:
                 self.write('\n')
                 self.writeIndent()
            self.m_newLine = True
