#!/usr/bin/python
#JSH: for detecting whether hardware is Mac or not 

import os
def isMac( self ):
    try:
    	file = open("/sys/devices/virtual/dmi/id/bios_vendor", "r")
    	if file:
    	    buffer = file.read()
    	    file.close()
    	    # iMac x64 contains: "Apple Inc."
    	    # Mac Pro contains : "Apple Computer, Inc."
    	    if buffer.__contains__("Apple"):
    	    	return 1
    	    else:
    	    	return 0
    	else:
    	    return 0
    except:
    	return 0
	
	