import json
from pabiana import Area, repo, trigger
from .setup import setup

area = Area(repo['area-name'], host='0.0.0.0')
config = {
	'clock-name': 'clock',
	'context-values': {
		'temperature': 5,
		'humidity': 40
	}
}


@area.pulse
def publish():
	if area.time % 8 == 0:
		area.publish({
			'temperature': area.context['temperature'],
			'humidity': area.context['humidity']
		})

