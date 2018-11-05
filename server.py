import os
from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain
from splunk import SplunkClient
from network import Network


app = Flask(__name__)
node_identifier = os.environ["NODE_NAME"]
sclient = SplunkClient()
blockchain = Blockchain(node_identifier, sclient)
network = Network(blockchain, sclient)


@app.route('/send', methods=['GET'])
def new_transaction():
    recipient = request.args.get('recipient')
    amount = request.args.get('amount')
    blockchain.new_transaction(node_identifier, recipient, amount)
    response = blockchain.mine()
    return jsonify(response), 201


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    ip = values.get('address')
    network.register_node(ip)
    response = {
        'result': True
    }
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200
