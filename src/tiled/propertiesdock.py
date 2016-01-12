##
# propertiesdock.py
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

from utils import Utils
from object import Object
from pyqtcore import QString
from propertybrowser import PropertyBrowser
from documentmanager import DocumentManager
from changeproperties import SetProperty, RemoveProperty, RenameProperty
from PyQt5.QtCore import (
    Qt,
    QSize,
    QEvent
)
from PyQt5.QtGui import (
    QIcon,
    QKeySequence
)
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QToolBar,
    QLineEdit, 
    QInputDialog,
    QAction,
    QDockWidget
)
def isExternal(object):
    if (not object):
        return False
    x = object.typeId()
    if x==Object.TilesetType:
        return object.isExternal()
    elif x==Object.TileType:
        return object.tileset().isExternal()
    elif x==Object.TerrainType:
        return object.tileset().isExternal()
    else:
        return False

class PropertiesDock(QDockWidget):

    def __init__(self, parent = None):
        super().__init__(parent)
        self.mMapDocument = None
        self.mPropertyBrowser = PropertyBrowser()

        self.setObjectName("propertiesDock")
        self.mActionAddProperty = QAction(self)
        self.mActionAddProperty.setEnabled(False)
        self.mActionAddProperty.setIcon(QIcon(":/images/16x16/add.png"))
        self.mActionAddProperty.triggered.connect(self.addProperty)
        self.mActionRemoveProperty = QAction(self)
        self.mActionRemoveProperty.setEnabled(False)
        self.mActionRemoveProperty.setIcon(QIcon(":/images/16x16/remove.png"))
        self.mActionRemoveProperty.triggered.connect(self.removeProperty)
        self.mActionRenameProperty = QAction(self)
        self.mActionRenameProperty.setEnabled(False)
        self.mActionRenameProperty.setIcon(QIcon(":/images/16x16/rename.png"))
        self.mActionRenameProperty.triggered.connect(self.renameProperty)
        Utils.setThemeIcon(self.mActionAddProperty, "add")
        Utils.setThemeIcon(self.mActionRemoveProperty, "remove")
        Utils.setThemeIcon(self.mActionRenameProperty, "rename")
        toolBar = QToolBar()
        toolBar.setFloatable(False)
        toolBar.setMovable(False)
        toolBar.setIconSize(QSize(16, 16))
        toolBar.addAction(self.mActionAddProperty)
        toolBar.addAction(self.mActionRemoveProperty)
        toolBar.addAction(self.mActionRenameProperty)
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)
        layout.addWidget(self.mPropertyBrowser)
        layout.addWidget(toolBar)
        widget.setLayout(layout)
        self.setWidget(widget)
        manager = DocumentManager.instance()
        manager.currentDocumentChanged.connect(self.mapDocumentChanged)
        self.mPropertyBrowser.currentItemChangedSignal.connect(self.currentItemChanged)
        self.retranslateUi()

    def bringToFront(self):
        self.show()
        self.raise_()
        self.mPropertyBrowser.setFocus()

    def event(self, event):
        x = event.type()
        if x==QEvent.KeyPress or x==QEvent.ShortcutOverride:
            keyEvent = event
            if (keyEvent.matches(QKeySequence.Delete) or keyEvent.key() == Qt.Key_Backspace):
                if event.type() == QEvent.KeyPress:
                    self.removeProperty()
                event.accept()
                return True
        elif x==QEvent.LanguageChange:
            self.retranslateUi()
        else:
            pass

        return super().event(event)

    def mapDocumentChanged(self, mapDocument):
        if type(mapDocument)==list:
            mapDocument = mapDocument[0]
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
        self.mMapDocument = mapDocument
        self.mPropertyBrowser.setMapDocument(mapDocument)
        if (mapDocument):
            mapDocument.currentObjectChanged.connect(self.currentObjectChanged)
            mapDocument.tilesetFileNameChanged.connect(self.tilesetFileNameChanged)
            mapDocument.editCurrentObject.connect(self.bringToFront)
            self.currentObjectChanged(mapDocument.currentObject())
        else:
            self.currentObjectChanged(None)

    def currentObjectChanged(self, object):
        if type(object)==list and len(object)>0:
            object = object[0]
        self.mPropertyBrowser.setObject(object)
        enabled = object != None and not isExternal(object)
        self.mPropertyBrowser.setEnabled(enabled)
        self.mActionAddProperty.setEnabled(enabled)

    def currentItemChanged(self, item):
        isCustomProperty = self.mPropertyBrowser.isCustomPropertyItem(item)
        external = isExternal(self.mPropertyBrowser.object())
        self.mActionRemoveProperty.setEnabled(isCustomProperty and not external)
        self.mActionRenameProperty.setEnabled(isCustomProperty and not external)

    def tilesetFileNameChanged(self, tileset):
        object = self.mMapDocument.currentObject()
        if (not object):
            return
        update = False
        x = object.typeId()
        if x==Object.TilesetType:
            update = object == tileset
        elif x==Object.TileType:
            update = object.tileset() == tileset
        elif x==Object.TerrainType:
            update = object.tileset() == tileset
        else:
            pass

        if (update):
            self.currentObjectChanged(object)
            self.currentItemChanged(self.mPropertyBrowser.currentItem())

    def addProperty(self, *args):
        l = len(args)
        if l==0:
            property, ok = QInputDialog.getText(self.mPropertyBrowser, self.tr("Add Property"),
                self.tr("Name:"), QLineEdit.Normal,'')
            if ok:
                self.addProperty(property)
        elif l==1:
            arg1 = args[0]
            tp = type(arg1)
            if tp==bool:
                self.addProperty()
            elif tp in [str, QString]:
                name = arg1
                if name=='':
                    return
                object = self.mMapDocument.currentObject()
                if (not object):
                    return
                if (not object.hasProperty(name)):
                    undoStack = self.mMapDocument.undoStack()
                    undoStack.push(SetProperty(self.mMapDocument, self.mMapDocument.currentObjects(), name, QString()))

                self.mPropertyBrowser.editCustomProperty(name)

    def removeProperty(self):
        item = self.mPropertyBrowser.currentItem()
        object = self.mMapDocument.currentObject()
        if (not item or not object):
            return
        name = item.property().propertyName()
        undoStack = self.mMapDocument.undoStack()
        items = item.parent().children()
        if items.count() > 1:
            currentItemIndex = items.indexOf(item)
            if item == items.last():
                self.mPropertyBrowser.setCurrentItem(items.at(currentItemIndex - 1))
            else:
                self.mPropertyBrowser.setCurrentItem(items.at(currentItemIndex + 1))

        undoStack.push(RemoveProperty(self.mMapDocument, self.mMapDocument.currentObjects(), name))

    def renameProperty(self, *args):
        l = len(args)
        if l==0:
            item = self.mPropertyBrowser.currentItem()
            if (not item):
                return
            oldName = item.property().propertyName()
            dialog = QInputDialog(self.mPropertyBrowser)
            dialog.setInputMode(QInputDialog.TextInput)
            dialog.setLabelText(self.tr("Name:"))
            dialog.setTextValue(oldName)
            dialog.setWindowTitle(self.tr("Rename Property"))
            dialog.open(self.renameProperty)
        elif l==1:
            name = args[0]
            if (name.isEmpty()):
                return
            item = self.mPropertyBrowser.currentItem()
            if (not item):
                return
            oldName = item.property().propertyName()
            if (oldName == name):
                return
            undoStack = self.mMapDocument.undoStack()
            undoStack.push(RenameProperty(self.mMapDocument, self.mMapDocument.currentObjects(), oldName, name))

    def retranslateUi(self):
        self.setWindowTitle(self.tr("Properties"))
        self.mActionAddProperty.setText(self.tr("Add Property"))
        self.mActionRemoveProperty.setText(self.tr("Remove Property"))
        self.mActionRenameProperty.setText(self.tr("Rename Property"))
