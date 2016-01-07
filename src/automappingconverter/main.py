##
# main.py
# Copyright 2011, Stefan Beller, stefanbeller@googlemail.com
#
# This file is part of the AutomappingConverter, which converts old rulemaps
# of Tiled to work with the latest version of Tiled.
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
from converterwindow import ConverterWindow
from PyQt5.QtWidgets import (
    QApplication
)
def main(argc, *argv):
    a = QApplication(argc, argv)
    w = ConverterWindow()
    w.show()
    return a.exec()

