##
# languagemanager.py
# Copyright 2009, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

import sys, os

import preferences
from PyQt5.QtCore import (
    QTranslator,
    QLocale,
    QLibraryInfo,
    QDirIterator,
    QDir,
    QCoreApplication
)
from pyqtcore import QStringList

class LanguageManager():
    mInstance = None
    def instance():
        if (not LanguageManager.mInstance):
            LanguageManager.mInstance = LanguageManager()
        return LanguageManager.mInstance

    def deleteInstance():
        del LanguageManager.mInstance
        LanguageManager.mInstance = None

    ##
    # Installs the translators on the application for Qt and Tiled. Should be
    # called again when the language changes.
    ##
    def installTranslators(self):
        # Delete previous translators
        del self.mQtTranslator
        del self.mAppTranslator
        self.mQtTranslator = QTranslator()
        self.mAppTranslator = QTranslator()
        language = preferences.Preferences.instance().language()
        if language=='':
            language = QLocale.system().name()
        qtTranslationsDir = QLibraryInfo.location(QLibraryInfo.TranslationsPath)
        if (self.mQtTranslator.load("qt_" + language, qtTranslationsDir)):
            QCoreApplication.installTranslator(self.mQtTranslator)
        else:
            del self.mQtTranslator
            self.mQtTranslator = None

        if (self.mAppTranslator.load("tiled_" + language, self.mTranslationsDir)):
            QCoreApplication.installTranslator(self.mAppTranslator)
        else:
            del self.mAppTranslator
            self.mAppTranslator = None

    ##
    # Returns the available languages as a list of country codes.
    ##
    def availableLanguages(self):
        if (self.mLanguages.isEmpty()):
            self.loadAvailableLanguages()
        return self.mLanguages

    def __init__(self):
        self.mQtTranslator = None
        self.mAppTranslator = None
        self.mLanguages = QStringList()

        self.mTranslationsDir, _ = os.path.split(sys.argv[0])
        if sys.platform == 'win32':
            self.mTranslationsDir += "/../translations"
        elif sys.platform == 'darwin':
            self.mTranslationsDir += "/../Translations"
        else:
            self.mTranslationsDir += "/../share/tiled/translations"

    def __del__(self):
        del self.mQtTranslator
        del self.mAppTranslator

    def loadAvailableLanguages(self):
        self.mLanguages.clear()
        nameFilters = QStringList()
        nameFilters.append("tiled_*.qm")
        iterator = QDirIterator(self.mTranslationsDir, nameFilters, QDir.Files | QDir.Readable)
        while (iterator.hasNext()):
            iterator.next()
            baseName = iterator.fileInfo().completeBaseName()
            # Cut off "tiled_" from the start
            self.mLanguages.append(baseName[6])
