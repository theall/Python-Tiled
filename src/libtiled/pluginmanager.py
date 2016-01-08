##
# pluginmanager.py
# Copyright 2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from PyQt5.QtCore import (
    QObject, 
    pyqtSignal
)
from pyqtcore import QList

##
# A loaded plugin.
##
class LoadedPlugin():
    def __init__(self, fileName, instance):
        self.fileName = fileName
        self.instance = instance

##
# The plugin manager loads the plugins and provides ways to access them.
##
class PluginManager(QObject):
    mInstance = None
    objectAdded = pyqtSignal(list)
    objectAboutToBeRemoved = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        
        self.mObjects = QList()
        self.mPlugins = QList()
        self.fileName = ''
        
    def __del__(self):
        pass

    ##
    # Returns the plugin manager instance.
    ##
    def instance():
        if (not PluginManager.mInstance):
            PluginManager.mInstance = PluginManager()
        return PluginManager.mInstance

    def deleteInstance():
        del PluginManager.mInstance
        PluginManager.mInstance = None

    ##
    # Adds the given \a object. This allows the object to be found later based
    # on the interfaces it implements.
    ##
    def addObject(self, object):
        PluginManager.mInstance.mObjects.append(object)
        PluginManager.mInstance.objectAdded.emit([object])
       
    ##
    # Removes the given \a object.
    ##
    def removeObject(self, object):
        PluginManager.mInstance.objectAboutToBeRemoved.emit([object])
        PluginManager.mInstance.mObjects.removeOne(object)

    ##
    # Returns the list of objects that implement a given interface.
    ##
    def objects(_type):
        results = QList()
        for object in PluginManager.mInstance.mObjects:
            if type(object) == _type:
                results.append(object)
        return results

    ##
    # Scans the plugin directory for plugins and attempts to load them.
    ##
    def loadPlugins(self):
        from plugins.csv.csvplugin import CsvPlugin
        from plugins.droidcraft.droidcraftplugin import DroidcraftPlugin
        from plugins.flare.flareplugin import FlarePlugin
        from plugins.json.jsonplugin import JsonPlugin
        from plugins.lua.luaplugin import LuaPlugin
        from plugins.replicaisland.replicaislandplugin import ReplicaIslandPlugin
        from plugins.tengine.tengineplugin import TenginePlugin
        from plugins.tmw.tmwplugin import TmwPlugin
        
        static_plugins = [
            {'name':'CsvPlugin', 'instance':CsvPlugin},
            {'name':'DroidcraftPlugin', 'instance':DroidcraftPlugin},
            {'name':'FlarePlugin', 'instance':FlarePlugin},
            {'name':'JsonPlugin', 'instance':JsonPlugin},
            {'name':'LuaPlugin', 'instance':LuaPlugin},
            {'name':'ReplicaIslandPlugin', 'instance':ReplicaIslandPlugin},
            {'name':'TenginePlugin', 'instance':TenginePlugin},
            {'name':'TmwPlugin', 'instance':TmwPlugin}
        ]
        
        # Load static plugins
        for plugin in static_plugins:
            name = plugin['name']
            instance = plugin['instance']
            self.mPlugins.append(LoadedPlugin(name, instance))
            if hasattr(instance, 'initialize'):
                instance().initialize()
            else:
                self.addObject(instance())

    ##
    # Returns the list of plugins found by the plugin manager.
    ##
    def plugins(self):
        return QList(self.fileName)

    ##
    # Returns the list of plugins that implement a given interface.
    ##
    def interfaces(self):
        results = QList()
        for plugin in self.mPlugins:
            result = plugin.instance
            if result:
                results.append(result)
        return results

    ##
    # Calls the given function for each object implementing a given interface.
    ##
    def each(helper, function):
        for object in PluginManager.mInstance.mObjects:
            if object:
                function(helper, object)
    
    def pluginByFileName(self, pluginFileName):
        for plugin in self.mPlugins:
            if (pluginFileName == plugin.fileName):
                return plugin
        return None

    ##
    # Returns the plugin, which implements the given interface.
    # This must be done via searching the plugins for the right plugins,
    # since casting doesn't work, an interface is not a plugin.
    ##
    def plugin(self, interface):
        for plugin in self.mPlugins:
            result = plugin.instance
            if result:
                if (result == interface):
                    return plugin
        return None
