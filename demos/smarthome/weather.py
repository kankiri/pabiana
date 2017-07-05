#!/usr/bin/env python3

import json
import logging

from pabiana import area
from pabiana.area import load_interfaces, pulse, scheduling, subscribe
from pabiana.node import create_publisher, run

NAME = 'weather'
publisher = None


# Reactions
@scheduling
def schedule():
	if keep_temp in area.demand:
		area.demand.pop(increase_temp, None)
		area.demand.pop(lower_temp, None)
	elif lower_temp in area.demand:
		area.demand.pop(increase_temp, None)


@pulse
def publish():
	if area.clock % 8 == 0:
		publisher.send_json({
			'temperature': area.context['temperature'],
			'humidity': area.context['humidity']
		})


if __name__ == '__main__':
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.DEBUG
	)
	
	load_interfaces('interfaces.json')
	subscribe([], 'pulse', '01')
	publisher = create_publisher(own_name=NAME, host='0.0.0.0')
	area.context['temperature'] = 5
	area.context['humidity'] = 40
	
	run(own_name=NAME, host='0.0.0.0')
