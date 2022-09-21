from ctypes import *
import sys
import struct

class timeval(Structure):
    _fields_ = [("tv_sec", c_long), ("tv_usec", c_long)]
    def ToString(self):
        print("Time: ", str(self.tv_sec) + "." + str(self.tv_usec))

class CoinBaseRecievedOrder(Structure):
    _fields_ = [('order_id', c_char * 64),
                ('client_oid', c_char * 64),
                ('size', c_double),
                ('price', c_double),
                ('funds', c_double),
                ('buysell', c_int),
                ('order_type', c_char)]
    def ToString(self):
        print("CoinBaseRecievedOrder ")
        print("Order Id: ", self.order_id)
        print("Client Order Id: ", self.client_oid)
        print("Size: ", self.size)
        print("Price: ", self.price)
        print("Funds: ", self.funds)
        print("BuySell: ", self.buysell)
        print("Order Type: ", self.order_type)


class CoinBaseOpenOrder(Structure):
    _fields_ = [('order_id', c_char * 64),
                ('price',c_double),
                ('remaining_size',c_double),
                ('buysell',c_int)]
    def ToString(self):
        print("CoinBaseOpenOrder ")
        print("Order Id: ", self.order_id)
        print("Price: ", self.price)
        print("Remaning Size: ", self.remaining_size)
        print("BuySell: ", self.buysell)


class CoinBaseDoneOrder(Structure):
    _fields_ = [('order_id',c_char * 64 ),
                ('price',c_double),
                ('remaining_size',c_double),
                ('cancel_reason',c_int),
                ('reason',c_char),
                ('buysell',c_int)]
    def ToString(self):
        print("CoinBaseDoneOrder ")
        print("Order Id: ", self.order_id)
        print("Price: ", self.price)
        print("Remaining Size: ", self.remaining_size)
        print("Cancel reason ", self.cancel_reason)
        print("Reason ", self.reason)
        print("BuySell", self.buysell)


class CoinBaseMatchOrder(Structure):
    _fields_ = [('maker_order_id',c_char * 64),
                ('taker_order_id',c_char * 64),
                ('trade_id',c_ulong),
                ('size',c_double),
                ('price',c_double),
                ('buysell',c_int)]
    def ToString(self):
        print("CoinBaseMatchOrder ")
        print("Order Id: ", self.maker_order_id)
        print("Order Id: ", self.taker_order_id)
        print("Trade Id: ", self.trade_id)
        print("Size: ", self.size)
        print("Price: ", self.price)
        print("BuySell: ", self.buysell)


class CoinBaseChangeOrder(Structure):
    _fields_ = [('order_id', c_char * 64 ),
                ('old_size',c_double),
                ('new_size',c_double),
                ('old_price',c_double),
                ('new_price',c_double),
                ('buysell',c_int),
		('reason',c_char)]
    def ToString(self):
        print("CoinBaseChangeOrder ")
        print("Order Id: ", self.order_id)
        print("Old Size: ", self.old_size )
        print("New Size: ", self.new_size )
        print("Old Price: ", self.old_price )
        print("New Price: ", self.new_price )
        print("BuySell: ", self.buysell )



class CoinBaseActiveOrder(Structure):
    _fields_ = [('profile_id', c_char * 64),
                ('order_id', c_char * 64),
                ('stop_price',c_double),
                ('size',c_double),
		('funds',c_double),
                ('user_id',c_ulong),
                ('buysell',c_int),
                ('stop_type',c_char),
                ('private_',c_bool)]
    def ToString(self):
        print("CoinBaseActiveOrder ")
        print("Profile Id: ", self.profile_id)
        print("Order Id: ", self.order_id)
        print("Stop Price: ", self.stop_price)
        print("Size ", self.size)
        print("User Id ", self.user_id)
        print("BuySell ", self.buysell)
        print("Stop Type ", self.stop_type)
        print("Private ", self.private_)

class OrderType(Union):
    _fields_ = [('coinbase_mkt_recieved_order', CoinBaseRecievedOrder),
                ('coinbase_mkt_open_order', CoinBaseOpenOrder),
                ('coinbase_mkt_done_order', CoinBaseDoneOrder),
                ('coinbase_mkt_match_order', CoinBaseMatchOrder),
                ('coinbase_mkt_change_order', CoinBaseChangeOrder),
                ('coinbase_mkt_active_order', CoinBaseActiveOrder)]

class CoinBaseMktStruct(Structure):
    _fields_ = [('product_id', c_char * 32),
                ('timeval_',timeval),
		('local_time_',timeval),
                ('msg_type',c_int),
                ('sequence',c_ulong),
                ('data',OrderType)]
    def ToString(self):
        print("Product Id: ", self.product_id)
        self.timeval_.ToString()
        print("Message Type: ", self.msg_type)
        print("Sequence: ", self.sequence)
        if (self.msg_type == 1):
            self.data.coinbase_mkt_recieved_order.ToString()
        elif(self.msg_type == 2):
            self.data.coinbase_mkt_open_order.ToString()
        elif(self.msg_type ==3):
            self.data.coinbase_mkt_done_order.ToString()
        elif(self.msg_type == 4):
            self.data.coinbase_mkt_match_order.ToString()
        elif(self.msg_type == 5):
            self.data.coinbase_mkt_change_order.ToString()
        else:
            self.data.coinbase_mkt_active_order.ToString()



'''
testing = CoinBaseMktStruct()
testing.msg_type = 1
testing.sequence = 10
#testing.data.coinbase_mkt_active_order.user_id = 34
testing.product_id = "ETH-USD".encode("UTF-8")
testing.data.coinbase_mkt_recieved_order.order_id = "ac928c66-ca53-498f-9c13-a110027a60e8".encode("UTF-8")
testing.data.coinbase_mkt_recieved_order.size = 20
testing.data.coinbase_mkt_recieved_order.price = 12
i = 4
print("INT SIZE: ",len(bytearray(i)))
t1 = CoinBaseMktStruct()
print("CoinBaseMktStruct Size: ", len(bytearray(t1)))
t2 = CoinBaseRecievedOrder()
print("CoinBaseRecievedOrder Size: ", len(bytearray(t2)))
t3 = CoinBaseOpenOrder()
print("CoinBaseOpenOrder Size: ", len(bytearray(t3)))
t4 = CoinBaseDoneOrder()
print("CoinBaseDoneOrder Size: ", len(bytearray(t4)))
t5 = CoinBaseMatchOrder()
print("CoinBaseMatchOrder Size: ", len(bytearray(t5)))
t6 = CoinBaseChangeOrder()
print("CoinBaseChangeOrder Size: ", len(bytearray(t6)))
t7 = CoinBaseActiveOrder()
print("CoinBaseActiveOrder Size: ", len(bytearray(t7)))

#print(struct.calcsize(CoinBaseMktStruct))
#print(sys.getsizeof(CoinBaseMktStruct)
testing.ToString()
#print(testing)
print()
testing.msg_type = 6
testing.sequence = 11
testing.data.coinbase_mkt_active_order.user_id = 34
testing.data.coinbase_mkt_active_order.profile_id = "222928c66-ca53-498f-9c13-a110027a60e8".encode("UTF-8")
testing.data.coinbase_mkt_active_order.order_id = "ac928c66-ca53-498f-9c13-a110027a60e8".encode("UTF-8")
testing.data.coinbase_mkt_active_order.stop_price = 200.7
testing.data.coinbase_mkt_active_order.size = 66
print("Checking Struct Size: ", sys.getsizeof(CoinBaseMktStruct))
print("Testing: " ,sys.getsizeof(testing))
testing.ToString()
print("PRint Size: ", testing.__sizeof__())
print("Checking Struct Size Done")
#exit(0)
file_path="/NAS1/data/CryptoData/coinbase/ETH-EUR"
print("Reading File: ", file_path)
'''
