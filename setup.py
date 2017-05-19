from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

setup(
	name='Pabiana',
	version='0.0.1',
	url='https://github.com/kankiri/pabiana',
	author='Alexander Schöberl',
	author_email='alexander.schoeberl@gmail.com',
	description='A minimalistic framework to build distributed cognitive applications based on ØMQ',
	long_description=open(os.path.join(ROOT, 'README.md')).read(),
	packages=find_packages(),
	install_requires=['pyzmq'],
	setup_requires=['pytest-runner'],
	tests_require=['pytest']
)
