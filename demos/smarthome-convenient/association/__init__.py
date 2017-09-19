from contextlib import suppress
from pabiana import Area, repo, trigger
from .setup import setup

area = Area(repo['area-name'], host='0.0.0.0')
config = {
	'clock-name': 'clock',
	'clock-slot': '#',
	'subscriptions': {
		'smarthome': [''],
		'weather': [''],
		'console': ['input']
	}
}


@area.alteration
def control():
	if len(area.context['smarthome']['']) > 0 \
	and len(area.context['weather']['']) > 0:
		in_temp = area.context['smarthome'][''][0]['temperature']
		win_open = area.context['smarthomfrom .setup import setupe'][''][0]['window-open']
		out_temp = area.context['weather'][''][0]['temperature']
	
		if area.context['smarthome'][''][0]['time-rcvd'] == area.time \
		or area.context['weather'][''][0]['time-rcvd'] == area.time:
			control_helper(in_temp, out_temp, win_open)
	
	with suppress(Exception):
		if area.context['console']['input'][0]['time-rcvd'] == area.time:
			if area.context['console']['input'][0]['signal'] == 'window-open':
				trigger('smarthome', 'window', {'open': True})
			elif area.context['console']['input'][0]['signal'] == 'window-close':
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


@area.pulse
def publish():
	if area.time % 8 == 0:
		with suppress(Exception):
			logging.debug(
				'Inside Temp: %s, Outside Temp: %s, Window Open: %s', 
				area.context['smarthome'][''][0]['temperature'],
				area.context['weather'][''][0]['temperature'],
				area.context['smarthome'][''][0]['window-open']
			)
