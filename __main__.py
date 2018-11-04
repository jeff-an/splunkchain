import subprocess
from aiohttp import web

routes = web.RouteTableDef()

def run_splunk():
	subprocess.Popen(["/sbin/entrypoint.sh", "start-service"])

@routes.get('/')
async def handle_healthcheck(request):
	run_splunk()
	return web.Response(text="Hello World!")	

app = web.Application()
app.add_routes(routes)
web.run_app(app)