from pabiana import Clock, repo

from utils import utils


clock = Clock(repo['area-name'], host='0.0.0.0')
premise = utils.setup
config = {
	'timeout': 1000,
	'use-template': True
}
