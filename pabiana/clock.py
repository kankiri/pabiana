import logging
from .node import Node

EMPTY = {}


class Clock(Node):
	def __init__(self, name, host=None):
		super().__init__(name, host)
		self.timeout = None
		self.time = 1
	
	def pulse(self, func):
		"""
		"""
		self.timeout_callback = func
		return func
	
	def receiver_message(self, func_name, message):
		if func_name == 'exit':
			self.goon = False
			return
		logging.warning('Unavailable Trigger called: %s', func_name)
	
	def setup(self, timeout=1000, use_template=False):
		self.timeout = timeout
		if use_template:
			self.timeout_callback = self.template
		self.setup_receiver(self.receiver_message)
	
	def run(self):
		super().run(self.timeout)
	
	def template(self):
		if self.time % 32 == 0:
			self.publish(EMPTY, slot='#####')
		elif self.time % 16 == 0:
			self.publish(EMPTY, slot='####')
		elif self.time % 8 == 0:
			self.publish(EMPTY, slot='###')
		elif self.time % 4 == 0:
			self.publish(EMPTY, slot='##')
		elif self.time % 2 == 0:
			self.publish(EMPTY, slot='#')
		else:
			self.publish(EMPTY)
		self.time += 1

