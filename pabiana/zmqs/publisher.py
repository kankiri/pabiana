import json

import zmq

from .. import abcs
from ..utils import rslv
from .utils import Socket


class DictPubMixin(abcs.DictPubMixin):
	def __init__(self):
		self.publisher = None
	
	def publish(self, message: dict, slot: str = None):
		if self.publisher is None:
			self.publisher = create_publisher(own_name=self.name, host=self.host, context=self.zmq)
		if slot is None:
			self.publisher.send_json(message)
		else:
			message = json.dumps(message)
			self.publisher.send_multipart([slot.encode('utf-8'), message.encode('utf-8')])


def create_publisher(own_name: str, host: str = None, context=zmq.Context.instance()) -> Socket:
	"""
	Creates and returns a Publishing Interface.
	"""
	if type(context) is str:
		context = zmq.Context()
	ip, port = rslv(own_name, 'pub')
	host = host or ip
	publisher = context.socket(zmq.PUB)
	publisher.bind('tcp://{}:{}'.format(host, port))
	return publisher
