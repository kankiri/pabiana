#!/usr/bin/env python3

import logging
import time

from pabiana import area
from pabiana.area import create_publisher, register, run, timeout

NAME = 'smarthome'
publisher = None
context = {
	'temp': 25,
	'window': False,
	'procedure': 0
}


# Triggers
@register
def increase_temp():
	context['procedure'] = 1


@register
def lower_temp():
	context['procedure'] = -1


@register
def keep_temp():
	context['procedure'] = 0


@register
def window(open):
	if context['window'] != open:
		time.sleep(5)
		context['window'] = open
	if open:
		logging.info('Window was opened')
	else:
		logging.info('Window was closed')


@register
def shutdown():
	area.goon = False


@timeout
def update():
	context['temp'] = context['temp'] + context['procedure']
	if context['procedure']:
		logging.info('Home Temperature: %s', context['temp'])
	publisher.send_json({'temperature': context['temp'], 'open': context['window'], 'procedure': context['procedure']})


if __name__ == '__main__':
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.DEBUG
	)
	
	publisher = create_publisher(own_name=NAME, host='0.0.0.0')
	run(own_name=NAME, host='0.0.0.0', timeout_ms=60000)