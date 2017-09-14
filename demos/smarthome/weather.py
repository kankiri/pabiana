#!/usr/bin/env python3

import json
import logging

from pabiana import Area, load_interfaces

NAME = 'weather'
area = Area(NAME, host='0.0.0.0')


@area.pulse
def publish():
	if area.time % 8 == 0:
		area.publish({
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
	area.setup('clock')
	area.context['temperature'] = 5
	area.context['humidity'] = 40
	area.run()

