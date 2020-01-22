import json
import web
import RecEnergy.server


urls = (
	"/SaveBACNET","SaveBACNET",
	"/SaveParameters", "SaveParameters",
	"/GetParameters", "GetParameters"
)


class SaveBACNET:
	def POST(self):
		D = ["nwc1000m_light",
			"nwc10hallway_light",
			"nwc10elevator_light",
			"nwc8_light",
			"nwc7_light",
			"nwc1003b_light",
			"nwcM1_fcu",
			"nwcM2_fcu",
			"nwcM3_fcu",
			"nwcM4_fcu",
			"nwc1008_fcu",
			"nwc1008_light",
			"nwc1003b_b_plug",
			"nwc1003b_c_plug",
			"nwc1003t_light",
			"nwc1003d_light"]
		print("Reporting BACNET")
		raw_data=web.data()
		data=json.loads(raw_data)
		for device in data:
			if device in D:
				continue
			server.db.ReportEnergyValue(device, data[device], None)
		return "200 OK"

class SaveParameters:
	def POST(self):
		print("Reporting Parameters")
		raw_data=web.data()
		data=json.loads(raw_data)
		server.db.SaveParameters(data)

class GetParameters:
	def GET(self):
		print("Getting bacnet data")
		return server.db.GetParameters()


ReportBACNET = web.application(urls, locals())