from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.CommandUIClusters.ConfirmationBox import ConfirmationBox
from Resources import Enumerators


class AutomaticEStopControls(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Automatic E-Stop", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.enable_auto_button = QPushButton("Enable", self)
        self.enable_auto_button.setFixedSize(80, 25)
        self.enable_auto_button.move(10, 20)
        self.enable_auto_button.clicked.connect(self.enable_auto)
        self.enable_auto_button.setEnabled(False)

        self.reset_estop_button = QPushButton("Reset", self)
        self.reset_estop_button.setFixedSize(80, 25)
        self.reset_estop_button.move(100, 20)
        self.reset_estop_button.clicked.connect(self.reset_estop)
        self.reset_estop_button.setEnabled(True)

        self.disable_auto_button = QPushButton("Disable", self)
        self.disable_auto_button.setFixedSize(80, 25)
        self.disable_auto_button.move(190, 20)
        self.disable_auto_button.clicked.connect(self.disable_auto)
        self.disable_auto_button.setEnabled(True)

        self.robot.attach_on_connect_callback(self.on_robot_connection)
        self.robot.attach_on_disconnect_callback(self.on_robot_disconnection)

    def reset_estop(self):
        # Create a confirmation dialog box and wait for the user to confirm
        # If the user confirms, then send the commmand to actuate the door
        try:
            # Open a confirmation dialog box
            confirm = ConfirmationBox(self, title="Clear E-Stop", message="Are you sure you want to clear the active E-Stop?",
                                      detailed_message="Clearing the E-Stop will close the High Voltage Contactor and supply "
                                                       "power to the motor controllers, make sure that all personnel are clear "
                                                       "of the rover before continuing.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.get_state('/mciu/estop_controller').value = Enumerators.EStopCommands.RESET
        except Exception as e:
            logging.error(e)

    def disable_auto(self):
        try:
            confirm = ConfirmationBox(self, title="Disable Automatic E-Stop",
                                      message="Are you sure you want to disable PRIMROSE's auto E-Stop system?",
                                      detailed_message="Disabling the automatic E-Stop will prevent PRIMROSE from E-Stopping "
                                                       "when it detects a fault, this will prevent any "
                                                       "false positives but be aware that PRIMROSE will no longer "
                                                       "automatically stop the rover if it detects a fault and may damage itself")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.get_state('/mciu/estop_controller').value = Enumerators.EStopCommands.DISABLE_AUTO
        except Exception as e:
            logging.error(e)

    def enable_auto(self):
        try:
            self.robot.get_state('/mciu/estop_controller').value = Enumerators.EStopCommands.ENABLE_AUTO
        except Exception as e:
            logging.error(e)

    def update(self):
        pass

    def on_robot_connection(self):
        self.enable_auto_button.setEnabled(True)
        self.reset_estop_button.setEnabled(True)
        self.disable_auto_button.setEnabled(True)

    def on_robot_disconnection(self):
        self.enable_auto_button.setEnabled(False)
        self.reset_estop_button.setEnabled(False)
        self.disable_auto_button.setEnabled(False)
