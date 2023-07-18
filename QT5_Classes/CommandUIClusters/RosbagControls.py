import os
import threading

from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.ConfirmationBox import ConfirmationBox

import paramiko

from QT5_Classes.ErrorBox import ErrorBox


class RosbagControls(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot
        self.bag_file_location = "/home/jetson/bag_files/"
        self.save_location = "copied_bag_files"  # The location on the local machine to save the bag files to

        self.surface = QWidget(self)
        self.surface.setFixedSize(280, 50)
        super().setFixedSize(280, 50)
        self.ssh_client = None
        self.sftp = None

        self.surface.setStyleSheet("border: 1px solid black; border-radius: 5px; background-color: white;")

        self.header = QLabel("BagFile Controls", self.surface)
        self.header.setStyleSheet("font-weight: bold; font-size: 15px; border: 0px; "
                                  "background-color: transparent;")
        self.header.setAlignment(Qt.Qt.AlignCenter)
        self.header.move(round(self.width() / 2 - self.header.width() / 2) - 5, 0)

        self.copy_all_button = QPushButton("Copy All", self)
        self.copy_all_button.setFixedSize(80, 25)
        self.copy_all_button.move(10, 20)
        self.copy_all_button.clicked.connect(self.copy_all)

        self.copy_new_button = QPushButton("Copy New", self)
        self.copy_new_button.setFixedSize(80, 25)
        self.copy_new_button.move(100, 20)
        self.copy_new_button.clicked.connect(self.copy_new)

        self.delete_all_button = QPushButton("Delete.A", self)
        self.delete_all_button.setFixedSize(80, 25)
        self.delete_all_button.move(190, 20)
        self.delete_all_button.clicked.connect(self.delete_all)

    def establish_connection(self):
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(self.robot.ip, username="jetson", password=self.robot.password)
            self.sftp = self.ssh_client.open_sftp()
        except Exception as e:
            logging.error(f"Error establishing connection: {e}")
            ErrorBox(self, title="SFTP Connection Error", message="Error establishing SFTP connection", error=e)

    def get_file_list(self):
        try:
            if self.sftp is None:
                self.establish_connection()
            return self.sftp.listdir(self.bag_file_location)
        except Exception as e:
            logging.error(f"Error getting file list: {e}")
            ErrorBox(self, title="SFTP File List Error", message="Error getting file list", error=e)

    def copy_thread(self, files):
        try:
            if self.sftp is None:
                self.establish_connection()
            for file in files:
                self.sftp.get(self.bag_file_location + file, self.save_location + file)
        except Exception as e:
            logging.error(f"Error copying files: {e}")
            ErrorBox(self, title="SFTP Copy Error", message="Error copying files", error=e)

    def copy_all(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm SFTP Connection",
                                      message="Are you sure you want to establish an SFTP connection?",
                                      detailed_message="While the connection is being established, the GUI will be unresponsive.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                files = self.get_file_list()
                # Calculate the total size of the files to be copied and display it in the second confirmation box
                total_size = 0
                for file in files:
                    total_size += self.sftp.stat(self.bag_file_location + file).st_size
                confirm = ConfirmationBox(self, title="Confirm Copy",
                                          message=f"Are you sure you want to copy {len(files)} files?",
                                          detailed_message=f"This will copy {len(files)} files, with a total size of {total_size} bytes.")
                confirm.exec_()
                if confirm.result() == Qt.QMessageBox.Yes:
                    # Create a thread to copy the files so that the GUI doesn't freeze
                    thread = threading.Thread(target=self.copy_thread, args=(files,), daemon=True)
                    thread.start()
        except Exception as e:
            logging.error(f"Error in copy_all: {e}")
            ErrorBox(self, title="Error Copying Files", message="Error copying files", error=e)

    def copy_new(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm SFTP Connection",
                                      message="Are you sure you want to establish an SFTP connection?",
                                      detailed_message="While the connection is being established, the GUI will be unresponsive.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                files = self.get_file_list()
                # Compare the files in the save location to the files on the Jetson and only copy the new ones
                new_files = []
                for file in files:
                    if file not in os.listdir(self.save_location):
                        new_files.append(file)
                # Calculate the total size of the files to be copied and display it in the second confirmation box
                total_size = 0
                for file in new_files:
                    total_size += self.sftp.stat(self.bag_file_location + file).st_size
                confirm = ConfirmationBox(self, title="Confirm Copy",
                                          message=f"Are you sure you want to copy {len(new_files)} files?",
                                          detailed_message=f"This will copy {len(new_files)} files, with a total size of {total_size} bytes.")
                confirm.exec_()
                if confirm.result() == Qt.QMessageBox.Yes:
                    # Create a thread to copy the files so that the GUI doesn't freeze
                    thread = threading.Thread(target=self.copy_thread, args=(new_files,), daemon=True)
                    thread.start()
        except Exception as e:
            logging.error(f"Error in copy_new: {e}")
            ErrorBox(self, title="Error Copying Files", message="Error copying files", error=e)

    def delete_all(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Stop",
                                      message="Are you sure you want to stop the Jetson?",
                                      detailed_message="This will stop the Jetson, this action is irreversible.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                logging.info("Sending command to stop the Jetson")
                self.send_ssh_command("sudo shutdown -h now")
        except Exception as e:
            logging.error(f"Error stopping Jetson: {e}")
            ErrorBox(self, title="Error Stopping Jetson", message="Error stopping Jetson", error=e)
