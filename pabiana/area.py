import logging
from collections import deque, Mapping

from .node import Node


class Area(Node):
	def __init__(self, name, host=None, global_interfaces=None):
		super().__init__(name, host, global_interfaces)
		self.clock_name = None
		self.clock_slot = None
		self.pulse_function = None
		self.schedule_function = Area._call
		self.time = 1
		self.context = {}
		self.parsers = {}
		self.triggers = {}
		self.demand = {}
		self.demand_loop = {}
		self.processors = {}
		self.alterations = set()
		self.alts_loop = set()
	
	def register(self, func):
		"""
		Registers this function as remote Trigger.
		"""
		self.triggers[func.__name__] = func
		return func
	
	def alteration(self, internal_func=None, area_name=None, slot=None):
		"""
		Registers this function to be called when context changes.
		"""
		def decorator(func):
			if area_name is None:
				self.processors[None] = func
			else:
				if area_name not in self.processors:
					self.processors[area_name] = {}
				self.processors[area_name][slot] = func
			return func
		
		if internal_func:
			return decorator(internal_func)
		return decorator
	
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
		def combined(*args):
			Area._call(*func(args))
		self.schedule_function = combined
		return func
	
	def clock_callback(self):
		if self.demand_loop:
			self.demand.update(self.demand_loop)
			self.demand_loop.clear()
		if self.alts_loop:
			self.alterations.update(self.alts_loop)
			self.alts_loop.clear()
		if self.demand or self.alterations:
			self.schedule_function(self.demand, self.alterations)
			self.demand.clear()
			self.alterations.clear()
		if self.pulse_function is not None:
			self.pulse_function()
		self.time += 1
	
	def subscriber_message(self, area_name, slot, message):
		if area_name == self.clock_name:  # and slot == self.clock_slot:
			logging.log(5, 'Clock Message from "%s" - "%s"', area_name, slot)
			self.clock_callback()
		else:
			try:
				self.parsers[area_name][slot](area_name, slot, message)
				if area_name in self.processors:
					if slot in self.processors[area_name]:
						self.alterations.add(self.processors[area_name][slot])
					elif None in self.processors[area_name]:
						self.alterations.add(self.processors[area_name][None])
				elif None in self.processors:
					self.alterations.add(self.processors[None])
				logging.debug('Subscriber Message from "%s" - "%s"', area_name, slot)
			except KeyError:
				logging.debug('Unsubscribed Message from "%s" - "%s"', area_name, slot)
	
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
	
	def autoloop(self, trigger_function=None, params={}, area_name=None, slot=None):
		if trigger_function is not None:
			self.demand_loop[trigger_function] = params
		elif area_name is not None:
			self.alts_loop.add(self.processors[area_name][slot])
		else:
			self.alts_loop.add(self.processors[area_name])
	
	@staticmethod
	def _call(*args):
		for functions in args:
			if isinstance(functions, Mapping):
				for func in functions:
					func(**functions[func])
			else:
				for func in functions:
					func()
