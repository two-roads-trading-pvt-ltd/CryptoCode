import json
import pprint
import sys
import websocket
import load_param
import json
from datetime import datetime
from websocket import create_connection

#websocket.enableTrace(True)
websocket._logging._logger.level = -99

params_ = load_param.LoadParam()
for x in params_.myvars:
    print (x," = ", params_.myvars[x])
print ("Exchange EndPoint to Connect", params_.myvars["Endpoint"])
product = list(params_.myvars["product_ids"].strip().split(","))
product = ["ETC-USD"]
#product_ticker_ = list(params_.myvars["ticker"].split(","))
#for x in range(len(product)):
#    print (product[x],)
channels_ = list(params_.myvars["channels"].strip().split(","))
channels_ = ["level2"]
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
#    print(message)
    if type_ == 'l2update':
#        print(message)
        pass
    elif type_ == 'open' or type_ == 'received' or type_ == 'done' or type_ == 'match':
        prod = message.get('product_id')
#        print(prod)
        seq = message.get('sequence')
#        print("SEQUence: ", seq)
        if  seq > product_seq[prod]:
            print("Drop on seq: ", product_seq[prod], seq , " of size: ", seq - product_seq[prod])
        elif seq < product_seq[prod]:
            print ("Sequence already recieved: " , seq , " Expected: ", product.seq[prod])
            return
#        file_obj = product_file[prod]
#        file_obj.write(str(message))
        product_seq[prod] = seq + 1
#        print("NEXT", product_seq[prod])
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
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    print("Server down Time =", current_time)
    for prod in product:
        product_file[prod].close()

product_file = { }
product_seq = { }
for prod in product:
    file_name = params_.myvars["location"].strip() + "/" + prod.strip()
    print("Opening File:: ", file_name)
    file_object = open(file_name, 'a')
    product_file[prod] = file_object
    product_seq[prod] = 1

ws = websocket.WebSocketApp(params_.myvars["Endpoint"],
        on_message=on_message,
        on_close=on_close,
        on_error=on_error,
        on_open=on_open)

now = datetime.now()
current_time = now.strftime("%Y-%m-%d %H:%M:%S")
print("Server Uptime Time =", current_time)
ws.run_forever()
