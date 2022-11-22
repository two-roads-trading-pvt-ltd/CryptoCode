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


def decodeOrderBook(orderbook_message):
    for bid_values in orderbook_message['data']['bids']:
        if bid_values[1] == 0.0:
            del bid_price_size[bid_values[0]]
        else:
            bid_price_size[bid_values[0]] = bid_values[1]
    for ask_values in orderbook_message['data']['asks']:
        if ask_values[1] == 0.0:
            del ask_price_size[ask_values[0]]
        else:
            ask_price_size[ask_values[0]] = ask_values[1]

    channel_ = orderbook_message.get('channel')
    dump_string = str(channel_) + ",ftx," + str(orderbook_message['market']) + "," + str(orderbook_message['data']['time'])
    sorted_ask = dict(sorted(ask_price_size.items(), reverse=False))
    sorted_bid = dict(sorted(bid_price_size.items(), reverse=True))
    count = 0
#    for (askp,asks), (bidp,bids) in sorted(zip(ask_price_size.items(), bid_price_size.items())):
    for (askp,asks), (bidp,bids) in zip(sorted_ask.items(), sorted_bid.items()):
       count += 1
       if count > 25:
           break
       dump_string = dump_string + "," + str(askp) + "," + str(asks) + "," + str(bidp) + "," + str(bids)
    output_file_obj.write(dump_string + "\n")

def readDecodeMessage():
    for data in input_file_obj: 
        message = json.loads(data)
        type_ = message.get('type')
        channel_ = message.get('channel')
        if type_ == 'update':
            if channel_ == 'orderbook':
                decodeOrderBook(message)
            elif channel_ == 'ticker':
                dump_string = str(channel_) + ",ftx," + str(message['market']) + "," + str(message['data']['time'])
                dump_string = dump_string + "," + str(message['data']['askSize']) + "," + str(message['data']['ask']) + "," + str(message['data']['bid']) + "," + str(message['data']['bidSize'])
                output_file_obj.write(dump_string + "\n")
            elif channel_ == 'trades':
                for trade_data in message['data']:
                    dump_string = str(channel_) + ",ftx," + str(message['market']) + "," + str(trade_data['time'])
                    dump_string = dump_string + "," + str(trade_data['id']) + "," + str(trade_data['side']) + "," + str(trade_data['price']) + "," + str(trade_data['size'])
                    output_file_obj.write(dump_string + "\n")

        elif type_ == 'partial':
            if channel_ == 'orderbook':
                decodeOrderBook(message)


parser = argparse.ArgumentParser()
parser.add_argument("--outputfile")
parser.add_argument("--inputfile")

args = parser.parse_args()
output_file = str(args.outputfile) if args.outputfile else "/tmp/temp_crypto_data"
input_file = str(args.inputfile) if args.inputfile else exit()
print ("OutputFile: " + str(output_file) + " InputFile: " + str(input_file))

input_file_obj = open(str(input_file), 'r')
output_file_obj = open(str(output_file), 'w')
readDecodeMessage()
input_file_obj.close()
output_file_obj.close()


