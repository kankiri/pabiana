import json
import logging
from typing import Any, Callable, Dict, Optional, Sequence, Set

import zmq

from .extensions import Publisher, Trigger
from .node import Node
from .parsers import init_full, imprint_full
from .utils import caller
from .. import abcs
from ..utils import Interfaces


class Area(abcs.Area, Node, Publisher, Trigger):
	"""Class that implements the Pabiana Area interface based on the ZMQ Node class.

	A ZMQ Pabiana Area can provide one Puller (as Receiver) and multiple Subscriber Interfaces.
	Other ZMQ Pabiana Areas could Push Triggers on and Publish messages to these Interfaces.
	"""
	def __init__(self, name: str, interfaces: Interfaces):
		super().__init__(name, interfaces)
		self._pulse_function = None
		self._schedule_function = caller
		self._triggers = {}  # type: Dict[str, Callable]
		self._processors = {}  # type: Dict[Optional[str], Dict[Optional[str], Callable]]
		self._demand = {}  # type: Dict[Callable, Dict[str, Any]]
		self._demand_loop = {}  # type: Dict[Callable, Dict[str, Any]]
		self._alterations = set()  # type: Set[Callable]
		self._alts_loop = set()  # type: Set[Callable]
		
		self._triggers['exit'] = self.stop
	
	def scheduling(self, func: Callable) -> Callable:
		def combined(*args):
			caller(*func(args))
		self._schedule_function = combined
		return func
	
	def subscribe(self, clock_name: str, clock_slot: str=None, subscriptions: Dict[str, Any]={}):
		self.clock_name = clock_name
		self.clock_slot = clock_slot
		
		for area in subscriptions:  # type: str
			init_full(self, area, subscriptions[area])
			subscriptions[area] = {'slots': subscriptions[area]}
		
		subscriptions[clock_name] = {'slots': clock_slot and [clock_slot], 'buffer-length': 1}
		super().setup(puller=True, subscriptions=subscriptions)
	
	def _process(self, interface: int, message: Sequence[str], source: str=None):
		if interface == zmq.PULL:
			message = json.loads(message[0])
			trigger_name = message['trigger']
			del message['trigger']
			self.comply(trigger_name, message)
		else:
			if source == self.clock_name:
				logging.log(5, 'Tick')
				self.proceed()
			else:
				slot = message[0]
				message = json.loads(message[1])
				self.process(source, message, slot)
	
	# ------------- Trigger processing functions -------------
	
	def register(self, func: Callable) -> Callable:
		self._triggers[func.__name__] = func
		return func
	
	def comply(self, trigger: str, parameters: Dict[str, Any]={}):
		try:
			logging.debug('Trigger call: "%s"', trigger)
			func = self._triggers[trigger]
			self._demand[func] = parameters
		except KeyError:
			logging.warning('Unavailable Trigger called')
		
	def autoloop(self, trigger: str, parameters: Dict[str, Any]={}):
		func = self._triggers[trigger]
		self._demand_loop[func] = parameters
	
	# ------------- Message processing functions -------------
	
	def alteration(self, func: Callable=None, source: str=None, slot: str=None) -> Callable:
		def decorator(internal_func):
			if source not in self._processors:
				self._processors[source] = {}
			self._processors[source][slot] = internal_func
			return func
		if func:
			return decorator(func)
		return decorator
	
	def process(self, source: str, message: Dict, slot: str=None):
		try:
			imprint_full(self, source, message, slot)
			if source in self._processors:
				if slot in self._processors[source]:
					self._alterations.add(self._processors[source][slot])
				elif None in self._processors[source]:
					self._alterations.add(self._processors[source][None])
			elif None in self._processors:
				self._alterations.add(self._processors[None][None])
			logging.debug('Subscriber Message from "%s" - "%s"', source, slot)
		except KeyError:
			logging.debug('Unsubscribed Message from "%s" - "%s"', source, slot)
		
	def alter(self, source: str=None, slot: str=None):
		self._alts_loop.add(self._processors[source][slot])
	
	# ------------- Clock processing functions -------------
	
	def pulse(self, func: Callable) -> Callable:
		self._pulse_function = func
		return func
	
	def proceed(self):
		if self._demand_loop:
			self._demand.update(self._demand_loop)
			self._demand_loop.clear()
		if self._alts_loop:
			self._alterations.update(self._alts_loop)
			self._alts_loop.clear()
		if self._demand or self._alterations:
			self._schedule_function(self._demand, self._alterations)
			self._demand.clear()
			self._alterations.clear()
		if self._pulse_function is not None:
			self._pulse_function()
		self.time += 1
