import os
import threading
import time

from PyQt5 import Qt
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel

from loguru import logger as logging

from QT5_Classes.ConfirmationBox import ConfirmationBox

import paramiko

from QT5_Classes.ErrorBox import ErrorBox
from QT5_Classes.ProgressBar import ProgressBar


class RosbagControls(QWidget):

    def __init__(self, robot, parent=None):
        super().__init__(parent)
        self.robot = robot
        self.bag_file_location = "/media/ssd/fdr/"
        self.save_location = "copied_bag_files"  # The location on the local machine to save the bag files to

        if not os.path.exists(self.save_location):
            os.mkdir(self.save_location)

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

        self.reindex_button = QPushButton("Reindex", self)
        self.reindex_button.setFixedSize(80, 25)
        self.reindex_button.move(190, 20)
        self.reindex_button.clicked.connect(self.reindex_all)

    def establish_connection(self):
        try:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(self.robot.address, username="ubuntu", password=self.robot.password)
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
            index = 0
            for file in files:
                logging.info(f"Copying {file}")
                # progress_box.update_progress(index, f"Copying {file}...")
                self.sftp.get(self.bag_file_location + file, os.path.join(self.save_location, file))
                index += 1
                logging.info(f"Finished copying {file}")
            # progress_box.close()
        except Exception as e:
            logging.error(f"Error copying files: {e}")
            ErrorBox(self, title="SFTP Copy Error", message="Error copying files", error=e)

    def reindex_thread(self, files):
        try:
            if self.sftp is None:
                self.establish_connection()
            for file in files:
                # Run rosbag reindex on any files that end in .active
                if file.endswith(".active"):
                    logging.info(f"Reindexing {file}")
                    self.sftp.exec_command(f"rosbag reindex {self.bag_file_location + file} -f")
                    logging.info(f"Finished reindexing {file}")
        except Exception as e:
            logging.error(f"Error reindexing files: {e}")
            ErrorBox(self, title="SFTP Reindex Error", message="Error reindexing files", error=e)

    def copy_all(self):
        try:
            # progress = ProgressBar(self, title="Copying Files", message="Copying files...")
            # for i in range(100):
            #     progress.set_progress(i, f"Copying file {i}...")
            #     time.sleep(1)

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
                    progress = ProgressBar(self, title="Copying Files", message="Copying files...", max_value=len(files))
                    # Create a thread to copy the files so that the GUI doesn't freeze
                    thread = threading.Thread(target=self.copy_thread, args=(files, progress), daemon=True)
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
            logging.exception(e)
            ErrorBox(self, title="Error Copying Files", message="Error copying files", error=e)

    def reindex_all(self):
        try:
            confirm = ConfirmationBox(self, title="Confirm Reindex",
                                      message="Are you sure you want to reindex all files?",
                                      detailed_message="This will reindex all files in the save location.")
            confirm.exec_()
            if confirm.result() == Qt.QMessageBox.Yes:
                # Create a thread to reindex the files so that the GUI doesn't freeze
                thread = threading.Thread(target=self.reindex_thread, args=(os.listdir(self.save_location),), daemon=True)
                thread.start()
        except Exception as e:
            logging.error(f"Error in reindex_all: {e}")
            ErrorBox(self, title="Error Reindexing Files", message="Error reindexing files", error=e)
