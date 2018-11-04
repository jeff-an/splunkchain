import subprocess

def run_splunk():
	subprocess.Popen(["/sbin/entrypoint.sh", "start-service"])
	subprocess.run(["tail", "-f", "Dockerfile"])

run_splunk()