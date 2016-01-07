##
# rangeset.py
# Copyright 2011, Ben Longbons
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

from pyqtcore import (
    QMap
)
##*
# Logically, a set, but implemented as a set of ranges. This class is only
# intended to be used with primitive integral types.
##
class RangeSet():

    # This class is based on std.map rather than QMap since std.map's insert
    # method has an overload that takes a hint about where to insert the new
    # pair.
    def __init__(self):
        self.mMap = QMap()

    ##
    # Extends the real iterator type with some convenience methods.
    ##
    class Range():
        ##*
        # Returns the first value included in this range.
        ##
        def first(self):
            return self.first
        ##*
        # Returns the last value included in this range.
        ##
        def last(self):
            return self.second
        ##*
        # Returns the number of values included in this range.
        ##
        def length(self):
            return self.last() - self.first() + 1

    ##*
    # Insert \a value in the set of ranges. Has no effect when the value is
    # already part of an existing range. When possible, an existing range is
    # extended to include the new value, otherwise a new range is inserted.
    ##
    def insert(self, value):
        if (self.mMap.empty()):
            self.mMap.insert(value, value)
            return

        # We can now assume that 'it' will be at most one end of the range
        # This is the only full-tree search of the map, everything else is
        # relative to this
        it = self.mMap.lower_bound(value)
        begin = self.mMap.begin()
        end = self.mMap.end()
        if (it == end):
            # Check whether the value is included in the last range
            # assert: it != begin
            it -= 1
            # assert: it.first < value
            if (it.second >= value):
                return
            # Try to add the value to the end of the previous range
            if (++it.second == value):
                return
            # Didn't work, restore the previous range
            --it.second
            # We have to insert a new range
            self.mMap.insert(it, [value, value])
            return

        # Now we can dereference 'it' itself
        # assert: it.first >= value
        if (it.first == value):
            return
        # Check whether we can extend the range downwards to include value
        if (it.first == value + 1):
            # When extending the range downwards, it may need to be merged
            # with the previous range.
            # Remember 'prev' for the insertion hint. It is not necessarily
            # before the value, if it == begin.
            prev = it
            if (it != begin):
                --prev
                if (prev.second == value - 1):
                    # The new value fills the gab. Merge the ranges, leaving
                    # only the first, but with a larger range.
                    prev.second = it.second
                    self.mMap.erase(it)
                    return

            # No merge needed
            # To change the key, we have to both add and remove. Add first,
            # then remove, to avoid invalidating the iterator too early.
            self.mMap.insert(prev, [value, it.second])
            self.mMap.erase(it)
            return

        # Check if we can grow the previous range upwards to include value
        if (it != begin):
            --it
            if (it.second == value - 1):
                it.second += 1
                return

        # 'it' now points below the range, unless it was already begin
        # We couldn't increase an existing range
        self.mMap.insert(it, [value, value])

    ##*
    # Removes all ranges from this set.
    ##
    def clear(self):
        self.mMap.clear()

    # Only are provided, because it is not safe to modify the
    # underlying list. Note that const_iterator is a typedef for Range.
    def begin(self):
        return RangeSet.Range(self.mMap.begin())

    def end(self):
        return RangeSet.Range(self.mMap.end())

    def isEmpty(self):
        return self.mMap.empty()

