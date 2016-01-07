##
# varianteditorfactory.py
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

from fileedit import FileEdit
from variantpropertymanager import VariantPropertyManager
from qtvariantproperty import QtVariantEditorFactory
from PyQt5.QtCore import (
    Qt,
    QVariant
)
from PyQt5.QtWidgets import (
    QCompleter
)
from pyqtcore import QMap, QMapList
##
# Extension of the QtVariantEditorFactory that adds support for a FileEdit,
# used for editing file references.
#
# It also adds support for a "suggestions" attribute for string values.
##
class VariantEditorFactory(QtVariantEditorFactory):
    def __init__(self, parent = None):
        super().__init__(parent)

        self.mCreatedEditors = QMapList()
        self.mEditorToProperty = QMap()

    def __del__(self):
        self.mEditorToProperty.clear()

    def connectPropertyManager(self, manager):
        manager.valueChangedSignal.connect(self.slotPropertyChanged)
        manager.attributeChangedSignal.connect(self.slotPropertyAttributeChanged)
        super().connectPropertyManager(manager)

    def createEditor(self, manager, property, parent):
        type = manager.propertyType(property)
        if (type == VariantPropertyManager.filePathTypeId()):
            editor = FileEdit(parent)
            editor.setFilePath(manager.value(property))
            editor.setFilter(manager.attributeValue(property, "filter"))
            self.mCreatedEditors[property].append(editor)
            self.mEditorToProperty[editor] = property
            editor.filePathChanged.connect(self.slotSetValue)
            editor.destroyed.connect(self.slotEditorDestroyed)
            return editor

        editor = super().createEditor(manager, property, parent)
        if (type == QVariant.String):
            # Add support for "suggestions" attribute that adds a QCompleter to the QLineEdit
            suggestions = manager.attributeValue(property, "suggestions")
            if suggestions and len(suggestions)>0:
                lineEdit = editor
                if lineEdit:
                    completer = QCompleter(suggestions, lineEdit)
                    completer.setCaseSensitivity(Qt.CaseInsensitive)
                    lineEdit.setCompleter(completer)
        return editor

    def disconnectPropertyManager(self, manager):
        manager.valueChangedSignal.disconnect(self.slotPropertyChanged)
        manager.attributeChangedSignal.disconnect(self.slotPropertyAttributeChanged)
        super().disconnectPropertyManager(manager)

    def slotPropertyChanged(self, property, value):
        if (not self.mCreatedEditors.contains(property)):
            return
        editors = self.mCreatedEditors[property]
        for itEditor in editors:
            itEditor.setFilePath(value.toString())

    def slotPropertyAttributeChanged(self, property, attribute, value):
        if (not self.mCreatedEditors.contains(property)):
            return
        if (attribute != "filter"):
            return
        editors = self.mCreatedEditors[property]
        for itEditor in editors:
            itEditor.setFilter(value.toString())

    def slotSetValue(self, value):
        object = self.sender()
        itEditor = self.mEditorToProperty.constBegin()
        while (itEditor != self.mEditorToProperty.constEnd()):
            if (itEditor.key() == object):
                property = itEditor.value()
                manager = self.propertyManager(property)
                if (not manager):
                    return
                manager.setValue(property, value)
                return

            itEditor += 1

    def slotEditorDestroyed(self, object):
        for itEditor in self.mEditorToProperty:
            if (itEditor.key() == object):
                editor = itEditor.key()
                property = itEditor.value()
                self.mEditorToProperty.remove(editor)
                self.mCreatedEditors[property].removeAll(editor)
                if (self.mCreatedEditors[property].isEmpty()):
                    self.mCreatedEditors.remove(property)
                return
