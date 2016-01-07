##
# mapformat.py
# Copyright 2008-2015, Thorbjørn Lindeijer <bjorn@lindeijer.nl>
# Copyright 2015-2016, Bilge Theall <bilge.theall@gmail.com.cn>
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

from pluginmanager import PluginManager
from pyqtcore import (
    QList,
    QMap,
    QStringList
)
from PyQt5.QtCore import (
    QObject
)   

class FileFormat(QObject):
    NoCapability    = 0x0
    Read            = 0x1
    Write           = 0x2
    ReadWrite       = Read | Write
    
    def __init__(self, parent = None):
        super().__init__(parent)

    ##
    # Returns whether this format has Read and/or Write capabilities.
    ##
    def capabilities(self):
        return FileFormat.ReadWrite
        
    ##
    # Returns whether this format has all given capabilities.
    ##
    def hasCapabilities(self, caps):
        return (self.capabilities() & caps) == caps
    ##
    # Returns the absolute paths for the files that will be written by
    # the map writer.
    ##
    def outputFiles(self, arg1, fileName):
        return QStringList(fileName)
    ##
    # Returns name filter for files in this map format.
    ##
    def nameFilter(self):
        pass
    ##
    # Returns whether this map format supports reading the given file.
    #
    # Generally would do a file extension check.
    ##
    def supportsFile(self, fileName):
        pass
    ##
    # Returns the error to be shown to the user if an error occured while
    # trying to read a map.
    ##
    def errorString(self):
        pass
##
# An interface to be implemented for adding support for a map format to Tiled.
# It can implement support for either loading or saving to a certain map
# format, or both.
##
class MapFormat(FileFormat):

    def __init__(self, parent = None):
        super().__init__(parent)

    ##
    # Reads the map and returns a new Map instance, or 0 if reading failed.
    ##
    def read(self, fileName):
        pass
    ##
    # Writes the given \a map based on the suggested \a fileName.
    #
    # This function may write to a different file name or may even write to
    # multiple files. The actual files that will be written to can be
    # determined by calling outputFiles().
    #
    # @return <code>True</code> on success, <code>False</code> when an error
    #         occurred. The error can be retrieved by errorString().
    ##
    def write(self, map, fileName):
        pass
##
# Convenience class for adding a format that can only be read.
##
class ReadableMapFormat(MapFormat):

    def capabilities(self):
        return FileFormat.Read
        
    def write(self, arg1, arg2):
        return False
        
##
# Convenience class for adding a format that can only be written.
##
class WritableMapFormat(MapFormat):
    
    def capabilities(self):
        return FileFormat.Write
        
    def read(self, arg1):
        return None
        
    def supportsFile(self, arg1):
        return False
        
##
# Convenience class that can be used when implementing file dialogs.
##
class FormatHelper():
    
    def __init__(self, capabilities, initialFilter):       
        self.mFilter = initialFilter
        self.mFormats = QList()
        self.mFormatByNameFilter = QMap()
        
        def t(self, capabilities, format):
            if (format.hasCapabilities(capabilities)):
                nameFilter = format.nameFilter()
                self.mFilter += ";;"
                self.mFilter += nameFilter
                self.mFormats.append(format)
                self.mFormatByNameFilter.insert(nameFilter, format)
        
        PluginManager.each(t)
    
    def filter(self):
        return self.mFilter
        
    def formats(self):
        return self.mFormats
        
    def formatByNameFilter(self, nameFilter):
        return self.mFormatByNameFilter.value(nameFilter)

