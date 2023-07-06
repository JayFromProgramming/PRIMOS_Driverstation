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

    if os.path.exists("configs/target_address.json"):
        values = json.load(open("configs/target_address.json"))
        target_address = values["address"]
        target_port = values["port"]
    else:
        os.mkdir("configs")
        target_address = None
        target_port = None

    parser = argparse.ArgumentParser(description='PRIMROSE Driver Station')
    parser.add_argument('--ros-address', type=str, default=target_address, help='ROS Bridge IP Address',
                        required=True if target_address is None else False)
    parser.add_argument('--ros-port', type=int, default=target_port, help='ROS Bridge Port',
                        required=True if target_port is None else False)
    args = parser.parse_args()

    # Save the new target address and port
    with open("configs/target_address.json", "w") as f:
        json.dump({"address": args.ros_address, "port": args.ros_port}, f, indent=4)

    print(f"Main started with PID {os.getpid()} Address: {args.ros_address}:{args.ros_port}")
    app = QApplication([])
    app.setStyle('Windows')
    app.setApplicationName("PRIMROSE Driver Station - Initializing...")
    app.setApplicationVersion("1.0.0")
    app.setWindowIcon(QtGui.QIcon("resources/icon.svg"))
    app.setQuitOnLastWindowClosed(True)

    myappid = 'pstdl.primrose.drivestation'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # while pioneer.client.is_connecting:
    #     pass
    primrose = ROSInterface(args)  # MAC: a0:a8:cd:be:8d:2c
    # while pioneer.client.is_connecting:
    #     pass
    gui = DriverStatonUI.DriverStationUI(primrose)
    # threading.Thread(target=gui.run, daemon=True).start()

    app.exec_()
    # gui.run()
    # while pioneer.client.is_connected:
    #     pass
    primrose.disconnect()
    # Terminate the process PID
    os.kill(os.getpid(), 9)

