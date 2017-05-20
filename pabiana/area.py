"""
Use this module to start a new Pabiana Area.
Each Area is initialized with a Receiver Interface.
The Receiver Interface accepts Requests for remote Triggers.
Subscription Interfaces are created as defined.
Subscription Interfaces call defined Reactions.
The Area name must not contain "_" characters.
A Publishing Interface can be added optionally.
"""

import json
import logging
import os
import sys
from threading import Thread
import time

import zmq

config = {}
_cbks = {}
_trgs = {}
goon = True


def rslv(interface):
	"""
	Returns a dictionary containing the ip and the port of the interface.
	"""
	with open(config['ifs-path'], encoding='utf-8') as f:
		ifs = json.load(f)
	return ifs[interface]


def register(func):
	"""
	Registers this function as remote Trigger.
	"""
	_trgs[func.__name__] = func
	return func


def reg_name(name):
	"""
	Registers this function as remote Trigger with the specified name.
	"""
	def decorator(func):
		_trgs[name] = func
		return func
	return decorator


def split_func_name(name):
	pos = name.find('_')
	if pos == -1:
		pos = len(name)
	area_name = name[:pos]
	topic = name[pos + 1:]
	topic = topic.replace('_', '.')
	topic = topic.replace('𒐀', '-')
	return area_name, topic


def subscribe(func):
	"""
	Registers this function as a Reaction to a Subscription.

	The area name must be separated from the topic through a "_" character.
	Within the topic, "_" characters are replaced with topic separators ("." characters).
	Within the topic, "𒐀" characters are replaced with "-" characters.
	"""
	area_name, topic = split_func_name(func.__name__)
	_cbks[area_name] = {}
	_cbks[area_name][topic] = func
	return func


def sub_name(name, topic):
	"""
	Registers this function as a Reaction to a Subscription with the specified Area name and topic.
	"""
	def decorator(func):
		_cbks[name] = {}
		_cbks[name][topic] = func
		return func
	return decorator


# TODO: Add functions to subscribe/unsubscribe


def _decoder(rcvd):
	if len(rcvd) == 1:
		rcvd = [''] + rcvd
	[topic, message] = [x.decode('utf-8') for x in rcvd]
	message = json.loads(message)
	return [topic, message]


def run(own_name, host=None):
	"""
	Starts a new Pabiana Area.
	Use Control-C to stop.
	"""
	config['name'] = own_name
	context = zmq.Context.instance()
	poller = zmq.Poller()
	
	# Receiver Interface
	ip = rslv(own_name + '-rcv')
	host = host or ip['ip']
	receiver = context.socket(zmq.REP)
	receiver.bind('tcp://{}:{}'.format(host, ip['port']))
	poller.register(receiver, zmq.POLLIN)
	logging.info('Waiting for Connections on %s:%s', host, ip['port'])
	
	# Subscription Interfaces
	subs = {}
	for area_nm in _cbks:
		ip = rslv(area_nm + '-pub')
		subscriber = context.socket(zmq.SUB)
		subscriber.connect('tcp://{}:{}'.format(ip['ip'], ip['port']))
		for topic in _cbks[area_nm]:
			subscriber.setsockopt(zmq.SUBSCRIBE, topic.encode('utf-8'))
		poller.register(subscriber, zmq.POLLIN)
		subs[subscriber] = area_nm
	logging.info('Listening to %s', list(_cbks))
	
	try:
		while goon:  # TODO: What happens if > 1 messages
			socks = dict(poller.poll(1000))
			for sock in socks:
				if sock == receiver:
					message = receiver.recv_json()
					logging.debug('Receiver Message: %s', message)
					receiver.send(b'')
					func_name = message['function']
					del message['function']
					try:
						_trgs[func_name](**message)
					except KeyError:
						logging.warning('Unavailable Trigger called')
				else:
					area_nm = subs[sock]
					[topic, message] = _decoder(sock.recv_multipart())
					logging.debug('Subscriber Message from %s: %s/%s', area_nm, topic, message)
					key = next(key for key in _cbks[area_nm] if topic.startswith(key))
					_cbks[area_nm][key](**message)
	except KeyboardInterrupt:
		pass
	finally:
		context.destroy()
		logging.debug('Context destroyed')


def create_publisher(own_name, host=None):
	"""
	Creates and returns an optional Publishing Interface.
	"""
	ip = rslv(own_name + '-pub')
	host = host or ip['ip']
	context = zmq.Context.instance()
	publisher = context.socket(zmq.PUB)
	publisher.bind('tcp://{}:{}'.format(host, ip['port']))
	return publisher


def trigger(area_name, trigger_name, params={}, context=None):
	"""
	Sends a Request for a remote Trigger to a Receiver Interface.
	"""
	ip = rslv(area_name + '-rcv')
	context = context or zmq.Context.instance()
	requester = context.socket(zmq.REQ)
	requester.connect('tcp://{}:{}'.format(ip['ip'], ip['port']))
	params['function'] = trigger_name
	requester.send_json(params)
	requester.recv()
	requester.close()


def _timer(seconds):
	time.sleep(seconds)
	trigger(config['name'], 'timer', context=zmq.Context())


def set_timer(seconds):
	"""
	Sends a Request to the 'timer'-Trigger of this Area, after the specified number of seconds.
	"""
	Thread(target=_timer, args=(seconds,), daemon=True).start()


def __init():
	config['name'] = None
	if sys.argv[0]:
		config['main-path'] = os.path.dirname(os.path.realpath(sys.argv[0]))
		config['global-path'] = os.path.dirname(config['main-path'])
	else:
		config['main-path'] = os.getcwd()
		config['global-path'] = config['main-path']
	config['ifs-path'] = os.path.join(config['main-path'], 'interfaces.json')
	if not os.path.isfile(config['ifs-path']):
		config['ifs-path'] = os.path.join(config['global-path'], 'interfaces.json')

__init()
