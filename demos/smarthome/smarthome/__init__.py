from pabiana import Area, repo
from pabiana.utils import multiple

from . import utils

area = Area(repo['area-name'], repo['interfaces'])
premise = utils.setup
config = {
	'clock-name': 'clock',
	'clock-slots': multiple(1, 6),
	'context-values': {
		'temperature': 18,
		'window-open': False
	}
}


@area.register
def increase_temp():
	area.context['temperature'] += 0.1
	area.autoloop('increase_temp')


@area.register
def lower_temp():
	area.context['temperature'] -= 0.1
	area.autoloop('lower_temp')


@area.register
def keep_temp():
	pass


@area.register
def window(open):
	area.context['window-open'] = open


@area.scheduling
def schedule(demand: dict, alterations: set, looped: set=None, altered: set=None):
	"""Prioritizes Triggers called from outside."""
	if looped is not None and len(demand) != len(looped):
		for func in looped: del demand[func]
	if keep_temp in demand:
		demand.pop(increase_temp, None)
		demand.pop(lower_temp, None)
	elif lower_temp in demand:
		demand.pop(increase_temp, None)
	return demand, alterations


@area.pulse
def routine():
	if area.time % 8 == 0:
		area.publish({
			'temperature': area.context['temperature'],
			'window-open': area.context['window-open']
		})
