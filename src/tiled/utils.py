##
# utils.py
# Copyright 2009-2010, Thorbjørn Lindeijer
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

import sys
import preferences
from pyqtcore import QString
from PyQt5.QtCore import (
    QByteArray, 
    QCoreApplication
)
from PyQt5.QtGui import (
    QImageWriter,
    QImageReader,
    QIcon
)

def toImageFileFilter(formats):
    filter = QString(QCoreApplication.translate("Utils", "Image files"))
    filter += " ("
    first = True
    for format in formats:
        format = format.data().decode()
        if (not first):
            filter += ' '
        first = False
        filter += "*."
        filter += format.lower()

    filter += ')'
    return filter

class Utils():
    ##
    # Returns a file dialog filter that matches all readable image formats.
    ##
    def readableImageFormatsFilter():
        return toImageFileFilter(QImageReader.supportedImageFormats())

    ##
    # Returns a file dialog filter that matches all writable image formats.
    ##
    def writableImageFormatsFilter():
        return toImageFileFilter(QImageWriter.supportedImageFormats())

    ##
    # Looks up the icon with the specified \a name from the system theme and set
    # it on the instance \a t when found.
    #
    # This is a template method which is used on instances of QAction, QMenu,
    # QToolButton, etc.
    #
    # Does nothing when the platform is not Linux.
    ##
    def setThemeIcon(t, name):
        if sys.platform == 'linux':
            themeIcon = QIcon.fromTheme(name)
            if (not themeIcon.isNull()):
                t.setIcon(themeIcon)

    ##
    # Restores a widget's geometry.
    # Requires the widget to have its object name set.
    ##
    def restoreGeometry(widget):
        key = widget.objectName() + "/Geometry"
        settings = preferences.Preferences.instance().settings()
        try:
            geo = QByteArray(settings.value(key))
        except:
            geo = QByteArray()
        widget.restoreGeometry(geo)

    ##
    # Saves a widget's geometry.
    # Requires the widget to have its object name set.
    ##
    def saveGeometry(widget):
        key = widget.objectName() + "/Geometry"
        settings = preferences.Preferences.instance().settings()
        settings.setValue(key, widget.saveGeometry())
