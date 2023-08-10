from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.ErrorBox import ErrorBox
from Resources import Enumerators
from Resources.Enumerators import ActuatorCommands, SteeringStates, SuspensionModes


class SteeringModesCluster(QWidget):

    def __init__(self, robot, parent=None, controller=None):
        super().__init__(parent)
        self.robot = robot
        self.controller = controller

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Set Steering Mode", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 15, 0)

        self.on_point_steering_button = QPushButton("Turn", self)
        self.on_point_steering_button.setFixedSize(80, 25)
        self.on_point_steering_button.move(10, 20)
        self.on_point_steering_button.clicked.connect(self.in_point_steering)
        self.on_point_steering_button.setEnabled(False)

        self.fused_steering_button = QPushButton("Drive", self)
        self.fused_steering_button.setFixedSize(80, 25)
        self.fused_steering_button.move(100, 20)
        self.fused_steering_button.clicked.connect(self.fused_steering)
        self.fused_steering_button.setEnabled(False)

        self.parked_steering_button = QPushButton("Parked", self)
        self.parked_steering_button.setFixedSize(80, 25)
        self.parked_steering_button.move(190, 20)
        self.parked_steering_button.clicked.connect(self.parked_steering)
        self.parked_steering_button.setEnabled(False)

        self.robot.attach_on_connect_callback(self.on_robot_connected)
        self.robot.attach_on_disconnect_callback(self.on_robot_disconnected)

        self.connection_check_timer = Qt.QTimer(self)
        self.connection_check_timer.timeout.connect(self.state_loop)
        self.connection_check_timer.start(1000)

    def state_loop(self):
        def on_success(response):
            self.on_point_steering_button.setEnabled(True)
            logging.info("Successfully executed steering_mode service.")

        def on_failure(error):
            # ErrorBox(title="Service Failure", message="Was unable to execute steering_mode service.", detailed_message=error)
            self.on_point_steering_button.setEnabled(True)
            logging.error(error)


        font_weight = 500
        deselected = "red"
        selected = "green"
        try:
            # handle controller input:
            a = self.controller.A
            x = self.controller.X
            b = self.controller.B
            y = self.controller.Y
            if a == 1:
                self.robot.execute_custom_service("/qmc/steer_service", {"state": SteeringStates.DRIVING}, "primrose_qmc/set_state",
                                                  callback=on_success, errback=on_failure)
                logging.info("Sent steering mode request.")
            elif x == 1:
                self.robot.execute_custom_service("/qmc/steer_service", {"state": SteeringStates.PARKED}, "primrose_qmc/set_state",
                                                  callback=on_success, errback=on_failure)
                logging.info("Sent steering mode request.")
            elif b == 1:
                self.robot.execute_custom_service("/qmc/steer_service", {"state": SteeringStates.TURNING}, "primrose_qmc/set_state",
                                                  callback=on_success, errback=on_failure)
                logging.info("Sent steering mode request.")
            elif y == 1:
                self.robot.execute_custom_service("/qmc/steer_service", {"state": SteeringStates.PARKED}, "primrose_qmc/set_state",
                                                  callback=on_success, errback=on_failure)
                logging.info("Sent steering mode request.")


            # handle colors
            steer_state = self.robot.get_state('/qmc/steer_state').value
            match steer_state:
                case SteeringStates.PARKED:
                    self.parked_steering_button.setStyleSheet(f"color: {selected}; font-weight: bold;")
                    self.fused_steering_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.on_point_steering_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                case SteeringStates.TURNING:
                    self.parked_steering_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.fused_steering_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.on_point_steering_button.setStyleSheet(f"color: {selected}; font-weight: bold;")
                case SteeringStates.DRIVING:
                    self.parked_steering_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.fused_steering_button.setStyleSheet(f"color: {selected}; font-weight: bold;")
                    self.on_point_steering_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                case _:
                    self.parked_steering_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.fused_steering_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
                    self.on_point_steering_button.setStyleSheet(f"color: {deselected}; font-weight: {font_weight};")
        except Exception as e:
            logging.exception(e)

    def in_point_steering(self):

        def on_success(response):
            self.on_point_steering_button.setEnabled(True)
            logging.info("Successfully executed steering_mode service.")

        def on_failure(error):
            # ErrorBox(title="Service Failure", message="Was unable to execute steering_mode service.", detailed_message=error)
            self.on_point_steering_button.setEnabled(True)
            logging.error(error)

        try:
            self.robot.execute_custom_service("/qmc/steer_service", {"state": SteeringStates.TURNING}, "primrose_qmc/set_state",
                                              callback=on_success, errback=on_failure)
            # self.on_point_steering_button.setEnabled(False)
            # self.robot.execute_custom_service("/qmc/drive_service", {"in_": False}, "primrose_qmc/set_armed")
            self.robot.steering_enabled = True
            self.robot.driving_enabled = False
            logging.info("Sent steering mode request.")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Was unable to execute steering_mode service.", error=e)
            self.on_point_steering_button.setEnabled(True)

    def fused_steering(self):

        def on_success(response):
            self.fused_steering_button.setEnabled(True)
            logging.info("Successfully executed steering_mode service.")

        def on_failure(error):
            # ErrorBox(title="Service Failure", message="Was unable to execute steering_mode service.", detailed_message=error)
            self.fused_steering_button.setEnabled(True)
            logging.error(error)

        try:
            self.robot.execute_custom_service("/qmc/steer_service", {"state": SteeringStates.DRIVING}, "primrose_qmc/set_state",
                                              callback=on_success, errback=on_failure)
            # self.robot.execute_custom_service("/qmc/drive_service", {"in_": False}, "primrose_qmc/set_armed")
            self.robot.steering_enabled = False
            self.robot.driving_enabled = True
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Was unable to execute steering_mode service.", error=e)

    def parked_steering(self):

        def on_success(response):
            self.parked_steering_button.setEnabled(True)
            logging.info("Successfully executed steering_mode service.")

        def on_failure(error):
            # ErrorBox(title="Service Failure", message="Was unable to execute steering_mode service.", detailed_message=error)
            self.parked_steering_button.setEnabled(True)
            logging.error(error)

        try:
            self.robot.execute_custom_service("/qmc/steer_service", {"state": SteeringStates.PARKED}, "primrose_qmc/set_state",
                                              callback=on_success, errback=on_failure)
            self.robot.steering_enabled = False
            self.robot.driving_enabled = False
            # self.robot.execute_custom_service("/qmc/drive_service", {"in_": False}, "primrose_qmc/set_armed")
        except Exception as e:
            logging.error(e)
            ErrorBox(self, title="Service Error", message="Was unable to execute steering_mode service.", error=e)

    def update(self):
        print("test")

    def on_robot_connected(self):
        self.on_point_steering_button.setEnabled(True)
        self.fused_steering_button.setEnabled(True)
        self.parked_steering_button.setEnabled(True)

    def on_robot_disconnected(self):
        self.on_point_steering_button.setEnabled(False)
        self.fused_steering_button.setEnabled(False)
        self.parked_steering_button.setEnabled(False)
