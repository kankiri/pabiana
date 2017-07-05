#!/usr/bin/env python3

from datetime import datetime

from pabiana import area
from pabiana.area import load_interfaces, pulse, register, subscribe
from pabiana.node import create_publisher, run

NAME = 'timer'
publisher = None


# Triggers
@register
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


# Reactions
@pulse
def update():
	now = datetime.utcnow()
	for key in area.context['timers']:
		if now > key:
			message = '{}'.encode('utf-8')
			for slot_name in area.context['timers'][key]:
				publisher.send_multipart([slot_name.encode('utf-8'), message])
			del area.context['timers'][key]


if __name__ == '__main__':
	load_interfaces('interfaces.json')
	subscribe([], 'pulse', '02')
	publisher = create_publisher(own_name=NAME, host='0.0.0.0')
	area.context['timers'] = {}
	
	run(own_name=NAME, host='0.0.0.0')
