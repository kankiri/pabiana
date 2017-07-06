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

from pabiana import node

clock = 1
demand = {}
loop = {}
context = {}

_triggers = {}
_pulse_name = None
_pulse_slot = None
_received = False
_alt_function = None
_pulse_function = None


def register(func):
	"""
	Registers this function as remote Trigger.
	"""
	_triggers[func.__name__] = func
	return func


def alteration(func):
	"""
	Registers this function to be called when context changes.
	"""
	global _alt_function
	_alt_function = func
	return func


def pulse(func):
	"""
	Registers this function to be called at every pulse.
	"""
	global _pulse_function
	_pulse_function = func
	return func


def scheduling(func):
	"""
	Registers this function to be called directly before call_triggers.
	"""
	global call_triggers
	old = call_triggers
	
	def schedule():
		func()
		old()
	
	call_triggers = schedule
	return func


def call_triggers():
	"""
	Calls every trigger from demand and loop with their stored parameters.
	"""
	if loop:
		demand.update(loop)
	for func in demand:
		try:
			func(**demand[func])
		except TypeError:
			logging.warning('Trigger Parameter Error')


def _pulse_callback():
	global clock
	global _received
	if loop or demand:
		call_triggers()
		loop.clear()
		demand.clear()
	if _received and _alt_function:
		_received = False
		_alt_function()
	if _pulse_function:
		_pulse_function()
	clock += 1


def _subscriber_callback(area_name, slot, message):
	if area_name == _pulse_name and slot == _pulse_slot:
		_pulse_callback()
	else:
		try:
			area_dict = context[area_name]
			area_dict[slot]  # test for subscription
			area_dict[slot] = clock
			area_dict[slot + '-data'].update(message)
		except KeyError:
			if area_name not in context or slot not in area_dict:
				logging.warning('Message from Slot not subscribed')
				return
			area_dict[slot + '-data'] = message
		global _received
		_received = True


def _trigger_callback(func_name, message):
	try:
		func = _triggers[func_name]
		demand[func] = message
	except KeyError:
		if func_name == 'exit':
			node.goon = False
			return
		logging.warning('Unavailable Trigger called')


def subscribe(subscriptions, clock_name, clock_slot):
	global _pulse_name
	global _pulse_slot
	_pulse_name = clock_name
	_pulse_slot = clock_slot
	for item in subscriptions:
		context[item[0]] = {}
		context[item[0]][item[1]] = None
	subscriptions.append((clock_name, clock_slot, 1))
	node.subscriptions = subscriptions
	node.subscriber_cb = _subscriber_callback
	node.trigger_cb = _trigger_callback


def autoloop(func=None, params={}):
	if func:
		loop[func] = params
	else:
		global _received
		_received = True


def load_interfaces(path):
	with open(path, encoding='utf-8') as f:
		node.interfaces = json.load(f)


def rslv(interface):
	"""
	Returns a dictionary containing the ip and the port of the interface.
	"""
	return node.interfaces[interface]
