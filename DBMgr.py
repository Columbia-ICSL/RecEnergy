import pymongo
import datetime
import time
import calendar
import pprint

def dump_debug_log():
	return pprint.pformat(
		list(pymongo.MongoClient().log_db.log.find()),
	indent=2)

class DBMgr(object):
	def _GetConfigValue(self,key):
		try:
			ret=self.config_col.find_one({"_id":key})
			return ret["value"]
		except:
			return None

	def _SetConfigValue(self,key,value):
		self.config_col.replace_one({"_id":key},{"value":value},True)

	def _ReadConfigs(self):
		self.ROOM_DEFINITION=self._GetConfigValue("ROOM_DEFINITION")
		self.APPLIANCE_DEFINITION=self._GetConfigValue("APPLIANCE_DEFINITION")
		self.SAMPLING_TIMEOUT_SHORTEST=self._GetConfigValue("SAMPLING_TIMEOUT_SHORTEST")
		self.SAMPLING_TIMEOUT_LONGEST=self._GetConfigValue("SAMPLING_TIMEOUT_LONGEST")
		self.WATCHDOG_TIMEOUT_USER=self._GetConfigValue("WATCHDOG_TIMEOUT_USER")
		self.WATCHDOG_TIMEOUT_APPLIANCE=self._GetConfigValue("WATCHDOG_TIMEOUT_APPLIANCE")

	def _ConstructInMemoryGraph(self):
		self.list_of_rooms={};
		self.list_of_appliances={};
		self.location_of_users={};

		for room in self.ROOM_DEFINITION:
			room["appliances"]=[]
			room["users"]=[]
			self.list_of_rooms[room["id"]]=room

		for appliance in self.APPLIANCE_DEFINITION:
			appliance["value"]=0
			appliance["total_users"]=0
			appliance["rooms"].sort()
			self.list_of_appliances[appliance["id"]]=appliance
			for roomID in appliance["rooms"]:
				self.list_of_rooms[roomID]["appliances"]+=[appliance["id"]]

		for room in self.ROOM_DEFINITION:
			self.list_of_rooms[room["id"]]["appliances"].sort()

	def _HardcodeValues(self):
		if ("nwc1000m_light" in self.list_of_appliances):
			self.list_of_appliances["nwc1000m_light"]["value"] = 300
		if ("nwc10hallway_light" in self.list_of_appliances):
			self.list_of_appliances["nwc10hallway_light"]["value"] = 100
		if ("nwc10elevator_light" in self.list_of_appliances):
			self.list_of_appliances["nwc10elevator_light"]["value"] = 150
		if ("nwc8_light" in self.list_of_appliances):
			self.list_of_appliances["nwc8_light"]["value"] = 150
		if ("nwc7_light" in self.list_of_appliances):
			self.list_of_appliances["nwc7_light"]["value"] = 150
		if ("nwc1003b_light" in self.list_of_appliances):
			self.list_of_appliances["nwc1003b_light"]["value"] = 675
		if ("nwcM1_fcu" in self.list_of_appliances):
			self.list_of_appliances["nwcM1_fcu"]["value"] = 930
		if ("nwcM2_fcu" in self.list_of_appliances):
			self.list_of_appliances["nwcM2_fcu"]["value"] = 930
		if ("nwcM3_fcu" in self.list_of_appliances):
			self.list_of_appliances["nwcM3_fcu"]["value"] = 930
		if ("nwcM4_fcu" in self.list_of_appliances):
			self.list_of_appliances["nwcM4_fcu"]["value"] = 930
		if ("nwc1008_fcu" in self.list_of_appliances):
			self.list_of_appliances["nwc1008_fcu"]["value"] = 550
		if ("nwc1008_light" in self.list_of_appliances):
			self.list_of_appliances["nwc1008_light"]["value"] = 240
		if ("nwc1003b_b_plug" in self.list_of_appliances):
			self.list_of_appliances["nwc1003b_b_plug"]["value"] = 93
		if ("nwc1003b_c_plug" in self.list_of_appliances):
			self.list_of_appliances["nwc1003b_c_plug"]["value"] = 63
		if ("nwc1003t_light" in self.list_of_appliances):
			self.list_of_appliances["nwc1003t_light"]["value"] = 675
		if ("nwc1003d_light" in self.list_of_appliances):
			self.list_of_appliances["nwc1003d_light"]["value"] = 675

	def __init__(self, start_bg_thread=True):
		self.dbc=pymongo.MongoClient()

		self.registration_col1=self.dbc.db.registration_col1
		self.ranking = self.dbc.db.ranking
		self.indirectSensing = self.dbc.db.indirectSensing
		self.particleSensor = self.dbc.db.particleSensor
		self.suggestionsML = self.dbc.db.suggestionsML
		#user registration
		self.config_col=self.dbc.db.config
		#metadata col
		self.raw_data=self.dbc.db.raw_data
		#any raw data document.
		self.events_col=self.dbc.db.events_col
		#any events

		self.fintubeMonitor=self.dbc.db.fintubeMonitor
		#save fin tube radiator data, for building modeling

		self.snapshots_parameters=self.dbc.db.snapshots_parameters
		self.snapshots_col_rooms=self.dbc.db.snapshots_col_rooms
		self.snapshots_col_appliances=self.dbc.db.snapshots_col_appliances
		self.snapshots_col_users=self.dbc.db.snapshots_col_users
		#snapshot storage

		self.pushManagement_push_col=self.dbc.db.pushManagement_push_col
		self.pushManagement_disp_col=self.dbc.db.pushManagement_disp_col
		#push management timestamp storage

		self.historicalCumulativeEnergy=self.dbc.db.historicalCumulativeEnergy
		self.todayCumulativeEnergy=self.dbc.db.todayCumulativeEnergy

		self.humanCentricZones=self.dbc.db.humanCentricZones
		self.humanCentricZonesTesting=self.dbc.db.humanCentricZonesTesting
		
		self.recommendationTimestamps = self.dbc.db.recommendationTimestamps

		self._ReadConfigs()
		## Data Structure Init: bipartite graph between rooms and appls
		## TODO: Add a web interface to update config in db, and pull new config into memory.

		self._ConstructInMemoryGraph()
		## Construct bipartite graph.
		# self._accumulator()
		# self._GracefulReloadGraph()
		## Read appliance values from database; TODO: occupants location
		self._HardcodeValues()
		self.watchdogInit()

	def startDaemon(self):
		t=Thread(target=self._backgroundLoop,args=())
		t.setDaemon(True)
		t.start()

	def watchdogInit(self):
		self.watchdogLastSeen_User={}
		self.watchdogLastSeen_Appliance={}