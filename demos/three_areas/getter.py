#!/usr/bin/env python3

import json
import logging
from threading import Thread
import time

from pabiana import area
from pabiana.area import create_publisher, register, run, subscribe, trigger

NAME = 'getter'
publisher = None


# Triggers
@register
def timer(seconds):
	def _timer():
		time.sleep(seconds)
		trigger(NAME, 'timer', {'seconds':seconds}, context='new')
	Thread(target=_timer, daemon=True).start()


@register
def status():
	pass


@register
def shutdown():
	area.goon = False


# Reactions
@subscribe
def internal_update():
	temp = 5
	if temp < 0:
		data = {'current': 'ice'}
	elif temp < 15:
		data = {'current': 'cold'}
	elif temp < 25:
		data = {'current': 'good'}
	elif temp < 32:
		data = {'current': 'hot'}
	else:
		data = {'current': 'fire'}
	publisher.send_multipart(['temperature'.encode('utf-8'), json.dumps(data).encode('utf-8')])


if __name__ == '__main__':
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.DEBUG
	)
	
	timer(60)
	publisher = create_publisher(own_name=NAME, host='0.0.0.0')
	run(own_name=NAME, host='0.0.0.0')