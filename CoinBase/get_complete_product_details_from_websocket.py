import json
import pprint
import sys
import websocket
import load_param
import json
from websocket import create_connection

#websocket.enableTrace(True)

params_ = load_param.LoadParam()

for x in params_.myvars:
    print (x," = ", params_.myvars[x])
print ("Exchange EndPoint to Connect", params_.myvars["Endpoint"])
#print(type(params_.myvars["Endpoint"]))
try:
    ws = create_connection(params_.myvars["Endpoint"])
except Exception as e:
    print ("Couldnt connect with the socket-server: terminating program" )
    sys.exit(1)

subscribe_ = {
    "type": "subscribe",
    "channels": [{ "name": "status"}]
}



subscribe_json_ = json.dumps(subscribe_)
#z = json.loads(y)
ws.send(subscribe_json_)
#exit(0)
# Printing all the result
while True:
    try:
        result = ws.recv()
        pi = json.loads(result)
#        for product in result:
#            print ("ID: ", type(product))
#            print(product)
#            exit(0)
        print(result)
    except Exception as e:
        print(e)
