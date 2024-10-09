from flask import Flask, render_template, jsonify, request
from time import time
from flask_cors import CORS
from collections import OrderedDict
import binascii
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA
from uuid import uuid4
import json
import hashlib

MINING_SENDER = 'The Blockchain'
MINING_REWARD = 1

class Blockchain:
  def __init__(self):
    self.transactions = []
    self.chain = []
    self.node_id = str(uuid4()).replace('-', '')
    # Create the genesis block
    self.create_block(0, '00')
    
  def create_block(self, nonce, previous_hash):
    """
    Add a block of transaction to the blockchain
    """
    block = {
      'block_number': len(self.chain) + 1,
      'timestamp': time(),
      'transactions': self.transactions,
      'nonce': nonce,
      'previous_hash': previous_hash
    }
    # Reset the transaction
    self.transactions = []
    self.chain.append(block)
    return block
    
  def verify_transaction_signature(self, sender_public_key, signature, transaction):
    public_key = RSA.importKey(binascii.unhexlify(sender_public_key))
    verifier = PKCS1_v1_5.new(public_key)
    hash = SHA.new(str(transaction).encode('utf8'))
    try:
      verifier.verify(hash, binascii.unhexlify(signature))
      return True
    except ValueError:
      return False
    
    
  def proof_of_work(self):
    last_block = self.chain[-1]
    last_hash = self.hash(last_block)
    
    nonce = 0
    while self.valid_proof(self.transactions, last_hash, nonce) is False:
      nonce += 1
    
    return nonce
  
  def valid_proof(self, transactions, last_hash, nonce, difficulty=2):
    guess = (str(transactions) + str(last_hash) + str(nonce)).encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:difficulty] == '0' * difficulty
  
  def hash(self, block):
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()
    
  def submit_transaction(self, sender_public_key, recipient_public_key, amount, signature):
    transaction = OrderedDict({ 
      'sender_public_key': sender_public_key,
      'recipient_public_key': recipient_public_key,
      'amount': amount
    })
    
    if sender_public_key == MINING_SENDER:
      self.transactions.append(transaction)
      return len(self.chain) + 1
    else:
      signature_verification = self.verify_transaction_signature(sender_public_key, signature, transaction)
      if signature_verification:
        self.transactions.append(transaction)
        return len(self.chain) + 1
      else:
        return False
  

    
# Instantiate the Blockchain
blockchain = Blockchain()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
  return render_template('./index.html')


@app.route('/chain', methods=['GET'])
def get_chain():
  response = {
    'chain': blockchain.chain,
    'length': len(blockchain.chain)
  }
  return jsonify(response), 200

@app.route('/transactions/get', methods=['GET'])
def get_transactions():
  transactions = blockchain.transactions
  response = {
    'transactions': transactions
  }
  return jsonify(response), 200


@app.route('/mine', methods=['GET'])
def mine():
  nonce = blockchain.proof_of_work()
  blockchain.submit_transaction(sender_public_key=MINING_SENDER, recipient_public_key=blockchain.node_id, amount=MINING_REWARD, signature='')

  last_block = blockchain.chain[-1]
  previous_hash = blockchain.hash(last_block)
  block = blockchain.create_block(nonce, previous_hash)
  
  response = {
    'message': "New Block Forged",
    'block_number': block['block_number'],
    'transactions': block['transactions'],
    'nonce': block['nonce'],
    'previous_hash': block['previous_hash'],
  }
  return jsonify(response), 200

@app.route('/transaction/new', methods=['POST'])
def new_transaction():
  values = request.form 
  required = ['confirmation_sender_public_key', 'confirmation_recipient_public_key', 'confirmation_amount', 'transaction_signature']
  if not all(k in values for k in required):
    response = {'message': 'Missing values'}
    return jsonify(response), 400
  
  transaction_result = blockchain.submit_transaction(values['confirmation_sender_public_key'], values['confirmation_recipient_public_key'], values['confirmation_amount'], values['transaction_signature'])
  
  if transaction_result == False:
    response = {'message': 'Invalid transaction!'}
    return jsonify(response), 406
  else:
    response = {'message': 'Transaction will be added to block' + str(transaction_result)}
    return jsonify(response), 201




if __name__ == '__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('-p', '--port', default=5001, type=int, help='port to listen on')
  args = parser.parse_args()
  port = args.port
  
  app.run(host='127.0.0.1', port=port, debug=True)