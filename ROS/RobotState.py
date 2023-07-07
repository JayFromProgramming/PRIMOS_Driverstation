import base64
import random
import threading
import time
from io import BytesIO

import cv2
import numpy as np
import roslibpy
import logging
from PIL import Image

from loguru import logger as logging

class SmartTopic:

    def __init__(self, topic_name, disp_name=None, **kwargs):
        if disp_name is None:
            disp_name = topic_name
        logging.info(f"Initializing {disp_name} on topic {topic_name}")
        self.disp_name = disp_name
        self.topic_name = topic_name

        self.exists = False
        self.has_data = False
        self.is_single = True
        self._has_changed = False

        self._update_interval = []  # Used to calculate the update rate over the last 10 updates

        self.client = kwargs.get("client", None)
        self.topic_type = kwargs.get("topic_type", None)
        self.throttle_rate = kwargs.get("throttle_rate", 0)
        self.queue_size = kwargs.get("queue_size", 5)
        self.auto_reconnect = kwargs.get("auto_reconnect", True)
        self.allow_update = kwargs.get("allow_update", False)
        self.hidden = kwargs.get("hidden", False)
        self._compression = kwargs.get("compression", None)

        self._value = None
        self._lock = threading.Lock()
        self._last_update = 0
        self._listener = None  # type: roslibpy.Topic or None
        self._publisher = None  # type: roslibpy.Topic or None
        logging.info(f"{self.disp_name} created and initialized... Waiting for connection")
        if self.client is not None:
            self.client.on_ready(self.connect, run_in_thread=True)

    def set_client(self, client):
        try:
            self.client = client
            self.client.on_ready(self.connect, run_in_thread=True)
        except Exception as e:
            logging.error(f"Error setting client for {self.disp_name}: {e}")

    def set_type(self, topic_type):
        self.topic_type = topic_type

    def _topic_type_callback(self, topic_type):
        if topic_type == "":
            self.exists = False
            logging.debug(f"Topic {self.topic_name} does not exist")
            thread = threading.Thread(target=self._recheck_exists, daemon=True)
            thread.start()
        else:
            logging.info(f"Acquired type {topic_type} for topic {self.topic_name}")
            self.connect()

    def connect(self):
        if self.topic_type is None:
            # Get the type of the topic from the ROS master
            self.topic_type = self.client.get_topic_type(self.topic_name)
            if self.topic_type == "":
                self.exists = False
                logging.error(f"Topic {self.topic_name} does not exist")
                return
            else:
                logging.info(f"Acquired type {self.topic_type} for topic {self.topic_name}")
                self.exists = True

        self._listener = roslibpy.Topic(self.client, self.topic_name, self.topic_type, queue_size=5,
                                        throttle_rate=self.throttle_rate, reconnect_on_close=self.auto_reconnect,
                                        compression=self._compression)
        self._listener.subscribe(self._update)
        if self.allow_update:
            logging.info(f"Creating publisher for {self.disp_name}")
            self._publisher = roslibpy.Topic(self.client, self.topic_name, self.topic_type)
            self._publisher.advertise()
        else:
            self._publisher = None
            logging.info(f"Listener for {self.disp_name} created")

    def _update(self, message):
        """
        :param message:
        :return:
        """
        self._lock.acquire()
        self.has_data = True
        if "data" in message:
            value = message["data"]
        else:
            value = message
            self.not_single = True
        if self._value != value:
            self._value = value
            self._has_changed = True
        self._lock.release()

        self._last_update = time.time()
        self._update_interval.append(self._last_update)
        if len(self._update_interval) > 10:
            self._update_interval.pop(0)

    def has_changed(self):
        """Returns None if the value hasn't changed and the new value if it has"""
        self._lock.acquire()
        if self._has_changed:
            self._has_changed = False
            self._lock.release()
            return self._value
        self._lock.release()
        return None

    @property
    def value(self):
        self._lock.acquire()
        value = self._value
        self._lock.release()
        return value

    @value.setter
    def value(self, updated_values):
        if self.client is None:
            raise ConnectionAbortedError("Cannot update value when client is not set")
        if not self.client.is_connected:
            raise ConnectionError("Cannot update value when client is not connected")
        if self._publisher is None:
            # Create a publisher for the topic if there was an attempt to publish to it
            logging.info(f"Creating publisher for {self.disp_name}")
            self._publisher = roslibpy.Topic(self.client, self.topic_name, self.topic_type)
            self._publisher.advertise()
        if self.is_single and self.topic_type != "geometry_msgs/Twist":
            msg = roslibpy.Message({"data": updated_values})
            # logging.debug(f"Publishing {updated_values} to {self.topic_name}")
        else:
            # If the value is not a single value, but a list of values or a dictionary
            # Then we need to update the values in the dictionary and publish the entire dictionary
            # Generate an instance of the message type
            if self.has_data:
                # If we have data, then we can use the current value as a template
                msg = roslibpy.Message(self.value)
            else:
                # Otherwise, we need to create a blank message
                msg = roslibpy.Message({})
            # Update the values in the message
            for key, value in updated_values.items():
                msg[key] = value

        self._publisher.publish(msg)

    def get_update_rate(self) -> float:
        """Returns the current update rate of the topic in Hz"""
        if len(self._update_interval) > 1:
            try:
                return 1 / ((self._update_interval[-1] - self._update_interval[0]) / len(self._update_interval))
            except ZeroDivisionError:
                return 0
        else:
            return 0

    def get_status(self):
        """Returns the current state of the topic, and that states associated color"""
        if self.exists:
            if self.has_data:
                if self._listener.is_subscribed:
                    if self._last_update > time.time() - 5:
                        return f"{round(self.get_update_rate())}Hz: OK", "green"
                    else:
                        return "STALE", "darkorange"
                else:
                    return "UNSUBED", "darkorange"
            else:
                return "NO DATA", "red"
        elif not self.client:
            return "NO CLIENT", "red"
        elif not self.client.is_connected:
            return "NO CONN", "red"
        else:
            return "MISSING", "red"

    def unsub(self):
        if self._listener:
            self._listener.unsubscribe()
        if self._publisher:
            self._publisher.unadvertise()

        self.exists = False
        self.has_data = False
        self._value = None
        self._has_changed = False
        self._last_update = 0
        logging.info(f"{self.disp_name} unsubscribed from {self.topic_name}")

    def unsubscribe(self):
        self._listener.unsubscribe()

    def resubscribe(self):
        self._listener.subscribe(self._update)

    def is_stale(self):
        if self._last_update > time.time() - 5:
            return False
        else:
            return True

class RobotState:

    def __init__(self):
        self._topics = {}

    # def add_watcher(self, client, name, topic, topic_type, allow_setting=False):
    #     topic = roslibpy.Topic(client, topic, topic_type, reconnect_on_close=True)
    #     if topic_type == "/camera/image/compressed":
    #         state = ImageHandler(name)
    #         topic.subscribe(state.handle_image)
    #     else:
    #         state = State(name, topic, allow_setting)
    #     self._topics[name] = state
    #     logging.info(f"Added watcher for {name} on {topic} of type {topic_type}")

    def add_watcher(self, smart_topic):
        self._topics[smart_topic.disp_name] = smart_topic

    def state(self, name):
        for smart_topic in self.states():
            if smart_topic.disp_name == name or smart_topic.topic_name == name:
                return smart_topic
        return None

    def states(self):
        return self._topics.values()
