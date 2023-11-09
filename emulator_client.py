# Import SDK packages
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json
import pandas as pd
import numpy as np
import os


#TODO 1: modify the following parameters
#Starting and end index, modify this
device_st = 0
device_end = 100

#Path to your certificates, modify this
formatter_ = "./certs/{}/{}"

def get_devices_meta(certs_dir: str, num_devices=1):
    for i, thing_name in enumerate(os.listdir(certs_dir)):
        if i != num_devices and os.path.isdir(os.path.join(certs_dir, thing_name)):
            yield (thing_name, "cert.pem", "private.key", "public.key")


class MQTTClient:
    def __init__(self, device_id, cert, key):
        # For certificate based connection
        self.device_id = str(device_id)
        self.state = 0
        self.client = AWSIoTMQTTClient(self.device_id)
        #TODO 2: modify your broker address
        self.client.configureEndpoint("a23i9qqmyyct7i-ats.iot.us-east-1.amazonaws.com", 8883)
        self.client.configureCredentials("./certs/AmazonRootCA1.pem", key, cert)
        self.client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        self.client.configureDrainingFrequency(2)  # Draining: 2 Hz
        self.client.configureConnectDisconnectTimeout(10)  # 10 sec
        self.client.configureMQTTOperationTimeout(5)  # 5 sec
        self.client.onMessage = self.customOnMessage
        
    def customOnMessage(self, message):
        #TODO3: fill in the function to show your received message
        print("client {} received payload {} from topic {}".format(self.device_id, message.payload, message.topic))

    # Suback callback
    def customSubackCallback(self, mid, data):
        print(f"Subscription Callback: {mid} -> {data}")

    # Puback callback
    def customPubackCallback(self, mid):
        print(f"Publisher Callback: {mid}")

    def publish(self, payload=None):
        if not payload:
            payload = f"Hello from: {self.device_id}"
        self.client.subscribeAsync("myTopic", 0, ackCallback=self.customSubackCallback) 
        self.client.publishAsync("myTopic", payload, 0, ackCallback=self.customPubackCallback)



print("Loading vehicle data...")
data_path = "./data/vehicle{}.csv"
data = []
for i in range(1):
    a = pd.read_csv(data_path.format(i))
    data.append(a)

print("Initializing MQTTClients...")
clients = []
for thing_name, cert_fname, priv_fname, _ in get_devices_meta("./certs/"):
    client = MQTTClient(thing_name, formatter_.format(thing_name, cert_fname), formatter_.format(thing_name, priv_fname))
    client.client.connect()
    clients.append(client)
 

while True:
    print("send now?")
    x = input()
    if x == "s":
        for i, c in enumerate(clients):
            c.publish()

    elif x == "d":
        for c in clients:
            c.client.disconnect()
        print("All devices disconnected")
        exit()
    else:
        print("wrong key pressed")

    time.sleep(3)





