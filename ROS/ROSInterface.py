import os
import threading
import time
import traceback

import paramiko
import roslibpy
# import threading
import multiprocessing
import logging

from ROS.RobotState import RobotStateLoader, SmartTopic

logging = logging.getLogger(__name__)

topic_targets = [
    SmartTopic("motor_state_info", "/system_diagnostics/motors/info"),
    SmartTopic("tell_tails", "/system_diagnostics/tell_tails"),
]


def ros_serial(address="localhost", username="ubuntu", password="ubuntu"):
    logging.info("Connecting over SSH to %s", address)
    ssh = paramiko.SSHClient()  # type: paramiko.SSHClient
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # Set policy to auto add host key
    try:
        ssh.connect(address, port=22, username=username, password=password)  # Connect to server
    except Exception as e:
        logging.error(f"SSH connection failed: {e}")
        return False
    else:
        # Execute the ros start.py script
        print("Starting ROSSERIAL to interface with the arduino")
        stdin, stdout, stderr = ssh.exec_command("rosrun rosserial_python serial_node.py _port:=/dev/ttyACM0")
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                print(stdout.channel.recv(1024).decode("utf-8"), end="")
            if stderr.channel.recv_stderr_ready():
                print(stderr.channel.recv_stderr(1024).decode("utf-8"), end="")

        if stdout.channel.recv_exit_status() != 0:
            logging.error("SSH command failed")
            return False

        ssh.close()
        return True


class RobotStateMonitor:

    def __init__(self, client, state_watcher):
        self.client = client
        self.state_watcher = state_watcher
        self.smart_topics = []
        self.cached_topics = {}
        self.setup_watchers()

    def _load_topics(self):
        logging.info("RobotStateMonitor: Loading topics")
        topic_dict = {}
        for topic in self.client.get_topics():
            if topic in self.cached_topics:
                continue
            topic_type = self.client.get_topic_type(topic)
            topic_dict[topic] = {"name": topic, "type": topic_type}
            logging.info(f"Loaded topic {topic} of type {topic_type}")
        self.cached_topics = topic_dict
        logging.info("RobotStateMonitor: Loaded topics")

    def set_client(self, client):
        self.client = client
        for smart_topic in topic_targets:
            smart_topic.set_client(self.client)

    def unsub_all(self):
        logging.info("Unsubscribing from all topics")
        for smart_topic in self.state_watcher.states():
            smart_topic.unsub()

    def setup_watchers(self):
        for smart_topic in topic_targets:
            self.state_watcher.add_watcher(smart_topic)
            # self.state_watcher[smart_topic.disp_name] = smart_topic
            self.smart_topics.append(smart_topic)  # Used so the garbage collector doesn't collect the topic

    # def setup_listener(self, name, topic):
    #     message_type = self.cached_topics[topic]["type"]
    #     logging.info(f"Setting up listener for {topic} of type {message_type}")
    #     self.state_watcher.add_watcher

    def get_state(self, name):
        return self.state_watcher.state(name)

    def get_states(self):
        return self.state_watcher.states()

    def is_state_available(self, name):
        return name in self.state_watcher.states()


class ROSInterface:
    """
    This class handles the connection to the ROS bridge and all the SmartTopics
    """

    def __init__(self, queue):
        print(f"ROSInterface started with PID {os.getpid()}")
        self.client = None  # type: roslibpy.Ros or None
        self.address = None
        self.port = None
        self.robot_state = RobotStateLoader(queue)
        self.robot_state_monitor = RobotStateMonitor(self.client, self.robot_state)
        self.background_thread = None

        self.smart_topics = topic_targets
        self.rosserial_thread = None  # type: multiprocessing.Process or None
        self.future_callbacks = []

        self.connect("141.219.125.127", 9090)

    @property
    def is_connected(self):
        return self.client.is_connected if self.client is not None else False

    def hook_on_ready(self, callback):
        if self.client is not None:
            self.client.on_ready(callback)
        else:
            self.future_callbacks.append(callback)

    def connect(self, address, port):
        try:
            logging.info("Connecting to ROS bridge")
            self.address = address
            self.port = port
            self.client = roslibpy.Ros(host=self.address, port=self.port)
            self.robot_state_monitor.set_client(self.client)
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
            self.robot_state_monitor.set_client(self.client)
        except Exception as e:
            logging.error(f"Failed to disconnect: {e} {traceback.format_exc()}")

    def terminate(self):
        logging.info("Terminating ROSInterface")
        self.robot_state_monitor.unsub_all()
        if self.client is not None:
            self.client.terminate()
            del self.client
        self.client = None
        # self.robot_state_monitor.set_client(self.client)

    def _maintain_connection(self):
        # self._connect()
        # while True:
        #     time.sleep(1)
        #     if not self.client.is_connected:
        #         logging.info("Connection to ROS bridge lost, reconnecting")
        #         self._connect()
        pass

    def _connect(self):
        try:
            self.client.run()
        except Exception as e:
            logging.error(f"Connection to ROS bridge failed: {e}")
            self.client.close()
        else:
            self.robot_state_monitor = RobotStateMonitor(self.client, self.robot_state)
            print(f"Topics: {self.get_topics()}")
            print(f"Services: {self.get_services()}")
            print(f"Nodes: {self.get_nodes()}")
            for callback in self.future_callbacks:
                self.client.on_ready(callback)

    def _setup_publisher(self, topic, message_type="std_msgs/String"):
        publisher = roslibpy.Topic(self.client, topic, message_type)
        publisher.advertise()
        logging.info(f" Publisher setup for topic: {topic}")
        return publisher

    def get_state(self, name):
        return self.robot_state_monitor.get_state(name)

    def get_smart_topics(self):
        return self.robot_state_monitor.get_states()

    def drive(self, forward=0.0, turn=0.0):
        state = self.get_state("cmd_vel")
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
