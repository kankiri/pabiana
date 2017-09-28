from pabiana import Area, repo
from utils import utils


area = Area(repo['area-name'], host='0.0.0.0')
setup = utils.setup
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
