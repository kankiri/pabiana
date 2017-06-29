import json
import logging

import zmq

interfaces = {}
subscriptions = []
subscriber_cb = None
trigger_cb = None
name = None
goon = None


def create_publisher(own_name, host=None):
	"""
	Creates and returns an optional Publishing Interface.
	"""
	ip = interfaces[own_name + '-pub']
	host = host or ip['ip']
	context = zmq.Context.instance()
	publisher = context.socket(zmq.PUB)
	publisher.bind('tcp://{}:{}'.format(host, ip['port']))
	return publisher


def trigger(area_name, trigger_name, params={}, context=zmq.Context.instance()):
	"""
	Sends a Request for a remote Trigger to a Receiver Interface.
	"""
	ip = interfaces[area_name + '-rcv']
	if type(context) is str:
		context = zmq.Context()
	requester = context.socket(zmq.PUSH)
	requester.connect('tcp://{}:{}'.format(ip['ip'], ip['port']))
	params['function'] = trigger_name
	requester.send_json(params)
	requester.close()
	logging.debug('Trigger %s of %s called', trigger_name, area_name)


def run(own_name, host=None):
	"""
	Starts a new Pabiana Area.
	Use Control-C to stop.
	"""
	global name
	name = own_name
	context = zmq.Context.instance()
	poller = zmq.Poller()
	
	# Receiver Interface
	ip = interfaces[own_name + '-rcv']
	host = host or ip['ip']
	receiver = context.socket(zmq.PULL)
	receiver.bind('tcp://{}:{}'.format(host, ip['port']))
	poller.register(receiver, zmq.POLLIN)
	logging.info('Waiting for Connections on %s:%s', host, ip['port'])
	
	# Subscription Interfaces
	subs = {}
	for item in subscriptions:
		ip = interfaces[item[0] + '-pub']
		subscriber = context.socket(zmq.SUB)
		subscriber.subscribe(item[1])
		if len(item) == 3:
			subscriber.set_hwm(item[2])
		subscriber.connect('tcp://{}:{}'.format(ip['ip'], ip['port']))
		poller.register(subscriber, zmq.POLLIN)
		subs[subscriber] = item[0]
	logging.info('Listening to %s', subscriptions)
	
	# Runner Initialization
	global goon
	goon = True
	
	# Runner
	try:
		while goon:
			socks = dict(poller.poll())
			for sock in socks:
				if sock == receiver:
					message = receiver.recv_json()
					logging.debug('Receiver Message: %s', message)
					func_name = message['function']
					del message['function']
					trigger_cb(func_name, message)
				else:
					area_nm = subs[sock]
					[topic, message] = _decoder(sock.recv_multipart())
					logging.debug('Subscriber Message from %s: %s/%s', area_nm, topic, message)
					subscriber_cb(area_nm, topic, message)
	except KeyboardInterrupt:
		pass
	finally:
		context.destroy(linger=2000)
		logging.debug('Context destroyed')


def _decoder(rcvd):
	if len(rcvd) == 1:
		rcvd = [b''] + rcvd
	# TODO: make faster
	[topic, message] = [x.decode('utf-8') for x in rcvd]
	message = json.loads(message)
	return [topic, message]
