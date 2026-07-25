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

from PyQt6.QtWidgets import QWizardPage, QLabel, QGroupBox, QVBoxLayout, QSpacerItem, QSizePolicy, QHBoxLayout,\
    QComboBox, QPushButton, QFileDialog
from PyQt6.QtGui import *
from PyQt6.QtCore import *

from PyQt6.QtMultimediaWidgets import QVideoWidget #QCameraViewfinder
from PyQt6.QtMultimedia import QCamera, QCameraDevice, QImageCapture, QMediaDevices, QMediaCaptureSession #QCameraInfo, QCameraImageCapture, QCameraImageProcessing

import os
import shutil
import subprocess
import getpass


class AvatarWidget(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSubTitle(self.tr("<h2>Create Your Avatar</h2>"))

        vlayout = QVBoxLayout(self)

        labelLayout = QHBoxLayout()
        labelImage = QLabel()
        labelImage.setPixmap(QIcon.fromTheme("preferences-desktop-user").pixmap(64, 64))
        labelImage.setMaximumSize(64, 64)
        labelLayout.addWidget(labelImage)

        label = QLabel(self)
        label.setWordWrap(True)
        label.setText(self.tr("<p>This screen helps you set your <strong>user picture</strong>. You can either choose "
                              "an image from a file or you can capture an image from your camera. Select an option "
                              "from the <strong>options</strong> menu.</p>"))
        labelLayout.addWidget(label)
        vlayout.addLayout(labelLayout)

        vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))

        centerLayout = QHBoxLayout()
        centerLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))

        groupBox = QGroupBox()
        groupBox.setMaximumWidth(500)
        vlayout2 = QVBoxLayout(groupBox)
        hlayout = QHBoxLayout()

        comboBox = QComboBox()
        comboBox.setMinimumWidth(250)
        comboBox.addItems([self.tr("Options"), self.tr("Choose an Image...")])

        #Camera control
        self.cameraInfo = None
        self.camera = None
        self.cameraImageCapture = None
        self.captureSession = None

        try:
            cameras = QMediaDevices.videoInputs()
            if len(cameras):
                self.cameraInfo = cameras[0]
                comboBox.addItem(self.tr("Camera ") + self.cameraInfo.description())
                self.camera = QCamera(self.cameraInfo)
                self.captureSession = QMediaCaptureSession()
                self.captureSession.setCamera(self.camera)
                self.cameraImageCapture = QImageCapture()
                self.captureSession.setImageCapture(self.cameraImageCapture)
                self.cameraImageCapture.imageCaptured.connect(self.imageCapture)
        except Exception:
            pass



        self.buttonCam = QPushButton()
        self.buttonCam.setText(self.tr("Capture"))
        self.buttonCam.setIcon(QIcon.fromTheme("camera-web"))
        self.buttonCam.setEnabled(False)

        self.buttonReplay = QPushButton()
        self.buttonReplay.setText(self.tr("Recapture"))
        self.buttonReplay.setIcon(QIcon.fromTheme("view-refresh"))
        self.buttonReplay.setEnabled(False)

        hlayout.addWidget(comboBox)
        hlayout.addItem(QSpacerItem(300, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))
        hlayout.addWidget(self.buttonCam)
        hlayout.addWidget(self.buttonReplay)

        vlayout2.addLayout(hlayout)

        hlayout2 = QHBoxLayout()

        hlayout2.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))

        self.cameraLabel = QLabel()
        self.cameraLabel.setScaledContents(True)
        self.cameraLabel.setStyleSheet("background-color: black;")
        self.cameraLabel.setMinimumSize(320, 240)
        self.cameraLabel.setMaximumSize(320, 240)

        # self.cameraView = QCameraViewfinder()
        self.cameraView = QVideoWidget()
        self.cameraView.setMaximumSize(320,240)
        self.cameraView.setMinimumSize(320,240)
        self.cameraView.hide()

        hlayout2.addWidget(self.cameraLabel)
        hlayout2.addWidget(self.cameraView)

        hlayout2.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))
        vlayout2.addLayout(hlayout2)

        centerLayout.addWidget(groupBox)
        centerLayout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))
        vlayout.addLayout(centerLayout)
        vlayout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred))

        comboBox.currentIndexChanged.connect(self.avatarSelect)
        self.buttonCam.clicked.connect(self.buttonCamChanged)
        self.buttonReplay.clicked.connect(self.buttonReplayChanged)

        self.userAvatar = None

    def avatarSelect(self, index):
        if index == 0:
            if self.camera is not None:
                QTimer.singleShot(0, self.camera.stop)
            self.buttonReplay.setEnabled(False)
            self.buttonCam.setEnabled(False)
            self.cameraView.hide()
            self.cameraLabel.show()
        elif index == 1:
            if self.camera is not None:
                QTimer.singleShot(0, self.camera.stop)
            self.userAvatar = None
            self.buttonReplay.setEnabled(False)
            self.buttonCam.setEnabled(False)
            self.cameraView.hide()
            self.cameraLabel.show()
            file_url, file_type = QFileDialog.getOpenFileName(self, self.tr("Choose Avatar"), QDir.homePath(), "Image (*.png *.jpg)")
            if file_url != "":
                p = QPixmap(file_url)
                self.cameraLabel.setPixmap(p)
                self.userAvatar = file_url
        elif index == 2:
            self.userAvatar = None
            self.cameraLabel.hide()
            self.cameraView.show()
            if self.captureSession:
                self.captureSession.setVideoOutput(self.cameraView)
            if self.camera:
                self.camera.start()
            self.buttonCam.setEnabled(True)
            self.buttonReplay.setEnabled(False)

    def buttonCamChanged(self):
        self.buttonCam.setEnabled(False)
        self.buttonReplay.setEnabled(True)
        if self.cameraImageCapture:
            self.cameraImageCapture.capture()

    def buttonReplayChanged(self):
        self.userAvatar = None
        self.buttonReplay.setEnabled(False)
        self.buttonCam.setEnabled(True)
        if self.camera:
            self.camera.start()
        self.cameraLabel.hide()
        self.cameraView.show()

    def imageCapture(self, id, preview):
        try:
            if not preview.isNull():
                pixmap = QPixmap.fromImage(preview)
                preview.save("/tmp/avatar.jpg")
                self.userAvatar = "/tmp/avatar.jpg"
                self.cameraView.hide()
                self.cameraLabel.show()
                self.cameraLabel.setPixmap(pixmap)
            if self.camera is not None:
                QTimer.singleShot(100, self.camera.stop)
        except Exception as e:
            print("Error capturing image:", e)

    def execute(self):
        try:
            if self.userAvatar and os.path.exists(self.userAvatar):
                username = os.environ.get("USER") or getpass.getuser()
                user_face = os.path.join(QDir.homePath(), ".face.icon")
                shutil.copy(self.userAvatar, user_face)

                dest = f"/var/lib/AccountsService/icons/{username}"
                try:
                    shutil.copy(self.userAvatar, dest)
                except (PermissionError, OSError):
                    subprocess.run(["pkexec", "cp", self.userAvatar, dest], capture_output=True)
        except Exception as e:
            with open("/tmp/.kaptan.bug", "w") as d:
                d.write(f"Avatar couldn't be changed: {e}")
