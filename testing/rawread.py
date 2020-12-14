import obspy
import pyseedb
import tempfile
import struct

def main():
	file = open("examine.mseed", "rb")
	data = file.read()
	file.close()

	binary_string = data
	byte_order='>'
	block_size=512

	header=dict(zip(('sequence_number',
                 'data_header_indicator',
                 'reserved_byte',
                 'station',
                 'location',
                 'channel',
                 'network'),
                struct.unpack(byte_order+'6s2c5s2s3s2s', binary_string[:20])))
	print(header)
if __name__ == '__main__':
	main()
