import logging
from collections import deque

from .node import Node


class Area(Node):
	def __init__(self, name, host=None, global_interfaces=None):
		super().__init__(name, host, global_interfaces)
		self.clock_name = None
		self.clock_slot = None
		self.received = None
		self.alt_function = None
		self.pulse_function = None
		self.time = 1
		self.demand = {}
		self.loop = {}
		self.alt_functions = {}
		self.context = {}
		self.triggers = {}
		self.parsers = {}
		self.alterations = set()
	
	def register(self, func):
		"""
		Registers this function as remote Trigger.
		"""
		self.triggers[func.__name__] = func
		return func
	
	def alteration(self, internal_func=None, area_name=None, slot=''):
		"""
		Registers this function to be called when context changes.
		"""
		def decorator1(func):
			self.alt_function = func
			return func
		
		def decorator2(func):
			if area_name not in self.alt_functions:
				self.alt_functions[area_name] = {}
			self.alt_functions[area_name][slot] = func
			return func
		
		if internal_func:
			return decorator1(internal_func)
		return decorator2
	
	def pulse(self, func):
		"""
		Registers this function to be called at every pulse.
		"""
		self.pulse_function = func
		return func
	
	def scheduling(self, func):
		"""
		Registers this function to be called directly before call_triggers.
		"""
		old = self.call_triggers
		
		def schedule():
			func(); old()
			
		self.call_triggers = schedule
		return func
	
	def call_triggers(self):
		if self.loop:
			self.demand.update(self.loop)
			self.loop.clear()
		for func in self.demand:
			try:
				func(**self.demand[func])
			except TypeError:
				logging.warning('Trigger Parameter Error')
		self.demand.clear()
	
	def clock_callback(self):
		if self.loop or self.demand:
			self.call_triggers()
		if self.received:
			self.received = False
			if self.alt_function is not None:
				self.alt_function()
			if self.alterations:
				for func in self.alterations:
					func()
		if self.pulse_function is not None:
			self.pulse_function()
		self.time += 1
	
	def subscriber_message(self, area_name, slot, message):
		if area_name == self.clock_name:  # and slot == self.clock_slot:
			logging.log(5, 'Clock Message from "%s" - "%s"', area_name, slot)
			self.clock_callback()
		try:
			self.parsers[area_name][slot](area_name, slot, message)
			if area_name in self.alt_functions and slot in self.alt_functions[area_name]:
				self.alterations.add(self.alt_functions[area_name][slot])
			self.received = True
			logging.debug('Subscriber Message from "%s" - "%s"', area_name, slot)
		except KeyError:
			logging.warning('Unsubscribed Message from "%s" - "%s"', area_name, slot)
	
	def receiver_message(self, func_name, message):
		try:
			logging.debug('Receiver Message "%s": "%s"', func_name, message)
			func = self.triggers[func_name]
			self.demand[func] = message
		except KeyError:
			if func_name == 'exit':
				self.goon = False
				return
			logging.warning('Unavailable Trigger called')
	
	def imprint(self, area_name, slot, message):
		self.context[area_name][slot].appendleft(message)
		self.context[area_name][slot][0]['time-rcvd'] = self.time
	
	def init_slot(self, area_name, slot):
		self.context[area_name][slot] = deque(maxlen=100)
	
	def setup(self, clock_name, clock_slot='', subscriptions={}):
		self.clock_name = clock_name
		self.clock_slot = clock_slot
		node_subs = {}
		
		for area_name in subscriptions:
			self.context[area_name] = {}
			self.parsers[area_name] = {}
			node_subs[area_name] = {'topics': set()}
			for slot in set(subscriptions[area_name]):
				if type(slot) is not str:
					raise ValueError
				try:
					self.parsers[area_name][slot] = subscriptions[area_name][slot]['parser']
					subscriptions[area_name][slot]['init'](area_name, slot)
				except (TypeError, KeyError):
					self.parsers[area_name][slot] = self.imprint
					self.init_slot(area_name, slot)
				node_subs[area_name]['topics'].add(slot)
		
		node_subs[clock_name] = {'topics': {clock_slot}, 'buffer-length': 1}
		self.setup_receiver(self.receiver_message)
		self.setup_subscribers(node_subs, self.subscriber_message)
	
	def autoloop(self, func=None, params={}):
		if func is not None:
			self.loop[func] = params
		else:
			self.received = True
			# TODO: autoloop from trigger problem
