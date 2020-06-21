import time, hmac, hashlib, random, threading
from dnslib.server import DNSServer, RR
from flask import Flask, jsonify

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
		qname = str(request.questions[0].qname)
		if 16 == request.questions[0].qtype and qname.endswith(domain):
			key = qname[:-len(domain)]
			if validkey(key):
				keys[key] = time.time() + 60
		reply = request.reply()
		reply.add_answer(*RR.fromZone(qname + " 60 TXT ok"))
		return reply

def key_clear():
	while True:
		for i in keys:
			if keys[i] < time.time():
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

@app.route('/getkey')
def getkey():
	return jsonify({'key': genkey()})

@app.route('/checkkey/<key>')
def checkkey(key):
	if key in keys:
		return jsonify({'token': gettoken()})
	return jsonify({'token': ''})

app.run(host='127.0.0.1', port=9999)
