from pabiana import Area, repo

from utils import utils


area = Area(repo['area-name'], host='0.0.0.0')
setup = utils.setup
config = {
	'clock-name': 'clock',
	'context-values': {
		'temperature': 18,
		'window-open': False
	}
}


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
