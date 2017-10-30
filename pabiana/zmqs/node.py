import logging
import signal
from abc import abstractmethod
from typing import Any, Dict, Iterable, Sequence

import zmq

from .utils import Context, decoder, Poller, Socket
from .. import abcs
from ..utils import Interfaces


class Node(abcs.Node):
	"""Abstract class that implements the Pabiana Node interface based on the ZMQ library.

	A ZMQ Pabiana Node can provide one Puller and multiple Subscriber Interfaces.
	Other ZMQ Pabiana Nodes could Push and Publish messages to these Interfaces.
	"""
	def __init__(self, name: str, interfaces: Interfaces):
		super().__init__(name, interfaces)
		self._goon = None  # type: bool
		self._zmq = zmq.Context.instance()  # type: Context
		self._poller = zmq.Poller()  # type: Poller
		
		self._puller = None  # type: Socket
		self._subscribers = {}  # type: Dict[Socket, str]
	
	def _setup(self, puller: Socket=None, subscribers: Iterable[Socket]=[]):
		if puller is not None:
			self._poller.register(puller, zmq.POLLIN)
		for subscriber in subscribers:
			self._poller.register(subscriber, zmq.POLLIN)
	
	def setup(self, puller: bool=None, subscriptions: Dict[str, Any]={}):
		"""Sets up this Node with the specified Interfaces before it is run.

		Args:
			puller: Indication if a Puller Interface should be created.
			subscriptions: Collection of the Subscriber Interfaces to be created and their Slots.
		"""
		if puller:
			self._puller = self._zmq.socket(zmq.PULL)
			ip, port, host = self.rslv('rcv')
			self._puller.bind('tcp://{}:{}'.format(host or ip, port))
		if subscriptions:
			for publisher in subscriptions:  # type: str
				subscriber = self._zmq.socket(zmq.SUB)  # type: Socket
				if subscriptions[publisher]['slots'] is None:
					subscriber.subscribe('')
				else:
					for slot in subscriptions[publisher]['slots']:  # type: str
						subscriber.subscribe(slot)
				if 'buffer-length' in subscriptions[publisher]:
					subscriber.set_hwm(subscriptions[publisher]['buffer-length'])
				ip, port, host = self.rslv(name=publisher, interface='pub')
				subscriber.connect('tcp://{}:{}'.format(ip, port))
				self._subscribers[subscriber] = publisher
		self._setup(self._puller, self._subscribers)
	
	@abstractmethod
	def _process(self, interface: int, message: Sequence[str], source: str=None):
		pass
	
	def run(self, timeout: int=1000, linger: int=1000):
		self._goon = True
		signal.signal(signal.SIGINT, self.stop)
		try:
			while self._goon:
				socks = self._poller.poll(timeout)
				for sock, event in socks:
						self._process(sock.socket_type, decoder(sock.recv_multipart()), self._subscribers.get(sock))
		finally:
			self._zmq.destroy(linger=linger)
			logging.debug('Context destroyed')
			logging.shutdown()
	
	def stop(self, *args, **kwargs):
		self._goon = False
