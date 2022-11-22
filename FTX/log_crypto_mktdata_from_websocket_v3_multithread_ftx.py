import json
import pprint
import websocket
import load_param
import json
from websocket import create_connection
import ctypes
import struct_types_ftx
from datetime import datetime
from datetime import date
import time
import logging
import sys
import argparse
#from websockets.extensions import permessage_deflate
import rel
import threading
from decimal import Decimal


class FTXLogger(threading.Thread):
    global params_
    x_time = date.today()
    prev_date = int(x_time.strftime("%Y%m%d"))
    current_date = prev_date
    heartbeat_sec = 0
    print("Starting Client For Date: ", prev_date)
    ftxmktdata = struct_types_ftx.FTXMktStruct()

    def __init__(self, product, channel ):
        self.product = product
        self.channels_ = channel
        file_name = params_.myvars["location"].strip() + "/" + product.replace("/","-").strip() + "_" + str(self.prev_date)
        info_str = "Opening File:: " + file_name
        logging.info(info_str)
#    file_object = open(file_name, 'ab') TESTING PURPOSE
        file_object = open(file_name, 'ab')
        self.product_file = file_object

        self.connect()
        threading.Thread.__init__(self)

    def connect(self):
        print("WebSocket Connect Call ",self.product )
        self.ws = websocket.WebSocketApp(params_.myvars["Endpoint"],
            on_message=self.on_message,
            on_close=self.on_close,
            on_error=self.on_error,
            on_open=self.on_open)

    def run(self):
        print("Running Forever ",self.product)
        self.ws.run_forever(skip_utf8_validation = True)
        # dispatcher=rel) 
        # Set dispatcher to automatic reconnection
        #only Works in Int Main
  #      rel.signal(2, rel.abort)  # Keyboard Interrupt
  #      rel.dispatch()
    def reconnect(self):
        print("WebSocket Reconnect Call ", self.product)
        self.connect()
        self.ws.run_forever(skip_utf8_validation = True)


#    def dumpDataToFile(self):
    def checkNewDay(self):
        #file_obj = self.product_file
        if self.current_date != self.prev_date:
            file_name = params_.myvars["location"].strip() + "/" + self.product.replace("/","-").strip() + "_" + str(self.prev_date)
            info_str = "Closing File: " + file_name
            logging.info(info_str)
            self.product_file.flush()
            self.product_file.close()
            self.prev_date = self.current_date
            file_name = params_.myvars["location"].strip() + "/" + self.product.replace("/","-").strip() + "_" + str(self.prev_date)
            info_str = "Opening File:: " + file_name
            logging.info(info_str)
            file_obj = open(file_name, 'wb')
            self.product_file = file_obj

        #self.product_file.write(bytearray(self.ftxmktdata))

    def decodeTrade(self ,trade_message):
        # Get current time
        #self.x_time = datetime.now()
        #self.current_date = int(self.x_time.strftime("%Y%m%d"))

        trade_count = 0
        for trade_data in trade_message['data']:
            trade_count += 1
            date_time_str = str(trade_data['time'])
            date_format = datetime.strptime(date_time_str,  "%Y-%m-%dT%H:%M:%S.%f+00:00")
            self.ftxmktdata.product = trade_message.get('market').encode('UTF-8')# if message.get('market') is not None else None
            self.ftxmktdata.exch_time.tv_sec = int(time.mktime(date_format.timetuple()))
            self.ftxmktdata.exch_time.tv_usec = int(date_format.strftime("%f"))
            self.ftxmktdata.local_time.tv_sec = int(time.mktime(self.x_time.timetuple()))
            self.ftxmktdata.local_time.tv_usec = int(self.x_time.strftime("%f"))
            self.ftxmktdata.price = float(trade_data['price'])
            self.ftxmktdata.size = float(trade_data['size'])
            self.ftxmktdata.msg_type = 2
            if str(trade_data['side']) == "buy":
                self.ftxmktdata.buysell = b'B'
            else:
                self.ftxmktdata.buysell = b'S'
            if trade_count == len(trade_message['data']):
                self.ftxmktdata.intermediate = b'N'
            else:
                self.ftxmktdata.intermediate = b'Y'
            self.product_file.write(bytearray(self.ftxmktdata))
            #self.dumpDataToFile()

        send_heartbeat_diff = int(time.mktime(self.x_time.timetuple())) - self.heartbeat_sec
        if send_heartbeat_diff > 10:
            self.heartbeat_ping()
            self.heartbeat_sec = int(time.mktime(self.x_time.timetuple()))
            
    def decodeTicker(self ,ticker_message):
        # Get current time
        #self.x_time = datetime.now()
        #self.current_date = int(self.x_time.strftime("%Y%m%d"))

        date_time_str = str(ticker_message['data']['time'])
        date_format = date_time_str.split(".")
        self.ftxmktdata.product = ticker_message.get('market').encode('UTF-8')# if message.get('market') is not None else None
        self.ftxmktdata.exch_time.tv_sec = int(date_format[0])
        self.ftxmktdata.exch_time.tv_usec = int(date_format[1])
        self.ftxmktdata.local_time.tv_sec = int(time.mktime(self.x_time.timetuple()))
        self.ftxmktdata.local_time.tv_usec = int(self.x_time.strftime("%f"))
        self.ftxmktdata.price = float(ticker_message['data']['bid'])
        self.ftxmktdata.size = float(ticker_message['data']['bidSize'])
        self.ftxmktdata.msg_type = 1
        self.ftxmktdata.buysell = b'B'
        self.ftxmktdata.intermediate = b'Y'
        self.product_file.write(bytearray(self.ftxmktdata))
        #self.dumpDataToFile()
        self.ftxmktdata.price = float(ticker_message['data']['ask'])
        self.ftxmktdata.size = float(ticker_message['data']['askSize'])
        self.ftxmktdata.buysell = b'S'
        self.ftxmktdata.intermediate = b'N'
        self.product_file.write(bytearray(self.ftxmktdata))
        #self.dumpDataToFile()
        
        send_heartbeat_diff = int(time.mktime(self.x_time.timetuple())) - self.heartbeat_sec
        if send_heartbeat_diff > 15:
            self.heartbeat_ping()
            self.heartbeat_sec = int(time.mktime(self.x_time.timetuple()))

    def decodeOrderBook(self, orderbook_message):
        # Get current time
        #self.x_time = datetime.now()
        #self.current_date = int(self.x_time.strftime("%Y%m%d"))

        date_time_str = str(orderbook_message['data']['time'])
        date_format = date_time_str.split(".")
        self.ftxmktdata.product = orderbook_message.get('market').encode('UTF-8')# if message.get('market') is not None else None
        self.ftxmktdata.exch_time.tv_sec = int(date_format[0])
        self.ftxmktdata.exch_time.tv_usec = int(date_format[1])
        self.ftxmktdata.local_time.tv_sec = int(time.mktime(self.x_time.timetuple()))
        self.ftxmktdata.local_time.tv_usec = int(self.x_time.strftime("%f"))
        self.ftxmktdata.msg_type = 3

        ask_arrary_len = len(orderbook_message['data']['asks'])
        order_count = 0
        for bid_values in orderbook_message['data']['bids']:
            self.ftxmktdata.price = float(bid_values[0])
            self.ftxmktdata.size = float(bid_values[1])
            self.ftxmktdata.buysell = b'B'
            if ask_arrary_len == 0:
                order_count += 1
            if order_count == len(orderbook_message['data']['bids']):
                self.ftxmktdata.intermediate = b'N'
            else:
                self.ftxmktdata.intermediate = b'Y'
            self.product_file.write(bytearray(self.ftxmktdata))
            #self.dumpDataToFile()

        for ask_values in orderbook_message['data']['asks']:
            order_count += 1
            self.ftxmktdata.price = float(ask_values[0])
            self.ftxmktdata.size = float(ask_values[1])
            self.ftxmktdata.buysell = b'S'
            if order_count == len(orderbook_message['data']['asks']):
                self.ftxmktdata.intermediate = b'N'
            else:
                self.ftxmktdata.intermediate = b'Y'
            self.product_file.write(bytearray(self.ftxmktdata))
            #self.dumpDataToFile()

        send_heartbeat_diff = int(time.mktime(self.x_time.timetuple())) - self.heartbeat_sec
        if send_heartbeat_diff > 15:
            self.heartbeat_ping()
            self.heartbeat_sec = int(time.mktime(self.x_time.timetuple()))

    def heartbeat_ping(self):
        subscribe_ = {
          "op": "ping"
        }
        self.ws.send(json.dumps(subscribe_))

    def on_open(self, ws):
        for ch in self.channels_:
            subscribe_ = {
              "op": "subscribe",
              "channel": ch,
              "market": self.product
            }
            print(subscribe_)
            ws.send(json.dumps(subscribe_))
            logging.info("Subscription Request of " + self.product + " for channel " + ch + " sent")
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        warning_str = "Server Up Time = ", current_time
        logging.warning(warning_str)

    def on_message(self, ws, data):
        message = json.loads(data)
        #print (message)
        debug_str = "Message Recieved: " + str(message)
        logging.debug(debug_str)
        type_ = message.get('type')
        channel_ = message.get('channel')
    #    debug_str = "Message Recieved of type: " + type_ + " channel: " + channel_
    #    logging.debug(debug_str)
 
        self.x_time = datetime.now()
        self.current_date = int(self.x_time.strftime("%Y%m%d"))
        self.checkNewDay()

        if type_ == 'update':
            if channel_ == 'orderbook':
                self.decodeOrderBook(message)
            elif channel_ == 'ticker':
                self.decodeTicker(message)
            elif channel_ == 'trades':
                self.decodeTrade(message)

        elif type_ == 'partial':
            if channel_ == 'orderbook':
                self.decodeOrderBook(message)

        elif type_ == 'pong':
            logging.debug(debug_str)
            logging.debug("Not Handled")
            pass
            
        elif type_ == 'subscribed':
            logging.debug(debug_str)
            logging.debug("Not Handled")
            print(message,self.product)
            pass
        elif type_ == 'unsubscribed':
            logging.debug(debug_str)
            logging.debug("Not Handled")
            print(message,self.product)
            pass
        elif type_ == 'info':
            print ("info")
            logging.info(debug_str)
            print(message,self.product)
            if message.get('code') == 20001:
                self.reconnect()
            pass
        elif type_ == 'error':
            print ("error")
            logging.error(debug_str)
            print(message,self.product)
        
        else:
            logging.debug(debug_str)
            logging.debug("Not Handled")
            debug_str = "Unknown type of Message:  " + type_ + " " + str(self.product)
            logging.debug(debug_str)
    #        print(type_)
            pass


    def on_error(self, ws, error):
        error_str = 'Error:' + str(error) + " For " + str(self.product)
        logging.error(error_str)

    def on_close(self, ws, close_status_code, close_message):
        warning_str = "WebSocket Closed for " + str(self.product)  + ": " + str(close_message) + " " + str(close_status_code)
        logging.warning(warning_str)
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        warning_str = "Server down " + str(self.product) + " Time = " + str(current_time)
        logging.warning(warning_str)
        self.reconnect()
        return
        # Not Closing Files as it will try to reconnect itself
        for prod in product:
            product_file[prod].flush()
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

def main():
    for prod in product:
        print("Spawing Logger Thread for ",prod)
        FTXLogger(prod,channels_).start()
        pass

main()
