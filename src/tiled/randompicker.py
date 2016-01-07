##
# randompicker.py
# Copyright 2015, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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

from pyqtcore import (
    QMap, 
    rand, 
    RAND_MAX
)
##
# A class that helps pick random things that each have a probability
# assigned.
##

class RandomPicker():

    def __init__(self):
        self.mSum = 0.0
        self.mThresholds = QMap()

    def add(self, value, probability = 1.0):
        self.mSum += probability
        self.mThresholds.insert(self.mSum, value)
    
    def isEmpty(self):
        return self.mThresholds.isEmpty()
    
    def pick(self):
        random = (rand() / RAND_MAX) * self.mSum
        it = self.mThresholds.lowerBound(random)
        if (it != self.mThresholds.end()):
            return self.mThresholds.itemByIndex(it)[1]
        else:
            return self.mThresholds.itemByIndex(-1)[1]
    
    def clear(self):
        self.mSum = 0.0
        self.mThresholds.clear()

