import json
import pprint
import sys
import websocket
import load_param
from websocket import create_connection

websocket.enableTrace(True)

params_ = load_param.LoadParam()

#for x in params_.myvars:
#    print (x, params_.myvars[x])
print ("Exchange EndPoint to Connect", params_.myvars["Endpoint"])
#print(type(params_.myvars["Endpoint"]))
try:
	ws = create_connection(params_.myvars["Endpoint"])
except Exception as e:
	print ("Couldnt connect with the socket-server: terminating program" )
	sys.exit(1)
#print(ws.recv())
#print("Sending 'Hello, World'...")
#ws.send("Hello, World")
#print("Sent")
#print("Receiving...")
#result =  ws.recv()
#print("Received '%s'" % result)
#ws.close()
