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
import os
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

def decodeMarketDetails(orderbook_message):
    for security in orderbook_message['data']['data']:
        if orderbook_message['data']['data'][security]['type'] == "spot":
            spot_string = str(orderbook_message['data']['data'][security]['name']) + "," + str(orderbook_message['data']['data'][security]['enabled']) + "," + str(orderbook_message['data']['data'][security]['priceIncrement']) + "," + str(orderbook_message['data']['data'][security]['sizeIncrement']) + "," + str(orderbook_message['data']['data'][security]['type']) + "," + str(orderbook_message['data']['data'][security]['baseCurrency']) + "," + str(orderbook_message['data']['data'][security]['quoteCurrency']) + "," + str(orderbook_message['data']['data'][security]['underlying']) + "," + str(orderbook_message['data']['data'][security]['restricted']) + "," + str(orderbook_message['data']['data'][security]['highLeverageFeeExempt']) + "," + str(orderbook_message['data']['data'][security]['largeOrderThreshold']) + "\n"
            product_file["spot"].write(spot_string)
        elif orderbook_message['data']['data'][security]['type'] == "future":
            fut_string = str(orderbook_message['data']['data'][security]['future']['name']) + "," + str(orderbook_message['data']['data'][security]['future']['underlying']) + "," + str(orderbook_message['data']['data'][security]['future']['description']) + "," + str(orderbook_message['data']['data'][security]['future']['type']) + "," + str(orderbook_message['data']['data'][security]['future']['expiry']) + "," + str(orderbook_message['data']['data'][security]['future']['perpetual']) + "," + str(orderbook_message['data']['data'][security]['future']['expired']) + "," + str(orderbook_message['data']['data'][security]['future']['enabled']) + "," + str(orderbook_message['data']['data'][security]['future']['postOnly']) + "," + str(orderbook_message['data']['data'][security]['future']['imfFactor']) + "," + str(orderbook_message['data']['data'][security]['future']['underlyingDescription']) + "," + str(orderbook_message['data']['data'][security]['future']['expiryDescription']) + "," + str(orderbook_message['data']['data'][security]['future']['moveStart']) + "," + str(orderbook_message['data']['data'][security]['future']['positionLimitWeight']) + "," + str(orderbook_message['data']['data'][security]['future']['group']) + "\n"
            product_file["fut"].write(fut_string)

def on_open(ws):
    subscribe_ = {
     "op": "subscribe",
     "channel": "markets",
    }
    ws.send(json.dumps(subscribe_))
    logging.info("Subscription Request for channel markets sent")

def on_message(ws, data):
    message = json.loads(data)
    debug_str = "Message Recieved: " + str(message)
    logging.debug(debug_str)
    type_ = message.get('type')
    channel_ = message.get('channel')
    debug_str = "Message Recieved of type: " + type_ + " channel: " + channel_
#    logging.debug(debug_str)

    if type_ == 'partial':
        if channel_ == 'markets':
            decodeMarketDetails(message)
        logging.info(debug_str)
        exit()
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
parser.add_argument("--outputdir")

args = parser.parse_args()
enable_debug = bool(args.debug) if args.debug else False
enable_info = bool(args.info) if args.info else False
enable_trace = bool(args.trace) if args.trace else False
output_file_dir = str(args.outputdir) if args.outputdir else "/tmp"
print ("Output file Directory: " + str(output_file_dir))

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
logging.debug("...End..")

logging.info("Channel : markets" )
logging.debug("...End..")

file_name_spot = str(output_file_dir) + "/" + "ftx_crypto_spot_products_" + str(prev_date)
file_name_fut = str(output_file_dir) + "/" + "ftx_crypto_fut_products_" + str(prev_date)
info_str = "Opening File:: 1. " + file_name_spot + "\nOpening File:: 2. " + file_name_fut
logging.info(info_str)
#file_object = open(file_name, 'ab') TESTING PURPOSE
file_exist_spot = os.path.exists(str(file_name_spot))
file_exist_fut = os.path.exists(str(file_name_fut))
if file_exist_spot:
    file_object_spot = open(file_name_spot, 'a')
else:
    spot_data_fields = "name,enabled,priceIncrement,sizeIncrement,type,baseCurrency,quoteCurrency,underlying,restricted,future,highLeverageFeeExempt,largeOrderThreshold\n"
    file_object_spot = open(file_name_spot, 'w')
    file_object_spot.write(spot_data_fields)
    
if file_exist_fut:
    file_object_fut = open(file_name_fut, 'a')
else:
    fut_data_fields = "name,underlying,description,type,expiry,perpetual,expired,enabled,postOnly,imfFactor,underlyingDescription,expiryDescription,moveStart,positionLimitWeight,group\n"
    file_object_fut = open(file_name_fut, 'w')
    file_object_fut.write(fut_data_fields)

product_file = {}
product_file["spot"] = file_object_spot
product_file["fut"] = file_object_fut

ws = websocket.WebSocketApp(params_.myvars["Endpoint"],
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close)

ws.run_forever(dispatcher=rel)
# Set dispatcher to automatic reconnection
rel.signal(2, rel.abort)  # Keyboard Interrupt
rel.dispatch()
