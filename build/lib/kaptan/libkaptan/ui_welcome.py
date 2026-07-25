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

import os
from PyQt6.QtWidgets import QWizardPage, QLabel, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QFrame #, QAction
from PyQt6.QtCore import Qt, QT_VERSION_STR, PYQT_VERSION_STR, QSysInfo
from PyQt6.QtSvgWidgets import QSvgWidget
from .version import Version


class WelcomeWidget(QWizardPage):
    def get_welcome_image_path(self):
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        candidates = [
            os.path.join(base_dir, "data", "images", "kaptan_welcome.svg"),
            os.path.join(base_dir, "data", "images", "kaptan-welcome.svg"),
            "/usr/share/kaptan/images/kaptan_welcome.svg",
            "/usr/share/kaptan/images/kaptan-welcome.svg",
            "data/images/kaptan_welcome.svg",
            "data/images/kaptan-welcome.svg",
            ":/data/images/kaptan_welcome.svg",
            ":/data/images/kaptan-welcome.svg",
        ]
        for path in candidates:
            if path.startswith(":") or os.path.exists(path):
                return path
        return None

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSubTitle(self.tr("<h2>Welcome to LupuS!</h2>"))

        # Ana düzen
        vlayout = QVBoxLayout(self)
        vlayout.setContentsMargins(20, 20, 20, 20)
        vlayout.setSpacing(15)

        # Üst bölüm: Açıklama ve Logo Kartı
        content_layout = QHBoxLayout()
        content_layout.setSpacing(25)

        # Sol sütun: Açıklama yazıları
        desc_container = QFrame(self)
        desc_container.setObjectName("descContainer")
        desc_layout = QVBoxLayout(desc_container)
        desc_layout.setContentsMargins(0, 0, 0, 0)
        desc_layout.setSpacing(10)

        title = QLabel(self)
        title.setText(self.tr("<h1>What is LupuS?</h1>"))
        title.setTextFormat(Qt.TextFormat.RichText)
        desc_layout.addWidget(title)

        body = QLabel(self)
        body.setText(self.tr(
            "<p><strong>LupuS</strong> is a reliable, secure, fast and user friendly operating system.</p>"
            "<p>With LupuS, you can connect to the internet, read your e-mails, work with your office documents, "
            "watch movies, play music, develop applications, play games and much more!</p>"
            "<p><strong>Kaptan</strong>, will help you personalize your LupuS workspace easily and quickly. "
            "Please click <strong>Next</strong> in order to begin.</p>"
        ))
        body.setWordWrap(True)
        body.setTextFormat(Qt.TextFormat.RichText)
        desc_layout.addWidget(body)

        content_layout.addWidget(desc_container, 1)

        # Sağ sütun: Welcome SVG Görseli
        welcome_img_path = self.get_welcome_image_path()
        if welcome_img_path:
            logo_container = QFrame(self)
            logo_container.setObjectName("welcomeLogoContainer")
            logo_layout = QVBoxLayout(logo_container)
            logo_layout.setContentsMargins(10, 10, 10, 10)
            logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            svg_widget = QSvgWidget(welcome_img_path, logo_container)
            svg_widget.setFixedSize(240, 240)
            logo_layout.addWidget(svg_widget)

            content_layout.addWidget(logo_container, 0, Qt.AlignmentFlag.AlignCenter)

        vlayout.addLayout(content_layout)

        # Dikey esneme payı
        vlayout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding))

        # Alt bölüm: Sistem Bilgi Kartları
        info_group = QFrame(self)
        info_group.setObjectName("infoGroup")
        info_layout = QHBoxLayout(info_group)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(12)

        def create_info_card(title_text, val_text):
            card = QFrame(self)
            card.setObjectName("infoCard")
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 8, 10, 8)
            card_layout.setSpacing(2)
            card_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            lbl_title = QLabel(title_text, card)
            lbl_title.setObjectName("cardTitle")
            lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

            lbl_val = QLabel(val_text, card)
            lbl_val.setObjectName("cardVal")
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_val.setWordWrap(True)

            card_layout.addWidget(lbl_title)
            card_layout.addWidget(lbl_val)
            return card

        # Bilgi kartlarını oluştur ve ekle
        card_os = create_info_card(self.tr("OS"), f"{QSysInfo.prettyProductName()}")
        card_kernel = create_info_card(self.tr("KERNEL"), QSysInfo.kernelVersion().split("-")[0])
        card_kaptan = create_info_card(self.tr("KAPTAN"), f"v{Version.VersionString}")
        card_qt = create_info_card(self.tr("QT / PYQT"), f"{QT_VERSION_STR} / {PYQT_VERSION_STR}")

        info_layout.addWidget(card_os)
        info_layout.addWidget(card_kernel)
        info_layout.addWidget(card_kaptan)
        info_layout.addWidget(card_qt)

        vlayout.addWidget(info_group)

        # Görsel stil ayarları
        self.setStyleSheet("""
            QLabel {
                font-family: 'Segoe UI', 'Outfit', 'Inter', 'Noto Sans', sans-serif;
            }
            #infoCard {
                background-color: rgba(255, 255, 255, 0.04);
                border: 1px solid rgba(128, 128, 128, 0.15);
                border-radius: 10px;
            }
            #infoCard:hover {
                border: 1px solid #409eff;
                background-color: rgba(64, 158, 255, 0.05);
            }
            #cardTitle {
                color: #888888;
                font-size: 9px;
                font-weight: bold;
                letter-spacing: 1px;
            }
            #cardVal {
                font-size: 11px;
                font-weight: bold;
            }
        """)
