import logging
from contextlib import suppress

from pabiana import Area, repo
from pabiana.utils import multiple

from . import utils


area = Area(repo['area-name'], repo['interfaces'])
premise = utils.setup
config = {
	'clock-name': 'clock',
	'clock-slots': multiple(2, 6),
	'subscriptions': {
		'smarthome': None,
		'weather': None,
		'console': ['input']
	}
}


@area.alteration
def control():
	if len(area.context['smarthome']) > 0 and len(area.context['weather']) > 0:
		in_temp = area.context['smarthome'][0]['temperature']
		win_open = area.context['smarthome'][0]['window-open']
		out_temp = area.context['weather'][0]['temperature']
	
		if area.time in {area.context['smarthome'][0]['time-rcvd'], area.context['weather'][0]['time-rcvd']}:
			control_helper(in_temp, out_temp, win_open)


def control_helper(in_temp, out_temp, win_open):
	if win_open:
		if in_temp > out_temp + 1:
			area.trigger('smarthome', 'lower_temp')
		elif in_temp < out_temp - 1:
			area.trigger('smarthome', 'increase_temp')
		else:
			area.trigger('smarthome', 'keep_temp')
	else:
		if in_temp > 24 + 1:
			area.trigger('smarthome', 'lower_temp')
		elif in_temp < 24 - 1:
			area.trigger('smarthome', 'increase_temp')
		else:
			area.trigger('smarthome', 'keep_temp')


@area.alteration(source='console', slot='input')
def console_input():
	if area.context['console']['input'][0]['signal'] == 'window-open':
		area.trigger('smarthome', 'window', {'open': True})
	elif area.context['console']['input'][0]['signal'] == 'window-close':
		area.trigger('smarthome', 'window', {'open': False})


@area.pulse
def publish():
	if area.time % 8 == 0:
		with suppress(IndexError):
			logging.debug(
				'Inside Temp: %s, Outside Temp: %s, Window Open: %s', 
				round(area.context['smarthome'][0]['temperature'], 2),
				round(area.context['weather'][0]['temperature'], 2),
				area.context['smarthome'][0]['window-open']
			)
