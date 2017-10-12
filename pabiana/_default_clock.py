import logging

from . import Clock


def setup():
	logging.basicConfig(
		format='%(asctime)s %(levelname)s %(message)s',
		datefmt='%Y-%m-%d %H:%M:%S',
		level=logging.INFO
	)

clock = Clock('clock', host='0.0.0.0')
premise = setup
config = {
	'timeout': 1000,
	'use-template': True
}
