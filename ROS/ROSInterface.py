import argparse
import os
import threading
import time
import traceback

import paramiko
import roslibpy
import threading
import logging

# from roslibpy.core import RosTimeoutError

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
        self.twister = None
        self.address = arguments.ros_address
        self.port = arguments.ros_port
        self.password = arguments.ros_password

        self.ping_time = 0

        self.background_thread = None

        self.connection_ready = False

        self.driving_enabled = False
        self.steering_enabled = False

        self.smart_topics = topic_targets
        self.future_callbacks = []

        self.on_connect_callbacks = []  # type: list[callable]
        self.on_disconnect_callbacks = []  # type: list[callable]

        self.connection_thread = None  # type: threading.Thread
        self.establish_connection()

    def background_ping_thread(self):
        # Ping the jetson every second and calculate the ping time in ms
        service = roslibpy.Service(self.client, "/qmc/ping_service", "primrose-qmc/ping")
        request = roslibpy.ServiceRequest()
        while True:
            if not self.is_connected:
                time.sleep(5)
                continue
            try:
                start = time.time()
                service.call(request)
                ping_time = (time.time() - start) * 1000
                if ping_time != 0:
                    self.ping_time = ping_time
                # logging.debug(f"Ping time: {self.ping_time}ms")
            except Exception as e:
                logging.error(f"Error in ping thread: {e}")
            time.sleep(1)

    def wait_for_reconnect(self):
        logging.info("Waiting for reconnect")
        # while not self.is_connected:
        #     self.connection_ready = True
        #     time.sleep(0.1)
        # logging.info("Reconnected")
        # # Call the on_connect callbacks
        # for callback in self.on_connect_callbacks:
        #     try:
        #         callback()
        #     except Exception as e:
        #         logging.error(f"Error in on_connect_callback: {e}")
        #         logging.exception(e)

    @property
    def is_connected(self):
        return self.connection_ready

    @property
    def is_connecting(self):
        return self.connection_ready is False and self.client.is_connected

    def attach_on_connect_callback(self, callback):
        self.on_connect_callbacks.append(callback)

    def attach_on_disconnect_callback(self, callback):
        self.on_disconnect_callbacks.append(callback)

    def hook_on_ready(self, callback):
        self.future_callbacks.append(callback)

    def on_ready(self):
        logging.info(f"Connection to ROS bridge at {self.address}:{self.port} established")
        logging.debug(f"ROS topics: {self.client.get_topics()}")
        logging.debug(f"ROS services: {self.client.get_services()}")
        logging.debug(f"ROS nodes: {self.client.get_nodes()}")
        for callback in self.on_connect_callbacks:
            try:
                callback()
            except Exception as e:
                logging.error(f"Error in on_connect_callback: {e}")
                logging.exception(e)
        for smart_topic in self.smart_topics:
            smart_topic.set_client(self.client)
        for callback in self.future_callbacks:
            self.client.on_ready(callback)
        self.connection_ready = True
        threading.Thread(target=self.background_ping_thread, daemon=True).start()

    def on_close(self, event):
        self.connection_ready = False
        logging.info(f"Connection to ROS bridge at {self.address}:{self.port} was lost")
        threading.Thread(target=self.wait_for_reconnect, daemon=True).start()
        # for callback in self.on_disconnect_callbacks:
        #     try:
        #         callback()
        #     except Exception as e:
        #         logging.error(f"Error in on_disconnect_callback: {e}")
        #         logging.exception(e)

    def establish_connection(self):
        self.connection_thread = threading.Thread(target=self.connect, daemon=True)
        self.connection_thread.start()

    def connect(self):
        try:
            logging.info(f"Attempting to connect to ROS bridge at {self.address}:{self.port}")
            self.client = roslibpy.Ros(host=self.address, port=self.port)
            self.twister = self.client.factory
            self.twister.set_max_delay(5)
            self.client.on_ready(self.on_ready)
            self.client.on("close", self.on_close)
            self._connect()

            # Make sure the process doesn't close
            # while True:
            #     time.sleep(1)

            # self.rosserial_thread = threading.Thread(target=ros_serial, daemon=True, args=(address,))
            # self.rosserial_thread.start()

            # for smart_topic in self.smart_topics:
            #     smart_topic.connect()

        except Exception as e:
            logging.error(f"Error connecting to ROS bridge: {e} {traceback.format_exc()}")

    def disconnect(self):
        try:
            self.terminate()
            self.client = None
        except Exception as e:
            logging.error(f"Failed to disconnect: {e} {traceback.format_exc()}")

    def terminate(self):
        if self.connection_thread is not None:
            if self.connection_thread.is_alive():
                logging.info("Terminating ROSInterface connection thread")
                self.connection_thread.join(5)
        logging.info("Unsubscribing from all topics, and unadvertizing all publishers")
        for smart_topic in self.smart_topics:
            smart_topic.unsub()
        logging.info("Terminating ROSInterface")
        # if self.client is not None:
        #     try:
        #         self.client.terminate()
        #     except roslibpy.core.RosTimeoutError:
        #         logging.error(f"Unable to disconnect from ROS bridge")
        #     else:
        #         logging.info(f"Disconnected from ROS bridge at {self.address}:{self.port}")

    def _connect(self):
        try:
            self.client.run()
        except roslibpy.core.RosTimeoutError:
            logging.error(f"Initial connection attempt to the ROS bridge timed out, automatic retry is enabled")
            for callback in self.on_connect_callbacks:
                try:
                    callback()
                except Exception as e:
                    logging.error(f"Error in on_connect_callback: {e}")
                    logging.exception(e)
        except Exception as e:
            logging.error(f"Connection to ROS bridge failed: {e}")
            logging.exception(e)

    def get_services(self):
        return self.client.get_services()

    def get_topics(self):
        return self.client.get_topics()

    def get_nodes(self):
        return self.client.get_nodes()

    def execute_service(self, name, callback=None, errback=None, timeout=5):
        if self.client is None:
            raise ConnectionAbortedError("No ROS client")
        if not self.client.is_connected:
            raise ConnectionError("Not connected to ROS bridge")
        # if name not in self.client.get_services():
        #     raise Exception(f"Service {name} not available")
        service = roslibpy.Service(self.client, name, 'std_srvs/Empty')
        request = roslibpy.ServiceRequest()
        service.call(request, callback=callback, errback=errback, timeout=timeout)

    def execute_custom_service(self, name, args: dict, service_type, callback=None, errback=None, timeout=5):
        if self.client is None:
            raise ConnectionAbortedError("No ROS client")
        if not self.client.is_connected:
            raise ConnectionError("Not connected to ROS bridge")
        # if name not in self.client.get_services():
        #     raise Exception(f"Service {name} not available")
        service = roslibpy.Service(self.client, name, service_type)
        request = roslibpy.ServiceRequest(args)
        service.call(request, callback=callback, errback=errback, timeout=timeout)

    def get_state(self, name):
        for smart_topic in self.smart_topics:
            if smart_topic.disp_name == name:
                return smart_topic
        # Create a new SmartTopic
        new_topic = SmartTopic(name, allow_update=True)
        new_topic.set_client(self.client)
        self.smart_topics.append(new_topic)
        return new_topic
