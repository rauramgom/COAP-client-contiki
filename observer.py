#!/usr/bin/python
from coapthon.client.helperclient import HelperClient
import random
import re
import time
import signal

from COAPclient import *

serverRequest = None
countObserver = 0

def observer_func():
	global serverRequest

	while (1):
		type_of_var = raw_input("Local or Remote resource? [L/R]:")
		if (type_of_var.lower() == "l" or type_of_var.lower() == "r"):
			while (1):
				type_of_sensor = raw_input("Temp or Volt? [T/V]: ")
				if (type_of_sensor.lower() == "t" or type_of_sensor.lower() == "v"):
					port, path = create_pkt(type_of_var, type_of_sensor)
					host = "aaaa::212:4b00:7bb:1384"
					break
				else:
					print "Unrecognized choose."
			break
		else:
			print "Unrecognized choose."

	print "[{0}] Making an observer request: [{1}]:{2}{3}".format(time.ctime(), host,port,path)
	serverRequest = HelperClient(server=(host, port))
	if serverRequest:
		serverRequest.observe(path, client_callback_observe)
# End of observer_func()


def client_callback_observe(response):
	global serverRequest
	global countObserver
	option=""
	
	#print response
	print "Writing new observed measure..."
	flag = write_file(response)
	if flag:
		countObserver += 1
		if countObserver==50:
			while (1):
				option = raw_input("Stop observing? [y/N]: ")
				if (option.lower() == "y" or option.lower() == "n"):
					break
				else:
					print "Unrecognized choose."

			if option.lower() == "y":
				# RFC7641 explicit cancel is by sending OBSERVE=1 with the same token,
				# not by an unsolicited RST (which may would be ignored)
				print "Sending request with OBSERVE=1 to cancel the observation...\n"
				serverRequest.cancel_observing(response, True)
				time.sleep(2.0)
				main()

			elif option.lower() == "n":
				countObserver = 0
	else:
		print "	Sending request with OBSERVE=1 to cancel the observation...\n"
		serverRequest.cancel_observing(response, True)
		time.sleep(2.0)
		main()
# End of client_callback_observe()