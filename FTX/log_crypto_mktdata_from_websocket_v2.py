import json
import pprint
import websocket
import load_param
import json
from websocket import create_connection
import ctypes
from datetime import datetime
from datetime import date
import time
import logging
import sys
import argparse
#from websockets.extensions import permessage_deflate
import rel
from decimal import Decimal

x_time = date.today()
prev_date = int(x_time.strftime("%Y%m%d"))
current_date = prev_date
print("Starting Client For Date: ", prev_date)
bid_price_size = {}
ask_price_size = {}


def dump_data_to_file(data_string):
    global current_date, prev_date
    x_time = datetime.now()
    current_date = int(x_time.strftime("%Y%m%d"))
    file_obj = product_file[prod]
#   print("Current Date: ", current_date, " Prev Date: ", prev_date)
    if current_date != prev_date:
        file_name = params_.myvars["location"].strip() + "/" + prod.strip() + "_" + str(prev_date)
        info_str = "Closing File: " + file_name
        logging.info(info_str)
        prev_date = current_date
        file_name = params_.myvars["location"].strip() + "/" + prod.strip() + "_" + str(prev_date)
        info_str = "Opening File:: " + file_name
        logging.info(info_str)
        #file_object = open(file_name, 'ab') TESTING PURPOSE
        file_obj = open(file_name, 'w')
        product_file[prod] = file_obj

#   array = bytearray(coinbasemktdata)
#   print(len(array))
    file_obj.write(data_string)

def decodeOrderBook(orderbook_message):
    for values in orderbook_message['data']['bids']:
        bid_price_size[values[0]] = values[1]
    for values in orderbook_message['data']['asks']:
        ask_price_size[values[0]] = values[1]

    channel_ = orderbook_message.get('channel')
    dump_string = str(channel_) + ",ftx," + str(orderbook_message['market']) + "," + str(orderbook_message['data']['time'])
    for (askp,asks), (bidp,bids) in zip(ask_price_size.items(), bid_price_size.items()):
       dump_string = dump_string + "," + str(askp) + "," + str(asks) + "," + str(bidp) + "," + str(bids)
    dump_data_to_file(dump_string + "\n")

def on_open(ws):
    for prod in product:
      for ch in channels_:
        subscribe_ = {
          "op": "subscribe",
          "channel": ch,
          "market": prod
        }
        ws.send(json.dumps(subscribe_))
        logging.info("Subscription Request of " + prod + " for channel " + ch + " sent")

def on_message(ws, data):
    message = json.loads(data)
    debug_str = "Message Recieved: " + str(message)
    logging.debug(debug_str)
    type_ = message.get('type')
    channel_ = message.get('channel')
    debug_str = "Message Recieved of type: " + type_ + " channel: " + channel_
#    logging.debug(debug_str)

    if type_ == 'update':
        if channel_ == 'orderbook':
            decodeOrderBook(message)
        elif channel_ == 'ticker':
            dump_string = str(channel_) + ",ftx," + str(message['market']) + "," + str(message['data']['time'])
            dump_string = dump_string + "," + str(message['data']['askSize']) + "," + str(message['data']['ask']) + "," + str(message['data']['bid']) + "," + str(message['data']['bidSize'])
            dump_data_to_file(dump_string + "\n")
        elif channel_ == 'trades':
            for trade_data in message['data']:
              dump_string = str(channel_) + ",ftx," + str(message['market']) + "," + str(trade_data['time'])
              dump_string = dump_string + "," + str(trade_data['id']) + "," + str(trade_data['side']) + "," + str(trade_data['price']) + "," + str(trade_data['size'])
              dump_data_to_file(dump_string + "\n")

    elif type_ == 'partial':
        if channel_ == 'orderbook':
            decodeOrderBook(message)
        logging.info(debug_str)
        pass
    elif type_ == 'subscribed':
        print ("subscirbed")
        logging.info(debug_str)
        print(message)
        pass
    elif type_ == 'unsubscribed':
        print ("unsubscirbed")
        logging.info(debug_str)
        print(message)
        pass
    elif type_ == 'info':
        print ("info")
        logging.info(debug_str)
        print(message)
        pass
    elif type_ == 'error':
        error_str = 'Error:' + str(error)
        logging.error(error_str)
        
    else:
        logging.debug(debug_str)
        logging.debug("Not Handled")
        debug_str = "Unknown type of Message:  " + type_
        logging.debug(debug_str)
#        print(type_)
        pass


def on_error(ws, error):
    error_str = 'Error:' + str(error)
    logging.error(error_str)

def on_close(ws, close_status_code, close_message):
    warning_str = "WebSocket Closed: " + close_message + " " + close_status_code
    logging.warning(warning_str)
    now = datetime.now()
    current_time = now.strftime("%Y-%m-%d %H:%M:%S")
    warning_str = "Server down Time = ", current_time
    logging.warning(warning_str)
    return
    # Not Closing Files as it will try to reconnect itself
    for prod in product:
        product_file[prod].close()
        logging.warning(prod)
    logging.warning("All Open File Closed")


parser = argparse.ArgumentParser()
parser.add_argument("--debug")
parser.add_argument("--trace")
parser.add_argument("--info")

args = parser.parse_args()
enable_debug = bool(args.debug) if args.debug else False
enable_info = bool(args.info) if args.info else False
enable_trace = bool(args.trace) if args.trace else False
## For Debugging Purpose
if enable_debug: # enable both info and debug
    logging.basicConfig(level=logging.DEBUG)
    logging.debug('---------------------------Debugging Messages Enabled-------------------------')
    logging.info('---------------------------Info Messages Enabled-------------------------')
if enable_info:  # enable only info
    logging.basicConfig(level=logging.INFO)
    logging.info('---------------------------Info Messages Enabled-------------------------')
## Tracing Packet from Websocket
if enable_trace:
    websocket.enableTrace(True)
    websocket._logging._logger.level = -99
    logging.debug('---------------------------Tracing WebSocket Enabled--------------------------')


params_ = load_param.LoadParam()
for x in params_.myvars:
    info_str = x +" = " + params_.myvars[x]
    logging.info(info_str)
info_str = "Exchange EndPoint to Connect " + params_.myvars["Endpoint"]
logging.info(info_str)
product = list(params_.myvars["product_ids"].strip().split(","))
#product_ticker_ = list(params_.myvars["ticker"].split(","))
logging.debug("Product Data Logging...")
for x in range(len(product)):
    logging.debug(product[x])
logging.debug("...End..")

channels_ = list(params_.myvars["channels"].strip().split(","))
logging.debug("Channel Data Logging...")
for x in range(len(channels_)):
    logging.debug(channels_[x])
logging.debug("...End..")

product_file = {}
for prod in product:
    file_name = params_.myvars["location"].strip() + "/" + prod.strip() + "_" + str(prev_date)
    info_str = "Opening File:: " + file_name
    logging.info(info_str)
#    file_object = open(file_name, 'ab') TESTING PURPOSE
    file_object = open(file_name, 'w')
    product_file[prod] = file_object

ws = websocket.WebSocketApp(params_.myvars["Endpoint"],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)

ws.run_forever(dispatcher=rel)
# Set dispatcher to automatic reconnection
rel.signal(2, rel.abort)  # Keyboard Interrupt
rel.dispatch()
