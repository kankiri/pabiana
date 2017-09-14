#!/usr/bin/env python3

import logging

from pabiana import Area, load_interfaces, trigger

NAME = 'association'


@area.alteration
def control():
	in_temp = area.context['smarthome'][''][0]['temperature']
	win_open = area.context['smarthome'][''][0]['window-open']
	out_temp = area.context['weather'][''][0]['temperature']
	
	if area.context['smarthome'][''][0]['time-rcvd'] == area.time or
	area.context['weather'][''][0]['time-rcvd'] == area.time:
		control_helper(in_temp, out_temp, win_open)
	
	if area.context['console']['input'][0]['time-rcvd'] == area.time:
		if area.context['console']['input-data']['signal'] == 'window-open':
			trigger('smarthome', 'window', {'open': True})
		elif area.context['console']['input-data']['signal'] == 'window-close':
			trigger('smarthome', 'window', {'open': False})


def control_helper(in_temp, out_temp, win_open):
	if win_open:
		if in_temp > out_temp + 1:
			trigger('smarthome', 'lower_temp')
		elif in_temp < out_temp - 1:
			trigger('smarthome', 'increase_temp')
		else:
			trigger('smarthome', 'keep_temp')
	else:
		if in_temp > 24 + 1:
			trigger('smarthome', 'lower_temp')
		elif in_temp < 24 - 1:
			trigger('smarthome', 'increase_temp')
		else:
			trigger('smarthome', 'keep_temp')


if __name__ == '__main__':
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.DEBUG
	)
	
	load_interfaces('interfaces.json')
	area = Area(NAME, host='0.0.0.0')
	area.setup('clock', '#', {'smarthome': [''], 'weather': [''], 'console': ['input']})
	area.run()

