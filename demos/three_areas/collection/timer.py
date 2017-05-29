#!/usr/bin/env python3

from datetime import datetime

from pabiana.area import create_publisher, reg_name, run, timeout

publisher = None
context = {'timers': {}}


@reg_name('set')
def trgr_set(recv_name, dttime):
	"""
	Set a timer to be published at the specified minute.
	"""
	dttime = datetime.strptime(dttime, '%Y-%m-%d %H:%M:%S')
	dttime = dttime.replace(second=0, microsecond=0)
	try:
		context['timers'][dttime].append(recv_name)
	except KeyError:
		context['timers'][dttime] = [recv_name]


@timeout
def update():
	now = datetime.utcnow()
	for key in sorted(context['timers']):
		if key > now:
			break
		for recv_name in context['timers'][key]:
			publisher.send_multipart([recv_name.encode('utf-8'), '{}'.encode('utf-8')])
		del context['timers'][key]


if __name__ == '__main__':
	publisher = create_publisher(own_name=sys.argv[1], host='0.0.0.0')
	run(own_name='timer', host='0.0.0.0', timeout_ms=10000)
