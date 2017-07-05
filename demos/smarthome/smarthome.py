import logging

from pabiana import area
from pabiana.area import autoloop, load_interfaces, pulse, register, scheduling, subscribe
from pabiana.node import create_publisher, run

NAME = 'smarthome'
publisher = None


# Triggers
@register
def increase_temp():
	area.context['temperature'] += 0.25
	autoloop(increase_temp)


@register
def lower_temp():
	area.context['temperature'] -= 0.25
	autoloop(lower_temp)


@register
def keep_temp():
	pass


@register
def window(open):
	area.context['window-open'] = open


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
			'window-open': area.context['window-open']
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
	area.context['temperature'] = 18
	area.context['window-open'] = False
	
	run(own_name=NAME, host='0.0.0.0')
