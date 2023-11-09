import json
import logging
import sys

import greengrasssdk

# Logging
logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Source: CS437_Lab4_Lambda -> Target: Client device Vehicle_1 Topic: vehicle_1/emission/processed

# Source: Vehicle_1	-> Target: CS437_Lab4_Lambda Topic: vehicle_1/process/trigger

# SDK Client
client = greengrasssdk.client("iot-data")
vehicle_data = {}

def lambda_handler(event, context):
    # body = event.get("body")
    # if body is None:
    #     print(str(type(event)), str(event))
    #     #logger.error("No body was found in Lambda event: {}".format(str(type(event))))
    #     return
    body = event #json.loads(body)
    vehicle_id = body.get("vehicle_id")
    vehicle_co2 = body.get("vehicle_CO2")
    should_return_max_co2 = body.get("should_return_max_co2")
    if vehicle_id is None or vehicle_co2 is None:
        print("No vehicle data was found in payload: {}".format(str(body)))
        return
    
    if not vehicle_id in vehicle_data:
        vehicle_data[vehicle_id] = vehicle_co2
    vehicle_data[vehicle_id] = max(vehicle_data[vehicle_id], vehicle_co2)

    if should_return_max_co2:
        client.publish(
            topic="vehicle_{}/emission/processed".format(int(vehicle_id)),
            payload=json.dumps(
                {"max_co2": vehicle_data[vehicle_id]}
            ),
        )
    return