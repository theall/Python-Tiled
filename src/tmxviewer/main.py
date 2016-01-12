##
# main.py
# Copyright 2010, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
#
# This file is part of the TMX Viewer example.
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

import sys
sys.path.append('./../')
sys.path.append('./../libtiled')
sys.path.append('./../QtProperty')
sys.path.append('./../libqt5')
sys.path.append('./../tiled')
sys.path.append('./../plugins')
from tmxviewer import TmxViewer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import (
    qWarning
)
class CommandLineOptions:
    def __init__(self):
        self.showHelp = False
        self.showVersion = False
        self.fileToOpen = ''

def showHelp():
    # TODO: Make translatable
    qWarning("Usage: tmxviewer [option] [file]\n\n"
             "Options:\n"
             "  -h --help    : Display this help\n"
             "  -v --version : Display the version")

def showVersion():
    qWarning("TMX Map Viewer" + QApplication.applicationVersion())

def parseCommandLineArguments(options):
    arguments = sys.argv
    for i in range(1, len(arguments)):
        arg = arguments[i]
        if (arg == "--help") or arg == "-h":
            options.showHelp = True
        elif (arg == "--version"
                or arg == "-v"):
            options.showVersion = True
        elif arg[0] == '-':
            qWarning("Unknown option" + arg)
            options.showHelp = True
        elif (options.fileToOpen==''):
            options.fileToOpen = arg

def main(argv):
    # Avoid performance issues with X11 engine when rendering objects
    if sys.platform == 'linux':
        QApplication.setGraphicsSystem("raster")

    a = QApplication(argv)
    a.setOrganizationDomain("mapeditor.org")
    a.setApplicationName("TmxViewer")
    a.setApplicationVersion("1.0")
    options = CommandLineOptions()
    parseCommandLineArguments(options)
    if (options.showVersion):
        showVersion()
    if (options.showHelp or (options.fileToOpen=='' and not options.showVersion)):
        showHelp()
    if (options.showVersion
            or options.showHelp
            or options.fileToOpen==''):
        return 0
    w = TmxViewer()
    if (not w.viewMap(options.fileToOpen)):
        return 1
    w.show()
    return a.exec()

if __name__ == '__main__':
    main(sys.argv)
