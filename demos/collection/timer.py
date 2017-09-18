#!/usr/bin/env python3

from datetime import datetime

from pabiana import Area, load_interfaces

NAME = 'timer'
EMPTY = {}


@area.register
def place(slot_name, dttime):
	"""
	Set a timer to be published at the specified minute.
	"""
	dttime = datetime.strptime(dttime, '%Y-%m-%d %H:%M:%S')
	dttime = dttime.replace(second=0, microsecond=0)
	try:
		area.context['timers'][dttime].add(slot_name)
	except KeyError:
		area.context['timers'][dttime] = {slot_name}


@area.pulse
def update():
	now = datetime.utcnow()
	for key in area.context['timers']:
		if now > key:
			for slot_name in area.context['timers'][key]:
				area.publish(EMPTY, slot=slot_name)
			del area.context['timers'][key]


if __name__ == '__main__':
	load_interfaces('interfaces.json')
	area = Area(NAME, host='0.0.0.0')
	area.setup('clock', '##')
	area.context['timers'] = {}
	area.run()

