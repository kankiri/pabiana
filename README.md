[![Build Status](https://travis-ci.org/kankiri/pabiana.svg?branch=master)](https://travis-ci.org/kankiri/pabiana)

# Pabiana

A smart home consists of various remotely controllable devices and sensors, all of which posses a distinct interface.
These devices are controlled either manually with an app or by an adaptive algorithm based on sensor input.
To be controllable from software each of these interfaces has to be represented in code.
This demands for a particularly *modular software design* to be maintainable.
Also, physical distances in larger smart homes call for a *distributed control system*.

Processing and integrating sensor input from various sources and of various types and controlling multiple devices based on the results, including feedback loops, can quickly get very complicated.
A *hierarchical data processing model* can limit the complexity to a manageable degree.
A hierarchical system control model on the other hand can enable steady monitoring and supervision of multiple semi-autonomous systems.

**Pabiana** is a minimalistic Python framework that lets you build software complying with these principles.
Applications consist of a number of submodules running in parallel, distributed over several nodes.
These modules are, however, closely interconnected.
Constant streams of messages are passed between them as a means of communication.
Messaging over the network is handled by the *ØMQ* library.

Besides home automation systems, Pabiana can be used to develop intelligent assistants, robot control systems or any other software that controls actuators based on sensory input.

## Installation

Pabiana is currently tested with Python ≥ 3.5.
It is hosted on PyPI.
To integrate Pabiana into your projects, you can install it with:

    pip install --upgrade pabiana

It is recommended to use a virtual environment for your project.

## Application Design

The first step in the development of a Pabiana application is to think about the different submodules your application will be split in.
At the bottom of the hierarchical structure you will usually find I/O modules for different media of communication.
One module might be responsible for http, another one for UHF radio signals and a third one for audio signals.
These modules rely strongly on resources like drivers provided by the operating system.
However, they are rather generic and can be shared between applications.
It might make sense to split input and output between two modules running in parallel if significant feedback loops occur within a medium of communication.

Upper modules receive input from lower ones.
They integrate information from different communication media, as well as over time.
These modules are responsible for representing reality and keeping track of it's state.
For a home automation system, in this layer you might create a separate module for every important real-world device.

Top layer modules monitor actions and states of lower ones and intervene where necessary.
They implement complex logic to orchestrate the interaction between devices.

## Usage

Processes that run Pabiana modules are called *areas*. Each area can publish messages, subscribe to messages, trigger procedures of other areas and receive trigger calls. To start an area you have to use the following command:

    python -m pabiana module_name:area_name

For this command to work, you have to provide a JSON file called `interfaces.json` in the working directory specifying the addresses for both networking interfaces of all the areas of your application.
The structure of this file is as follows:

    {
        "area1-pub": {"ip": "127.0.0.1", "port": 10001},
        "area1-rcv": {"ip": "127.0.0.1", "port": 10002},
        "area2-pub": {"ip": "127.0.0.1", "port": 10003},
        "area2-rcv": {"ip": "127.0.0.1", "port": 10004, "host": "0.0.0.0"}
    }

In the current working directory there also has to be a folder called like the module and containing a Python file called `__init__.py` (a Python module).
In this file you will define the functionality of the area.

    from pabiana import Area, repo

    area = Area(repo['area-name'], repo['interfaces'])
    config = {
        'subscriptions': {'area2': ['ran', 'dom']}
    }

    @area.alteration(source='area2', slot='ran')
    def input(recent, complete):
        print(recent)

    @area.register
    def procedure(parameter):
        area.publish({'foo': 'bar'}, slot='important')

This code creates an area that will listen to messages from `area2` on two slots.
If it receives messages from `area2` it will print them.
It's important to note that messages are queued for some time before they are processed together.
A procedure is defined to be called from other areas.
Return values for procedures are ignored.
It is recommended to create a separate file for message handlers and procedures.

If a module requires a third-party library, it is possible to specify it in a `requirements.txt` file within the module directory.
The specified libraries will be installed through Pip at start time.
This feature was included to support automatic deployment of applications on different platforms.
