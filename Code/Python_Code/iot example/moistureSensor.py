
from adafruit_seesaw.seesaw import Seesaw
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from board import SCL, SDA
from datetime import date, datetime

import logging
import time
import json
import argparse
import busio

# Shadow JSON schema:
#
# {
#   "state": {
#       "desired":{
#           "moisture":<INT VALUE>,
#           "temp":<INT VALUE>            
#       }
#   }
# }

# Function called when a shadow is updated
def customShadowCallback_Update(payload, responseStatus, token):

    # Display status and data from update request
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")

    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("moisture: " + str(payloadDict["state"]["reported"]["moisture"]))
        print("temperature: " + str(payloadDict["state"]["reported"]["temp"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")

# Function called when a shadow is deleted
def customShadowCallback_Delete(payload, responseStatus, token):

     # Display status and data from delete request
    if responseStatus == "timeout":
        print("Delete request " + token + " time out!")

    if responseStatus == "accepted":
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Delete request with token: " + token + " accepted!")
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")

    if responseStatus == "rejected":
        print("Delete request " + token + " rejected!")


# Read in command-line parameters
def parseArgs():

    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--endpoint", action="store", required=True, dest="host", help="Your AWS IoT custom endpoint")
    parser.add_argument("-r", "--rootCA", action="store", required=True, dest="rootCAPath", help="Root CA file path")
    parser.add_argument("-c", "--cert", action="store", dest="certificatePath", help="Certificate file path")
    parser.add_argument("-k", "--key", action="store", dest="privateKeyPath", help="Private key file path")
    parser.add_argument("-p", "--port", action="store", dest="port", type=int, help="Port number override")
    parser.add_argument("-n", "--thingName", action="store", dest="thingName", default="Bot", help="Targeted thing name")
    parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="basicShadowUpdater", help="Targeted client id")

    args = parser.parse_args()
    return args


# Configure logging
# AWSIoTMQTTShadowClient writes data to the log
def configureLogging():

    logger = logging.getLogger("AWSIoTPythonSDK.core")
    logger.setLevel(logging.DEBUG)
    streamHandler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)


# Parse command line arguments
args = parseArgs()

if not args.certificatePath or not args.privateKeyPath:
    parser.error("Missing credentials for authentication.")
    exit(2)

# If no --port argument is passed, default to 8883
if not args.port: 
    args.port = 8883


myMQTTClient = AWSIoTMQTTClient(args.clientId)
myMQTTClient.configureEndpoint(args.host, args.port)
myMQTTClient.configureCredentials(args.rootCAPath, args.privateKeyPath, args.certificatePath)
myMQTTClient.configureOfflinePublishQueueing(-1) # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2) # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10) # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5) # 5 sec


now = datetime.utcnow()
now_str = now.strftime('%Y-%m-%dT%H:%M:%SZ')
payload = '{ "timestamp": "' + now_str + '","message": ' + "hello testing IOT" + ' }'
myMQTTClient.publish("thing01/data", payload, 0)
time.sleep(10)




# # Init AWSIoTMQTTShadowClient
# myAWSIoTMQTTClient = None
# myAWSIoTMQTTClient = AWSIoTMQTTClient(args.clientId)
# myAWSIoTMQTTClient.configureEndpoint(args.host, args.port)
# print("args.rootCAPath " + args.rootCAPath)
# print("args.privateKeyPath " + args.privateKeyPath)
# print("args.certificatePath " + args.certificatePath)





# myAWSIoTMQTTClient.configureCredentials(args.rootCAPath, args.privateKeyPath, args.certificatePath)

# # AWSIoTMQTTShadowClient connection configuration
# myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
# myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10) # 10 sec
# myAWSIoTMQTTClient.configureMQTTOperationTimeout(5) # 5 sec

# # # Initialize Raspberry Pi's I2C interface
# # i2c_bus = busio.I2C(SCL, SDA)

# # # Intialize SeeSaw, Adafruit's Circuit Python library
# # ss = Seesaw(i2c_bus, addr=0x36)

# # Connect to AWS IoT
# myAWSIoTMQTTClient.connect()

# # Publish to the same topic in a loop forever
# loopCount = 0

# while True:
#     message = {}
#     message['message'] = "demo-topic-sample-message"
#     message['sequence'] = loopCount
#     messageJson = json.dumps(message)
#     myAWSIoTMQTTClient.publish(topic, messageJson, 1)
#     print('Published topic %s: %s\n' % (topic, messageJson))
#     loopCount += 1
#     time.sleep(10)

# myAWSIoTMQTTClient.disconnect()

# # Create a device shadow handler, use this to update and delete shadow document
# deviceShadowHandler = myAWSIoTMQTTClient.createShadowHandlerWithName(args.thingName, True)

# # Delete current shadow JSON doc
# deviceShadowHandler.shadowDelete(customShadowCallback_Delete, 5)

# # Read data from moisture sensor and update shadow
# while True:

#     # read moisture level through capacitive touch pad
#     moistureLevel = ss.moisture_read()

#     # read temperature from the temperature sensor
#     temp = ss.get_temp()

#     # Display moisture and temp readings
#     print("Moisture Level: {}".format(moistureLevel))
#     print("Temperature: {}".format(temp))
    
#     # Create message payload
#     payload = {"state":{"reported":{"moisture":str(moistureLevel),"temp":str(temp)}}}

#     # Update shadow
#     deviceShadowHandler.shadowUpdate(json.dumps(payload), customShadowCallback_Update, 5)
#     time.sleep(1)