##
# geometry.py
# Copyright 2010-2011, Stefan Beller, stefanbeller@googlemail.com
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

from PyQt5.QtCore import (
    QPoint
)
from pyqtcore import QVector, QList

##
# Returns a lists of points on an ellipse.
# (x0,y0) is the midpoint
# (x1,y1) determines the radius.
#
# It is adapted from http://en.wikipedia.org/wiki/Midpoint_circle_algorithm
# here is the orginal: http://homepage.smc.edu/kennedy_john/belipse.pdf
##
def pointsOnEllipse(*args):
    l = len(args)
    if l==2:
        a, b = args
        return pointsOnLine(a.x(), a.y(), b.x(), b.y())
    elif l==4:
        x0, y0, x1, y1 = args
        ret = QVector()
        ellipseError = 0
        if x0 > x1:
            radiusX = x0 - x1
        else:
            radiusX = x1 - x0
        if y0 > y1:
            radiusY = y0 - y1
        else:
            radiusY = y1 - y0
        if (radiusX == 0 and radiusY == 0):
            return ret
        twoXSquare = 2 * radiusX * radiusX
        twoYSquare = 2 * radiusY * radiusY
        x = radiusX
        y = 0
        xChange = radiusY * radiusY * (1 - 2 * radiusX)
        yChange = radiusX * radiusX
        ellipseError = 0
        stoppingX = twoYSquare*radiusX
        stoppingY = 0
        while (stoppingX >= stoppingY):
            ret += QPoint(x0 + x, y0 + y)
            ret += QPoint(x0 - x, y0 + y)
            ret += QPoint(x0 + x, y0 - y)
            ret += QPoint(x0 - x, y0 - y)
            y += 1
            stoppingY += twoXSquare
            ellipseError += yChange
            yChange += twoXSquare
            if ((2 * ellipseError + xChange) > 0):
                x -= 1
                stoppingX -= twoYSquare
                ellipseError += xChange
                xChange += twoYSquare

        x = 0
        y = radiusY
        xChange = radiusY * radiusY
        yChange = radiusX * radiusX * (1 - 2 * radiusY)
        ellipseError = 0
        stoppingX = 0
        stoppingY = twoXSquare * radiusY
        while (stoppingX <= stoppingY):
            ret += QPoint(x0 + x, y0 + y)
            ret += QPoint(x0 - x, y0 + y)
            ret += QPoint(x0 + x, y0 - y)
            ret += QPoint(x0 - x, y0 - y)
            x += 1
            stoppingX += twoYSquare
            ellipseError += xChange
            xChange += twoYSquare
            if ((2 * ellipseError + yChange) > 0):
                y -= 1
                stoppingY -= twoXSquare
                ellipseError += yChange
                yChange += twoXSquare

        return ret

##
# Returns the lists of points on a line from (x0,y0) to (x1,y1).
#
# This is an implementation of bresenhams line algorithm, initially copied
# from http://en.wikipedia.org/wiki/Bresenham's_line_algorithm#Optimization
# changed to C++ syntax.
##
def pointsOnLine(*args):
    l = len(args)
    if l==2:
        a, b = args
        return pointsOnLine(a.x(), a.y(), b.x(), b.y())
    else:
        x0, y0, x1, y1 = args
        ret = QVector()
        steep = abs(y1 - y0) > abs(x1 - x0)
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        reverse = x0 > x1
        if reverse:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        deltax = x1 - x0
        deltay = abs(y1 - y0)
        error= int(deltax / 2)
        ystep = 0
        y = y0
        if (y0 < y1):
            ystep = 1
        else:
            ystep = -1
        for x in range(x0, x1+1):
            if (steep):
                ret.append(QPoint(y, x))
            else:
                ret.append(QPoint(x, y))
            error = error - deltay
            if (error < 0):
                 y = y + ystep
                 error = error + deltax

        if reverse:
            ret.reverse()
            
        return ret

##
# Checks if a given rectangle \a rect is coherent to another given \a region.
# 'coherent' means that either the rectangle is overlapping the region or
# the rectangle contains at least one tile, which is a direct neighbour
# to a tile, which belongs to the region.
##
def isCoherentTo(rect, region):
    # check if the region is coherent at top or bottom
    if (region.intersects(rect.adjusted(0, -1, 0, 1))):
        return True
    # check if the region is coherent at left or right side
    if (region.intersects(rect.adjusted(-1, 0, 1, 0))):
        return True
    return False

##
# Calculates all coherent regions occupied by the given \a region.
# Returns a list of regions, where each region is coherent in it
##
def coherentRegions(region):
    result = QList()
    rects = region.rects()
    while (not rects.isEmpty()):
        newCoherentRegion = rects.last()
        rects.pop_back()
        # Add up all coherent rects until there is no rect left which is
        # coherent to the newly created region.
        foundRect = True
        while (foundRect):
            foundRect = False
            for i in range(rects.size() - 1, -1, -1):
                if (isCoherentTo(rects.at(i), newCoherentRegion)):
                    newCoherentRegion += rects.at(i)
                    rects.remove(i)
                    foundRect = True

        result += newCoherentRegion

    return result
