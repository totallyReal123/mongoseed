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

	#nibs = chunks(list_to_string(frame_list[0][0]), 2)
	nibs = frame_list[0]
	print(format(11, "08b"))

	'''
	foo = open("examine.txt", "w")
	foo.write(str(bar))
	foo.close()
	'''

if __name__ == '__main__':
	main()