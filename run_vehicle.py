# /*
# * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# *
# * Licensed under the Apache License, Version 2.0 (the "License").
# * You may not use this file except in compliance with the License.
# * A copy of the License is located at
# *
# *  http://aws.amazon.com/apache2.0
# *
# * or in the "license" file accompanying this file. This file is distributed
# * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# * express or implied. See the License for the specific language governing
# * permissions and limitations under the License.
# */


import os
import sys
import time
import uuid
import json
import logging
import random
import pandas as pd
from AWSIoTPythonSDK.core.greengrass.discovery.providers import DiscoveryInfoProvider
from AWSIoTPythonSDK.core.protocol.connection.cores import ProgressiveBackOffCore
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from AWSIoTPythonSDK.exception.AWSIoTExceptions import DiscoveryInvalidRequestException

AllowedActions = ['both', 'publish', 'subscribe']

# General message notification callback
def customOnMessage(message):
    print('Received message on topic %s: %s\n' % (message.topic, message.payload))

MAX_DISCOVERY_RETRIES = 10
GROUP_CA_PATH = "./groupCA/"

# Source: CS437_Lab4_Lambda -> Target: Client device Vehicle_1 Topic: vehicle_1/emission/processed

# Source: Vehicle_1	-> Target: CS437_Lab4_Lambda Topic: vehicle_1/process/trigger

# Publishing Data to AWS IoT Analytics Topic -> vehicle/data/publish -> IAM Role Name: Lab4_Analytics

# Data Store ID: lab4_datastore

# Pipeline Name: lab4_pipeline

# Data Set Name: lab4_dataset

host = "a23i9qqmyyct7i-ats.iot.us-east-1.amazonaws.com"
rootCAPath = "vehicles/AmazonRootCA1.pem"
certificatePath = "vehicles/Vehicle_1/f52d60682db5e47bd3891f8caaef40c29d3967a424b25f734258310170104a3e-certificate.pem.crt"
privateKeyPath = "vehicles/Vehicle_1/f52d60682db5e47bd3891f8caaef40c29d3967a424b25f734258310170104a3e-private.pem.key"
clientId = "Vehicle_1"
thingName = "Vehicle_1"
subscribe_to_topic = lambda vid: "vehicle_{}/emission/processed".format(vid)
publish_to_topic = lambda vid: "vehicle_{}/process/trigger".format(vid)
vehicle_data_path = lambda vid: "data/vehicle{}.csv".format(vid)
vehicle_id = 1

if not os.path.isfile(rootCAPath):
    print("Root CA path does not exist {}".format(rootCAPath))
    exit(3)

if not os.path.isfile(certificatePath):
    print("No certificate found at {}".format(certificatePath))
    exit(3)

if not os.path.isfile(privateKeyPath):
    print("No private key found at {}".format(privateKeyPath))
    exit(3)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.ERROR)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Progressive back off core
backOffCore = ProgressiveBackOffCore()

# Discover GGCs
discoveryInfoProvider = DiscoveryInfoProvider()
discoveryInfoProvider.configureEndpoint(host)
discoveryInfoProvider.configureCredentials(rootCAPath, certificatePath, privateKeyPath)
discoveryInfoProvider.configureTimeout(10)  # 10 sec

retryCount = MAX_DISCOVERY_RETRIES #if not print_only else 1
discovered = False
groupCA = None
coreInfo = None
while retryCount != 0:
    try:
        discoveryInfo = discoveryInfoProvider.discover(thingName)
        caList = discoveryInfo.getAllCas()
        coreList = discoveryInfo.getAllCores()

        # We only pick the first ca and core info
        groupId, ca = caList[0]
        coreInfo = coreList[0]
        print("Discovered GGC: %s from Group: %s" % (coreInfo.coreThingArn, groupId))

        print("Now we persist the connectivity/identity information...")
        groupCA = GROUP_CA_PATH + groupId + "_CA_" + str(uuid.uuid4()) + ".crt"
        if not os.path.exists(GROUP_CA_PATH):
            os.makedirs(GROUP_CA_PATH)
        groupCAFile = open(groupCA, "w")
        groupCAFile.write(ca)
        groupCAFile.close()

        discovered = True
        print("Now proceed to the connecting flow...")
        break
    except DiscoveryInvalidRequestException as e:
        print("Invalid discovery request detected!")
        print("Type: %s" % str(type(e)))
        print("Error message: %s" % str(e))
        print("Stopping...")
        break
    except BaseException as e:
        print("Error in discovery!")
        print("Type: %s" % str(type(e)))
        print("Error message: %s" % str(e))
        retryCount -= 1
        print("\n%d/%d retries left\n" % (retryCount, MAX_DISCOVERY_RETRIES))
        print("Backing off...\n")
        backOffCore.backOff()

if not discovered:
    print("Discovery failed after %d retries. Exiting...\n" % (MAX_DISCOVERY_RETRIES))
    sys.exit(-1)

# Iterate through all connection options for the core and use the first successful one
myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
myAWSIoTMQTTClient.configureCredentials(groupCA, privateKeyPath, certificatePath)
myAWSIoTMQTTClient.onMessage = customOnMessage

connected = False
for connectivityInfo in coreInfo.connectivityInfoList:
    currentHost = connectivityInfo.host
    currentPort = connectivityInfo.port
    print("Trying to connect to core at %s:%d" % (currentHost, currentPort))
    myAWSIoTMQTTClient.configureEndpoint(currentHost, currentPort)
    try:
        myAWSIoTMQTTClient.connect()
        connected = True
        break
    except BaseException as e:
        print("Error in connect!")
        print("Type: %s" % str(type(e)))
        print("Error message: %s" % str(e))

if not connected:
    print("Cannot connect to core %s. Exiting..." % coreInfo.coreThingArn)
    sys.exit(-2)


myAWSIoTMQTTClient.subscribe(subscribe_to_topic(vehicle_id), 0, None)
time.sleep(2)

# vehicle_data = pd.read_csv(vehicle_data_path(vehicle_id))
# nrows, ncols = 20, 2#vehicle_data.shape
# for row_idx in range(nrows):
#     co2 = vehicle_data["vehicle_CO2"][row_idx]
#     # vehicle_id = body.get("vehicle_id")
#     # vehicle_co2 = body.get("vehicle_co2")
#     # should_return_max_co2 = body.get("should_return_max_co2")
#     #should_return = row_idx == nrows - 1
#     #should_return = row_idx % 2 == 0
#     #message = {"vehicle_id": vehicle_id, "vehicle_CO2": co2, "should_return_max_co2" : should_return}
#     message = {"co2":  random.randint(0, 10_000)}
#     messageJson = json.dumps(message)
#     myAWSIoTMQTTClient.publish(publish_to_topic(vehicle_id), messageJson, 0)
#     print('Published topic %s: %s\n' % (publish_to_topic(vehicle_id), messageJson))
#     time.sleep(2)

# while True:
#     time.sleep(1)


# Source: device Vehicle_1 Target: Service IoT Cloud Topic: vehicle/data/publish

# For IoT Analytics Data
for row_idx in range(100):
    message = {"co2":  random.randint(0, 10_000)}
    messageJson = json.dumps(message)
    myAWSIoTMQTTClient.publish("vehicle/data/publish", messageJson, 0)
    print('Published topic %s: %s\n' % ("vehicle/data/publish", messageJson))
    time.sleep(1)


    