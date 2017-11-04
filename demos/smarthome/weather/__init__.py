from pabiana import Area, repo
from pabiana.utils import multiple

from . import utils

area = Area(repo['area-name'], repo['interfaces'])
premise = utils.setup
config = {
	'clock-name': 'clock',
	'clock-slots': multiple(4, 6),
	'context-values': {
		'temperature': 10,
		'humidity': 40
	}
}


@area.pulse
def publish():
	area.publish({
		'temperature': area.context['temperature'],
		'humidity': area.context['humidity']
	})
