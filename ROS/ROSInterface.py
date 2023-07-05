import argparse
import os
import threading
import time
import traceback

import paramiko
import roslibpy
import threading
import logging

from ROS.RobotState import SmartTopic

from loguru import logger as logging

topic_targets = [
    SmartTopic("/driv/cmd_vel", topic_type="geometry_msgs/Twist", allow_update=True),
    SmartTopic("/mciu/Hopper/loadcells/control", allow_update=True),
    SmartTopic("/mciu/Suspension/loadcells/control", allow_update=True),
    SmartTopic("/mciu/Front_Left/actuators/input", allow_update=True),
    SmartTopic("/mciu/Front_Right/actuators/input", allow_update=True),
    SmartTopic("/mciu/Rear_Left/actuators/input", allow_update=True),
    SmartTopic("/mciu/Rear_Right/actuators/input", allow_update=True),
    SmartTopic("/mciu/Front_Left/odrive/input", allow_update=True),
    SmartTopic("/mciu/Front_Right/odrive/input", allow_update=True),
    SmartTopic("/mciu/Rear_Left/odrive/input", allow_update=True),
    SmartTopic("/mciu/Rear_Right/odrive/input", allow_update=True),
    SmartTopic("/mciu/Trencher/odrive/input", allow_update=True),
    SmartTopic("/mciu/Conveyor/odrive/input", allow_update=True),
    SmartTopic("/driv/Trencher/throttle", allow_update=True),
    SmartTopic("/mciu/estop_controller", allow_update=True),
    SmartTopic("/mciu/battery_monitor", allow_update=True),
]


class ROSInterface:
    """
    This class handles the connection to the ROS bridge and all the SmartTopics
    """

    def __init__(self, arguments: argparse.Namespace):
        self.client = None  # type: roslibpy.Ros or None
        self.address = arguments.ros_address
        self.port = arguments.ros_port

        self.background_thread = None

        self.smart_topics = topic_targets
        self.future_callbacks = []

        threading.Thread(target=self.establish_connection, daemon=True).start()

    @property
    def is_connected(self):
        return self.client.is_connected if self.client is not None else False

    def hook_on_ready(self, callback):
        if self.client is not None:
            self.client.on_ready(callback)
        else:
            self.future_callbacks.append(callback)

    def establish_connection(self):
        self.connect(address=self.address, port=self.port)

    def connect(self, address, port):
        try:
            logging.info("Connecting to ROS bridge")
            self.address = address
            self.port = port
            self.client = roslibpy.Ros(host=self.address, port=self.port)
            self._connect()

            # Make sure the process doesn't close
            while True:
                time.sleep(1)

            # self.rosserial_thread = threading.Thread(target=ros_serial, daemon=True, args=(address,))
            # self.rosserial_thread.start()

            # for smart_topic in self.smart_topics:
            #     smart_topic.connect()

        except Exception as e:
            logging.error(f"Error connecting to ROS bridge: {e} {traceback.format_exc()}")

    def disconnect(self):
        try:
            self.terminate()
            del self.client  # Force garbage collection of the client
            self.client = None
            # self.client = roslibpy.Ros(host=self.address, port=self.port)
        except Exception as e:
            logging.error(f"Failed to disconnect: {e} {traceback.format_exc()}")

    def terminate(self):
        logging.info("Terminating ROSInterface")
        # self.robot_state_monitor.unsub_all()
        if self.client is not None:
            self.client.terminate()
            del self.client
        self.client = None
        # self.robot_state_monitor.set_client(self.client)

    def _connect(self):
        try:
            self.client.run()
        except Exception as e:
            logging.error(f"Connection to ROS bridge failed: {e}")
            self.client.close()
        else:
            logging.info("Connected to ROS bridge")
            print(f"Topics: {self.get_topics()}")
            print(f"Services: {self.get_services()}")
            print(f"Nodes: {self.get_nodes()}")
            for smart_topic in self.smart_topics:
                smart_topic.set_client(self.client)
                # smart_topic.connect()
            for callback in self.future_callbacks:
                self.client.on_ready(callback)

    def drive(self, forward=0.0, turn=0.0):
        state = self.get_state("primrose/cmd_vel")
        state.value = {"linear": {"x": forward, "y": 0, "z": 0},
                       "angular": {"x": 0, "y": 0, "z": turn}}
        # logging.info(f"Driving forward: {forward}, turn: {turn}")

    def get_services(self):
        return self.client.get_services()

    def get_topics(self):
        return self.client.get_topics()

    def get_nodes(self):
        return self.client.get_nodes()

    def execute_service(self, name, callback=None, errback=None, timeout=5):
        if self.client is None:
            raise Exception("No ROS client")
        if not self.client.is_connected:
            raise Exception("Not connected to ROS bridge")
        # if name not in self.client.get_services():
        #     raise Exception(f"Service {name} not available")
        service = roslibpy.Service(self.client, name, 'std_srvs/Empty')
        request = roslibpy.ServiceRequest()
        service.call(request, callback=callback, errback=errback, timeout=timeout)

    def execute_custom_service(self, name, args: dict, service_type, callback=None, errback=None, timeout=5):
        if self.client is None:
            raise Exception("No ROS client")
        if not self.client.is_connected:
            raise Exception("Not connected to ROS bridge")
        # if name not in self.client.get_services():
        #     raise Exception(f"Service {name} not available")
        service = roslibpy.Service(self.client, name, service_type)
        request = roslibpy.ServiceRequest(args)
        service.call(request, callback=callback, errback=errback, timeout=timeout)

    def get_state(self, name):
        for smart_topic in self.smart_topics:
            if smart_topic.disp_name == name:
                return smart_topic
        return None