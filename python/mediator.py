
import utils
import packet

local_port = 20000

hosts_by_service = {}
agents_by_reference = {}

ref = 0

class Host:

	def __init__(self, hostname, addr):
		self.hostname = hostname
		self.addr = addr
	
class Client:
	
	def __init__(self, clientname, addr):
		self.clientname = clientname
		self.addr = addr

if __name__ == "__main__":
	sock = utils.UDPSocket((utils.ALL_INTERFACES, local_port))
	
	print "socket created on", sock.getsockname()
	

	while True:
		print "listening for packets"
		pack, addr = sock.recvfrom(65535)	
		print "received", repr(pack), "from", addr
		
		if pack.maintype != packet.TYPE_CONTROL:			#mediator doesn't handle data packets
			print "not a control packet, continue"
			continue
			
		if pack.subtype == packet.SUBTYPE_HOST_SERVER_REGISTER:
			hostname, servicename = packet.getHostServerRegisterData(pack)
			if not servicename in hosts_by_service:
				hosts_by_service[servicename] = []
				
			hosts_by_service[servicename].append(Host(hostname, addr))
			print "host", hostname, "registered for service", servicename
		
			ack = packet.getAckPacket(pack.number+1, pack.number)	
			sock.sendto(ack, addr)
			print "sent", repr(ack), "to", addr, "(host)"
			
			
			
		elif pack.subtype == packet.SUBTYPE_HOST_SERVER_RDY:
			reference = packet.getHostServerReadyData(pack)
			
			if not reference in agents_by_reference:
				continue
				
			agents = agents_by_reference[reference]
			host = agents[0]
			client = agents[1]
			
			if not host.addr[0] == addr[0]:
				print "wrong host ip"
				continue
				
			tohost = packet.get_server_agent_connect_packet(0, (client.clientname, client.addr[0], client.addr[1]))
			toclient = packet.get_server_agent_connect_packet(0, (host.hostname, host.addr[0], host.addr[1]))
			
			sock.sendto(tohost, addr)
			sock.sendto(toclient, client.addr)
			print "sent connect packets"
			
		elif pack.subtype == packet.SUBTYPE_CLIENT_SERVER_REQ_HOST:
		
			clientname, hostname, service = packet.get_client_server_req_host_data(pack)
			
			if not service in hosts_by_service:
				continue
				
			host = None
			for h in hosts_by_service[service]:
			
				if h.hostname == hostname:
					host = h
					break
		
			if host == None:
				continue
				
			reference = ref
			ref = ref + 1
			
			agents_by_reference[reference] = (host, Client(clientname, addr))
			
			op = packet.getServerHostOpenPacket(0, reference)
			sock.sendto(op, host.addr)
			print "sent", repr(op), "to", host.addr, "(host)"
			
	sock.close()
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
