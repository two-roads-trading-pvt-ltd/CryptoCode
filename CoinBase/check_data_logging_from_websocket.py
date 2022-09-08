import json
import pprint
import sys
import websocket
import load_param
import json
from websocket import create_connection

###websocket.enableTrace(True)

params_ = load_param.LoadParam()
for x in params_.myvars:
    print (x," = ", params_.myvars[x])
print ("Exchange EndPoint to Connect", params_.myvars["Endpoint"])
product = list(params_.myvars["product_ids"].strip().split(","))
#product_ticker_ = list(params_.myvars["ticker"].split(","))
#for x in range(len(product)):
#    print (product[x],)
channels_ = list(params_.myvars["channels"].strip().split(","))
#for x in range(len(channels_)):
#    print (channels_[x],)

def on_open(ws):
  subscribe_ = {
    "type": "subscribe",
    "product_ids": product,
#    "currencies": [ "BTC", "USD" ],
    "channels": channels_
  }
  ws.send(json.dumps(subscribe_))

def on_message(ws, data):
    message = json.loads(data)
    type_ = message.get('type')
#    print(type_)
    print(message)
    if type_ == 'l2update':
#        print(message)
        pass
    elif type_ == 'ticker':
        pass
    elif type_ == 'snapshot':
        pass
    elif type_ == 'heartbeat':
        pass
    elif type_ == 'subscriptions':
        print(message)
        pass
    elif message.get('message') is not None:
        print(message['message'])
    else:
#        print(type_)
         pass

def on_error(ws, error):
    print('Error:', error)

def on_close(ws, close_status_code, close_message):
    print('WebSocket Closed:', close_message, close_status_code)

#product_file = {
"""
for prod in product:
	file_name=
	print("Opening File:: ")
	file_object = open(, 'a')
"""
ws = websocket.WebSocketApp(params_.myvars["Endpoint"],
        on_message=on_message,
        on_close=on_close,
        on_error=on_error,
        on_open=on_open)

ws.run_forever()

