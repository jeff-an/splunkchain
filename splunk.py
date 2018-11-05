import sys
import time
import json
import os
import subprocess
from subprocess import DEVNULL, PIPE

class SplunkClient():
	DATA_DIR = '/tmp/data'
	DATA_FILE = 'events.log'
	DATA_FILE_PATH = '{}/{}'.format(DATA_DIR, DATA_FILE)
	SPLUNK_HOME = '/opt/splunk'
	SPLUNK_BINARY = SPLUNK_HOME + "/bin/splunk"

	def __init__(self):
		self._file = self._create_data_file()
		if not os.path.exists(SplunkClient.SPLUNK_BINARY):
			print("Beginning Splunk installation...")
			subprocess.Popen(["/sbin/entrypoint.sh", "start-service"], stdout=DEVNULL, stderr=DEVNULL)
			time.sleep(40)
		self._add_splunk_file_monitor()
		print("Succesfully initialized Splunk and file monitor")
		#self.test()

	def test(self):
		a = {"host": "jan", "event": {"key": "hello"}, "time": 1541373097.5642061}
		b = {"host": "jan", "event": {"key": "world"}, "time": 23402349}
		self._file.write(json.dumps(a))
		self._file.write(json.dumps(b))

	def __del__(self):
		if hasattr(self, "_file"):
			self._file.close()

	def _create_data_file(self):
		if not os.path.exists(SplunkClient.DATA_DIR):
			os.mkdir(SplunkClient.DATA_DIR)
		return open(SplunkClient.DATA_FILE_PATH, "a+")

	def _add_splunk_file_monitor(self):
		attempt = 1
		while True:
			try:
				print("Attempt {} to add file monitor".format(attempt))
				process = subprocess.Popen(["/bin/bash",
											"-c",
											"{} login -auth admin:Chang3d! && {} add monitor {}"
												.format(SplunkClient.SPLUNK_BINARY,
														SplunkClient.SPLUNK_BINARY,
														SplunkClient.DATA_FILE_PATH)],
											stdin=PIPE,
											stdout=PIPE,
											stderr=PIPE,
											universal_newlines=True)
				print(process.communicate())
				break
			except Exception as e:
				print("Encountered exception while adding file monitor: {}".format(e))
				attempt += 1
				if attempt > 20:
					sys.exit(1)
				time.sleep(1.5)
			

