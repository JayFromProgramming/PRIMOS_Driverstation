import threading

from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.ConfirmationBox import ConfirmationBox

import paramiko

from QT5_Classes.ErrorBox import ErrorBox


class JetsonControls(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("Jetson Controls", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.reboot_button = QPushButton("Reboot", self)
        self.reboot_button.setFixedSize(80, 25)
        self.reboot_button.move(10, 20)
        self.reboot_button.clicked.connect(self.reboot)

        self.restart_button = QPushButton("Restart", self)
        self.restart_button.setFixedSize(80, 25)
        self.restart_button.move(100, 20)
        self.restart_button.clicked.connect(self.restart)

        self.stop_button = QPushButton("Stop", self)
        self.stop_button.setFixedSize(80, 25)
        self.stop_button.move(190, 20)
        self.stop_button.clicked.connect(self.stop)

    def send_ssh_command(self, command):
        def execute():
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(self.robot.address, username="jetson", password="primrosepassword")
                ssh.exec_command(command)
                ssh.close()
            except Exception as e:
                logging.error(f"Error sending SSH command: {e}")
                ErrorBox(self, title="Error Sending SSH Command", message=f"Error sending SSH command \"{command}\"", error=e)
        threading.Thread(target=execute, daemon=True).start()

    def reboot(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Reboot",
                                      message="Are you sure you want to reboot the Jetson?",
                                      detailed_message="This will reboot the Jetson, this action is irreversible.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                logging.info("Sending command to reboot the Jetson")
                self.send_ssh_command("sudo reboot")
        except Exception as e:
            logging.error(f"Error rebooting Jetson: {e}")
            ErrorBox(self, title="Error Rebooting Jetson", message="Error rebooting Jetson", error=e)

    def restart(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Restart",
                                      message="Are you sure you want to restart the Jetson?",
                                      detailed_message="This will restart the Jetson, this action is irreversible.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                logging.info("Sending command to restart the Jetson")
                self.send_ssh_command("sudo systemctl restart primrose-start.service")
        except Exception as e:
            logging.error(f"Error restarting Jetson: {e}")
            ErrorBox(self, title="Error Restarting Jetson", message="Error restarting Jetson", error=e)

    def stop(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Stop",
                                      message="Are you sure you want to stop the Jetson?",
                                      detailed_message="This will stop the Jetson, this action is irreversible.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                logging.info("Sending command to stop the Jetson")
                self.send_ssh_command("sudo systemctl stop primrose-start.service")
        except Exception as e:
            logging.error(f"Error stopping Jetson: {e}")
            ErrorBox(self, title="Error Stopping Jetson", message="Error stopping Jetson", error=e)