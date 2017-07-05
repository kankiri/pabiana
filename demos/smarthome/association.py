import logging

from pabiana import area
from pabiana.area import alteration, load_interfaces, subscribe
from pabiana.node import run, trigger

NAME = 'association'


# Reactions
@alteration
def forward():
	in_temp = area.context['smarthome']['-data']['temperature']
	win_open = area.context['smarthome']['-data']['window-open']
	out_temp = area.context['weather']['-data']['temperature']
	
	if area.context['smarthome'][''] == area.clock or area.context['weather'][''] == area.clock:
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
	
	if area.context['console']['input'] == area.clock:
		if area.context['console']['input-data']['signal'] == 'window-open':
			trigger('smarthome', 'window', {'open': True})
		elif area.context['console']['input-data']['signal'] == 'window-close':
			trigger('smarthome', 'window', {'open': False})


if __name__ == '__main__':
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.DEBUG
	)
	
	load_interfaces('interfaces.json')
	subscribe([('smarthome', ''), ('weather', ''), ('console', 'input')], 'pulse', '02')
	
	run(own_name=NAME, host='0.0.0.0')
