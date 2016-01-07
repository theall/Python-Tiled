##
# tilesetmanager.py
# Copyright 2008-2014, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2009, Edward Hutchins
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

from tileset import Tileset
from tileanimationdriver import TileAnimationDriver
from filesystemwatcher import FileSystemWatcher
from PyQt5.QtCore import (
    QTimer,
    QObject,
    pyqtSignal,
    QAbstractAnimation
)
from pyqtcore import QString, QMap, QSet

##
# A tileset specification that uniquely identifies a certain tileset. Does not
# take into account tile properties!
##
class TilesetSpec():
    def __init__(self):
        self.imageSource = QString()
        self.tileWidth = 0
        self.tileHeight = 0
        self.tileSpacing = 0
        self.margin = 0

##
# The tileset manager keeps track of all tilesets used by loaded maps. It also
# watches the tileset images for changes and will attempt to reload them when
# they change.
##
class TilesetManager(QObject):
    mInstance = None
    ##
    # Emitted when a tileset's images have changed and views need updating.
    ##
    tilesetChanged = pyqtSignal(Tileset)
    ##
    # Emitted when any images of the tiles in the given \a tileset have
    # changed. This is used to trigger repaints for displaying tile
    # animations.
    ##
    repaintTileset = pyqtSignal(Tileset)

    ##
    # Constructor. Only used by the tileset manager it
    ##
    def __init__(self):
        super().__init__()

        ##
        # Stores the tilesets and maps them to the number of references.
        ##
        self.mTilesets = QMap()
        self.mChangedFiles = QSet()
        self.mWatcher = FileSystemWatcher(self)
        self.mAnimationDriver = TileAnimationDriver(self)
        self.mReloadTilesetsOnChange = False
        self.mChangedFilesTimer = QTimer()

        self.mWatcher.fileChanged.connect(self.fileChanged)
        self.mChangedFilesTimer.setInterval(500)
        self.mChangedFilesTimer.setSingleShot(True)
        self.mChangedFilesTimer.timeout.connect(self.fileChangedTimeout)
        self.mAnimationDriver.update.connect(self.advanceTileAnimations)

    ##
    # Destructor.
    ##
    def __del__(self):
        # Since all MapDocuments should be deleted first, we assert that there are
        # no remaining tileset references.
        self.mTilesets.size() == 0

    ##
    # Requests the tileset manager. When the manager doesn't exist yet, it
    # will be created.
    ##
    def instance():
        if (not TilesetManager.mInstance):
            TilesetManager.mInstance = TilesetManager()
        return TilesetManager.mInstance

    ##
    # Deletes the tileset manager instance, when it exists.
    ##
    def deleteInstance():
        del TilesetManager.mInstance
        TilesetManager.mInstance = None

    def findTileset(self, arg):
        tp = type(arg)
        if tp in [QString, str]:
            ##
            # Searches for a tileset matching the given file name.
            # @return a tileset matching the given file name, or 0 if none exists
            ##
            fileName = arg
            for tileset in self.tilesets():
                if (tileset.fileName() == fileName):
                    return tileset
            return None
        elif tp==TilesetSpec:
            ##
            # Searches for a tileset matching the given specification.
            # @return a tileset matching the given specification, or 0 if none exists
            ##
            spec = arg
            for tileset in self.tilesets():
                if (tileset.imageSource() == spec.imageSource
                    and tileset.tileWidth() == spec.tileWidth
                    and tileset.tileHeight() == spec.tileHeight
                    and tileset.tileSpacing() == spec.tileSpacing
                    and tileset.margin() == spec.margin):

                    return tileset

            return None

    ##
    # Adds a tileset reference. This will make sure the tileset is watched for
    # changes and can be found using findTileset().
    ##
    def addReference(self, tileset):
        if (self.mTilesets.contains(tileset)):
            self.mTilesets[tileset] += 1
        else:
            self.mTilesets.insert(tileset, 1)
            if (tileset.imageSource()!=''):
                self.mWatcher.addPath(tileset.imageSource())

    ##
    # Removes a tileset reference. When the last reference has been removed,
    # the tileset is no longer watched for changes.
    ##
    def removeReference(self, tileset):
        if self.mTilesets[tileset]:
            self.mTilesets[tileset] -= 1
        if (self.mTilesets[tileset] == 0):
            self.mTilesets.remove(tileset)
            if (tileset.imageSource()!=''):
                self.mWatcher.removePath(tileset.imageSource())

    ##
    # Convenience method to add references to multiple tilesets.
    # @see addReference
    ##
    def addReferences(self, tilesets):
        for tileset in tilesets:
            self.addReference(tileset)

    ##
    # Convenience method to remove references from multiple tilesets.
    # @see removeReference
    ##
    def removeReferences(self, tilesets):
        for tileset in tilesets:
            self.removeReference(tileset)

    ##
    # Returns all currently available tilesets.
    ##
    def tilesets(self):
        return self.mTilesets.keys()

    ##
    # Forces a tileset to reload.
    ##
    def forceTilesetReload(self, tileset):
        if (not self.mTilesets.contains(tileset)):
            return
        fileName = tileset.imageSource()
        if (tileset.loadFromImage(fileName)):
            self.tilesetChanged.emit(tileset)

    ##
    # Sets whether tilesets are automatically reloaded when their tileset
    # image changes.
    ##
    def setReloadTilesetsOnChange(self, enabled):
        self.mReloadTilesetsOnChange = enabled
        # TODO: Clear the file system watcher when disabled

    def reloadTilesetsOnChange(self):
        return self.mReloadTilesetsOnChange
    ##
    # Sets whether tile animations are running.
    ##
    def setAnimateTiles(self, enabled):
        # TODO: Avoid running the driver when there are no animated tiles
        if (enabled):
            self.mAnimationDriver.start()
        else:
            self.mAnimationDriver.stop()

    def animateTiles(self):
        return self.mAnimationDriver.state() == QAbstractAnimation.Running

    def fileChanged(self, path):
        if (not self.mReloadTilesetsOnChange):
            return
        ##
        # Use a one-shot timer since GIMP (for example) seems to generate many
        # file changes during a save, and some of the intermediate attempts to
        # reload the tileset images actually fail (at least for .png files).
        ##
        self.mChangedFiles.insert(path)
        self.mChangedFilesTimer.start()

    def fileChangedTimeout(self):
        for tileset in self.tilesets():
            fileName = tileset.imageSource()
            if (self.mChangedFiles.contains(fileName)):
                if (tileset.loadFromImage(fileName)):
                    self.tilesetChanged.emit(tileset)

        self.mChangedFiles.clear()

    def advanceTileAnimations(self, ms):
        # TODO: This could be more optimal by keeping track of the list of
        # actually animated tiles
        for tileset in self.tilesets():
            imageChanged = False
            for tile in tileset.tiles():
                imageChanged |= tile.advanceAnimation(ms)
            if (imageChanged):
                self.repaintTileset.emit(tileset)

