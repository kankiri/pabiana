#!/usr/bin/env python3

import logging

from pabiana import Area, load_interfaces

NAME = 'smarthome'
area = Area(NAME, host='0.0.0.0')


@area.register
def increase_temp():
	area.context['temperature'] += 0.5
	area.autoloop(increase_temp)


@area.register
def lower_temp():
	area.context['temperature'] -= 0.5
	area.autoloop(lower_temp)


@area.register
def keep_temp():
	pass


@area.register
def window(open):
	area.context['window-open'] = open


@area.scheduling
def schedule():
	if keep_temp in area.demand:
		area.demand.pop(increase_temp, None)
		area.demand.pop(lower_temp, None)
	elif lower_temp in area.demand:
		area.demand.pop(increase_temp, None)


@area.pulse
def publish():
	if area.time % 8 == 0:
		area.publish({
			'temperature': area.context['temperature'],
			'window-open': area.context['window-open']
		})


if __name__ == '__main__':
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.DEBUG
	)
	
	load_interfaces('interfaces.json')
	area.setup('clock')
	area.context['temperature'] = 18
	area.context['window-open'] = False
	area.run()

