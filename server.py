"""
Python file for running the recommender system server using web.py.
"""
import web
import os
import datetime
import time
import calendar
import DBMgr
import api.energySensing.bacnet as bacnet
import api.energySensing.plugmeter as plugmeter
import api.websiteAPI as websiteAPI
db = DBMgr.DBMgr()

urls = ("/debug", "Debug",
        "/api/webAPI", websiteAPI.websiteParameters,
        "/api/EnergyReport",plugmeter.ReportPlugmeter,
        "/api/EnergyHVAC", bacnet.ReportBACNET,
        "/stateVector", "GetState")

class Debug:
    """
    """
    def GET(self):
        return DBMgr.dump_debug_log()

class GetState:
    def GET(self):
        return DBMgr.constructParameterValue()

class MyApplication(web.application):
    """
    web.py web application class.
    """
    def run(self, port=8070, *middleware):
        func = self.wsgifunc(*middleware)
        return web.httpserver.runsimple(func, ('0.0.0.0', port))

def notfound():
    return web.notfound("404 Not Found")

def run():
    app = MyApplication(urls, globals())
    app.notfound = notfound
    app.run(port=8000)
