import json
import web
import server


urls = (
	"/monthlyEarnings","monthlyEarnings",
	"/annualEarnings","annualEarnings"
)

class monthlyEarnings:
    """
    Example for dynamic html, sends example earnings.
    TODO: Change return to compute the actual earnings.
    """
    def GET(self):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        return "$10,315"

class annualEarnings:
    """
    Example for dynamic html, sends example earnings.
    TODO: Change return to compute the actual earnings.
    """
    def GET(self):
        web.header('Access-Control-Allow-Origin', '*')
        web.header('Access-Control-Allow-Credentials', 'true')
        return "$221,043"

websiteParameters = web.application(urls, locals())