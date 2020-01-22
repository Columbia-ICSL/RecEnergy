"""
Python file for running the recommender system server using web.py.
"""
import web
import os
import datetime
import time
import calendar
import RecEnergy.DBMgr
import RecEnergy.api.bacnet as bacnet
db = DBMgr.DBMgr()

urls = ("/debug", "Debug",
        "/testEarnings", "Earnings",
        "/api/EnergyHVAC", bacnet.ReportBACNET)

class Debug:
    """
    """
    def GET(self):
        return DBMgr.dump_debug_log()

class Earnings:
    """
    Example for dynamic html, sends example earnings.
    TODO: Change return to compute the actual earnings.
    """
    def GET(self):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        return "$15,315"

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
