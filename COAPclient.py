#!/usr/bin/python
from coapthon.client.helperclient import HelperClient
import random
import re
import time
import signal

from observer import *

serverRequest = None

def write_file(response):
	flag = True
	parserFullLine = re.compile("From \('(.*)', (\d+)\).* ({.*):?\.\.\.")
	fullLine = parserFullLine.findall(str(response))
	if len(fullLine)>0:
		if len(fullLine[0])==3:
			parserType = re.compile("{\"(.*)\":{")
			fieldType = parserType.findall(str(response))
			if (len(fieldType) and fieldType[0]=="Volt"):
				unit = ":\"mV\""
				measure = (fullLine[0][2], "}}")
				newLine = "From: ({0}:{1}), Receive: {2}, Date: {3}\n".format(fullLine[0][0], fullLine[0][1], unit.join(measure), time.ctime())
			elif (len(fieldType) and fieldType[0]=="Temp"):
				unit = "\"C\""
				measure = (fullLine[0][2], "}}")
				newLine = "From: ({0}:{1}), Receive: {2}, Date: {3}\n".format(fullLine[0][0], fullLine[0][1], unit.join(measure), time.ctime())
			else:
				flag = False
				print "[**ERROR**] There is an error while getting Type value."
			
			with open('/tmp/results_demo.txt', 'a') as f:
				f.write(newLine)
		else:
			print "[**ERROR**] There is an error while parsing full line."
			flag = False
	else:
		print "[**ERROR**] The parsed full line is empty!"
		flag = False

	return flag
# End of write_file()


def create_pkt(type_of_var, type_of_sensor):
	resources = ["sen/local temp", "sen/local volt", "sen/remote temp", "sen/remote volt"]
	if type_of_var.lower() == "l":
		if type_of_sensor.lower() == "t":
			payload = resources[0]
		else:
			payload = resources[1]
	else:
		if type_of_sensor.lower() == "t":
			payload = resources[2]
		else:
			payload = resources[3]

	#host = random.choice(["aaaa::212:4b00:7e1:c280", "aaaa::212:4b00:7e1:d086"])
	#host = "aaaa::212:4b00:7e1:d086"
	udp_port = 5683

	#return host, udp_port, payload
	return udp_port, payload
# End of create_pkt()




def simple_request(type_of_var, type_of_sensor):

	port, path = create_pkt(type_of_var, type_of_sensor)
	host = "aaaa::212:4b00:7bb:1384"

	print "[{0}] Making GET request: [{1}]:{2}{3}".format(time.ctime(), host,port,path)
	serverRequest = HelperClient(server=(host, port))
	if serverRequest:
		response = serverRequest.get(path)
		if response:
			serverRequest.stop()
			write_file(response)
	else:
		print "[**ERROR**] No response has been received from the server.\n"
# End of simple_request()


def main():
	print "----------------------------------------------------------"
	type_of_request = raw_input("Choose to do a simple Request(R) or to set an Observer(O): ")
	if type_of_request == "" or not (type_of_request.upper()=="R" or type_of_request.upper()=="O"):
		print "Unrecognized choose."
	elif type_of_request.upper()=="R":
		timer_req = raw_input("Choose a timer to make periodical requests (0 for only one): ")
		while (1):
			type_of_var = raw_input("Local or Remote resource? [L/R]:")
			if (type_of_var.lower() == "l" or type_of_var.lower() == "r"):
				while (1):
					type_of_sensor = raw_input("Temp or Volt? [T/V]: ")
					if (type_of_sensor.lower() == "t" or type_of_sensor.lower() == "v"):
						break
					else:
						print "Unrecognized choose."
				break
		else:
			print "Unrecognized choose."

		if timer_req=="0":
			simple_request(type_of_var, type_of_sensor)
		elif timer_req>"0":
			try:
				while (1):
					simple_request(type_of_var, type_of_sensor)
					time.sleep(float(timer_req))
			except KeyboardInterrupt:
				print "\nStopping requests...\n"
				main()
		else:
			print "Unrecognized choose."

	elif type_of_request.upper()=="O":
		observer_func()
# End of main()

if __name__ == '__main__':
	main()