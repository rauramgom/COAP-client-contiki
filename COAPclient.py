from coapthon.client.helperclient import HelperClient
import random
import re
import time

def countdown(n):
	while n>0:
		time.sleep(1)
		n=n-1
	main()


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
	parserFullLine = re.compile("From \('(.*)', (\d+)\).* ({.*:)")
	FullLine=parserFullLine.findall(response)
	if len(FullLine):
		if len(FullLine[0])==3:
			parserType = re.compile("{\"(.*)\":{")
			Type=parserType.findall(response)
		
			if (len(Type) and Type[0]=="Volt"):
				unit="\"mV\""
			elif (len(Type) and Type[0]=="Temp"):
				unit="\"C\""
			else:
				flag=ERROR
				print "[**ERROR**] There is an error while getting Type value.\n"

			if flag==ERROR:
				newLine = "[**ERROR**] Error parsing this line!"
			else:
				measure = (FullLine[0][2], "}}")
				newLine = "From: ({0}:{1}), Receive: {2}, Date: {3}\n".format(FullLine[0][0], FullLine[0][1], unit.join(measure), time.ctime())
			
			with open('file.txt', 'a') as f:
				f.write(newLine)
		else:
			print "[**ERROR**] There is an error while parsing full line.\n"
	else:
		print "[**ERROR**] The parsed full line is empty!\n"
# End of write_file()

def main():
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
	countdown(5)
# End of main()

if __name__ == '__main__':
	main()