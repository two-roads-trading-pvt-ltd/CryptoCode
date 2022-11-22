from ctypes import *
import sys
import struct

class timeval(Structure):
    _fields_ = [("tv_sec", c_long), ("tv_usec", c_long)]
    def ToString(self):
        print("Time: ", str(self.tv_sec) + "." + str(self.tv_usec))

class FTXMktStruct(Structure):
    _fields_ = [('product', c_char * 32),
                ('exch_time',timeval),
		('local_time',timeval),
                ('price',c_double),
                ('size',c_double),
                ('msg_type',c_int),
                ('buysell',c_char),
                ('intermediate',c_char)]
    def ToString(self):
        print("Product: ", self.product)
        print("Exch Time: ", str(self.exch_time.tv_sec) + "." + str(self.exch_time.tv_usec))
        print("Local Time: ", str(self.local_time.tv_sec) + "." + str(self.local_time.tv_usec))
        print("Price: ", self.price)
        print("Size: ", self.size)
        print("Message Type: ", self.msg_type)
        print("BuySell: ", self.buysell)
        print("Intermediate: ", self.intermediate)

