from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.ConfirmationBox import ConfirmationBox

from QT5_Classes.ErrorBox import ErrorBox
from Resources import Enumerators


class DriveTrainControls(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Drivetrain Controls", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.enable_button = QPushButton("Enable", self)
        self.enable_button.setFixedSize(80, 25)
        self.enable_button.move(10, 20)
        self.enable_button.clicked.connect(self.enable)
        self.enable_button.setEnabled(True)

        self.disable_button = QPushButton("Disable", self)
        self.disable_button.setFixedSize(80, 25)
        self.disable_button.move(100, 20)
        self.disable_button.clicked.connect(self.disable)
        self.disable_button.setEnabled(False)

        self.calibrate_button = QPushButton("Calibrate", self)
        self.calibrate_button.setFixedSize(80, 25)
        self.calibrate_button.move(190, 20)
        self.calibrate_button.clicked.connect(self.calibrate)
        self.calibrate_button.setEnabled(False)

        self.robot.attach_on_connect_callback(self.on_robot_connection)
        self.robot.attach_on_disconnect_callback(self.on_robot_disconnection)

    def on_robot_connection(self):
        self.enable_button.setEnabled(True)
        self.disable_button.setEnabled(True)
        self.calibrate_button.setEnabled(True)

    def on_robot_disconnection(self):
        self.enable_button.setEnabled(False)
        self.disable_button.setEnabled(False)
        self.calibrate_button.setEnabled(False)

    def enable(self):
        # Create a confirmation dialog box and wait for the user to confirm
        # If the user confirms, then send the commmand to actuate the door
        try:
            for quarter_module in Enumerators.quarter_modules:
                self.robot.get_state(f'/mciu/{quarter_module}/odrive/input').value = \
                    [Enumerators.ODriveCommands.SET_CLOSED_LOOP, Enumerators.ODriveInputModes.VEL_RAMP]
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Internal Error", message="Error enabling drivetrain", error=e)

    def disable(self):
        try:
            for quarter_module in Enumerators.quarter_modules:
                self.robot.get_state(f'/mciu/{quarter_module}/odrive/input').value = [Enumerators.ODriveCommands.IDLE]
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Internal Error", message="Error disabling drivetrain", error=e)

    def calibrate(self):
        try:
            confirmation_box = ConfirmationBox(self, title="Begin Drivetrain Calibration?",
                                               message="Are you sure you want to calibrate the drive motors?",
                                               detailed_message="All drive wheels must be off the ground and able to spin freely "
                                               "in order to run the calibration sequence. These calibration results will be lost "
                                               "if the rover is power cycled.")
            confirmation_box.exec_()
            if confirmation_box.result() == Qt.QMessageBox.Yes:
                for quarter_module in Enumerators.quarter_modules:
                    logging.info(f"Commanding {quarter_module} to begin calibration sequence")
                    self.robot.get_state(f'/mciu/{quarter_module}/odrive/input').value = [Enumerators.ODriveCommands.BEGIN_CALIBRATION]
            else:
                logging.info("Operator cancelled calibration sequence")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Internal Error", message="Error calibrating drivetrain", error=e)
