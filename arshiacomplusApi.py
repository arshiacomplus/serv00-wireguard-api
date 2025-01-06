from flask import Flask, request, send_file
import requests
import io
import base64
import json
import os
import datetime
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519

app = Flask(__name__)

def byte_to_base64(myb):
  return base64.b64encode(myb).decode('utf-8')
   

def generate_public_key(key_bytes):
  # Convert the private key bytes to an X25519PrivateKey object
  private_key = x25519.X25519PrivateKey.from_private_bytes(key_bytes)
  
  # Perform the scalar multiplication to get the public key
  public_key = private_key.public_key()
  
  # Serialize the public key to bytes
  public_key_bytes = public_key.public_bytes(
    encoding=serialization.Encoding.Raw,
    format=serialization.PublicFormat.Raw
  )  
  return public_key_bytes



def generate_private_key():
  key = os.urandom(32)  
  # Modify random bytes using algorithm described at:
  # https://cr.yp.to/ecdh.html.
  key = list(key) # Convert bytes to list for mutable operations
  key[0] &= 248
  key[31] &= 127
  key[31] |= 64  
  return bytes(key) # Convert list back to bytes




def register_key_on_CF(pub_key):
  url = 'https://api.cloudflareclient.com/v0a4005/reg'
  # url = 'https://api.cloudflareclient.com/v0a2158/reg'
  # url = 'https://api.cloudflareclient.com/v0a3596/reg'

  body = {"key": pub_key,
      "install_id": "",
      "fcm_token": "",
      "warp_enabled": True,
      "tos": datetime.datetime.now().isoformat()[:-3] + "+07:00",
      "type": "Android",
      "model": "PC",
      "locale": "en_US"}

  bodyString = json.dumps(body)

  headers = {'Content-Type': 'application/json; charset=UTF-8',
        'Host': 'api.cloudflareclient.com',
        'Connection': 'Keep-Alive',
        'Accept-Encoding': 'gzip',
        'User-Agent': 'okhttp/3.12.1',
        "CF-Client-Version": "a-6.30-3596"
        }

  r = requests.post(url, data=bodyString, headers=headers,timeout=10)
  return r
def bind_keys():
  priv_bytes = generate_private_key()
  priv_string = byte_to_base64(priv_bytes)
  
  
  reserved="nothin"
  
  pub_bytes = generate_public_key(priv_bytes)
  pub_string = byte_to_base64(pub_bytes)
  
  



  result = register_key_on_CF(pub_string)

  b=""

  z = json.loads(result.content)
  client_id = z['config']["client_id"]   
  cid_byte = base64.b64decode(client_id)
  reserved = [int(j) for j in cid_byte]
  for i in reserved:
    b+=str(i)+" "
  print(priv_string)

  
  

  return  "address: "+'2606:4700:110:846c:e510:bfa1:ea9f:5247/128\n'+"private_key: "+priv_string+"\n"+"reserved: "+b+"\n"+ "public_key: "+'bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=' +"\n"
def get_key():
  data = bind_keys() 

  
  

  # Create a file-like object for binary data
  file_like_object = io.BytesIO(data.encode('utf-8')) 
  return send_file(
    file_like_object,
    mimetype='text/plain',
    as_attachment=True,
    download_name='weather_data.txt'
  )

@app.route("/arshiacomplus/api/wirekey")
def replace1():
	get_key()
@app.route("/")
def replace():
	get_key()

if __name__ == '__main__':
 app.run(debug=True,host="",port=0)
 
#created by arshiacomplus
