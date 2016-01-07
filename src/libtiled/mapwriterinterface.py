##
# mapwriterinterface.py
# Copyright 2008-2010, Thorbjørn Lindeijer
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

from pyqtcore import (
    QString,
    QStringList
)
##*
# An interface to be implemented by map writers. A map writer implements
# support for saving to a certain map format.
#
# Tiled provides a writer for its own .tmx map format through the
# TmxMapWriter. Other writers can be provided by plugins.
##
class MapWriterInterface():

    def __del__(self):
        pass
    ##*
    # Writes the given map to the given file name.
    #
    # @return <code>true</code> on success, <code>false when an error
    #         occurred. The error can be retrieved by self.errorString().
    ##
    def write(self, map, fileName):
        pass
    ##*
    # Returns name filters of this map writer, for multiple formats.
    ##
    def nameFilters(self):
        return QStringList(self.nameFilter())

    ##*
    # Returns the error to be shown to the user if an error occured while
    # trying to write a map.
    ##
    def errorString(self):
        pass

    ##*
    # Returns the name filter of this map writer.
    #
    # Protected because it should not be used outside the plugin since
    # plugins may expose multiple name filters. This thing exists only for
    # convenience for plugin writers since most plugins will have only one
    # name filter.
    ##
    def nameFilter(self):
        return QString()
