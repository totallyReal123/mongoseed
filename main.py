from modules import pyseed
import json
import pymongo
import tempfile
import obspy
import datetime
import logging

def load_settings():
	data = open("./config/config.json", "r").read()
	return json.loads(data)

def get_stream(channel: str):
	data = pyseed.get_channel_mseed(channel)

	fake_file = tempfile.TemporaryFile(mode="ab+")
	fake_file.write(data)

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


def main():
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
		print("MongoDB database '" + dbname + "' not found\nCreating Now...")

		for channel in channels:
			db.create_collection(channel)
	else:
		collections = db.list_collection_names()
		for channel in channels:
			if not(channel in collections):
				print("MongoDB collection '" + channel + "' not found\nCreating Now...")
				db.create_collection(channel)

	for channel in channels:
		tmpdict = {}

		tr = get_stream(channel)[0]
		timestamps = get_data_timestamps(tr)
		data = list(map(int, tr.data))

		tmpdict['timestamps'] = timestamps
		tmpdict['data'] = data

		db[channel].insert_one(tmpdict)

if __name__ == '__main__':
	main()