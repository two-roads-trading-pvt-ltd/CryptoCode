import os
from os.path import isdir

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)

class LoadParam:
    myvars = {}
    def __init__(self):
        print ("opening File: ../Config/ftx_api_server")
        with open(dname + "/../Config/ftx_api_server") as myfile:
            for line in myfile:
                name, var = line.partition("=")[::2]
                self.myvars[name.strip()] = var
