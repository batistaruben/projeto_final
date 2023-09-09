import paho.mqtt.publish as publish
import random
import time

""" This code Simulates a specific sensor """
class SensorSimulator:
    def __init__(self, broker_address, topic, min_val, max_val, interval):
        self.broker_address = broker_address
        self.topic = topic
        self.min_val = min_val
        self.max_val = max_val
        self.interval = interval

    def simulate(self):
        while True:
            value = round(random.uniform(self.min_val, self.max_val),2)
            publish.single(self.topic, str(value), hostname=self.broker_address)
            time.sleep(self.interval)

