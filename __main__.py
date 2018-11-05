from aiohttp import web
from splunk import SplunkClient

sclient = SplunkClient()
routes = web.RouteTableDef()

@routes.get('/')
async def handle_healthcheck(request):
	return web.Response(text="Hello World!")	

app = web.Application()
app.add_routes(routes)
web.run_app(app)