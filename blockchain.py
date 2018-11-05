import hashlib
import json
from time import time
from urllib.parse import urlparse
from collections import defaultdict


class Blockchain:
    def __init__(self, node_name, sclient):
        self.current_transactions = []
        self.chain = []
        self.sender = node_name
        self.sclient = sclient
    
    def init_chain(self):
        # Create the genesis block
        self.new_transaction("0", self.sender, 100)
        self.new_block(previous_hash='1', proof=100)

    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid
        :param chain: A blockchain
        :return: True if valid, False if not
        """
        if not len(chain):
            return True
        last_block = chain[0]
        current_index = 1
        balances = defaultdict(int)
        first_recipient = last_block['transactions'][0]['recipient']
        balances[first_recipient] += last_block['transactions'][0]['amount']
        while current_index < len(chain):
            block = chain[current_index]
            print(last_block)
            print(block)
            print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False
            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False
            for transaction in block['transactions']:
                recipient = transaction['recipient']
                sender = transaction['sender']
                amount = int(transaction['amount'])
                if sender == "0":
                    # From the system
                    continue
                balances[sender] -= amount
                if balances[sender] < 0:
                    print("Detected overspend by {} in transaction {}".format(sender, transaction))
                    return False
                balances[recipient] += amount
            last_block = block
            current_index += 1
        return True

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain
        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }
        # Reset the current list of transactions
        self.current_transactions = []
        self.chain.append(block)
        self.sclient.add_event(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block
        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })
        return len(self.chain)

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block
        :param block: Block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:
         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof
        :param last_block: <dict> last Block
        :return: <int>
        """
        last_proof = last_block['proof']
        last_hash = self.hash(last_block)
        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1
        return proof

    def mine(self):
        # We run the proof of work algorithm to get the next proof...
        last_block = self.last_block
        proof = self.proof_of_work(last_block)
        # We must receive a reward for finding the proof.
        # The sender is "0" to signify that this node has mined a new coin.
        self.new_transaction(
            sender="0",
            recipient=self.sender,
            amount=1,
        )
        # Forge the new Block by adding it to the chain
        previous_hash = self.hash(last_block)
        block = self.new_block(proof, previous_hash)
        response = {
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }
        return response

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.
        """
        guess = "{}{}{}".format(last_proof, proof, last_hash).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
