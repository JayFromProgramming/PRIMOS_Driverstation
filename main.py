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

import argparse

from ROS.ROSInterface import ROSInterface

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='PRIMROSE Driver Station')
    parser.add_argument('--ros-address', type=str, default="141.219.122.11", help='ROS Bridge IP Address')
    parser.add_argument('--ros-port', type=int, default=9090, help='ROS Bridge Port')

    args = parser.parse_args()

    print(f"Main started with PID {os.getpid()} Address: {args.ros_address}:{args.ros_port}")
    app = QApplication([])
    app.setStyle('Windows')
    app.setApplicationName("PRIMROSE Driver Station")
    app.setApplicationVersion("1.0.0")
    app.setWindowIcon(QtGui.QIcon("resources/icon.svg"))
    app.setQuitOnLastWindowClosed(True)

    myappid = 'pstdl.primrose.drivestation'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # while pioneer.client.is_connecting:
    #     pass
    pioneer = ROSInterface(args)  # MAC: a0:a8:cd:be:8d:2c
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

