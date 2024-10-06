from flask import Flask, render_template, jsonify, request
from time import time
from flask_cors import CORS
from collections import OrderedDict
import binascii
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA


MINING_SENDER = 'The Blockchain'

class Blockchain:
  def __init__(self):
    self.transaction = []
    self.chain = []
    # Create the genesis block
    self.create_block(0, '00')
    
  def create_block(self, nonce, previous_hash):
    """
    Add a block of transaction to the blockchain
    """
    block = {
      'block_number': len(self.chain) + 1,
      'timestamp': time(),
      'transaction': self.transaction,
      'nonce': nonce,
      'previous_hash': previous_hash
    }
    # Reset the transaction
    self.transaction = []
    self.chain.append(block)
    
  def verify_transaction_signature(self, sender_public_key, signature, transaction):
    public_key = RSA.importKey(binascii.unhexlify(sender_public_key))
    verifier = PKCS1_v1_5.new(public_key)
    hash = SHA.new(str(transaction).encode('utf8'))
    try:
      verifier.verify(hash, binascii.unhexlify(signature))
      return True
    except ValueError:
      return False
    
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
        self.transaction.append(transaction)
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