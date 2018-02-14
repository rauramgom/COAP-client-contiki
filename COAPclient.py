#!/usr/bin/python
from coapthon.client.helperclient import HelperClient
import random
import re
import time

serverRequest = None

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
				print "[**ERROR**] There is an error while getting Type value.\n"

			if flag==False:
				newLine = "[**ERROR**] Error parsing this line!"
			else:
				measure = (fullLine[0][2], "}}")
				newLine = "From: ({0}:{1}), Receive: {2}, Date: {3}\n".format(fullLine[0][0], fullLine[0][1], unit.join(measure), time.ctime())
			
			with open('results.txt', 'a') as f:
				f.write(newLine)
		else:
			print "[**ERROR**] There is an error while parsing full line.\n"
	else:
		print "[**ERROR**] The parsed full line is empty!\n"
# End of write_file()


def create_pkt():
	host = random.choice(["aaaa::212:4b00:7e1:c280", "aaaa::212:4b00:7e1:d086"])
	udp_port = 5683
	payload = random.choice(["/sen/temp","/sen/volt"])

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
	print response
	write_file(response)
	check=True
	while check:
		option = raw_input("Stop observing? [y/N]: ")
		if option != "" and not (option.lower() == "y" or option.lower() == "n"):
			print "Unrecognized choose."
			continue
		elif option.lower() == "y":
			while True:
				rst = raw_input("Send RST message? [y/N]: ")
				if rst != "" and not (rst.lower() == "n" or rst.lower() == "y"):
					print "Unrecognized choose."
					continue
				elif rst == "" or rst.lower() == "y":
					serverRequest.cancel_observing(response, True)
				else:
					serverRequest.cancel_observing(response, False)
				check = False
				break
		else:
			continue
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
			while (1):
				simple_request()
				time.sleep(float(timer_req))
		else:
			print "Unrecognized choose."

	elif type_of_request.upper()=="O":
		observer_func()


# End of main()

if __name__ == '__main__':
	main()