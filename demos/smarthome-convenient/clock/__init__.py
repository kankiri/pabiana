from pabiana import Clock, repo
from .setup import setup

clock = Clock(repo['area-name'], host='0.0.0.0')
config = {
	'timeout': 1000,
	'use-template': True
}

