import ctypes
import os
import json
import sys

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

    if not os.path.exists("configs"):
        os.mkdir("configs")

    if os.path.exists("configs/target_address.json"):
        values = json.load(open("configs/target_address.json"))
        target_address = values["address"] if "address" in values else None
        target_port = values["port"] if "port" in values else None
        target_password = values["password"] if "password" in values else None
    else:
        target_address = None
        target_port = None
        target_password = None

    parser = argparse.ArgumentParser(description='PRIMROSE Driver Station')
    parser.add_argument('--ros-address', type=str, default=target_address, help='ROS Bridge IP Address',
                        required=True if target_address is None else False)
    parser.add_argument('--ros-port', type=int, default=target_port, help='ROS Bridge Port',
                        required=True if target_port is None else False)
    parser.add_argument('--ros-password', type=str, default=target_password, help='ROS Bridge Password',
                        required=True if target_password is None else False)
    parser.add_argument('-always-on-top', action='store_true', help='Enable always on top mode')
    args = parser.parse_args()

    # Save the new target address and port
    with open("configs/target_address.json", "w") as f:
        json.dump({"address": args.ros_address, "port": args.ros_port, "password": args.ros_password}, f, indent=4)

    print(f"Main started with PID {os.getpid()} Address: {args.ros_address}:{args.ros_port}")
    app = QApplication([])
    app.setStyle('Windows')
    app.setApplicationName("PRIMROSE Driver Station - Initializing...")
    app.setApplicationVersion("1.0.0")
    app.setWindowIcon(QtGui.QIcon("resources/icon.svg"))
    app.setQuitOnLastWindowClosed(True)

    myappid = 'pstdl.primrose.drivestation'  # arbitrary string
    # Check if the OS is Windows
    if os.name == 'nt':  # If so then we need to sent and appID for the taskbar
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    primrose = ROSInterface(args)
    gui = DriverStatonUI.DriverStationUI(primrose, args)
    app.exec_()
    primrose.disconnect()
    # Terminate the process PID
    # os.kill(os.getpid(), 9)

