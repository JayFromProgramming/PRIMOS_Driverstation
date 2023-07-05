from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging


class RoverConnectionUI(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Rover Connection", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        # This element contains no controls, it just displays the connection status
        self.target_address = QLabel(f"<pre>Addr:   {self.robot.address}:{self.robot.port}</pre>", self)
        self.target_address.setStyleSheet("color: black; font-size: 13px; font-weight: bold;")
        # self.target_address.setFixedSize(100, 25)
        self.target_address.move(10, 16)

        self.connection_status = QLabel("<pre>Status: Disconnected</pre>", self)
        self.connection_status.setStyleSheet("color: red; font-size: 13px; font-weight: bold;")
        # self.connection_status.setFixedSize(150, 25)
        self.connection_status.move(10, 30)

        self.connection_check_timer = Qt.QTimer(self)
        self.connection_check_timer.timeout.connect(self.connection_check_loop)
        self.connection_check_timer.start(1000)

    def connection_check_loop(self):
        if self.robot.is_connected:
            self.connection_status.setText("<pre>Status: Connected</pre>")
            self.connection_status.setStyleSheet("color: green; font-size: 13px; font-weight: bold;")
        else:
            self.connection_status.setText("<pre>Status: Disconnected</pre>")
            self.connection_status.setStyleSheet("color: red; font-size: 13px; font-weight: bold;")
