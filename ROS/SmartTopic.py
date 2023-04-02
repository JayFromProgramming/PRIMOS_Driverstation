import time

import roslibpy


class SmartTopic:

    def __init__(self, name, topic_type, subscribe=False, publish=False):
        self.client = None
        self.name = name
        self.topic_type = topic_type
        self.subscribe = subscribe
        self.subscriber = None
        self.publish = publish
        self.publisher = None

        # Latching variables
        self.last_message = None
        self.last_message_time = None

    def connect(self, client: roslibpy.Ros):
        self.client = client
        if self.subscribe:
            self.subscriber = roslibpy.Topic(self.client, self.name, self.topic_type)
            self.subscriber.subscribe(self._on_message)

        if self.publish:
            self.publisher = roslibpy.Topic(self.client, self.name, self.topic_type)

    @property
    def value(self):
        return self.last_message

    @value.setter
    def value(self, value):
        self._publish(value)

    def _on_message(self, message):
        self.last_message = message
        self.last_message_time = time.time()

    def _publish(self, message):
        if self.publisher is not None:
            self.publisher.publish(message)
