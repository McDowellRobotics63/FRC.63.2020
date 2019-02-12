#!/usr/bin/env python3
#
# This is a NetworkTables client.  It is to be used when developing
# the raspberry pi vision code.  The raspberry pi must be setup to 
# be a network tables server in the frcvision.local configuration page.
# You need to tell it the IP address of the NetworkTables server (the
# raspberry pi).
#

import sys
import time
from networktables import NetworkTables

# To see messages from networktables, you must setup logging
import logging

logging.basicConfig(level=logging.DEBUG)

NetworkTables.initialize(server="10.0.63.55")

def valueChanged(table, key, value, isNew):
    print("valueChanged: key: '%s'; value: %s; isNew: %s" % (key, value, isNew))

def connectionListener(connected, info):
    print(info, "; Connected=%s" % connected)

NetworkTables.addConnectionListener(connectionListener, immediateNotify=True)

sd = NetworkTables.getTable("team63_vision_table")
sd.addEntryListener(valueChanged)

while True:
    time.sleep(1)