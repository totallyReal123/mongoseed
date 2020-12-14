import obspy

def chunks(lst:list, n:int):
	new_array = []
	for i in range(0, len(lst), n):
		new_array.append(lst[i:i+n])
	return new_array

def list_to_string(lst:list):
	temp = ''.join([str(elem) for elem in lst]) 
	return temp

def main():
	#create_temp_file()
	file = open("examine.mseed", "rb")
	data = file.read()
	file.close()

	bar = []
	for byte in data:
		bar.append(format(int(byte), '08b'))

	words_list = chunks(bar, 4)
	frame_list = chunks(words_list, 16)

	frame = frame_list[0 ]
	for word in frame:
		for byte in word:
			print(chr(int(byte, 2)), "-", int(byte, 2), "-", byte)

if __name__ == '__main__':
	#main()
	tr = obspy.read("examine.mseed")