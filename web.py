import time, hmac, hashlib, random, threading, binascii
from dnslib.server import DNSServer, RR
from flask import Flask, jsonify
from Crypto.Cipher import AES # used for WebVPN url generation

domain = '.tmptest.icu.'
salt_key = 'xxx'
salt_token = 'yyy'

keys = {}

def genkey():
	a = '%05x' % random.randint(0, 16**5 - 1)
	return a + hmac.new(salt_key.encode(), (str(int(time.time())) + a).encode(), hashlib.md5).hexdigest()[:10]

def validkey(x):
	t = int(time.time())
	for i in range(60):
		if hmac.new(salt_key.encode(), (str(t - i) + x[:5]).encode(), hashlib.md5).hexdigest()[:10] == x[5:]:
			return True
	return False

def gettoken():
	expire = int(time.time()) + 86400 # 1 day
	return hmac.new(salt_token.encode(), str(expire).encode()).hexdigest() + str(expire) # easy to check in other apps

class KeyResolver:
	def resolve(self,request,handler):
		print(request)
		qname = str(request.questions[0].qname)
		if 1 == request.questions[0].qtype and qname.endswith(domain):
			key = qname[:-len(domain)]
			if validkey(key):
				keys[key] = time.time() + 60
		reply = request.reply()
		reply.add_answer(*RR.fromZone(qname + " 60 A 1.0.0.1"))
		return reply

def key_clear():
	while True:
		popl = []
		for i in keys.copy():
			if keys[i] < time.time():
				popl.append(i)
		for i in popl:
			keys.pop(i)
		time.sleep(10)
threading.Thread(target=key_clear).start()

resolver = KeyResolver()
dnsserver = DNSServer(resolver,port=53,address="0.0.0.0")
dnsserver.start_thread()

app = Flask(__name__)

@app.route('/')
def index():
	return open('index.html').read()

@app.route('/geturl')
def geturl():
	key = genkey()
	aeskey = b'wrdvpnisthebest!'
	cipher = AES.new(aeskey, AES.MODE_CFB, iv=aeskey, segment_size=128)
	path = binascii.hexlify(aeskey + cipher.encrypt((key + domain[:-1]).encode())).decode()
	url = 'https://webvpn.tsinghua.edu.cn/https/' + path + '/'
	return jsonify({'key': key, 'url': url})

@app.route('/checkkey/<key>')
def checkkey(key):
	if key in keys:
		return jsonify({'token': gettoken()})
	return jsonify({'token': ''})

app.run(host='127.0.0.1', port=9999)
