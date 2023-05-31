import ctypes
import multiprocessing
import os
import sys
import asyncio
import threading

import roslibpy
from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication

from ROS import ROSInterface
import DriverStatonUI
import logging
import paramiko

from ROS.ROSInterface import ROSInterface

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    print(f"Main started with PID {os.getpid()}")
    app = QApplication([])
    app.setStyle('Windows')
    app.setApplicationName("PRIMROS Driver Station")
    app.setApplicationVersion("1.0.0")
    app.setWindowIcon(QtGui.QIcon("resources/icon.svg"))
    app.setQuitOnLastWindowClosed(True)

    myappid = 'pstdl.primrose.drivestation'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # while pioneer.client.is_connecting:
    #     pass
    pioneer = ROSInterface()  # MAC: a0:a8:cd:be:8d:2c
    # while pioneer.client.is_connecting:
    #     pass
    gui = DriverStatonUI.DriverStationUI(pioneer)
    # threading.Thread(target=gui.run, daemon=True).start()

    app.exec_()
    # gui.run()
    # while pioneer.client.is_connected:
    #     pass
    pioneer.terminate()
    # Set qt event loop

