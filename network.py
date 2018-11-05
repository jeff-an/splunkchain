import os
import requests
import time
import threading
import json
from splunk import SplunkClient


class setInterval():
    def __init__(self, interval, action) :
        self.interval = interval
        self.action = action
        self.stopEvent = threading.Event()
        thread = threading.Thread(target=self._setInterval)
        thread.start()

    def _setInterval(self) :
        nextTime = time.time() + self.interval
        while not self.stopEvent.wait(nextTime - time.time()):
            nextTime += self.interval
            self.action()

    def cancel(self) :
        self.stopEvent.set()


class Network():
    ''' Class responsible for data syncing '''
    def __init__(self, local_chain, sclient):
        self.sclient = sclient
        self.blockchain = local_chain
        self.node_name = local_chain.sender
        self.node_ip = os.environ['SPLUNKCHAIN_SVC_{}_SERVICE_HOST'.format(self.node_name)]
        self.peers = self._get_peers()
        self.register_self()
        self.sync_cron = setInterval(5, lambda: self.sync())

    @staticmethod
    def _set_interval(func, sec):
        def func_wrapper():
            Network._set_interval(func, sec)
            func()
        t = threading.Timer(sec, func_wrapper)
        t.start()
        return t

    def _get_peers(self):
        result = set()
        for key, val in os.environ.items():
            if "SPLUNKCHAIN_SVC" in key and "HOST" in key:
                if val != self.node_ip:
                    result.add(val)
        return result
       
    def register_node(self, ip):
        self.peers.add(ip)
    
    def register_self(self):
        for peer in self.peers:
            payload = {
                "address": self.node_ip
            }
            print("Registering {} at {}".format(self.node_ip, peer))
            response = requests.post('http://{}/nodes/register'.format(peer), json=payload)
            print(response)
        if len(self.peers):
            self.sync()
        else:
            self.blockchain.init_chain()
    
    def sync(self):
        ''' This is our consensus algorithm, it resolves conflicts '''
        neighbours = self.peers
        new_chain = None
        # We're only looking for chains longer than ours
        max_length = len(self.blockchain.chain)
        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get("http://{}/data".format(node))
            if response.status_code == 200:
                length = response.json()['chain']['length']
                chain = response.json()['chain']['data']
                # Check if the length is longer and the chain is valid
                if length > max_length and self.blockchain.valid_chain(chain):
                    max_length = length
                    new_chain = chain
        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            self.sclient.replace_events(response.json()['events'])
            return True
        return False
