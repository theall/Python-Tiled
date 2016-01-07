##
# undocommands.py
# Copyright 2009, Thorbjørn Lindeijer
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
# this program. If not, see .
##

##
# These undo command IDs are used by Qt to determine whether two undo commands
# can be merged.
##
class UndoCommands():
    Cmd_EraseTiles = 0
    Cmd_PaintTileLayer = 1
    Cmd_MoveTileset = 2
    Cmd_ChangeLayerOffset = 3
    Cmd_ChangeLayerOpacity = 4
    Cmd_ChangeTileTerrain = 5
    Cmd_ChangeTilesetTileOffset = 6
