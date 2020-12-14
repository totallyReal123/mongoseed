import obspy
import pyseedb
import tempfile

def main():
	file = open("examine.mseed", "rb")
	data = file.read()
	file.close()

	foo = tempfile.TemporaryFile(mode="w+b")
	foo.write(data)
	foo.seek(0)


	st = obspy.read(foo)
	print(st[0].stats)

if __name__ == '__main__':
	main()
