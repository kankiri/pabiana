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

step = 0
context = {}
interfaces = None

_triggers = {}
_trgs_rcvd = {}
_pulse_name = None
_pulse_topic = None
_received = False
_change_function = None
_pulse_function = None


def register(func):
	"""
	Registers this function as remote Trigger.
	"""
	_triggers[func.__name__] = func
	return func


def context_change(func):
	"""
	Registers this function to be called when context changes.
	"""
	global _change_function
	_change_function = func
	return func


def pulse(func):
	"""
	Registers this function to be called at every pulse.
	"""
	global _pulse_function
	_pulse_function = func
	return func


def _pulse_callback():
	global step
	step += 1
	for func_name in _trgs_rcvd:
		message = _trgs_rcvd[func_name]
		try:
			_triggers[func_name](**message)
		except KeyError:
			logging.warning('Unavailable Trigger called')
	_trgs_rcvd.clear()
	if _received:
		_change_function()
		global _received
		_received = False
	if _pulse_function:
		_pulse_function()


def _subscriber_callback(area_name, topic, message):
	if area_name == _pulse_name and topic == _pulse_topic:
		_pulse_callback()
	else:
		context[area_name][topic] = step
		context[area_name][topic+'-data'] = message
		global _received
		_received = True


def _trigger_callback(func_name, message):
	_trgs_rcvd[func_name] = message


def subscribe(subscriptions, pulse_name, pulse_topic):
	global _pulse_name
	global _pulse_topic
	_pulse_name = pulse_name
	_pulse_topic = pulse_topic
	for item in subscriptions:
		context[item[0]] = {}
		context[item[0]][item[1]] = None
	subscriptions.append((pulse_name, pulse_topic, 1))
	node.subscriptions = subscriptions
	node.subscriber_cb = _subscriber_callback
	node.trigger_cb = _trigger_callback


def load_interfaces(path):
	with open(path, encoding='utf-8') as f:
		global interfaces
		interfaces = json.load(f)


def rslv(interface):
	"""
	Returns a dictionary containing the ip and the port of the interface.
	"""
	return interfaces[interface]
