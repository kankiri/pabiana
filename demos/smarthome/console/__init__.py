import signal

from pabiana import repo, Runner

from . import utils


class Console(Runner):
	def __init__(self, name, interfaces):
		super().__init__(name, interfaces)
		self._goon = None

	def run(self):
		self._goon = True
		signal.signal(signal.SIGINT, self.stop)
		try:
			while self._goon:
				s = input('--> ').lower()
				if 'quit' in s:
					self.stop()
				if 'open' in s:
					self.publish({'signal': 'window-open'}, slot='input')
				elif 'close' in s:
					self.publish({'signal': 'window-close'}, slot='input')
		finally:
			self.trigger('association', 'exit')
			self.trigger('smarthome', 'exit')
			self.trigger('weather', 'exit')
			self.trigger('clock', 'exit')

	def stop(self):
		self._goon = False


runner = Console(repo['area-name'], repo['interfaces'])
premise = utils.setup
