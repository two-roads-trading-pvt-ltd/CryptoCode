import json
import pprint
import websocket
import load_param
import json
from websocket import create_connection
import ctypes
import struct_types_coinbase
from datetime import datetime
from datetime import date
import time
import logging
import sys
import argparse
#from websockets.extensions import permessage_deflate
import rel
import threading


class CoinBaseLogger(threading.Thread):
    global params_
    x_time = date.today()
    prev_date = int(x_time.strftime("%Y%m%d"))
    current_date = prev_date
    print("Starting Client For Date: ", prev_date)
    coinbasemktdata = struct_types_coinbase.CoinBaseMktStruct()
    product_seq = 1
    
    def __init__(self, product, channel ):
        self.product = [product]
        self.channels_ = channel
        file_name = params_.myvars["location"].strip() + "/" + product.strip() + "_" + str(self.prev_date)
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
        
        
    def decodeMessage(self, message):
        type_ = message.get('type')
        #debug_str = "Decode Message Type: " + type_
        #logging.debug(debug_str)
        #return
        date_time_str = message.get('time')
        date_format = datetime.strptime(date_time_str,  "%Y-%m-%dT%H:%M:%S.%fZ")
        # Get current time
        x_time = datetime.now()
        self.current_date = int(x_time.strftime("%Y%m%d"))
    #    print("Packet Received at =>" ,
    #      date_format.strftime('%Y-%m-%d %H:%M:%S.%f')," Current Time is: ", x_time.strftime("%Y-%m-%d %H:%M:%S.%f"))

        self.coinbasemktdata.timeval_.tv_sec = int(time.mktime(date_format.timetuple()))
        self.coinbasemktdata.timeval_.tv_usec = int(date_format.strftime("%f"))
        self.coinbasemktdata.local_time_.tv_sec = int(time.mktime(x_time.timetuple()))
        self.coinbasemktdata.local_time_.tv_usec = int(x_time.strftime("%f"))

    #    self.coinbasemktdata.timeval_.ToString()
        self.coinbasemktdata.product_id = message.get('product_id').encode('UTF-8')# if message.get('product_id') is not None else None
        self.coinbasemktdata.sequence = message.get('sequence')
        if type_ == 'received':
            #A valid order has been received and is now active.
            self.coinbasemktdata.msg_type = 1
            self.coinbasemktdata.data.coinbase_mkt_recieved_order.order_id = message.get('order_id').encode('UTF-8') #if message.get('order_id') is not None else None
            self.coinbasemktdata.data.coinbase_mkt_recieved_order.client_oid = message.get('client_oid').encode('UTF-8') #if message.get('client_oid') is not None else None
            self.coinbasemktdata.data.coinbase_mkt_recieved_order.size = float(message.get('size')) if message.get('size') is not None else 0
            self.coinbasemktdata.data.coinbase_mkt_recieved_order.price = float(message.get('price')) if message.get('price') is not None else 0
            #may have an optional funds field
            self.coinbasemktdata.data.coinbase_mkt_recieved_order.funds = float(message.get('funds')) if message.get('funds') is not None else 0
            if message.get('side').lower() == "buy":
                self.coinbasemktdata.data.coinbase_mkt_recieved_order.buysell = 0
            else:
                self.coinbasemktdata.data.coinbase_mkt_recieved_order.buysell = 1
            if message.get('order_type').lower() == "limit" :
                self.coinbasemktdata.data.coinbase_mkt_recieved_order.order_type = b'L' # Limit order
            else:
                self.coinbasemktdata.data.coinbase_mkt_recieved_order.order_type = b'M' # Market Order
        elif type_ == 'open':
            #The order is now open on the order book.
            self.coinbasemktdata.msg_type = 2
            self.coinbasemktdata.data.coinbase_mkt_open_order.order_id = message.get('order_id').encode('UTF-8') #if message.get('order_id') is not None else None
            self.coinbasemktdata.data.coinbase_mkt_open_order.price = float(message.get('price'))
            self.coinbasemktdata.data.coinbase_mkt_open_order.remaining_size = float(message.get('remaining_size'))
            if message.get('side').lower() == "buy":
                self.coinbasemktdata.data.coinbase_mkt_open_order.buysell = 0 #BUY
            else:
                self.coinbasemktdata.data.coinbase_mkt_open_order.buysell = 1 #SELL
        elif type_ == 'done':
            #There are no more messages for an order_id after a done message. 
            ''' Cancel Order Reason only for authencicated users 
                101:Time In Force
                102:Self Trade Prevention
                103:Admin
                104:Price Bound Order Protection
                105:Insufficient Funds
                106:Insufficient Liquidity
                107:Broker
            '''
            self.coinbasemktdata.msg_type = 3
            self.coinbasemktdata.data.coinbase_mkt_done_order.order_id = message.get('order_id').encode('UTF-8') #if message.get('order_id') is not None else None
            self.coinbasemktdata.data.coinbase_mkt_done_order.price = float(message.get('price')) if message.get('price') is not None else 0
            self.coinbasemktdata.data.coinbase_mkt_done_order.remaining_size = float(message.get('remaining_size')) if message.get('remaining_size') is not None else 0 # will be 0 for filled orders or for cancel how went unfilled
            if message.get('reason') == "Filled":
                self.coinbasemktdata.data.coinbase_mkt_done_order.reason = b'F' #Filled
            else:
                self.coinbasemktdata.data.coinbase_mkt_done_order.reason = b'C' #Canceled
                # that are authenticated and that originated with you the user return the reason in the cancel_reason field
                self.coinbasemktdata.data.coinbase_mkt_done_order.cancel_reason = int(message.get('cancel_reason')) if message.get('cancel_reason') is not None else 0
            if message.get('side').lower() == "buy":
                self.coinbasemktdata.data.coinbase_mkt_done_order.buysell = 0 #BUY
            else:
                self.coinbasemktdata.data.coinbase_mkt_done_order.buysell = 1 #SELL

        elif type_ == 'match':
            #A trade occurred between two orders.
            self.coinbasemktdata.msg_type = 4
            self.coinbasemktdata.data.coinbase_mkt_match_order.maker_order_id = message.get('maker_order_id').encode('UTF-8') #if message.get('maker_order_id') is not None else None
            self.coinbasemktdata.data.coinbase_mkt_match_order.taker_order_id = message.get('taker_order_id').encode('UTF-8') #if message.get('taker_order_id') is not None else None
            self.coinbasemktdata.data.coinbase_mkt_match_order.trade_id = int(message.get('trade_id'))
            self.coinbasemktdata.data.coinbase_mkt_match_order.size = float(message.get('size'))
            self.coinbasemktdata.data.coinbase_mkt_match_order.price = float(message.get('price'))
            #The side field indicates the maker order side.
            # If the side is sell this indicates the maker was a sell order and the match is considered an up-tick. A buy side match is a down-tick.
            if message.get('side').lower() == "buy":
                self.coinbasemktdata.data.coinbase_mkt_match_order.buysell = 0 #BUY
            else:
                self.coinbasemktdata.data.coinbase_mkt_match_order.buysell = 1 #SELL
            #If authenticated, the message would also have the extra fields: userid, taker profile profile id, taker_fee_rate
        elif type_ == 'change':
            #A change message can be the result of either a Self-trade Prevention (STP) or a Modify Order Request (beta):
            #If you are building a real-time order book, you can ignore change messages for received but not yet open orders.
            self.coinbasemktdata.msg_type = 5
            self.coinbasemktdata.data.coinbase_mkt_change_order.order_id = message.get('order_id').encode('UTF-8') #if message.get('order_id') is not None else None
            self.coinbasemktdata.data.coinbase_mkt_change_order.old_size  = float(message.get('old_size'))
            self.coinbasemktdata.data.coinbase_mkt_change_order.new_size  = float(message.get('new_size'))
            #STP messages have a new reason field and continue to use the price field (not new_price and old_price).
            self.coinbasemktdata.data.coinbase_mkt_change_order.old_price = float(message.get('old_price')) if message.get('old_price') is not None else float(message.get('price'))
            self.coinbasemktdata.data.coinbase_mkt_change_order.new_price = float(message.get('new_price')) if message.get('new_price') is not None else float(message.get('price'))
            if message.get('side').lower() == "buy":
                self.coinbasemktdata.data.coinbase_mkt_change_order.buysell = 0 #BUY
            else:
                self.coinbasemktdata.data.coinbase_mkt_change_order.buysell = 1 #SELL
            if message.get('reason').lower() == "STP":
                #A Self-trade Prevention adjusts the order size or available funds (and can only decrease).
                self.coinbasemktdata.data.coinbase_mkt_change_order.reason = b'S' # SELF Trade Prevention(STP)
            else:
                self.coinbasemktdata.data.coinbase_mkt_change_order.reason = b'M' # Modify
        elif type_ == 'activate':
            #An activate message is sent when a stop order is placed.
            self.coinbasemktdata.msg_type = 6
            self.coinbasemktdata.data.coinbase_mkt_active_order.profile_id = message.get('profile_id').encode('UTF-8') #if message.get('profile_id') is not None else None
            self.coinbasemktdata.data.coinbase_mkt_active_order.order_id = message.get('order_id').encode('UTF-8') #if message.get('order_id') is not None else None
            self.coinbasemktdata.data.coinbase_mkt_active_order.stop_price = float(message.get('stop_price'))
            self.coinbasemktdata.data.coinbase_mkt_active_order.size = float(message.get('size'))
            self.coinbasemktdata.data.coinbase_mkt_active_order.funds = float(message.get('funds'))
            self.coinbasemktdata.data.coinbase_mkt_active_order.user_id = int(message.get('user_id'))
            if message.get('side').lower() == "buy":
                self.coinbasemktdata.data.coinbase_mkt_active_order.buysell = 0 #BUY
            else:
                self.coinbasemktdata.data.coinbase_mkt_active_order.buysell = 1 #SELL
            if message.get('stop_type').lower() == "entry":
                self.coinbasemktdata.data.coinbase_mkt_active_order.stop_type = b"E" #ENTRY
            else:
                self.coinbasemktdata.data.coinbase_mkt_active_order.stop_type = b"I" #Invalid(No 2nd type yet)
            self.coinbasemktdata.data.coinbase_mkt_active_order.private_ = message.get('private')

    def on_open(self, ws):
        subscribe_ = {
        "type": "subscribe",
        "product_ids": self.product,
    #    "currencies": [ "BTC", "USD" ],
        "channels": self.channels_
        }
        print(subscribe_)
        #return
        ws.send(json.dumps(subscribe_))
        print(subscribe_)
        logging.info("Subscription Request Sent")
        now = datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        warning_str = "Server Up Time = ", current_time
        logging.warning(warning_str)

    def on_message(self, ws, data):
        message = json.loads(data)
        debug_str = "Message Recieved: " + str(message)
        logging.debug(debug_str)
        type_ = message.get('type')
        #debug_str = "Message Recieved of Type Update: " + type_
        #logging.debug(debug_str)

        if type_ == 'l2update':
            logging.debug(debug_str)
            logging.debug("Not Handled")
        elif  type_ == 'received' or type_ == 'open' or type_ == 'done' or type_ == 'match' or type_ == 'change' or type_ == 'activate':
            prod = message.get('product_id')
    #      print(prod)
            seq = message.get('sequence')
            debug_str = "Msg Sequence: " + str(seq)
            if  seq > self.product_seq:
                print("Drop for ", str(self.product)  + " of: ", self.product_seq, " from Seq: " , seq , " of Size: ", seq - self.product_seq)
            elif seq < self.product_seq:
                print ("Msg Sequence already recieved for " + str(self.product) + ": " , seq , " Expected: ", self.product_seq)
                return
            file_obj = self.product_file
            self.decodeMessage(message)
    #        print("Current Date: ", current_date, " Prev Date: ", prev_date)
            if self.current_date != self.prev_date:
                file_name = params_.myvars["location"].strip() + "/" + prod.strip() + "_" + str(self.prev_date)
                info_str = "Closing File: " + file_name
                logging.info(info_str)
                self.prev_date = self.current_date
                file_name = params_.myvars["location"].strip() + "/" + prod.strip() + "_" + str(self.prev_date)
                info_str = "Opening File:: " + file_name
                logging.info(info_str)
                #file_object = open(file_name, 'ab') TESTING PURPOSE
                file_obj = open(file_name, 'wb')
                self.product_file = file_obj

    #        array = bytearray(self.coinbasemktdata)
    #        print(len(array))
            file_obj.write(bytearray(self.coinbasemktdata))

            self.product_seq = seq + 1
    #        debug_str = "Next expected msg Seq: " + str(product_seq[prod])
    #        logging.debug(debug_str)
        elif type_ == 'ticker':
            logging.debug(debug_str)
            logging.debug("Not Handled")
            pass
        elif type_ == 'snapshot':
            logging.debug(debug_str)
            logging.debug("Not Handled")
            pass
        elif type_ == 'heartbeat':
            logging.debug(debug_str)
            logging.debug("Not Handled")
            pass
        elif type_ == 'subscriptions':
            logging.debug(debug_str)
            logging.debug("Not Handled")
            print(message)
            pass
        elif message.get('message') is not None:
            logging.debug(debug_str)
            logging.debug("Not Handled")
            print(message['message'])
        else:
            logging.debug(debug_str)
            logging.debug("Not Handled")
            debug_str = "Unknown type of Message:  " + type_
            logging.debug(debug_str)
    #        print(type_)
            pass

    def on_error(self,ws, error):
        error_str = 'Error:' + str(error) + " For " + str(self.product)
        logging.error(error_str)

    def on_close(self,ws, close_status_code, close_message):
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
        CoinBaseLogger(prod,channels_).start()
        pass

main()
