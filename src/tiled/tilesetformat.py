##
# tilesetformat.cpp
# Copyright 2015, Thorbj?rn Lindeijer <bjorn@lindeijer.nl>
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
import mapreader
from mapformat import FileFormat

def readTileset(fileName):
    error = ''
    # Try the first registered tileset format that claims to support the file
    for format in PluginManager.objects():
        if format.supportsFile(fileName):
            tileset = format.read(fileName)
            if (error):
                if (not tileset):
                   error = format.errorString()
                else:
                   error = ''
            
            return tileset, error

    # Fall back to default reader (TSX format)
    reader = mapreader.MapReader()
    tileset = reader.readTileset(fileName)
    if (error):
        if (not tileset):
           error = reader.errorString()
        else:
           error = ''
    
    return tileset, error

##
# An interface to be implemented for adding support for a tileset format to
# Tiled. It can implement support for either loading or saving to a certain
# tileset format, or both.
##
class TilesetFormat(FileFormat):

    def __init__(self, parent = None):
        super().__init__(parent)

    ##
    # Reads the tileset and returns a new Tileset instance, or a null shared
    # pointer if reading failed.
    ##
    def read(self, fileName):
        pass
    ##
    # Writes the given \a tileset based on the suggested \a fileName.
    #
    # This function may write to a different file name or may even write to
    # multiple files. The actual files that will be written to can be
    # determined by calling outputFiles().
    #
    # @return <code>true</code> on success, <code>false</code> when an error
    #         occurred. The error can be retrieved by errorString().
    ##
    def write(self, tileset, fileName):
        pass
