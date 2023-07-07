from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.ConfirmationBox import ConfirmationBox


class SuspensionModeSelect(QWidget):

    def __init__(self, robot, parent=None, controller=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.auto_controls = SuspensionAutoModes(self.robot, parent)
        self.manual_controls = SuspensionManualControl(self.robot, parent, controller)
        self.max_extension = MaxExtension(self.robot, parent)

        # Hide the manual controls by default
        self.auto_controls.hide()
        self.manual_controls.hide()

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Suspension Height", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        # self.header.setBaseSize(0, 0)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.auto_button = QPushButton("Auto", self)
        self.auto_button.setFixedSize(80, 25)
        self.auto_button.move(10, 20)
        self.auto_button.clicked.connect(self.auto_mode)
        self.auto_button.setDisabled(True)

        self.manual_button = QPushButton("Manual", self)
        self.manual_button.setFixedSize(80, 25)
        self.manual_button.move(100, 20)
        self.manual_button.clicked.connect(self.manual_mode)
        self.manual_button.setDisabled(True)

        self.maximum_button = QPushButton("Maximum", self)
        self.maximum_button.setFixedSize(80, 25)
        self.maximum_button.move(190, 20)
        self.maximum_button.clicked.connect(self.maximum)
        self.maximum_button.setDisabled(True)

        self.robot.attach_on_connect_callback(self.on_robot_connection)
        self.robot.attach_on_disconnect_callback(self.on_robot_disconnection)

    def moved(self, x, y):
        self.move(x, y)
        self.auto_controls.move(self.x(), self.y() + self.height() + 5)
        self.manual_controls.move(self.x(), self.y() + self.height() + 5)
        self.max_extension.move(self.x(), self.y() + self.height() + 5)

    def manual_mode(self):
        # Create a confirmation dialog box and wait for the user to confirm
        # If the user confirms, then send the commmand to actuate the door
        try:
            self.manual_controls.show()
            self.auto_controls.hide()
            self.max_extension.hide()
            self.robot.execute_custom_service("/trch/arm", {"in_": True}, "primrose_trch/set_armed")
        except Exception as e:
            logging.error(e)

    def auto_mode(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to Auto?",
                                      detailed_message="This will map suspension motion to drivetrain velocity.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.auto_controls.show()
                self.manual_controls.hide()
                self.max_extension.hide()
                self.robot.execute_custom_service("/trch/arm", {"in_": True}, "primrose_trch/set_armed")
        except Exception as e:
            logging.error(e)

    def maximum(self):
        try:
            self.auto_controls.hide()
            self.manual_controls.hide()
            self.max_extension.show()
            self.robot.execute_custom_service("/trch/arm", {"in_": True}, "primrose_trch/set_armed")
        except Exception as e:
            logging.error(e)

    def update(self):
        pass

    def on_robot_connection(self):
        self.auto_button.setDisabled(False)
        self.manual_button.setDisabled(False)
        self.maximum_button.setDisabled(False)

    def on_robot_disconnection(self):
        self.auto_button.setDisabled(True)
        self.manual_button.setDisabled(True)
        self.maximum_button.setDisabled(True)


class SuspensionAutoModes(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Suspension Mode", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        # self.header.setBaseSize(0, 0)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.auto_button = QPushButton("Initial Ramp", self)
        self.auto_button.setFixedSize(80, 25)
        self.auto_button.move(10, 20)
        self.auto_button.clicked.connect(self.initial_ramp)
        # self.auto_button.setDisabled(True)

        self.manual_button = QPushButton("Ramp Entry", self)
        self.manual_button.setFixedSize(80, 25)
        self.manual_button.move(100, 20)
        self.manual_button.clicked.connect(self.ramp_entry)
        # self.manual_button.setDisabled(True)

        self.maximum_button = QPushButton("Exit", self)
        self.maximum_button.setFixedSize(80, 25)
        self.maximum_button.move(190, 20)
        self.maximum_button.clicked.connect(self.exit)
        # self.maximum_button.setDisabled(True)

    def initial_ramp(self):
        try:
            self.robot.execute_custom_service("/trch/arm", {"in_": True}, "primrose_trch/set_armed")
        except Exception as e:
            logging.error(e)

    def ramp_entry(self):
        try:
            self.robot.execute_custom_service("/trch/arm", {"in_": True}, "primrose_trch/set_armed")
        except Exception as e:
            logging.error(e)

    def exit(self):
        try:
            self.robot.execute_custom_service("/trch/arm", {"in_": True}, "primrose_trch/set_armed")
        except Exception as e:
            logging.error(e)


class SuspensionManualControl(QWidget):

    def __init__(self, robot, parent=None, controller=None):
        super().__init__(parent)
        self.robot = robot
        self.controller = controller

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Manual Suspension Controls", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        # self.header.setBaseSize(0, 0)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 40, 0)

        self.text = QLabel("<pre>Selected Corner: </pre>", self.surface)
        self.text.setStyleSheet("font-weight: bold; font-size: 12px; border: 0px; "
                                "background-color: transparent;")
        self.text.setAlignment(Qt.Qt.AlignCenter)
        # self.header.setBaseSize(0, 0)
        self.text.move(10, 20)


class MaxExtension(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Manual Suspension Controls", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        # self.header.setBaseSize(0, 0)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 40, 0)

        self.text = QLabel("<pre>Disabled at Max Extension</pre>", self.surface)
        self.text.setStyleSheet("font-weight: bold; font-size: 12px; border: 0px; "
                                "background-color: transparent;")
        self.text.setAlignment(Qt.Qt.AlignCenter)
        # self.header.setBaseSize(0, 0)
        self.text.move(10, 20)
