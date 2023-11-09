#!/bin/sh
set -e
#python basicDiscovery.py -r ./certs/AmazonRootCA1.pem -c ./certs/LK0ru70tuWkY7ChufH6IVHYtA/cert.pem -k ./certs/LK0ru70tuWkY7ChufH6IVHYtA/private.key -e a23i9qqmyyct7i-ats.iot.us-east-1.amazonaws.com -n LK0ru70tuWkY7ChufH6IVHYtA -t hello/world/pubsub --mode publish --message 'Hello, World! Sent from HelloWorld_Publisher'

#python basicDiscovery.py -r ./certs/AmazonRootCA1.pem -c ./certs/0bl6zthTt9jXX9XfiMATbgtGx/cert.pem -k ./certs/0bl6zthTt9jXX9XfiMATbgtGx/private.key -e a23i9qqmyyct7i-ats.iot.us-east-1.amazonaws.com -n 0bl6zthTt9jXX9XfiMATbgtGx -t hello/world/pubsub --mode subscribe




# subscriber
python basicDiscovery.py --endpoint a23i9qqmyyct7i-ats.iot.us-east-1.amazonaws.com --rootCA GGCore/AmazonRootCA1.pem --cert ./certs/GG_Subscriber/c0d8987487c6afb5b799985d241ed123eaa057a53610cda00f7b28fbc2d3a836-certificate.pem.crt --key ./certs/GG_Subscriber/c0d8987487c6afb5b799985d241ed123eaa057a53610cda00f7b28fbc2d3a836-private.pem.key --thingName GG_Subscriber --topic 'hello/world/pubsub' --mode subscribe


# publisher
python basicDiscovery.py --endpoint a23i9qqmyyct7i-ats.iot.us-east-1.amazonaws.com --rootCA GGCore/AmazonRootCA1.pem --cert ./certs/GG_Publisher/42de9815bcbe38b35bab49c9c9a4d650ca7394d5804bce4a5469163d2981d6ed-certificate.pem.crt --key ./certs/GG_Publisher/42de9815bcbe38b35bab49c9c9a4d650ca7394d5804bce4a5469163d2981d6ed-private.pem.key --thingName GG_Publisher --topic 'hello/world/pubsub' --mode publish --message 'Hello, World! Sent from HelloWorld_Publisher'