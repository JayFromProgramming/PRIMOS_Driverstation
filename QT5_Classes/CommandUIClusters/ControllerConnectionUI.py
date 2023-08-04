from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging


class ControllerConnectionUI(QWidget):

    def __init__(self, robot, parent=None, controller=None):
        super().__init__(parent)
        self.robot = robot
        self.controller = controller

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Controller Connection", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 25, 0)

        # This element contains no controls, it just displays the current connection status of the xbox controller
        # it displays if the controller is connected and when the

        self.state_status = QLabel("<pre>Steer-state: -1 Susp-state: -1</pre>", self)
        self.state_status.setStyleSheet("color: red; font-size: 13px; font-weight: bold;")
        # self.connection_status.setFixedSize(150, 25)
        self.state_status.move(10, 16)

        self.connection_status = QLabel("<pre>Status: Disconnected</pre>", self)
        self.connection_status.setStyleSheet("color: red; font-size: 13px; font-weight: bold;")
        # self.connection_status.setFixedSize(150, 25)
        self.connection_status.move(10, 30)

        self.connection_check_timer = Qt.QTimer(self)
        self.connection_check_timer.timeout.connect(self.connection_check_loop)
        self.connection_check_timer.start(1000)

    def connection_check_loop(self):
        if self.controller.connected:
            # logging.debug(f"Controller {self.controller.usb_name} is connected")
            self.connection_status.setText("<pre>Status: Connected</pre>")
            self.connection_status.setStyleSheet("color: green; font-size: 13px; font-weight: bold;")

        else:
            self.connection_status.setText("<pre>Status: Disconnected</pre>")
            self.connection_status.setStyleSheet("color: red; font-size: 13px; font-weight: bold;")

        self.state_status.setText(f"<pre>Steer-state: {self.robot.get_state('/qmc/steer_state').value} Susp-state: {self.robot.get_state('/qmc/susp_state').value}</pre>")
        self.state_status.setStyleSheet("color: green; font-size: 13px; font-weight: bold;")


class ControllerMappingUI(QWidget):

    def __init__(self, robot, parent=None, controller=None):
        super().__init__(parent)
        self.robot = robot
        self.controller = controller

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Controller Mappings", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 20, 0)

        self.auto_button = QPushButton("Driving", self)
        self.auto_button.setFixedSize(80, 25)
        self.auto_button.move(10, 20)
        self.auto_button.clicked.connect(self.driving)
        # self.auto_button.setEnabled(False)

        self.manual_button = QPushButton("Excavating", self)
        self.manual_button.setFixedSize(80, 25)
        self.manual_button.move(100, 20)
        self.manual_button.clicked.connect(self.excavating)
        # self.manual_button.setEnabled(False)

        self.disable_button = QPushButton("Unused", self)
        self.disable_button.setFixedSize(80, 25)
        self.disable_button.move(190, 20)
        self.disable_button.clicked.connect(self.unused)
        # self.disable_button.setEnabled(False)
        self.controller.set_mapping("driving")

    def driving(self):
        self.controller.set_mapping("driving")

    def excavating(self):
        self.controller.set_mapping("excavating")

    def unused(self):
        self.controller.set_mapping("unused")
