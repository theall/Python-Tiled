##
# layerdock.py
# Copyright 2008-2013, Thorbjørn Lindeijer <thorbjorn@lindeijer.nl>
# Copyright 2010, Andrew G. Crowell <overkill9999@gmail.com>
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
from mapdocumentactionhandler import MapDocumentActionHandler
from layermodel import LayerModel
from PyQt5.QtGui import (
    QIcon
)
from PyQt5.QtCore import (
    Qt,
    QSize,
    QModelIndex,
    QEvent
)
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QSlider,
    QHBoxLayout,
    QVBoxLayout,
    QToolBar,
    QMenu,
    QToolButton,
    QTreeView,
    QDockWidget
)
##
# The dock widget that displays the map layers.
##
class LayerDock(QDockWidget):
    ##
    # Constructor.
    ##
    def __init__(self, parent = None):
        super().__init__(parent)
        self.mOpacityLabel = QLabel()
        self.mOpacitySlider = QSlider(Qt.Horizontal)
        self.mLayerView = LayerView()
        self.mMapDocument = None
        self.mUpdatingSlider = False
        self.mChangingLayerOpacity = False
        self.mUpdatingSlider = False

        self.setObjectName("layerDock")
        widget = QWidget(self)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        opacityLayout = QHBoxLayout()
        self.mOpacitySlider.setRange(0, 100)
        self.mOpacitySlider.setEnabled(False)
        opacityLayout.addWidget(self.mOpacityLabel)
        opacityLayout.addWidget(self.mOpacitySlider)
        self.mOpacityLabel.setBuddy(self.mOpacitySlider)
        handler = MapDocumentActionHandler.instance()
        newLayerMenu = QMenu(self)
        newLayerMenu.addAction(handler.actionAddTileLayer())
        newLayerMenu.addAction(handler.actionAddObjectGroup())
        newLayerMenu.addAction(handler.actionAddImageLayer())
        newIcon = QIcon(":/images/16x16/document-new.png")
        newLayerButton = QToolButton()
        newLayerButton.setPopupMode(QToolButton.InstantPopup)
        newLayerButton.setMenu(newLayerMenu)
        newLayerButton.setIcon(newIcon)
        Utils.setThemeIcon(newLayerButton, "document-new")
        buttonContainer = QToolBar()
        buttonContainer.setFloatable(False)
        buttonContainer.setMovable(False)
        buttonContainer.setIconSize(QSize(16, 16))
        buttonContainer.addWidget(newLayerButton)
        buttonContainer.addAction(handler.actionMoveLayerUp())
        buttonContainer.addAction(handler.actionMoveLayerDown())
        buttonContainer.addAction(handler.actionDuplicateLayer())
        buttonContainer.addAction(handler.actionRemoveLayer())
        buttonContainer.addSeparator()
        buttonContainer.addAction(handler.actionToggleOtherLayers())
        listAndToolBar = QVBoxLayout()
        listAndToolBar.setSpacing(0)
        listAndToolBar.addWidget(self.mLayerView)
        listAndToolBar.addWidget(buttonContainer)
        layout.addLayout(opacityLayout)
        layout.addLayout(listAndToolBar)
        self.setWidget(widget)
        self.retranslateUi()
        self.mOpacitySlider.valueChanged.connect(self.sliderValueChanged)
        self.updateOpacitySlider()

    ##
    # Sets the map for which the layers should be displayed.
    ##
    def setMapDocument(self, mapDocument):
        if (self.mMapDocument == mapDocument):
            return
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
        self.mMapDocument = mapDocument
        if (self.mMapDocument):
            self.mMapDocument.currentLayerIndexChanged.connect(self.updateOpacitySlider)
            self.mMapDocument.layerChanged.connect(self.layerChanged)
            self.mMapDocument.editLayerNameRequested.connect(self.editLayerName)

        self.mLayerView.setMapDocument(mapDocument)
        self.updateOpacitySlider()

    def changeEvent(self, e):
        super().changeEvent(e)
        x = e.type()
        if x==QEvent.LanguageChange:
            self.retranslateUi()
        else:
            pass

    def updateOpacitySlider(self):
        enabled = bool(self.mMapDocument and self.mMapDocument.currentLayerIndex() != -1)
        self.mOpacitySlider.setEnabled(enabled)
        self.mOpacityLabel.setEnabled(enabled)
        self.mUpdatingSlider = True
        if (enabled):
            opacity = self.mMapDocument.currentLayer().opacity()
            self.mOpacitySlider.setValue(opacity * 100)
        else:
            self.mOpacitySlider.setValue(100)

        self.mUpdatingSlider = False

    def layerChanged(self, index):
        if (index != self.mMapDocument.currentLayerIndex()):
            return
        # Don't update the slider when we're the ones changing the layer opacity
        if (self.mChangingLayerOpacity):
            return
        self.updateOpacitySlider()

    def editLayerName(self):
        if (not self.isVisible()):
            return
        layerModel = self.mMapDocument.layerModel()
        currentLayerIndex = self.mMapDocument.currentLayerIndex()
        row = layerModel.layerIndexToRow(currentLayerIndex)
        self.raise_()
        self.mLayerView.edit(layerModel.index(row))

    def sliderValueChanged(self, opacity):
        if (not self.mMapDocument):
            return
        # When the slider changes value just because we're updating it, it
        # shouldn't try to set the layer opacity.
        if (self.mUpdatingSlider):
            return
        layerIndex = self.mMapDocument.currentLayerIndex()
        if (layerIndex == -1):
            return
        layer = self.mMapDocument.map().layerAt(layerIndex)
        if ( (layer.opacity() * 100) != opacity):
            self.mChangingLayerOpacity = True
            layerModel = self.mMapDocument.layerModel()
            row = layerModel.layerIndexToRow(layerIndex)
            layerModel.setData(layerModel.index(row),
                                opacity / 100,
                                LayerModel.UserRoles.OpacityRole)
            self.mChangingLayerOpacity = False

    def retranslateUi(self):
        self.setWindowTitle(self.tr("Layers"))
        self.mOpacityLabel.setText(self.tr("Opacity:"))

##
# This view makes sure the size hint makes sense and implements the context
# menu.
##
class LayerView(QTreeView):

    def __init__(self, parent = None):
        super().__init__(parent)

        self.setRootIsDecorated(False)
        self.setHeaderHidden(True)
        self.setItemsExpandable(False)
        self.setUniformRowHeights(True)
        self.pressed.connect(self.indexPressed)

        self.mMapDocument = None

    def sizeHint(self):
        return QSize(130, 100)

    def setMapDocument(self, mapDocument):
        if (self.mMapDocument):
            self.mMapDocument.disconnect()
            s = self.selectionModel()
            s.currentRowChanged.disconnect(self.currentRowChanged)

        self.mMapDocument = mapDocument
        if (self.mMapDocument):
            self.setModel(self.mMapDocument.layerModel())
            self.mMapDocument.currentLayerIndexChanged.connect(self.currentLayerIndexChanged)
            s = self.selectionModel()
            s.currentRowChanged.connect(self.currentRowChanged)
            self.currentLayerIndexChanged(self.mMapDocument.currentLayerIndex())
        else:
            self.setModel(None)

    def contextMenuEvent(self, event):
        if (not self.mMapDocument):
            return

        index = self.indexAt(event.pos())
        m = self.mMapDocument.layerModel()
        layerIndex = m.toLayerIndex(index)
        handler = MapDocumentActionHandler.instance()
        menu = QMenu()
        menu.addAction(handler.actionAddTileLayer())
        menu.addAction(handler.actionAddObjectGroup())
        menu.addAction(handler.actionAddImageLayer())
        if (layerIndex >= 0):
            menu.addAction(handler.actionDuplicateLayer())
            menu.addAction(handler.actionMergeLayerDown())
            menu.addAction(handler.actionRemoveLayer())
            menu.addSeparator()
            menu.addAction(handler.actionMoveLayerUp())
            menu.addAction(handler.actionMoveLayerDown())
            menu.addSeparator()
            menu.addAction(handler.actionToggleOtherLayers())
            menu.addSeparator()
            menu.addAction(handler.actionLayerProperties())

        menu.exec(event.globalPos())

    def keyPressEvent(self, event):
        if (not self.mMapDocument):
            return
        index = self.currentIndex()
        if (not index.isValid()):
            return
        m = self.mMapDocument.layerModel()
        layerIndex = m.toLayerIndex(index)
        if (event.key() == Qt.Key_Delete):
            self.mMapDocument.removeLayer(layerIndex)
            return

        super().keyPressEvent(event)

    def currentRowChanged(self, index):
        layer = self.mMapDocument.layerModel().toLayerIndex(index)
        self.mMapDocument.setCurrentLayerIndex(layer)

    def indexPressed(self, index):
        layerIndex = self.mMapDocument.layerModel().toLayerIndex(index)
        if (layerIndex != -1):
            layer = self.mMapDocument.map().layerAt(layerIndex)
            self.mMapDocument.setCurrentObject(layer)

    def currentLayerIndexChanged(self, index):
        if (index > -1):
            layerModel = self.mMapDocument.layerModel()
            row = layerModel.layerIndexToRow(index)
            self.setCurrentIndex(layerModel.index(row, 0))
        else:
            self.setCurrentIndex(QModelIndex())
