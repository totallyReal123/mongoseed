import socket

server_address = ()

def init(addr: (str, int)):
	global server_address
	server_address = addr

def send_raw(command: str):
	instruct = bytes(command.encode(encoding='ascii'))

	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
		s.connect(server_address)

		s.sendall(instruct)
		data = s.recv(520)
	return data

def get_channel_mseed(channel: str):
	send_raw('SELECT ' + channel + '\r')
	data = send_raw('DATA\r')
	return data[8:]
