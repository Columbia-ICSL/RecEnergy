import pymongo
import datetime
import time
import calendar
import pprint

def dump_debug_log():
	return pprint.pformat(
		list(pymongo.MongoClient().log_db.log.find()),
	indent=2)