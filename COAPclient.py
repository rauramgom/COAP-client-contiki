#!/usr/bin/python
from coapthon.client.helperclient import HelperClient
import random
import re
import time
import signal

serverRequest = None
countObserver = 0

def write_file(response):
	flag=True
	parserFullLine = re.compile("From \('(.*)', (\d+)\).* ({.*):?\.\.\.")
	fullLine=parserFullLine.findall(str(response))
	if len(fullLine):
		if len(fullLine[0])==3:
			parserType = re.compile("{\"(.*)\":{")
			fieldType=parserType.findall(str(response))
			if (len(fieldType) and fieldType[0]=="Volt"):
				unit=":\"mV\""
			elif (len(fieldType) and fieldType[0]=="Temp"):
				unit="\"C\""
			else:
				flag=False
				print "[**ERROR**] There is an error while getting Type value."

			if flag==False:
				newLine = "[**ERROR**] Error parsing this line!"
			else:
				measure = (fullLine[0][2], "}}")
				newLine = "From: ({0}:{1}), Receive: {2}, Date: {3}\n".format(fullLine[0][0], fullLine[0][1], unit.join(measure), time.ctime())
			
			with open('results.txt', 'a') as f:
				f.write(newLine)
		else:
			print "[**ERROR**] There is an error while parsing full line."
	else:
		print "[**ERROR**] The parsed full line is empty!"
# End of write_file()


def create_pkt():
	#host = random.choice(["aaaa::212:4b00:7e1:c280", "aaaa::212:4b00:7e1:d086"])
	host = "aaaa::212:4b00:7e1:c280"
	udp_port = 5683
	payload = "/sen/temp"
	#payload = random.choice(["/sen/temp","/sen/volt"])
	return host, udp_port, payload
# End of create_pkt()


def observer_func():
	global serverRequest
	host, port, path = create_pkt()
	print "[{0}] Making an observer request: [{1}]:{2}{3}".format(time.ctime(), host,port,path)
	serverRequest = HelperClient(server=(host, port))
	if serverRequest:
		serverRequest.observe(path, client_callback_observe)
# End of observer_func()


def client_callback_observe(response):
	global serverRequest
	global countObserver
	check=True
	option=""
	
	print response
	print "Writing new observed measure..."
	write_file(response)
	countObserver += 1

	if countObserver==4:
		while check:
			option = raw_input("Stop observing? [y/N]: ")
			if (option.lower() == "y" or option.lower() == "n"):
				break
			else:
				print "Unrecognized choose."

		if option.lower() == "y":
			# RFC7641 explicit cancel is by sending OBSERVE=1 with the same token,
			# not by an unsolicited RST (which may would be ignored)
			print "Sending request with OBSERVE=1 to cancel an observation...\n"
			serverRequest.cancel_observing(response, True)
			time.sleep(2.0)
			main()

		elif option.lower() == "n":
			countObserver=0


	"""try:
		print "Writing new observed measure..."
		write_file(response)
		time.sleep(5)
	except KeyboardInterrupt:
		option = raw_input("Stop observing? [y/N]: ")
		if option != "" and not (option.lower() == "y" or option.lower() == "n"):
			print "Unrecognized choose."
		elif option.lower() == "y":
			print "Sending request with OBSERVE=1 to cancel an observation...\n"
			# RFC7641 explicit cancel is by sending OBSERVE=1 with the same token,
			# not by an unsolicited RST (which may would be ignored)
			serverRequest.cancel_observing(response, True)
			time.sleep(2.0)
			main()
		else:
			print "The observer has not been cancelled.\n"
			time.sleep(2.0)
			main()
	print "[**BORRAR**] Al final de client_callback_observe()"""
# End of client_callback_observe()


def simple_request():
	host, port, path = create_pkt()
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
		timer_req = raw_input("   Choose a timer to make periodical requests (0 for only one): ")
		if timer_req=="0":
			simple_request()
		elif timer_req>"0":
			try:
				while (1):
					simple_request()
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