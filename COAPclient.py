import coapDefines	as defines
from coapthon.client.helperclient import HelperClient
import random

def random_server():
	x = random.randint(1,10)
	if(x%2==0):
		return defines.SERVER_1
	elif(x%2==1):
		return defines.SERVER_2

def random_payload():
	x = random.randint(1,10)
	if(x%2==0):
		return defines.TEMP
	elif(x%2==1):
		return defines.VOLT

def create_pkt():
	#Net layer
	host = random_server()
	#Transport layer
	udp_port = 5683
	#App layer
	payload = random_payload()
	return host, udp_port, payload
	
def main():
	host, port, path = create_pkt()
	serverCOAP = HelperClient(server=(host, port))
	response = serverCOAP.get(path) 
	print response.pretty_print()
	serverCOAP.stop()

if __name__ == '__main__':
	main()