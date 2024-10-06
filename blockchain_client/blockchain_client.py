from flask import Flask, render_template, jsonify
import Crypto 
import Crypto.Random
from Crypto.PublicKey import RSA
import binascii

class Transaction:
  def __init__(self, sender_address, sender_private_key, recipient_address, value):
    self.sender_address = sender_address
    self.sender_private_key = sender_private_key
    self.recipient_address = recipient_address
    self.value = value
    

app = Flask(__name__)

@app.route('/')
def index():
  return render_template('./index.html')

@app.route('/make/transaction')
def make_transaction():
  return render_template('./make_transaction.html')

@app.route('/view/transactions') 
def view_transactions():
  return render_template('./view_transaction.html')


@app.route('/wallet/new')
def new_wallet():
  random_gen = Crypto.Random.new().read
  private_key = RSA.generate(1024, random_gen)
  public_key = private_key.publickey()
  
  private_key_hex = binascii.hexlify(private_key.export_key(format='DER')).decode('ascii')
  public_key_hex = binascii.hexlify(public_key.export_key(format='DER')).decode('ascii')
  response = {
    'private_key': private_key_hex,
    'public_key': public_key_hex
  }

  return jsonify(response), 200


if __name__ == '__main__':
  from argparse import ArgumentParser
  parser = ArgumentParser()
  parser.add_argument('-p', '--port', default=8081, type=int, help='port to listen on')
  args = parser.parse_args()
  port = args.port
  
  app.run(host='127.0.0.1', port=port, debug=True)