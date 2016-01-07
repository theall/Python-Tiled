##
# objectsdock.py
# Copyright 2012, Tim Baker
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

import preferences
from tiled_global import Int
from utils import Utils
from mapdocumentactionhandler import MapDocumentActionHandler
from documentmanager import DocumentManager
from pyqtcore import QList, QMapList
from PyQt5.QtCore import (
    QItemSelectionModel,
    QEvent,
    QSize,
    QVariant
)
from PyQt5.QtGui import (
    QIcon
)
from PyQt5.QtWidgets import (
    QWidget,
    QAction,
    QToolBar,
    QMenu,
    QToolButton,
    QTreeView,
    QVBoxLayout,
    QDockWidget,
    QAbstractItemView
)
FIRST_SECTION_SIZE_KEY = "ObjectsDock/FirstSectionSize"
class ObjectsDock(QDockWidget):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.mExpandedGroups = QMapList()
        self.mObjectsView = ObjectsView()
        self.mMapDocument = None

        self.setObjectName("ObjectsDock")
        self.mActionObjectProperties = QAction(self)
        self.mActionObjectProperties.setIcon(QIcon(":/images/16x16/document-properties.png"))
        Utils.setThemeIcon(self.mActionObjectProperties, "document-properties")
        self.mActionObjectProperties.triggered.connect(self.objectProperties)
        handler = MapDocumentActionHandler.instance()
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(0)
        layout.addWidget(self.mObjectsView)
        self.mActionNewLayer = QAction(self)
        self.mActionNewLayer.setIcon(QIcon(":/images/16x16/document-new.png"))
        self.mActionNewLayer.triggered.connect(handler.actionAddObjectGroup().triggered)
        self.mActionMoveToGroup = QAction(self)
        self.mActionMoveToGroup.setIcon(QIcon(":/images/16x16/layer-object.png"))
        toolBar = QToolBar()
        toolBar.setFloatable(False)
        toolBar.setMovable(False)
        toolBar.setIconSize(QSize(16, 16))
        toolBar.addAction(self.mActionNewLayer)
        toolBar.addAction(handler.actionDuplicateObjects())
        toolBar.addAction(handler.actionRemoveObjects())
        toolBar.addAction(self.mActionMoveToGroup)
        button = toolBar.widgetForAction(self.mActionMoveToGroup)
        self.mMoveToMenu = QMenu(self)
        button.setPopupMode(QToolButton.InstantPopup)
        button.setMenu(self.mMoveToMenu)
        self.mMoveToMenu.aboutToShow.connect(self.aboutToShowMoveToMenu)
        self.mMoveToMenu.triggered.connect(self.triggeredMoveToMenu)
        toolBar.addAction(self.mActionObjectProperties)
        layout.addWidget(toolBar)
        self.setWidget(widget)
        self.retranslateUi()
        DocumentManager.instance().documentAboutToClose.connect(self.documentAboutToClose)

    def setMapDocument(self, mapDoc):
        if (self.mMapDocument):
            self.saveExpandedGroups(self.mMapDocument)
            self.mMapDocument.disconnect()

        self.mMapDocument = mapDoc
        self.mObjectsView.setMapDocument(mapDoc)
        if (self.mMapDocument):
            self.restoreExpandedGroups(self.mMapDocument)
            self.mMapDocument.selectedObjectsChanged.connect(self.updateActions)

        self.updateActions()

    def changeEvent(self, e):
        super().changeEvent(e)
        x = e.type()
        if x==QEvent.LanguageChange:
            self.retranslateUi()
        else:
            pass

    def updateActions(self):
        if self.mMapDocument:
            count = self.mMapDocument.selectedObjects().count()
        else:
            count = 0
        enabled = count > 0
        self.mActionObjectProperties.setEnabled(count == 1)
        if (self.mMapDocument and (self.mMapDocument.map().objectGroupCount() < 2)):
            enabled = False
        self.mActionMoveToGroup.setEnabled(enabled)
        self.mActionMoveToGroup.setToolTip(self.tr("Move %n Object(s) to Layer", "", count))

    def aboutToShowMoveToMenu(self):
        self.mMoveToMenu.clear()
        for objectGroup in self.mMapDocument.map().objectGroups():
            action = self.mMoveToMenu.addAction(objectGroup.name())
            action.setData(QVariant(objectGroup))

    def triggeredMoveToMenu(self, action):
        handler = MapDocumentActionHandler.instance()
        objectGroup = action.data()
        handler.moveObjectsToGroup(objectGroup)

    def objectProperties(self):
        selectedObjects = self.mMapDocument.selectedObjects()
        mapObject = selectedObjects.first()
        self.mMapDocument.setCurrentObject(mapObject)
        self.mMapDocument.emitEditCurrentObject()

    def documentAboutToClose(self, mapDocument):
        self.mExpandedGroups.remove(mapDocument)

    def retranslateUi(self):
        self.setWindowTitle(self.tr("Objects"))
        self.mActionNewLayer.setToolTip(self.tr("Add Object Layer"))
        self.mActionObjectProperties.setToolTip(self.tr("Object Properties"))
        self.updateActions()

    def saveExpandedGroups(self, mapDoc):
        self.mExpandedGroups[mapDoc].clear()
        for og in mapDoc.map().objectGroups():
            if (self.mObjectsView.isExpanded(self.mObjectsView.model().index(og))):
                self.mExpandedGroups[mapDoc].append(og)

    def restoreExpandedGroups(self, mapDoc):
        for og in self.mExpandedGroups[mapDoc]:
            self.mObjectsView.setExpanded(self.mObjectsView.model().index(og), True)
        self.mExpandedGroups[mapDoc].clear()
        # Also restore the selection
        for o in mapDoc.selectedObjects():
            index = self.mObjectsView.model().index(o)
            self.mObjectsView.selectionModel().select(index, QItemSelectionModel.Select | QItemSelectionModel.Rows)

class ObjectsView(QTreeView):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.mMapDocument = None
        self.mSynching = False

        self.setUniformRowHeights(True)
        self.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.pressed.connect(self.onPressed)
        self.activated.connect(self.onActivated)
        self.header().sectionResized.connect(self.onSectionResized)

    def sizeHint(self):
        return QSize(130, 100)

    def setMapDocument(self, mapDoc):
        if (mapDoc == self.mMapDocument):
            return
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
        self.mMapDocument = mapDoc
        if (self.mMapDocument):
            self.setModel(self.mMapDocument.mapObjectModel())
            # 2 equal-sized columns, user can't adjust
            settings = preferences.Preferences.instance().settings()
            firstSectionSize = Int(settings.value(FIRST_SECTION_SIZE_KEY, 200))
            self.header().resizeSection(0, firstSectionSize)
        
        else:
            self.setModel(None)

    def model(self):
        return super().model()

    def selectionChanged(self, selected, deselected):
        super().selectionChanged(selected, deselected)
        
        if (not self.mMapDocument or self.mSynching):
            return
        selectedRows = self.selectionModel().selectedRows()
        currentLayerIndex = -1
        selectedObjects = QList()
        for index in selectedRows:
            og = self.model().toLayer(index)
            if og:
                i = self.mMapDocument.map().layers().indexOf(og)
                if (currentLayerIndex == -1):
                    currentLayerIndex = i
                elif (currentLayerIndex != i):
                    currentLayerIndex = -2

            o = self.model().toMapObject(index)
            if o:
                selectedObjects.append(o)
        
        # Switch the current object layer if only one object layer (and/or its objects)
        # are included in the current selection.
        if (currentLayerIndex >= 0 and currentLayerIndex != self.mMapDocument.currentLayerIndex()):
            self.mMapDocument.setCurrentLayerIndex(currentLayerIndex)
        if (selectedObjects != self.mMapDocument.selectedObjects()):
            self.mSynching = True
            if (selectedObjects.count() == 1):
                o = selectedObjects.first()
                center = o.bounds().center()
                DocumentManager.instance().centerViewOn(center)

            self.mMapDocument.setSelectedObjects(selectedObjects)
            self.mSynching = False

    def onPressed(self, index):
        mapObject = self.model().toMapObject(index)
        if mapObject:
            self.mMapDocument.setCurrentObject(mapObject)
        else:
            objectGroup = self.model().toObjectGroup(index)
            if objectGroup:
                self.mMapDocument.setCurrentObject(objectGroup)

    def onActivated(self, index):
        mapObject = self.model().toMapObject(index)
        if mapObject:
            self.mMapDocument.setCurrentObject(mapObject)
            self.mMapDocument.emitEditCurrentObject()

    def onSectionResized(self, logicalIndex):
        if logicalIndex != 0:
            return

        settings = preferences.Preferences.instance().settings()
        settings.setValue(FIRST_SECTION_SIZE_KEY, self.header().sectionSize(0))

    def selectedObjectsChanged(self):
        if (self.mSynching):
            return
        if (not self.mMapDocument):
            return
        selectedObjects = self.mMapDocument.selectedObjects()
        self.mSynching = True
        self.clearSelection()
        for o in selectedObjects:
            index = self.model().index(o)
            self.selectionModel().select(index, QItemSelectionModel.Select |  QItemSelectionModel.Rows)

        self.mSynching = False
        if (selectedObjects.count() == 1):
            o = selectedObjects.first()
            self.scrollTo(self.model().index(o))
