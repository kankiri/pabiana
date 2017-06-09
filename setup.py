from os import path
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

setup(
	name='Pabiana',
	version='0.0.4',
	url='https://github.com/kankiri/pabiana',
	author='Alexander Schöberl',
	author_email='alexander.schoeberl@gmail.com',
	description='A minimalistic framework to build distributed cognitive applications based on ØMQ',
	long_description=open(path.join(here, 'README.md')).read(),
	packages=find_packages(),
	install_requires=['pyzmq>=16.0.2'],
	setup_requires=['pytest-runner>=2.11.1'],
	tests_require=['pytest>=3.0.7'],
	zip_safe=False
)
