##
# variantpropertymanager.py
# Copyright (C) 2006 Trolltech ASA. All rights reserved. (GPLv2)
# Copyright 2013, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
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
    QVariant
)
from pyqtcore import QMap, QMapList, QString, QStringList
from qtvariantproperty import QtVariantPropertyManager

##
# Extension of the QtVariantPropertyManager that adds support for a filePath
# data type.
##
class VariantPropertyManager(QtVariantPropertyManager):
    TYPEID_FILEPATH = 400

    class Data:
        def __init__(self):
            self.value = QString()
            self.filter = QString()

    def __init__(self, parent = None):
        self.mValues = QMap()
        self.mSuggestions = QMapList()
        self.mSuggestionsAttribute = QString()
        self.Data = VariantPropertyManager.Data()

        super().__init__(parent)
        self.mSuggestionsAttribute = "suggestions"

    def value(self, property):
        if (self.mValues.contains(property)):
            return self.mValues[property].value
        return super().value(property)

    def valueType(self, propertyType):
        if (propertyType == VariantPropertyManager.filePathTypeId()):
            return QVariant.String
        return super().valueType(propertyType)

    def isPropertyTypeSupported(self, propertyType):
        if (propertyType == VariantPropertyManager.filePathTypeId()):
            return True
        return super().isPropertyTypeSupported(propertyType)

    def attributes(self, propertyType):
        if (propertyType == VariantPropertyManager.filePathTypeId()):
            attr = QStringList()
            attr.append("filter")
            return attr

        return super().attributes(propertyType)

    def attributeType(self, propertyType, attribute):
        if (propertyType == VariantPropertyManager.filePathTypeId()):
            if (attribute == "filter"):
                return QVariant.String
            return 0

        return super().attributeType(propertyType, attribute)

    def attributeValue(self, property, attribute):
        if (self.mValues.contains(property)):
            if (attribute == "filter"):
                return self.mValues[property].filter
            return QVariant()

        if (attribute == self.mSuggestionsAttribute and self.mSuggestions.contains(property)):
            return self.mSuggestions[property]
        return super().attributeValue(property, attribute)

    def filePathTypeId():
        return VariantPropertyManager.TYPEID_FILEPATH

    def setValue(self, property, val):
        if (self.mValues.contains(property)):
            if type(val) != str:
                return
            s = val
            d = self.mValues[property]
            if (d.value == s):
                return
            d.value = s
            self.mValues[property] = d
            self.propertyChangedSignal.emit(property)
            self.valueChangedSignal.emit(property, s)
            return

        super().setValue(property, val)

    def setAttribute(self, property, attribute, val):
        if (self.mValues.contains(property)):
            if (attribute == "filter"):
                if type(val) != str:
                    return
                s = val
                d = self.mValues[property]
                if (d.filter == s):
                    return
                d.filter = s
                self.mValues[property] = d
                self.attributeChangedSignal.emit(property, attribute, s)

            return

        if (attribute == self.mSuggestionsAttribute and self.mSuggestions.contains(property)):
            self.mSuggestions[property] = val
        super().setAttribute(property, attribute, val)

    def valueText(self, property):
        if (self.mValues.contains(property)):
            return self.mValues[property].value
        return super().valueText(property)

    def initializeProperty(self, property):
        tp = self.propertyType(property)
        if (tp == VariantPropertyManager.filePathTypeId()):
            self.mValues[property] = VariantPropertyManager.Data()
        elif tp == QVariant.String:
            self.mSuggestions[property] = QStringList()
        super().initializeProperty(property)

    def uninitializeProperty(self, property):
        self.mValues.remove(property)
        self.mSuggestions.remove(property)
        super().uninitializeProperty(property)
