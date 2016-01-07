##
# main.py
# Copyright 2012, Vincent Petithory
#
# This file is part of the TMX Rasterizer.
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
#if QT_VERSION >= 0x050000
#else

from pyqtcore import QStringList
from tmxrasterizer import TmxRasterizer
from PyQt5.QtGui import (
    QGuiApplication
)
from PyQt5.QtCore import (
    qWarning,
    QCoreApplication
)
class CommandLineOptions():
    def __init__(self):
        self.showHelp = False
        self.showVersion = False
        self.scale = 1.0
        self.tileSize = 0
        self.useAntiAliasing = False
        self.ignoreVisibility = False
        self.layersToHide = QStringList()

def showHelp():
    # TODO: Make translatable
    qWarning(
            "Usage:\n"
            "  tmxrasterizer [options] [input file] [output file]\n"
            "\n"
            "Options:\n"
            "  -h --help               : Display this help\n"
            "  -v --version            : Display the version\n"
            "  -s --scale SCALE        : The scale of the output image (default: 1)\n"
            "  -t --tilesize SIZE      : The requested size in pixels at which a tile is rendered\n"
            "                            Overrides the --scale option\n"
            "  -a --anti-aliasing      : Smooth the output image using anti-aliasing\n"
            "     --ignore-visibility  : Ignore all layer visibility flags in the map file, and render all\n"
            "                            layers in the output (default is to omit invisible layers)\n"
            "     --hide-layer         : Specifies a layer to omit from the output image\n"
            "                            Can be repeated to hide multiple layers\n")

def showVersion():
    qWarning("TMX Map Rasterizer" + QCoreApplication.applicationVersion())

def parseCommandLineArguments(options):
    arguments = QCoreApplication.arguments()
    for i in range(1, arguments.size()):
        arg = arguments.at(i)
        if (arg == "--help") or arg == "-h":
            options.showHelp = True
        elif (arg == "--version"
                or arg == "-v"):
            options.showVersion = True
        elif (arg == "--scale"
                or arg == "-s"):
            i += 1
            if (i >= arguments.size()):
                options.showHelp = True
            else:
                scaleIsDouble = False
                options.scale = arguments.at(i).toDouble(scaleIsDouble)
                if (not scaleIsDouble):
                    qWarning(arguments.at(i) + ": the specified scale is not a number.")
                    options.showHelp = True
        elif (arg == "--tilesize"
                or arg == "-t"):
            i += 1
            if (i >= arguments.size()):
                options.showHelp = True
            else:
                tileSizeIsInt = False
                options.tileSize = arguments.at(i).toInt(tileSizeIsInt)
                if (not tileSizeIsInt):
                    qWarning(arguments.at(i) + ": the specified tile size is not an integer.")
                    options.showHelp = True
        elif (arg == "--hide-layer"):
            i += 1
            if (i >= arguments.size()):
                options.showHelp = True
            else:
                options.layersToHide.append(arguments.at(i))
        elif (arg == "--anti-aliasing"
                or arg == "-a"):
            options.useAntiAliasing = True
        elif (arg == "--ignore-visibility"):
            options.ignoreVisibility = True
        elif (arg.isEmpty()):
            options.showHelp = True
        elif (arg.at(0) == '-'):
            qWarning("Unknown option" + arg)
            options.showHelp = True
        elif (options.fileToOpen.isEmpty()):
            options.fileToOpen = arg
        elif (options.fileToSave.isEmpty()):
            options.fileToSave = arg
        else:
            # All args are already defined. Show help.
            options.showHelp = True

def main(argc, *argv):
    a = QGuiApplication(argc, argv)

    a.setOrganizationDomain("mapeditor.org")
    a.setApplicationName("TmxRasterizer")
    a.setApplicationVersion("1.0")
    options = CommandLineOptions()
    parseCommandLineArguments(options)
    if (options.showVersion):
        showVersion()
        return 0

    if (options.showHelp or options.fileToOpen.isEmpty() or options.fileToSave.isEmpty()):
        showHelp()
        return 0

    if (options.scale <= 0.0 and options.tileSize <= 0):
        showHelp()
        return 0

    w = TmxRasterizer()
    w.setAntiAliasing(options.useAntiAliasing)
    w.setIgnoreVisibility(options.ignoreVisibility)
    w.setLayersToHide(options.layersToHide)
    if (options.tileSize > 0):
        w.setTileSize(options.tileSize)
    elif (options.scale > 0.0):
        w.setScale(options.scale)

    return w.render(options.fileToOpen, options.fileToSave)

