#!/usr/bin/env python3
#
# Copyright 2016 Metehan Özbek <mthnzbk@gmail.com>
#           2020 Erdem Ersoy <erdemersoy@erdemersoy.net>
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

import sys
import os
from PyQt6 import QtWidgets
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, pyqtSignal, QProcess, QLocale, QTranslator, QThread
from kaptan.libkaptan import *



class Kaptan(QtWidgets.QWizard):
    def __init__(self):
        super().__init__()
        self.resize(1220, 720)
        self.setMinimumSize(1220, 720)

        self.setWindowTitle(self.tr("Kaptan"))
        self.setWindowIcon(QIcon.fromTheme("kaptan-icon"))

        # System-synchronized Modern Stylesheet
        self.setStyleSheet("""
            QWizard {
                background-color: palette(window);
                color: palette(window-text);
            }
            QWizardPage {
                background-color: palette(window);
            }
            QWizard > QWidget {
                background-color: palette(window);
            }
            QLabel {
                color: palette(window-text);
                font-size: 13px;
            }
            QLabel[text^="<h2>"] {
                color: palette(highlight);
                font-size: 20px;
                font-weight: bold;
            }
            QLabel[text^="<h1>"] {
                color: palette(highlight);
                font-size: 24px;
                font-weight: bold;
            }
            QGroupBox {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
                color: palette(window-text);
                padding-top: 16px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 12px;
                padding: 2px 8px;
                background-color: palette(window);
                border-radius: 4px;
            }
            QPushButton {
                background-color: palette(button);
                color: palette(button-text);
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 8px 24px;
                font-size: 13px;
                font-weight: 600;
                min-height: 24px;
                outline: none;
            }
            QPushButton:hover {
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border-color: palette(highlight);
            }
            QPushButton:pressed {
                background-color: palette(dark);
                padding: 9px 24px 7px 24px;
            }
            QPushButton:focus {
                border: 2px solid palette(highlight);
            }
            QPushButton:disabled {
                background-color: palette(window);
                color: palette(mid);
                border-color: palette(midlight);
            }
            QWizard > QWidget > QPushButton {
                min-width: 110px;
                min-height: 32px;
                padding: 8px 28px;
                font-size: 14px;
                border-radius: 10px;
            }
            QWizard > QWidget > QPushButton:hover {
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border-color: palette(highlight);
            }
            QWizard > QWidget > QPushButton:pressed {
                background-color: palette(dark);
            }
            QListWidget {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 8px;
                padding: 4px;
                color: palette(text);
            }
            QListWidget::item {
                background-color: transparent;
                border-radius: 6px;
                padding: 8px;
                margin: 2px;
            }
            QListWidget::item:hover {
                background-color: palette(window);
                color: palette(window-text);
            }
            QListWidget::item:selected {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
            QComboBox {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 6px;
                padding: 6px 12px;
                color: palette(text);
                min-width: 120px;
            }
            QComboBox:hover {
                border-color: palette(highlight);
            }
            QComboBox::drop-down {
                border: none;
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 24px;
            }
            QComboBox QAbstractItemView {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 6px;
                selection-background-color: palette(highlight);
                selection-color: palette(highlighted-text);
                color: palette(text);
            }
            QSpinBox {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 6px;
                padding: 6px 12px;
                color: palette(text);
            }
            QSpinBox:hover {
                border-color: palette(highlight);
            }
            QCheckBox, QRadioButton {
                color: palette(window-text);
                spacing: 8px;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QTabWidget::pane {
                border: 1px solid palette(mid);
                border-radius: 8px;
                background-color: palette(window);
                top: -1px;
            }
            QTabBar::tab {
                background-color: palette(button);
                color: palette(button-text);
                border: 1px solid palette(mid);
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                padding: 8px 16px;
                margin-right: 4px;
            }
            QTabBar::tab:hover {
                background-color: palette(window);
                color: palette(window-text);
            }
            QTabBar::tab:selected {
                background-color: palette(window);
                color: palette(highlight);
                border-color: palette(mid);
                border-bottom: 1px solid palette(window);
                font-weight: bold;
            }
            QProgressBar {
                border: 1px solid palette(mid);
                border-radius: 4px;
                text-align: center;
                color: palette(highlighted-text);
                background-color: palette(base);
            }
            QProgressBar::chunk {
                background-color: palette(highlight);
                border-radius: 3px;
            }
            QSlider::groove:horizontal {
                border: 1px solid palette(mid);
                height: 6px;
                background: palette(base);
                margin: 2px 0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: palette(highlight);
                border: none;
                width: 14px;
                height: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
            QSlider::handle:horizontal:hover {
                background: palette(highlight);
            }
            QScrollBar:vertical {
                background: palette(window);
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: palette(mid);
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: palette(highlight);
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QTextBrowser {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 8px;
                color: palette(text);
            }
        """)

        self.setButtonText(QtWidgets.QWizard.WizardButton.NextButton, self.tr("Next"))
        self.button(QtWidgets.QWizard.WizardButton.NextButton).setIcon(QIcon.fromTheme("arrow-right"))
        self.button(QtWidgets.QWizard.WizardButton.NextButton).setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.setButtonText(QtWidgets.QWizard.WizardButton.CancelButton, self.tr("Cancel"))
        self.button(QtWidgets.QWizard.WizardButton.CancelButton).setIcon(QIcon.fromTheme("dialog-cancel"))
        self.setOption(QtWidgets.QWizard.WizardOption.NoCancelButtonOnLastPage, True)
        self.setOption(QtWidgets.QWizard.WizardOption.CancelButtonOnLeft, True)

        self.setButtonText(QtWidgets.QWizard.WizardButton.BackButton, self.tr("Back"))
        self.setOption(QtWidgets.QWizard.WizardOption.NoBackButtonOnLastPage, True)
        self.setOption(QtWidgets.QWizard.WizardOption.NoBackButtonOnStartPage, True)
        self.button(QtWidgets.QWizard.WizardButton.BackButton).setIcon(QIcon.fromTheme("arrow-left"))

        self.setButtonText(QtWidgets.QWizard.WizardButton.FinishButton, self.tr("Finish"))
        self.button(QtWidgets.QWizard.WizardButton.FinishButton).setIcon(QIcon.fromTheme("dialog-ok-apply"))

        self.addPage(WelcomeWidget(self))
        self.addPage(MouseWidget(self))
        self.addPage(ThemeWidget(self))
        self.addPage(WallpaperWidget(self))
        self.addPage(AvatarWidget(self))
        self.sumId = self.addPage(SummaryWidget(self))
        self.otherId = self.addPage(OtherWidget(self))

        self.currentIdChanged.connect(self.optionsAccepted)
        self.button(QtWidgets.QWizard.WizardButton.FinishButton).clicked.connect(self.close)

    summaryVisible = pyqtSignal()

    def optionsAccepted(self, identity):
        if identity == self.otherId:
            # MouseWidget
            self.page(1).execute()
            # ThemeWidget
            self.page(2).execute()
            # WallpaperWidget
            self.page(3).execute()
            # AvatarWidget
            self.page(4).execute()

            QProcess.startDetached("kquitapp6", ["plasmashell"])
            QThread.msleep(2000)
            QProcess.startDetached("kstart", ["plasmashell"])

        if identity == self.sumId:
            self.setButtonText(QtWidgets.QWizard.WizardButton.NextButton, self.tr("Apply Settings"))
            self.button(QtWidgets.QWizard.WizardButton.NextButton).setIcon(QIcon.fromTheme("dialog-ok-apply"))
            self.summaryVisible.emit()
        else:
            self.setButtonText(QtWidgets.QWizard.WizardButton.NextButton, self.tr("Next"))
            self.button(QtWidgets.QWizard.WizardButton.NextButton).setIcon(QIcon.fromTheme("arrow-right"))

    def closeEvent(self, event):
        desktop_file = os.path.join(os.environ["HOME"], ".config", "autostart", "kaptan.desktop")
        if os.path.exists(desktop_file):
            os.remove(desktop_file)


def main():
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("Kaptan")
    app.setOrganizationName("Kaptan")
    app.setApplicationVersion(Version.getVersion())

    locale = QLocale.system().name()
    translator = QTranslator(app)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    local_qm = os.path.join(base_dir, "languages", "{}.qm".format(locale))
    if os.path.exists(local_qm):
        translator.load(local_qm)
    else:
        translator.load("/usr/share/kaptan/languages/{}.qm".format(locale))
    app.installTranslator(translator)

    kaptan = Kaptan()
    kaptan.show()
    app.exec()


if __name__ == "__main__":
    main()
