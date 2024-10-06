from flask import Flask, render_template, jsonify
from time import time
from flask_cors import CORS

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
  

    
# Instantiate the Blockchain
blockchain = Blockchain()

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
  return render_template('./index.html')

@app.route('/transaction/new', methods=['POST'])
def new_transaction():
  response = {
    'message': 'New transaction done'
  }
  
  return jsonify(response), 201

if __name__ == '__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('-p', '--port', default=5001, type=int, help='port to listen on')
  args = parser.parse_args()
  port = args.port
  
  app.run(host='127.0.0.1', port=port, debug=True)