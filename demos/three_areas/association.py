#!/usr/bin/env python3

from datetime import datetime
import logging
import time

from pabiana import area
from pabiana.area import register, run, subscribe, timeout, trigger

NAME = 'association'
context = {
	'to-bed': None,
	'at-home': None,
	'window-open': None,
	'in-temp': None,
	'out-temp': 'good',
	'sh-procedure': None
}


# Triggers
@register
def shutdown():
	area.goon = False


# Reactions
@subscribe
def getter(current):
	context['out-temp'] = current


@subscribe
def console_input(signal):
	if signal == 'sleep':
		context['to-bed'] = True
		context['at-home'] = True
	elif signal == 'awake':
		context['to-bed'] = False
	elif signal == 'home':
		context['at-home'] = True
	elif signal == 'away':
		context['at-home'] = False
		context['to-bed'] = False
	elif signal == 'update':
		context['in-temp'] = None
		context['out-temp'] = None


@subscribe
def smarthome(temperature, open, procedure):
	context['in-temp'] = temperature
	context['window-open'] = open
	context['sh-procedure'] = procedure


@timeout
def update():
	if context['in-temp'] is None:
		trigger('smarthome', 'keep_temp')
		return
	if context['out-temp'] is None:
		trigger('getter', 'pulse')
		return
	if context['window-open']:
		if context['to-bed'] or not context['at-home'] or not morning():
			trigger('smarthome', 'window', {'open':False})
			return
	else:
		if context['at-home'] and not context['to-bed'] and morning():
			trigger('smarthome', 'window', {'open':True})
			return
	if context['window-open'] or not context['at-home']:
		if context['in-temp'] < temp_range(context['out-temp'])[0]:
			trigger('smarthome', 'increase_temp')
		elif context['in-temp'] > temp_range(context['out-temp'])[1]:
			trigger('smarthome', 'lower_temp')
		elif context['sh-procedure']:
			trigger('smarthome', 'keep_temp')
	if context['at-home'] and not context['window-open']:
		if context['in-temp'] < 21:
			trigger('smarthome', 'increase_temp')
		elif context['in-temp'] > 23:
			trigger('smarthome', 'lower_temp')
		elif context['sh-procedure']:
			trigger('smarthome', 'keep_temp')
	
	time.sleep(5)  # delay for debugging


def morning():
	return datetime.now().hour < 12


def temp_range(name):
	if name == 'ice':
		return -100, 0
	elif name == 'cold':
		return 0, 15
	elif name == 'good':
		return 15, 25
	elif name == 'hot':
		return 25, 32
	else:
		return 32, 100


if __name__ == '__main__':
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.DEBUG
	)
	
	run(own_name=NAME, host='0.0.0.0')