import json
import logging
from typing import Any, Dict

import zmq

from .node import Node
from .utils import Socket
from .. import abcs
from ..utils import Interfaces


class Publisher(abcs.Publisher, Node):
	def __init__(self, name: str, interfaces: Interfaces):
		super().__init__(name, interfaces)
		self._publisher = None  # type: Socket
	
	def publish(self, message: dict, slot: str=None):
		if self._publisher is None:
			ip, port, host = self.rslv('pub')
			self._publisher = self._zmq.socket(zmq.PUB)
			self._publisher.bind('tcp://{}:{}'.format(host or ip, port))
		message = json.dumps(message)
		self._publisher.send_multipart([(slot or '').encode('utf-8'), message.encode('utf-8')])
		logging.debug('Message published at "%s"', slot)


class Trigger(abcs.Trigger, Node):
	def trigger(self, target: str, trigger: str, parameters: Dict[str, Any]={}):
		ip, port, host = self.rslv(name=target, interface='rcv')
		pusher = self._zmq.socket(zmq.PUSH)  # type: Socket
		pusher.connect('tcp://{}:{}'.format(ip, port))
		parameters['trigger'] = trigger
		pusher.send_json(parameters)
		pusher.close()
		logging.debug('Trigger "%s" of "%s" called', trigger, target)
