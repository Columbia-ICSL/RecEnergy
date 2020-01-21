import web
import os
import datetime
import time
import calendar
import DBMgr

db = DBMgr.DBMgr()

urls = ("/debug", "Debug",
		"/testEarnings", "Earnings")

class Debug:
    def GET(self):
        return DBMgr.dump_debug_log()

class Earnings:
	def GET(self):
		return "$15,315"

class MyApplication(web.application):
	def run(self, port=8070, *middleware):
		func = self.wsgifunc(*middleware)
		return web.httpserver.runsimple(func, ('0.0.0.0', port))

def notfound():
	return web.notfound("404 Not Found")

def run():
	app = MyApplication(urls, globals())
	app.notfound = notfound
	app.run(port=8000)