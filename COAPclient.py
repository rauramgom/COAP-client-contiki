#!/usr/bin/python
from coapthon.client.helperclient import HelperClient
import random
import re
import time

TRUE = 1
FALSE = 0

def random_server():
	server=["aaaa::212:4b00:7e1:c280", "aaaa::212:4b00:7e1:d086"]
	x = random.randint(1,2)
	return(server[x%2])
# End of random_server()


def random_payload():
	path=["/sen/temp","/sen/volt"]
	x = random.randint(1,2)
	return(path[x%2])
# End of random_payload()


def create_pkt():
	host = random_server()
	#host = "aaaa::212:4b00:7e1:d086"
	udp_port = 5683
	#payload = "/sen/temp"
	payload = random_payload()

	return host, udp_port, payload
# End of create_pkt()


def write_file(response):
	flag=TRUE
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
				flag=FALSE
				print "[**ERROR**] There is an error while getting Type value.\n"

			if flag==FALSE:
				newLine = "[**ERROR**] Error parsing this line!"
			else:
				measure = (fullLine[0][2], "}}")
				newLine = "From: ({0}:{1}), Receive: {2}, Date: {3}\n".format(fullLine[0][0], fullLine[0][1], unit.join(measure), time.ctime())
			
			with open('file.txt', 'a') as f:
				f.write(newLine)
		else:
			print "[**ERROR**] There is an error while parsing full line.\n"
	else:
		print "[**ERROR**] The parsed full line is empty!\n"
# End of write_file()

def main():
	while(1):
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
		time.sleep(5)
# End of main()

if __name__ == '__main__':
	main()