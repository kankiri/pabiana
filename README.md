[![Build Status](https://travis-ci.org/kankiri/pabiana.svg?branch=master)](https://travis-ci.org/kankiri/pabiana)

# Pabiana

Pabiana is a minimalistic Python framework that lets you build intelligent applications distributed over several nodes.
The architecture is inspired by the neocortex of the mammalian brain.
The applications are intended to consist of a number of submodules called *areas*.
Messages are passed between these areas as a means of communication.
Messaging over the network is handled by the ØMQ library.

Pabiana can be used to develop home automation systems, intelligent assistants or any other program that controls actuators based on sensory input.

## Installation

Pabiana is only tested against Python ≥ 3.5, but might also work with other versions.
To integrate Pabiana in your projects, you can install it with:

    pip install --upgrade pabiana

It is recommended to use a virtual environment for your project.

## Usage

Pabiana enforces a very specific style of programming and architecture.
Have a look at the *demos* directory to get an idea of how to use it.
