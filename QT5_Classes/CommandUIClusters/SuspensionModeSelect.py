from PyQt5 import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.ConfirmationBox import ConfirmationBox
from QT5_Classes.ErrorBox import ErrorBox
from Resources import Enumerators
from Resources.Enumerators import quarter_modules, ActuatorCommands


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
            # self.robot.execute_custom_service("/trch/arm", {"in_": True}, "primrose_trch/set_armed")
            self.manual_controls.show()
            self.auto_controls.hide()
            self.max_extension.hide()
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension to manual mode.", error=e)

    def auto_mode(self):
        try:
            self.auto_controls.show()
            self.manual_controls.hide()
            self.max_extension.hide()
        except Exception as e:
            logging.error(e)

    def maximum(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want set the suspension to maximum extension?",
                                      detailed_message="This will immediately extend all suspension actuators to their maximum extension.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                # self.robot.execute_custom_service("/trch/arm", {"in_": True}, "primrose_trch/set_armed")
                self.auto_controls.hide()
                self.manual_controls.hide()
                self.max_extension.show()
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension to maximum extension.", error=e)

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
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to Auto?",
                                      detailed_message="This will map suspension motion to drivetrain velocity.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/primrose_qmc/set_state", {"state": Enumerators.SuspensionModes.INIT_RAMP},
                                                  "qmc/susp_service")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension to initial ramp.", error=e)

    def ramp_entry(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to Auto?",
                                      detailed_message="This will map suspension motion to drivetrain velocity.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/primrose_qmc/set_state", {"state": Enumerators.SuspensionModes.LEVELING_RAMP},
                                                  "qmc/susp_service")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension to ramp entry.", error=e)

    def exit(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to Auto?",
                                      detailed_message="This will map suspension motion to drivetrain velocity.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/primrose_qmc/set_state", {"state": Enumerators.SuspensionModes.EXIT_RAMP},
                                                  "qmc/susp_service")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension to exit ramp.", error=e)


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

        self.text = QLabel("<pre>Selected Corner: No Module Selected</pre>", self.surface)
        self.text.setStyleSheet("font-weight: bold; font-size: 12px; border: 0px; "
                                "background-color: transparent;")
        # self.text.setAlignment(Qt.Qt.AlignCenter)
        # self.header.setBaseSize(0, 0)
        self.text.move(10, 20)
        self.selected_corner = 0
        self.key_release = False

        # Setup timer to update the UI
        self.ui_timer = QTimer(self)
        self.ui_timer.timeout.connect(self.update_ui)
        # self.ui_timer.startTimer(100)

        # Setup timer to read the controller
        self.controller_timer = QTimer(self)
        self.controller_timer.timeout.connect(self.read_controller)
        # self.controller_timer.startTimer(100)

    def hide(self) -> None:
        super().hide()
        self.ui_timer.stop()
        self.controller_timer.stop()

    def show(self) -> None:
        super().show()
        self.ui_timer.start(100)
        self.controller_timer.start(100)

    def update_ui(self):
        self.text.setText(f"<pre>Selected Corner: {quarter_modules[self.selected_corner]}</pre>")

    def read_controller(self):
        try:
            # Use the dpad left and right to change the selected corner
            # Use the dpad up and down to move the selected corner
            vert = self.controller.RightJoystickY
            turn = self.controller.RightJoystickX
            # logging.info(f"Vert: {vert}, Turn: {turn}")
            if abs(vert) > 0.1 or abs(turn) > 0.1:
                self.robot.get_state(f"/mciu/{quarter_modules[self.selected_corner]}/actuators/input").value = \
                    [ActuatorCommands.SET_DUTY_CYCLE, int(vert * -50), 0]
                self.robot.get_state(f"/mciu/{quarter_modules[self.selected_corner]}/actuators/input").value = \
                    [ActuatorCommands.SET_DUTY_CYCLE, int(turn * 50), 1]
            else:
                self.robot.get_state(f"/mciu/{quarter_modules[self.selected_corner]}/actuators/input").value = \
                    [ActuatorCommands.SET_DUTY_CYCLE, 0, 0]
                self.robot.get_state(f"/mciu/{quarter_modules[self.selected_corner]}/actuators/input").value = \
                    [ActuatorCommands.SET_DUTY_CYCLE, 0, 1]

            if not self.key_release:
                if self.controller.LeftDPad:
                    self.selected_corner = (self.selected_corner - 1) % 4
                    self.key_release = True
                elif self.controller.RightDPad:
                    self.selected_corner = (self.selected_corner + 1) % 4
                    self.key_release = True
            else:
                if not self.controller.LeftDPad and not self.controller.RightDPad and \
                        not self.controller.UpDPad and not self.controller.DownDPad:
                    self.key_release = False

        except Exception as e:
            logging.error(e)
            # ErrorBox(self, title="Manual Suspension Control Error",
            #          message="Error reading controller input or sending command to rover", error=e)


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
