##
# main.py
# Copyright 2008-2011, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2011, Ben Longbons
# Copyright 2011, Stefan Beller, stefanbeller@googlemail.com
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

import sys

from mapformat import MapFormat
from mapreader import MapReader
from tiledapplication import TiledApplication
import preferences
from pluginmanager import PluginManager
from languagemanager import LanguageManager
from mainwindow import MainWindow
from commandlineparser import CommandLineParser
from PyQt5.QtCore import (
    Qt,
    qWarning,
    QFileInfo,
    QCoreApplication
)
from PyQt5.QtWidgets import (
    QStyleFactory,
    QApplication
)
from pyqtcore import QChar, qgetenv

class CommandLineHandler(CommandLineParser):
    def __init__(self):
        super().__init__()

        self.quit = False
        self.showedVersion = False
        self.disableOpenGL = False
        self.exportMap = False

        self.option(
                    'v',
                    "--version",
                    self.tr("Display the version"))
        self.option(
                    QChar(),
                    "--quit",
                    self.tr("Only check validity of arguments"))
        self.option(
                    QChar(),
                    "--disable-opengl",
                    self.tr("Disable hardware accelerated rendering"))
        self.option(
                    QChar(),
                    "--export-map",
                    self.tr("Export the specified tmx file to target"))
        self.option(
                    QChar(),
                    "--export-formats",
                    self.tr("Print a list of supported export formats"))

    def tr(self, sourceText, disambiguation = '', n = -1):
        return QCoreApplication.translate('CommandLineHandler', sourceText, disambiguation, n)

    def showVersion(self):
        if (not self.showedVersion):
            self.showedVersion = True
            qWarning(QApplication.applicationDisplayName()+'\n'+QApplication.applicationVersion())
            self.quit = True

    def justQuit(self):
        self.quit = True

    def setDisableOpenGL(self):
        self.disableOpenGL = True

    def setExportMap(self):
        self.exportMap = True

    def showExportFormats(self):
        PluginManager.instance().loadPlugins()

        qWarning(self.tr("Export formats:"))
        formats = PluginManager.objects(MapFormat)
        for format in formats:
            if format.hasCapabilities(MapFormat.Write):
                qWarning(" " + format.nameFilter())

        self.quit = True

    # Convenience wrapper around registerOption
    def option(self, shortName, longName, help):
        CommandLineParser.registerOption(self, shortName, longName, help)

def main(argv):
    a = TiledApplication(argv)
    a.setOrganizationDomain("mapeditor.org")
    a.setApplicationName("Tiled")
    a.setApplicationVersion("0.14.2")

    if sys.platform == 'darwin':
        a.setAttribute(Qt.AA_DontShowIconsInMenus)

    # Enable support for highres images (added in Qt 5.1, but off by default)
    a.setAttribute(Qt.AA_UseHighDpiPixmaps)
    if sys.platform != 'win32':
        baseName = QApplication.style().objectName()
        if (baseName == "windows"):
            # Avoid Windows 95 style at all cost
            if (QStyleFactory.keys().contains("Fusion")):
                baseName = "fusion" # Qt5
            else: # Qt4
                # e.g. if we are running on a KDE4 desktop
                desktopEnvironment = qgetenv("DESKTOP_SESSION")
                if (desktopEnvironment == "kde"):
                    baseName = "plastique"
                else:
                    baseName = "cleanlooks"

            a.setStyle(QStyleFactory.create(baseName))
    languageManager = LanguageManager.instance()
    languageManager.installTranslators()
    commandLine = CommandLineHandler()
    if (not commandLine.parse(QCoreApplication.arguments())):
        return 0
    if (commandLine.quit):
        return 0
    if (commandLine.disableOpenGL):
        preferences.Preferences.instance().setUseOpenGL(False)
    PluginManager.instance().loadPlugins()
    if (commandLine.exportMap):
        # Get the path to the source file and target file
        if (commandLine.filesToOpen().length() < 2):
            qWarning(QCoreApplication.translate("Command line", "Export syntax is --export-map [format] "))
            return 1

        index = 0
        if commandLine.filesToOpen().length() > 2:
            filter = commandLine.filesToOpen().at(index)
            index += 1
        else:
            filter = None
        sourceFile = commandLine.filesToOpen().at(index)
        index += 1
        targetFile = commandLine.filesToOpen().at(index)
        index += 1
        
        chosenFormat = None
        formats = PluginManager.objects(MapFormat)

        if filter:
            # Find the map format supporting the given filter
            for format in formats:
                if not format.hasCapabilities(MapFormat.Write):
                    continue
                if format.nameFilter().lower()==filter.lower():
                    chosenFormat = format
                    break
            if not chosenFormat:
                qWarning(QCoreApplication.translate("Command line", "Format not recognized (see --export-formats)"))
                return 1
        else:
            # Find the map format based on target file extension
            suffix = QFileInfo(targetFile).completeSuffix()
            for format in formats:
                if not format.hasCapabilities(MapFormat.Write):
                    continue
                if format.nameFilter().contains(suffix, Qt.CaseInsensitive):
                    if chosenFormat:
                        qWarning(QCoreApplication.translate("Command line", "Non-unique file extension. Can't determine correct export format."))
                        return 1
                    chosenFormat = format
                    
            if not chosenFormat:
                qWarning(QCoreApplication.translate("Command line", "No exporter found for target file."))
                return 1

        # Load the source file
        reader = MapReader()
        map = reader.readMap(sourceFile)
        if (not map):
            qWarning(QCoreApplication.translate("Command line", "Failed to load source map."))
            return 1

        # Write out the file
        success = chosenFormat.write(map.data(), targetFile)

        if (not success):
            qWarning(QCoreApplication.translate("Command line", "Failed to export map to target file."))
            return 1

        return 0
    w = MainWindow()
    w.show()
    a.fileOpenRequest.connect(w.openFile)
    if (not commandLine.filesToOpen().isEmpty()):
        for fileName in commandLine.filesToOpen():
            w.openFile(fileName)
    elif preferences.Preferences.instance().openLastFilesOnStartup():
        w.openLastFiles()
    return a.exec()
