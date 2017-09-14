"""
Use this module to start a new Pabiana Node.
Each Node is initialized with a Receiver Interface.
The Receiver Interface accepts Requests for Remote Triggers.
Subscription Interfaces are created as defined.
Subscription Interfaces call defined Reactions.
This module also provides functions to call a Remote Trigger and to create Publishing Interfaces.
"""


import json
import logging
import os
import signal

import zmq

interfaces = None


class Node:
	def __init__(self, name, host=None, global_interfaces=None):
		self.name = name
		self.host = host
		self.goon = None
		self.receiver = None
		self.receiver_callback = None
		self.subscribers = None
		self.subscriber_callback = None
		self.publisher = None
		self.timeout_callback = None
		self.zmq = zmq.Context.instance()
		self.poller = zmq.Poller()
		
		if global_interfaces is not None:
			load_interfaces(global_interfaces)
	
	def rslv(self, interface):
		return rslv('{}-{}'.format(self.name, interface))
	
	def setup_receiver(self, receiver_callback):
		self.receiver = self.zmq.socket(zmq.PULL)
		host = self.host or self.rslv('rcv')['ip']
		self.receiver.bind('tcp://{}:{}'.format(host, self.rslv('rcv')['port']))
		self.poller.register(self.receiver, zmq.POLLIN)
		self.receiver_callback = receiver_callback
		logging.info('Waiting for Connections on %s:%s', host, self.rslv('rcv')['port'])
	
	def setup_subscribers(self, subscriptions, subscriber_callback):
		self.subscribers = {}
		for pub_name in subscriptions:
			address = interfaces[pub_name + '-pub']
			subscriber = self.zmq.socket(zmq.SUB)
			for topic in subscriptions[pub_name]['topics']:
				subscriber.subscribe(topic)
			if 'buffer-length' in subscriptions[pub_name]:
				subscriber.set_hwm(subscriptions[pub_name]['buffer-length'])
			subscriber.connect('tcp://{}:{}'.format(address['ip'], address['port']))
			self.poller.register(subscriber, zmq.POLLIN)
			self.subscribers[subscriber] = pub_name
		self.subscriber_callback = subscriber_callback
		logging.info('Listening to %s', subscriptions.keys())
	
	def publish(self, message, slot=None):
		"""
		Publishes the given message from the optional slot.
		"""
		if self.publisher is None:
			self.publisher = create_publisher(own_name=self.name, host=self.host)
		if slot is None:
			self.publisher.send_json(message)
		else:
			message = json.dumps(message)
			self.publisher.send_multipart([slot.encode('utf-8'), message.encode('utf-8')])
	
	def run(self, timeout=1000):
		self.goon = True
		signal.signal(signal.SIGINT, self.stop)
		try:
			while self.goon:
				socks = self.poller.poll(timeout)
				for sock, event in socks:
					if sock is self.receiver:
						message = self.receiver.recv_json()
						logging.debug('Receiver Message: %s', message)
						func_name = message['function']
						del message['function']
						self.receiver_callback(func_name, message)
					else:
						pub_name = self.subscribers[sock]
						[topic, message] = Node.decoder(sock.recv_multipart())
						logging.debug('Subscriber Message: %s:%s', pub_name, topic)
						self.subscriber_callback(pub_name, topic, message)
				if self.timeout_callback is not None:
					self.timeout_callback()
		finally:
			self.zmq.destroy(linger=2000)
			logging.debug('Context destroyed')
	
	def stop(self, *args, **kwargs):
		self.goon = False
	
	@staticmethod
	def decoder(rcvd):
		if len(rcvd) == 1:
			rcvd = [b''] + rcvd
		# TODO: make faster
		[topic, message] = [x.decode('utf-8') for x in rcvd]
		message = json.loads(message)
		return [topic, message]


def trigger(rcv_name, trigger_name, params={}, context=zmq.Context.instance()):
	"""
	Sends a Request for a Remote Trigger to a Receiver Interface.
	"""
	address = interfaces[rcv_name + '-rcv']
	if type(context) is str:
		context = zmq.Context()
	requester = context.socket(zmq.PUSH)
	requester.connect('tcp://{}:{}'.format(address['ip'], address['port']))
	params['function'] = trigger_name
	requester.send_json(params)
	requester.close()
	logging.debug('Trigger %s of %s called', trigger_name, rcv_name)


def create_publisher(own_name, host=None):
	"""
	Creates and returns a Publishing Interface.
	"""
	address = interfaces[own_name + '-pub']
	host = host or address['ip']
	context = zmq.Context.instance()
	publisher = context.socket(zmq.PUB)
	publisher.bind('tcp://{}:{}'.format(host, address['port']))
	return publisher	


def load_interfaces(path_or_dict):
	global interfaces
	if type(path_or_dict) is dict:
		interfaces = path_or_dict
	else:
		with open(path_or_dict, encoding='utf-8') as f:
			interfaces = json.load(f)


def rslv(interface_name):
	"""
	Returns a dictionary containing the ip and the port of the interface.
	"""
	return interfaces[interface_name]
