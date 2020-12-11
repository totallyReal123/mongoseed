import pymongo
import json

# Import settings as json object
data = open("./config/config.json", "r").read()
jdata = json.loads(data)

mongouri = "mongodb://" + jdata['mongoServer']['address'] + ":" + str(jdata['mongoServer']['port'])
client = pymongo.MongoClient(mongouri)

#print(dir(client), "\n")
dbname = jdata['mongoServer']['databaseName']
db = client[dbname]
client.drop_database(db)