##
# object.py
# Copyright 2010, Thorbjørn Lindeijer
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

from properties import Properties

##
# The base class for anything that can hold properties.
##
class Object():
    LayerType = 0
    MapObjectType = 1
    MapType = 2
    TerrainType = 3
    TilesetType = 4
    TileType = 5
    
    def __init__(self, arg):
        tp = type(arg)
        self.mProperties = Properties()

        if tp==int:
            self.mTypeId = arg
        elif tp==Object:
            self.mTypeId = arg.mTypeId
            self.mProperties = arg.mProperties

    ##
    # Virtual destructor.
    ##
    def __del__(self):
        pass
    ##
    # Returns the type of this object.
    ##
    def typeId(self):
        return self.mTypeId

    ##
    # Returns the properties of this object.
    ##
    def properties(self):
        return self.mProperties

    ##
    # Replaces all existing properties with a new set of properties.
    ##
    def setProperties(self, properties):
        self.mProperties = properties
    ##
    # Merges \a properties with the existing properties. Properties with the
    # same name will be overridden.
    #
    # \sa Properties.merge
    ##
    def mergeProperties(self, properties):
        self.mProperties.merge(properties)
    ##
    # Returns the value of the object's \a name property.
    ##
    def property(self, name):
        return self.mProperties.value(name,'')
    ##
    # Returns whether this object has a property with the given \a name.
    ##
    def hasProperty(self, name):
        return self.mProperties.contains(name)
    ##
    # Sets the value of the object's \a name property to \a value.
    ##
    def setProperty(self, name, value):
        self.mProperties.insert(name, value)
    ##
    # Removes the property with the given \a name.
    ##
    def removeProperty(self, name):
        self.mProperties.remove(name)

