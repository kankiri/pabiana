from datetime import datetime

from pabiana import Area, repo
from pabiana.utils import multiple


area = Area(repo['area-name'], repo['interfaces'])
config = {
	'clock-name': 'clock',
	'clock-slots': multiple(2, 32),
	'context-values': {
		'timers': {}
	}
}


@area.register
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
	area.publish({'status': 'placed'}, slot=slot_name)


@area.pulse
def update():
	now = datetime.utcnow()
	for key in area.context['timers']:
		if now > key:
			for slot_name in area.context['timers'][key]:
				area.publish({'status': 'reminder'}, slot=slot_name)
			del area.context['timers'][key]
