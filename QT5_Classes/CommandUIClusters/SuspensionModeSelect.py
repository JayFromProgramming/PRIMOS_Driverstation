from PyQt5 import Qt
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.ConfirmationBox import ConfirmationBox
from QT5_Classes.ErrorBox import ErrorBox
from QT5_Classes.QuickButton import QuickButton
from Resources import Enumerators
from Resources.Enumerators import quarter_modules, ActuatorCommands, SuspensionModes


class SuspensionModeSelect(QWidget):

    def __init__(self, robot, parent=None, controller=None):
        super().__init__(parent)
        self.robot = robot
        self.controller = controller

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.auto_controls = SuspensionAutoModes(self.robot, parent)
        self.manual_controls = SuspensionManualControl(self.robot, parent, controller)
        self.max_extension = MaxExtension(self.robot, parent)

        # Hide the manual controls by default
        self.auto_controls.hide()
        self.manual_controls.hide()
        self.max_extension.hide()

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

        self.connection_check_timer = Qt.QTimer(self)
        self.connection_check_timer.timeout.connect(self.state_loop)
        self.connection_check_timer.start(1000)

    def state_loop(self):
        def on_success(response):
            # self.on_point_steering_button.setEnabled(True)
            logging.info("Successfully executed steering_mode service.")

        def on_failure(error):
            # ErrorBox(title="Service Failure", message="Was unable to execute steering_mode service.", detailed_message=error)
            # self.on_point_steering_button.setEnabled(True)
            logging.error(error)
        font_weight = 500
        deselected = "red"
        selected = "green"
        try:
            a = self.controller.A
            x = self.controller.X
            b = self.controller.B
            y = self.controller.Y
            if a == 1:
                self.robot.execute_custom_service("/qmc/susp_service", {"state": SuspensionModes.DEFAULT}, "primrose_qmc/set_state",
                                                  callback=on_success, errback=on_failure)
                logging.info("Sent suspension mode request.")
                self.manual_controls.hide()
                self.auto_controls.hide()
                self.max_extension.hide()
            elif x == 1:
                pass
            elif b == 1:
                self.robot.execute_custom_service("/qmc/susp_service", {"state": SuspensionModes.DEFAULT}, "primrose_qmc/set_state",
                                                  callback=on_success, errback=on_failure)
                logging.info("Sent suspension mode request.")
            elif y == 1:
                self.robot.execute_custom_service("/qmc/susp_service", {"state": SuspensionModes.MANUAL}, "primrose_qmc/set_state",
                                                  callback=on_success, errback=on_failure)
                logging.info("Sent suspension mode request.")
                self.manual_controls.show()
                self.auto_controls.hide()
                self.max_extension.hide()

            susp_state = self.robot.get_state('/qmc/susp_state').value
            match susp_state:
                case SuspensionModes.DEFAULT:
                    self.drive_button.setStyleSheet(f"color: {selected}; font-weight: bold;")
                    self.manual_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.auto_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                case SuspensionModes.INITIAL_RAMP:
                    self.drive_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.manual_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.auto_button.setStyleSheet(f"color: {selected}; font-weight: bold;")
                case SuspensionModes.EXTRA_RAMP_1:
                    self.drive_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.manual_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.auto_button.setStyleSheet(f"color: {selected}; font-weight: bold;")
                case SuspensionModes.EXTRA_RAMP_2:
                    self.drive_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.manual_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.auto_button.setStyleSheet(f"color: {selected}; font-weight: bold;")
                case SuspensionModes.MANUAL:
                    self.drive_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.manual_button.setStyleSheet(f"color: {selected}; font-weight: bold;")
                    self.auto_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                case _:
                    self.drive_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.manual_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.auto_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
        except Exception as e:
            logging.exception(e)

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
                self.robot.execute_custom_service("/qmc/susp_service", {"state": Enumerators.SuspensionModes.MANUAL},
                                                  "/primrose_qmc/set_state")
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
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want set the suspension to maximum extension?",
                                      detailed_message="Use the dpad to select the target quarter module and the "
                                                       "right joystick to control the height of the suspension.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/qmc/susp_service", {"state": Enumerators.SuspensionModes.DEFAULT},
                                                  "/primrose_qmc/set_state")
                self.manual_controls.hide()
                self.auto_controls.hide()
                self.max_extension.hide()
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension to manual mode.", error=e)


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
        self.extra_ramp_1_button = QuickButton("Extra Ramp FR", self, (10, 50), self.extra_ramp_1)
        self.extra_ramp_2_button = QuickButton("Extra Ramp BR", self, (10, 80), self.extra_ramp_2)
        self.initial_ramp_button.setFixedSize(250,25)
        self.extra_ramp_1_button.setFixedSize(250,25)
        self.extra_ramp_2_button.setFixedSize(250,25)

        self.connection_check_timer = Qt.QTimer(self)
        self.connection_check_timer.timeout.connect(self.state_loop)
        self.connection_check_timer.start(1000)

    def state_loop(self):
        font_weight = 500
        deselected = "red"
        selected = "green"
        try:
            susp_state = self.robot.get_state('/qmc/susp_state').value
            match susp_state:
                case SuspensionModes.INITIAL_RAMP:
                    self.initial_ramp_button.setStyleSheet(f"color: {selected}; font-weight: bold;")
                    self.extra_ramp_1_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.extra_ramp_2_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                case SuspensionModes.EXTRA_RAMP_1:
                    self.initial_ramp_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.extra_ramp_1_button.setStyleSheet(f"color: {selected}; font-weight: bold;")
                    self.extra_ramp_2_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                case SuspensionModes.EXTRA_RAMP_2:
                    self.initial_ramp_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.extra_ramp_1_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.extra_ramp_2_button.setStyleSheet(f"color: {selected}; font-weight: bold;")
                case _:
                    self.initial_ramp_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.extra_ramp_1_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.extra_ramp_2_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
        except Exception as e:
            logging.exception(e)

    def initial_ramp(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to Initial Ramp?",
                                      detailed_message="This will map suspension motion to drivetrain velocity.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/qmc/susp_service", {"state": Enumerators.SuspensionModes.INITIAL_RAMP},
                                                  "/primrose_qmc/set_state")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension mode to initial ramp.", error=e)

    def extra_ramp_1(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to Extra Ramp FR?",
                                      detailed_message="This will map suspension motion to drivetrain velocity with manual control of the front right wheel.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/qmc/susp_service", {"state": Enumerators.SuspensionModes.EXTRA_RAMP_1},
                                                  "/primrose_qmc/set_state")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension mode to extra ramp.", error=e)

    def extra_ramp_2(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Suspension Mode Change",
                                      message="Are you sure you want to change the suspension mode to Extra Ramp BR?",
                                      detailed_message="This will map suspension motion to drivetrain velocity with manual control of the back right wheel.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                self.robot.execute_custom_service("/qmc/susp_service", {"state": Enumerators.SuspensionModes.EXTRA_RAMP_2},
                                                  "/primrose_qmc/set_state")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension mode to first wheel in.", error=e)


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
            vert = self.controller.LeftJoystickY
            turn = self.controller.RightJoystickX
            # logging.info(f"Vert: {vert}, Turn: {turn}")
            if self.selected_corner != 4:
                if abs(vert) > 0.1 or abs(turn) > 0.1:
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
                if abs(vert) > 0.1 or abs(turn) > 0.1:
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
                self.robot.execute_custom_service("/qmc/susp_service", {"state": Enumerators.SuspensionModes.INIT_RAMP},
                                                  "/primrose_qmc/set_state")
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
                self.robot.execute_custom_service("/qmc/susp_service", {"state": Enumerators.SuspensionModes.MAXIMUM},
                                                  "/primrose_qmc/set_state")
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
                self.robot.execute_custom_service("/qmc/susp_service", {"state": Enumerators.SuspensionModes.MAXIMUM},
                                                  "/primrose_qmc/set_state")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Error setting suspension to maximum.", error=e)
