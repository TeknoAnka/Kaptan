# Copyright 2016 Metehan Özbek <mthnzbk@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

from PyQt6.QtWidgets import (QTabWidget, QGridLayout, QLabel, QPushButton, QGroupBox, QComboBox, QHBoxLayout,
                             QVBoxLayout, QSpacerItem, QWidget, QSizePolicy, QRadioButton, QCheckBox, QFrame,
                             QProgressBar, QSlider, QScrollBar, QListView, QListWidget, QSpinBox, QListWidgetItem,
                             QTextBrowser, QStyleFactory)
from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QEvent, QSize, QRectF
from .tools import (iniToCss, get_cursor_themes, get_icon_themes, get_plasma_themes,
                    get_window_decorations, get_widget_styles, generate_cursor_preview,
                    generate_icon_theme_preview, generate_plasma_theme_preview,
                    get_color_schemes, generate_window_decoration_preview,
                    generate_color_scheme_preview)
import os

class ThemeTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("QTabWidget#tabWidget::tab-bar {alignment:center;}")
        self.setObjectName("tabWidget")
        self.setCurrentIndex(0)

        self.colorSchemePath = "/usr/share/color-schemes"

        self.createTabWidgetStyle()
        self.createTabWindowStyle()
        self.createTabColorScheme()
        self.createTabDesktopTheme()
        self.createTabMouseCursor()
        self.createTabIconSet()


    def createTabWidgetStyle(self):
        self.tabWidgetStyle = QWidget()
        self.tabWidgetStyle.setObjectName("tabWidgetStyle")

        self.verticalLayout = QVBoxLayout(self.tabWidgetStyle)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.labelWidgetStyle = QLabel(self.tabWidgetStyle)
        self.labelWidgetStyle.setText(self.tr("Widget Style:"))
        self.labelWidgetStyle.setObjectName("labelWidgetStyle")
        self.horizontalLayout.addWidget(self.labelWidgetStyle)

        self.comboBoxWidgetStyle = QComboBox(self.tabWidgetStyle)
        self.comboBoxWidgetStyle.setObjectName("comboBoxWidgetStyle")

        # Widget stillerini sistemden dinamik olarak çek
        widget_styles = get_widget_styles()
        for style in widget_styles:
            self.comboBoxWidgetStyle.addItem(style)

        self.horizontalLayout.addWidget(self.comboBoxWidgetStyle)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.verticalLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.previewWidgetStyle = PreviewWidgetStyle(self.tabWidgetStyle)

        # İlk stili uygula
        if widget_styles:
            self.previewWidgetStyle.tabWidget.setStyle(QStyleFactory.create(widget_styles[0]))

        self.verticalLayout.addWidget(self.previewWidgetStyle)


        self.addTab(self.tabWidgetStyle, self.tr("Widget Style"))

        self.comboBoxWidgetStyle.currentTextChanged.connect(self.previewStyle)

    def previewStyle(self, text):
        self.previewWidgetStyle.tabWidget.setStyle(QStyleFactory.create(text))

    def createTabWindowStyle(self):
        self.tabWindowStyle = QWidget()
        self.tabWindowStyle.setObjectName("tabWindowStyle")

        self.verticalLayout_6 = QVBoxLayout(self.tabWindowStyle)
        self.verticalLayout_6.setObjectName("verticalLayout_6")

        self.listWidgetWindowStyle = QListWidget(self.tabWindowStyle)
        self.listWidgetWindowStyle.setResizeMode(QListView.ResizeMode.Adjust)
        self.listWidgetWindowStyle.setIconSize(QSize(340, 105))
        self.listWidgetWindowStyle.setViewMode(QListView.ViewMode.IconMode)
        self.listWidgetWindowStyle.setObjectName("listWidgetWindowStyle")

        # Pencere dekorasyonlarını sistemden dinamik olarak çek
        decorations = get_window_decorations()
        for dec_id, display_name, theme_dir in decorations:
            item = QListWidgetItem(self.listWidgetWindowStyle)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
            preview = generate_window_decoration_preview(dec_id, theme_dir)
            if preview is not None and not preview.isNull():
                item.setIcon(QIcon(preview))
            else:
                # Dekorasyon için sistem ikonunu kullan (stretching engellemek için transparan tuval üzerine ortalanır)
                icon = QIcon.fromTheme("preferences-system-windows")
                if not icon.isNull():
                    pixmap = QPixmap(340, 105)
                    pixmap.fill(QColor(0, 0, 0, 0))
                    painter = QPainter(pixmap)
                    icon.paint(painter, (340 - 64) // 2, (105 - 64) // 2, 64, 64)
                    painter.end()
                    item.setIcon(QIcon(pixmap))
            item.setText(display_name)
            item.setStyleText = dec_id

        self.verticalLayout_6.addWidget(self.listWidgetWindowStyle)

        self.addTab(self.tabWindowStyle, self.tr("Window Style"))

    def createTabColorScheme(self):
        self.tabColorScheme = QWidget()
        self.tabColorScheme.setObjectName("tabColorScheme")

        self.verticalLayout_2 = QVBoxLayout(self.tabColorScheme)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.listWidgetColorScheme = QListWidget(self.tabColorScheme)
        self.listWidgetColorScheme.setObjectName("listWidgetColorScheme")
        self.verticalLayout_2.addWidget(self.listWidgetColorScheme)

        # Renk şemalarını sistemden dinamik olarak çek
        self.listWidgetColorScheme.setIconSize(QSize(64, 40))
        color_schemes = get_color_schemes()
        for display_name, file_path in color_schemes:
            item = QListWidgetItem(self.listWidgetColorScheme)
            item.setText(display_name)
            item.colorSchemeName = file_path
            
            preview = generate_color_scheme_preview(file_path)
            if preview is not None and not preview.isNull():
                item.setIcon(QIcon(preview))

        self.listWidgetColorScheme.itemClicked.connect(self.previewColorScheme)
        if self.listWidgetColorScheme.count() > 0:
            self.listWidgetColorScheme.setCurrentRow(0)

        self.previewWidgetColor = PreviewWidgetColor(self.tabColorScheme)
        self.verticalLayout_2.addWidget(self.previewWidgetColor)

        self.addTab(self.tabColorScheme, self.tr("Color Scheme"))

    def previewColorScheme(self, item):
        css = iniToCss(item.colorSchemeName)
        self.previewWidgetColor.previewGroupBox.setStyleSheet(css[0])
        self.previewWidgetColor.previewTextBrowser.setHtml("""<style>#unclicked {color : rgb(%s);}
        #clicked {color : rgb(%s);}</style>"""%(css[1][0],css[1][1]) +
        self.tr("""<p>Normal text <a id='unclicked' href='#'>link</a> <a id='clicked' href='#'>visited</a></p>"""))

    def createTabDesktopTheme(self):
        self.tabDesktopTheme = QWidget()
        self.tabDesktopTheme.setObjectName("tabDesktopTheme")

        self.gridLayoutDesktop = QGridLayout(self.tabDesktopTheme)
        self.gridLayoutDesktop.setObjectName("gridLayoutDesktop")

        self.listWidgetDesktopTheme = QListWidget(self.tabDesktopTheme)
        self.listWidgetDesktopTheme.setViewMode(QListView.ViewMode.IconMode)
        self.listWidgetDesktopTheme.setResizeMode(QListView.ResizeMode.Adjust)
        self.listWidgetDesktopTheme.setIconSize(QSize(64, 64))
        self.gridLayoutDesktop.addWidget(self.listWidgetDesktopTheme, 0, 0, 1, 1)

        # Plasma masaüstü temalarını sistemden dinamik olarak çek
        plasma_themes = get_plasma_themes()
        for theme_id, theme_dir, display_name in plasma_themes:
            item = QListWidgetItem(self.listWidgetDesktopTheme)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)

            # Masaüstü teması için sistem ikonunu kullan
            icon = QIcon.fromTheme("preferences-desktop-plasma")
            if icon.isNull():
                icon = QIcon.fromTheme("preferences-desktop-theme")
            if icon.isNull():
                icon = QIcon.fromTheme("kde")
            item.setIcon(icon)

            item.setText(display_name)
            item.panelText = theme_id

        self.addTab(self.tabDesktopTheme, self.tr("Desktop Theme"))

    def createTabMouseCursor(self):
        self.tabMouseCursor = QWidget()
        self.tabMouseCursor.setObjectName("tabMouseCursor")

        self.gridLayoutCursor = QGridLayout(self.tabMouseCursor)
        self.gridLayoutCursor.setObjectName("gridLayoutCursor")

        self.listWidgetMouseCursor = QListWidget(self.tabMouseCursor)
        self.listWidgetMouseCursor.setObjectName("listWidgetMouseCursor")
        self.listWidgetMouseCursor.setViewMode(QListView.ViewMode.IconMode)
        self.listWidgetMouseCursor.setResizeMode(QListView.ResizeMode.Adjust)
        self.listWidgetMouseCursor.setIconSize(QSize(220, 40))
        self.gridLayoutCursor.addWidget(self.listWidgetMouseCursor, 0, 0, 1, 1)

        # Cursor temalarını sistemden dinamik olarak çek
        cursor_themes = get_cursor_themes()
        for theme_name, theme_dir, display_name in cursor_themes:
            item = QListWidgetItem(self.listWidgetMouseCursor)
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)

            # Cursor önizleme görselini Xcursor dosyalarından oluştur
            preview = generate_cursor_preview(theme_dir)
            if preview is not None and not preview.isNull():
                item.setIcon(QIcon(preview))
            else:
                # Fallback: genel cursor ikonu
                fallback_icon = QIcon.fromTheme("input-mouse")
                if not fallback_icon.isNull():
                    item.setIcon(fallback_icon)

            item.setText(display_name)
            item.cursorThemeName = theme_name

        self.addTab(self.tabMouseCursor, self.tr("Mouse Cursor"))

    def createTabIconSet(self):
        self.tabIconSet = QWidget()
        self.tabIconSet.setObjectName("tabIconSet")

        self.verticalLayout_3 = QVBoxLayout(self.tabIconSet)
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.listWidgetIconSet = QListWidget(self.tabIconSet)
        self.listWidgetIconSet.setResizeMode(QListView.ResizeMode.Adjust)
        self.listWidgetIconSet.setObjectName("listWidgetIconSet")
        self.listWidgetIconSet.setViewMode(QListView.ViewMode.IconMode)
        self.listWidgetIconSet.setIconSize(QSize(370, 64))

        # İkon temalarını sistemden dinamik olarak çek
        icon_themes = get_icon_themes()
        for theme_name, theme_dir, display_name in icon_themes:
            item = QListWidgetItem(self.listWidgetIconSet)

            # İkon teması önizleme görselini oluştur
            preview = generate_icon_theme_preview(theme_dir)
            if preview is not None and not preview.isNull():
                item.setIcon(QIcon(preview))
            else:
                # Fallback: genel ikon teması ikonu
                fallback_icon = QIcon.fromTheme("preferences-desktop-icons")
                if not fallback_icon.isNull():
                    item.setIcon(fallback_icon)

            item.setText(display_name)
            item.iconThemeName = theme_name

        self.verticalLayout_3.addWidget(self.listWidgetIconSet)

        self.addTab(self.tabIconSet, self.tr("Icon Set"))


class PreviewWidgetStyle(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Preview"))
        self.setMaximumHeight(220)
        self.setObjectName("groupBox")

        self.verticalLayout = QVBoxLayout(self)
        self.verticalLayout.setObjectName("verticalLayout")

        self.tabWidget = QTabWidget(self)
        self.tabWidget.setObjectName("tabWidgetPreview")

        self.tab = QWidget()
        self.tab.setObjectName("tab")

        self.horizontalLayout = QHBoxLayout(self.tab)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.groupBox = QGroupBox(self.tab)
        self.groupBox.setTitle(self.tr("Group Box"))
        self.groupBox.setObjectName("groupBox")


        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")

        self.radioButton = QRadioButton(self.groupBox)
        self.radioButton.setText(self.tr("Radio Button"))
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName("radioButton")
        self.verticalLayout_2.addWidget(self.radioButton)

        self.radioButton_2 = QRadioButton(self.groupBox)
        self.radioButton_2.setText(self.tr("Radio Button"))
        self.radioButton_2.setObjectName("radioButton_2")
        self.verticalLayout_2.addWidget(self.radioButton_2)

        self.line = QFrame(self.groupBox)
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)

        self.checkBox = QCheckBox(self.groupBox)
        self.checkBox.setText(self.tr("Check Box"))
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.verticalLayout_2.addWidget(self.checkBox)

        self.horizontalLayout.addWidget(self.groupBox)


        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")

        self.progressBar = QProgressBar(self.tab)
        self.progressBar.setProperty("value", 75)
        self.progressBar.setObjectName("progressBar")
        self.verticalLayout_3.addWidget(self.progressBar)

        self.horizontalSlider = QSlider(self.tab)
        self.horizontalSlider.setProperty("value", 45)
        self.horizontalSlider.setSliderPosition(45)
        self.horizontalSlider.setOrientation(Qt.Orientation.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.verticalLayout_3.addWidget(self.horizontalSlider)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")

        self.spinBox = QSpinBox(self.tab)
        self.spinBox.setObjectName("spinBox")
        self.horizontalLayout_2.addWidget(self.spinBox)

        self.pushButton = QPushButton(self.tab)
        self.pushButton.setText(self.tr("Button"))
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout_2.addWidget(self.pushButton)

        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.comboBox = QComboBox(self.tab)
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem(self.tr("Combo Box"))
        self.verticalLayout_3.addWidget(self.comboBox)

        self.horizontalLayout.addLayout(self.verticalLayout_3)

        self.verticalScrollBar = QScrollBar(self.tab)
        self.verticalScrollBar.setPageStep(50)
        self.verticalScrollBar.setOrientation(Qt.Orientation.Vertical)
        self.verticalScrollBar.setObjectName("verticalScrollBar")
        self.horizontalLayout.addWidget(self.verticalScrollBar)
        self.tabWidget.addTab(self.tab, self.tr("Tab 1"))


        self.tab_2 = QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, self.tr("Tab 2"))

        self.verticalLayout.addWidget(self.tabWidget)

        self.pushButton.installEventFilter(self)
        self.pushButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.radioButton.installEventFilter(self)
        self.radioButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.radioButton_2.installEventFilter(self)
        self.radioButton_2.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.checkBox.installEventFilter(self)
        self.checkBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.comboBox.installEventFilter(self)
        self.comboBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.spinBox.installEventFilter(self)
        self.spinBox.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.horizontalSlider.installEventFilter(self)
        self.horizontalSlider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.verticalScrollBar.installEventFilter(self)
        self.verticalScrollBar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tab.installEventFilter(self)
        self.tab.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tab_2.installEventFilter(self)
        self.tab_2.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.tabWidget.installEventFilter(self)
        self.tabWidget.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.tabWidget.currentChanged.connect(self.noClick)

    def noClick(self, x):
        self.tabWidget.setCurrentIndex(0)

    def eventFilter(self, obj, event):
        if self.pushButton:
            if event.type() == QEvent.Type.MouseButtonRelease:
                return True
            elif event.type() == QEvent.Type.MouseButtonPress:
                return True
            elif event.type() == QEvent.Type.MouseButtonDblClick:
                return True
            else:
                return False
        else:
            super().eventFilter(obj, event)


class PreviewWidgetColor(QGroupBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(self.tr("Preview"))
        self.setMaximumHeight(180)
        self.parent = parent

        vboxLayout = QVBoxLayout(self)
        self.previewGroupBox = QGroupBox(self)
        self.previewGroupBox.setObjectName("previewGroupBox")
        vboxLayout.addWidget(self.previewGroupBox)

        self.horizontalLayout = QHBoxLayout(self.previewGroupBox)
        self.verticalLayout = QVBoxLayout()
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.previewLabel = QLabel(self.previewGroupBox)
        self.previewLabel.setText(self.tr("Window Text"))
        self.previewLabel.setObjectName("previewLabel")
        self.verticalLayout.addWidget(self.previewLabel)

        self.previewPushButton = QPushButton(self.previewGroupBox)
        self.previewPushButton.setText(self.tr("Button"))
        self.previewPushButton.setObjectName("previewPushButton")
        self.verticalLayout.addWidget(self.previewPushButton)

        self.previewTextBrowser = QTextBrowser(self.previewGroupBox)
        self.previewTextBrowser.setObjectName("previewTextBrowser")

        # İlk renk şeması için CSS oluştur
        listWidget = self.parent.children()[1]
        if listWidget.count() > 0:
            currentItem = listWidget.currentItem()
            if currentItem and hasattr(currentItem, 'colorSchemeName'):
                css = iniToCss(currentItem.colorSchemeName)

                self.previewTextBrowser.setHtml("""<style>#unclicked {color : rgb(%s);}
                #clicked {color : rgb(%s);}</style>"""%(css[1][0],css[1][1]) +
                self.tr("""<p>Normal text <a id='unclicked' href='#'>link</a> <a id='clicked' href='#'>visited</a></p>"""))


        self.horizontalLayout.addWidget(self.previewTextBrowser)


        self.previewPushButton.installEventFilter(self.previewGroupBox)
        self.previewPushButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        self.previewTextBrowser.installEventFilter(self.previewGroupBox)
        self.previewTextBrowser.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.previewTextBrowser.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

    def eventFilter(self, obj, event):
        if self.previewPushButton:
            if event.type() == QEvent.Type.MouseButtonRelease:
                return True
            elif event.type() == QEvent.Type.MouseButtonPress:
                return True
            elif event.type() == QEvent.Type.MouseButtonDblClick:
                return True

            else:
                return False
        else:
            super().eventFilter(obj, event)
