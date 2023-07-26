from PyQt5 import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.ConfirmationBox import ConfirmationBox
from QT5_Classes.ErrorBox import ErrorBox
from QT5_Classes.QuickButton import QuickButton
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

        self.header = QLabel("Suspension Mode Select", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        # self.header.setBaseSize(0, 0)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 30, 0)

        self.auto_button = QPushButton("Excavation", self)
        self.auto_button.setFixedSize(80, 25)
        self.auto_button.move(10, 20)
        self.auto_button.clicked.connect(self.auto_trenching)
        self.auto_button.setDisabled(True)

        self.manual_button = QPushButton("Manual", self)
        self.manual_button.setFixedSize(80, 25)
        self.manual_button.move(100, 20)
        self.manual_button.clicked.connect(self.manual_mode)
        self.manual_button.setDisabled(True)

        self.drive_button = QPushButton("Drive", self)
        self.drive_button.setFixedSize(80, 25)
        self.drive_button.move(190, 20)
        self.drive_button.clicked.connect(self.auto_driving)
        self.drive_button.setDisabled(True)

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
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want set the suspension to manual control?",
                                      detailed_message="Use the dpad to select the target quarter module and the "
                                                       "right joystick to control the height of the suspension.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/primrose_qmc/set_state", {"state": Enumerators.SuspensionModes.MANUAL},
                                                  "qmc/susp_service")
                self.manual_controls.show()
                self.auto_controls.hide()
                self.max_extension.hide()
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension to manual mode.", error=e)

    def auto_trenching(self):
        try:
            self.auto_controls.show()
            self.manual_controls.hide()
            self.max_extension.hide()
        except Exception as e:
            logging.error(e)

    def auto_driving(self):
        try:
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
        self.drive_button.setDisabled(False)

    def on_robot_disconnection(self):
        self.auto_button.setDisabled(True)
        self.manual_button.setDisabled(True)
        self.drive_button.setDisabled(True)


class SuspensionAutoModes(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 105)
        super().setFixedSize(280, 105)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Excavation Modes", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        # self.header.setBaseSize(0, 0)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.initial_ramp_button = QuickButton("Initial Ramp", self, (10, 20), self.initial_ramp)
        self.excavating_button = QuickButton("Excavating", self, (100, 20), self.excavating)
        self.first_in_button = QuickButton("First In", self, (10, 46), self.first_wheel_in)
        self.second_in_button = QuickButton("Second In", self, (100, 46), self.second_wheel_in)
        self.first_out_button = QuickButton("First Out", self, (10, 72), self.first_wheel_out)
        self.second_out_button = QuickButton("Second Out", self, (100, 72), self.second_wheel_out)

    def initial_ramp(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to Initial Ramp?",
                                      detailed_message="This will map suspension motion to drivetrain velocity.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/primrose_qmc/set_state", {"state": Enumerators.SuspensionModes.INITIAL_RAMP},
                                                  "qmc/susp_service")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension mode to initial ramp.", error=e)

    def excavating(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to Excavating?",
                                      detailed_message="This will map suspension motion to drivetrain velocity.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/primrose_qmc/set_state", {"state": Enumerators.SuspensionModes.EXCAVATING},
                                                  "qmc/susp_service")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension mode to excavating.", error=e)

    def first_wheel_in(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to First In?",
                                      detailed_message="This will map suspension motion to drivetrain velocity.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/primrose_qmc/set_state", {"state": Enumerators.SuspensionModes.FIRST_WHEEL_ENTERING},
                                                  "qmc/susp_service")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension mode to first wheel in.", error=e)

    def second_wheel_in(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to Second In?",
                                      detailed_message="This will map suspension motion to drivetrain velocity.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/primrose_qmc/set_state", {"state": Enumerators.SuspensionModes.SECOND_WHEEL_ENTERING},
                                                  "qmc/susp_service")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension mode to second wheel in.", error=e)

    def first_wheel_out(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to First Out?",
                                      detailed_message="This will map suspension motion to drivetrain velocity.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/primrose_qmc/set_state", {"state": Enumerators.SuspensionModes.FIRST_WHEEL_EXITING},
                                                  "qmc/susp_service")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension mode to first wheel out.", error=e)

    def second_wheel_out(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to Second Out?",
                                      detailed_message="This will map suspension motion to drivetrain velocity.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/primrose_qmc/set_state", {"state": Enumerators.SuspensionModes.SECOND_WHEEL_EXITING},
                                                  "qmc/susp_service")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension mode to second wheel out.", error=e)


class SuspensionManualControl(QWidget):

    def __init__(self, robot, parent=None, controller=None):
        super().__init__(parent)
        self.robot = robot
        self.controller = controller

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 105)
        super().setFixedSize(280, 105)

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
        if self.selected_corner != 4:
            self.text.setText(f"<pre>Selected Corner: {quarter_modules[self.selected_corner]}</pre>")
        else:
            self.text.setText(f"<pre>Selected Corner: All Corners</pre>")

    def read_controller(self):
        if not self.robot.is_connected:
            return
        try:
            # Use the dpad left and right to change the selected corner
            # Use the dpad up and down to move the selected corner
            vert = self.controller.RightJoystickY
            turn = self.controller.RightJoystickX
            # logging.info(f"Vert: {vert}, Turn: {turn}")
            if self.selected_corner != 4:
                if abs(vert) > 0.2 or abs(turn) > 0.2:
                    self.robot.get_state(f"/mciu/{quarter_modules[self.selected_corner]}/actuators/input").value = \
                        [ActuatorCommands.SET_DUTY_CYCLE, int(vert * -100), 0]
                    self.robot.get_state(f"/mciu/{quarter_modules[self.selected_corner]}/actuators/input").value = \
                        [ActuatorCommands.SET_DUTY_CYCLE, int(turn * 100), 1]
                else:
                    self.robot.get_state(f"/mciu/{quarter_modules[self.selected_corner]}/actuators/input").value = \
                        [ActuatorCommands.SET_DUTY_CYCLE, 0, 0]
                    self.robot.get_state(f"/mciu/{quarter_modules[self.selected_corner]}/actuators/input").value = \
                        [ActuatorCommands.SET_DUTY_CYCLE, 0, 1]
            else:
                # pass
                # self.robot.get_state(f"/mciu/Front_Right/actuators/input").value = \
                #     [ActuatorCommands.SET_POSITION, -1070, 0]
                if abs(vert) > 0.2 or abs(turn) > 0.2:
                    for i in range(4):
                        self.robot.get_state(f"/mciu/{quarter_modules[i]}/actuators/input").value = \
                            [ActuatorCommands.SET_DUTY_CYCLE, int(vert * -100), 0]
                        self.robot.get_state(f"/mciu/{quarter_modules[i]}/actuators/input").value = \
                            [ActuatorCommands.SET_DUTY_CYCLE, int(turn * 100), 1]
                else:
                    for i in range(4):
                        self.robot.get_state(f"/mciu/{quarter_modules[i]}/actuators/input").value = \
                            [ActuatorCommands.SET_DUTY_CYCLE, 0, 0]
                        self.robot.get_state(f"/mciu/{quarter_modules[i]}/actuators/input").value = \
                            [ActuatorCommands.SET_DUTY_CYCLE, 0, 1]

            if not self.key_release:
                if self.controller.LeftDPad:
                    self.selected_corner = (self.selected_corner - 1) % 5
                    self.key_release = True
                elif self.controller.RightDPad:
                    self.selected_corner = (self.selected_corner + 1) % 5
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
        self.surface.setFixedSize(280, 105)
        super().setFixedSize(280, 105)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Driving Suspension Controls", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        # self.header.setBaseSize(0, 0)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 40, 0)

        # self.text = QLabel("<pre>Disabled at Max Extension</pre>", self.surface)
        # self.text.setStyleSheet("font-weight: bold; font-size: 12px; border: 0px; "
        #                         "background-color: transparent;")
        # self.text.setAlignment(Qt.Qt.AlignCenter)
        # # self.header.setBaseSize(0, 0)
        # self.text.move(10, 20)

        self.auto_button = QPushButton("Excavate", self)
        self.auto_button.setFixedSize(80, 25)
        self.auto_button.move(10, 20)
        self.auto_button.clicked.connect(self.excavate)
        # self.auto_button.setDisabled(True)

        self.manual_button = QPushButton("Drive", self)
        self.manual_button.setFixedSize(80, 25)
        self.manual_button.move(100, 20)
        self.manual_button.clicked.connect(self.driving)
        # self.manual_button.setDisabled(True)

        self.maximum_button = QPushButton("Maximum", self)
        self.maximum_button.setFixedSize(80, 25)
        self.maximum_button.move(190, 20)
        self.maximum_button.clicked.connect(self.maximum)

        self.auto_button.setDisabled(True)
        self.manual_button.setDisabled(True)
        self.maximum_button.setDisabled(True)

        self.robot.attach_on_connect_callback(self.on_robot_connection)
        self.robot.attach_on_disconnect_callback(self.on_robot_disconnection)

    def on_robot_connection(self):
        self.auto_button.setDisabled(False)
        self.manual_button.setDisabled(False)
        self.maximum_button.setDisabled(False)

    def on_robot_disconnection(self):
        self.auto_button.setDisabled(True)
        self.manual_button.setDisabled(True)
        self.maximum_button.setDisabled(True)

    def excavate(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to excavate?",
                                      detailed_message="This will map suspension motion to drivetrain velocity.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/primrose_qmc/set_state", {"state": Enumerators.SuspensionModes.INIT_RAMP},
                                                  "qmc/susp_service")
                # self.robot.get_state("/mciu/Rear_Left/actuators/input").value = \
                #     [ActuatorCommands.SET_POSITION, -845, 1]
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension to excavate.", error=e)

    def driving(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to drive?",
                                      detailed_message="This will map suspension motion to drivetrain velocity.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/primrose_qmc/set_state", {"state": Enumerators.SuspensionModes.MAXIMUM},
                                                  "qmc/susp_service")
                # self.robot.get_state("/mciu/Rear_Left/actuators/input").value = \
                #     [ActuatorCommands.SET_POSITION, -510, 1]
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension to drive.", error=e)

    def maximum(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to maximum?",
                                      detailed_message="This will map suspension motion to maximum extension.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                # self.robot.execute_custom_service("/primrose_qmc/set_state", {"state": Enumerators.SuspensionModes.MAXIMUM},
                #                                   "qmc/susp_service")
                self.robot.get_state("/mciu/Rear_Left/actuators/input").value = \
                    [ActuatorCommands.SET_POSITION, -470, 1]
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension to maximum.", error=e)
