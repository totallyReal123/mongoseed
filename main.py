from modules import pyseed
import tempfile
import logging
import json
import time
import sys
import pymongo
import obspy

def load_settings():
	try:
		file = open("./config/config.json", "r")
	except FileNotFoundError:
		logging.critical("Unable to find config file")
		sys.exit(0)

	data = file.read()
	file.close()

	if len(data) == 0:
		logging.critical("No data found in config file")
		sys.exit(0)

	return json.loads(data)

def get_stream(channel: str):
	data = pyseed.get_channel_mseed(channel)

	fake_file = tempfile.TemporaryFile(mode="ab+")
	fake_file.write(data)
	fake_file.seek(0)

	st = obspy.read(fake_file)
	return st

def get_data_timestamps(trace):
	start = trace.stats.starttime.timestamp
	end = trace.stats.endtime.timestamp

	data = list(trace.data)
	time_correlation = []

	# Find intervals
	change = (end-start)/len(data)

	# Assign timestamp to each point
	for i in range(len(data)):
		timestamp = round(start + (i * change), 2)
		time_correlation.append(timestamp)

	return time_correlation

def serve_forever(channels: list, db: 'pymongo.database.Database'):
	while True:
		for channel in channels:
			tmpdict = {}

			tr = get_stream(channel)[0]
			timestamps = get_data_timestamps(tr)
			data = list(map(int, tr.data))

			tmpdict['timestamps'] = timestamps
			tmpdict['data'] = data

			db[channel].insert_one(tmpdict)
		time.sleep(2.5)

def main():
	# Set output level of logger
	logging.getLogger().setLevel(logging.INFO)

	# Load json data into variable
	jdata = load_settings()

	# Setup seedlink connection
	channels = jdata['seedServer']['channels']
	pyseed.init((str(jdata['seedServer']['address']), int(jdata['seedServer']['port'])))

	# Setup mongodb connection
	mongouri = "mongodb://" + jdata['mongoServer']['address'] + ":" + str(jdata['mongoServer']['port'])
	client = pymongo.MongoClient(mongouri)

	# Check and setup database and collections (if any collection doesn't exist, create it)
	dbname = str(jdata['mongoServer']['databaseName'])
	db = client[dbname]

	if not (dbname in client.list_database_names()):
		logging.warning("MongoDB database '" + dbname + "' not found - creating automagically")

		for channel in channels:
			db.create_collection(channel)
	else:
		collections = db.list_collection_names()
		for channel in channels:
			if not(channel in collections):
				logging.warning("MongoDB collection '" + channel + "' not found - creating automagically")
				db.create_collection(channel)

	logging.info("Starting server main loop")
	try:
		serve_forever(channels, db)
	except KeyboardInterrupt:
		pass
	logging.info("Keyboard Interrupt detected - closing server")

if __name__ == '__main__':
	main()