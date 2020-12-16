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
	fake_file.close()
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

def serve_forever(channels: list, db: 'pymongo.database.Database', batch_interval: float, single_interval: float):
	while True:
		for channel in channels:
			tr = get_stream(channel)[0]
			timestamps = get_data_timestamps(tr)
			data = list(map(int, tr.data))
			records_to_add = []

			for i in range(len(data)):
				temp_dict = {}
				temp_dict['timestamp'] = timestamps[i]
				temp_dict['data'] = data[i]
				records_to_add.append(temp_dict)

			db[channel].insert_many(records_to_add)
			logging.info("Logged data for channel '" + channel +"'")

			time.sleep(single_interval)
		time.sleep(batch_interval)

def main():
	# Set output level of logger
	logging.getLogger().setLevel(logging.INFO)

	# Load json data into variable
	jdata = load_settings()

	# Setup variables from settings
	try:
		channels = jdata['seedServer']['channels']

		seed_address = str(jdata['seedServer']['address'])
		seed_port = int(jdata['seedServer']['port'])

		mongouri = "mongodb://" + jdata['mongoServer']['address'] + ":" + str(jdata['mongoServer']['port'])
		dbname = str(jdata['mongoServer']['databaseName'])

		batch_interval = float(jdata['global']['batchInterval'])
		single_interval = float(jdata['global']['singleInterval'])	
	except KeyError as e:
		key_name = ''.join(e.args)
		logging.critical("Unable to find setting '" + key_name + "' in configuration file.")
		sys.exit(1)


	# Initialize pyseed
	pyseed.init((seed_address, seed_port))

	# Setup mongodb connection (and check and create missing collections automagically)
	client = pymongo.MongoClient(mongouri)
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

	# Start main loop
	logging.info("Starting server main loop")
	try:
		serve_forever(channels, db, batch_interval, single_interval)
	except KeyboardInterrupt:
		logging.info("Keyboard Interrupt detected - closing server")
		sys.exit(130)

if __name__ == '__main__':
        logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%d-%m-%y %H:%M:%S')
        main()
