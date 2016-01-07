##
# imagelayer.py
# Copyright 2011, Gregory Nickonov <gregory@nickonov.ru>
# Copyright 2012, Alexander Kuhrt <alex@qrt.de>
#
# This file is part of libtiled.
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

from layer import Layer
from pyqtcore import QString, QSet
from PyQt5.QtGui import (
    QBitmap,
    QPixmap,
    QColor
)

##
# An image on a map.
##
class ImageLayer(Layer):
    ##
    # Constructor.
    ##
    def __init__(self, name, x, y, width, height):
        super().__init__(Layer.ImageLayerType, name, x, y, width, height)

        self.mImage = QPixmap()
        self.mTransparentColor = QColor()
        self.mImageSource = QString()

    ##
    # Destructor.
    ##
    def __del__(self):
        pass

    def usedTilesets(self):
        return QSet()

    def referencesTileset(self, arg1):
        return False

    def replaceReferencesToTileset(self, arg1, arg2):
        pass

    def canMergeWith(self, arg1):
        return False

    def mergedWith(self, arg1):
        return None

    ##
    # Returns the transparent color, or an invalid color if no transparent
    # color is used.
    ##
    def transparentColor(self):
        return QColor(self.mTransparentColor)

    ##
    # Sets the transparent color. Pixels with this color will be masked out
    # when loadFromImage() is called.
    ##
    def setTransparentColor(self, c):
        self.mTransparentColor = c

    ##
    #  Sets image source file name
    ##
    def setSource(self, source):
        self.mImageSource = source

    ##
    # Returns the file name of the layer image.
    ##
    def imageSource(self):
        return self.mImageSource

    ##
    # Returns the image of this layer.
    ##
    def image(self):
        return QPixmap(self.mImage)

    ##
    # Sets the image of this layer.
    ##
    def setImage(self, image):
        self.mImage = image

    ##
    # Resets layer image.
    ##
    def resetImage(self):
        self.mImage = QPixmap()
        self.mImageSource = ''

    ##
    # Load this layer from the given \a image. This will replace the existing
    # image. The \a fileName becomes the new imageSource, regardless of
    # whether the image could be loaded.
    #
    # @param image    the image to load the layer from
    # @param fileName the file name of the image, which will be remembered
    #                 as the image source of this layer.
    # @return <code>true</code> if loading was successful, otherwise
    #         returns <code>false</code>
    ##
    def loadFromImage(self, image, fileName):
        self.mImageSource = fileName
        if (image.isNull()):
            self.mImage = QPixmap()
            return False

        self.mImage = QPixmap.fromImage(image)
        if (self.mTransparentColor.isValid()):
            mask = image.createMaskFromColor(self.mTransparentColor.rgb())
            self.mImage.setMask(QBitmap.fromImage(mask))

        return True

    ##
    # Returns True if no image source has been set.
    ##
    def isEmpty(self):
        return self.mImage.isNull()

    def clone(self):
        return self.initializeClone(ImageLayer(self.mName, self.mX, self.mY, self.mWidth, self.mHeight))

    def initializeClone(self, clone):
        super().initializeClone(clone)
        clone.mImageSource = self.mImageSource
        clone.mTransparentColor = self.mTransparentColor
        clone.mImage = self.mImage
        return clone

