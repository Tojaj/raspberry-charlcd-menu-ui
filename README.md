Raspberry CharLCD Menu UI
=========================

A menu-like user interface python library for LCD shield for Raspberry Pi (16x2 display, 5 buttons).

Usage
=====

    $ python3 example.py


Requirements
============

**Hardware components**

* Raspberry Pi
* LCD shield for Raspberry Pi (16x2 display, 5 buttons)
  * Compatible with Adafruit-CharLCD python library
  * [Example 1](https://www.adafruit.com/product/1115) or
    [Example 2](https://arduino-shop.cz/arduino/1210-lcd-shield-pro-raspberry-pi-b-b.html)


**Raspbian packages**

    sudo apt-get install -y \
        build-essential \
        python-dev \
        python-smbus \
	    python-pip \
	    git \
        i2c-tools


**Python libraries**

*Note: Before you install python modules by pip, you should consider
use of a python virtual environments. See next section of this readme.*

    pip install -r requirements.txt


Installation in virtual env
===========================

**1)** Install all necessary packages:

    sudo apt-get install virtualenv virtualenvwrapper

**2)** Add the next two lines at the bottom of your ``~/.profile`` file:

    export WORKON_HOME=~/.virtualenvs
    source /usr/share/virtualenvwrapper/virtualenvwrapper.sh

Note: If you have ~/.bash_profile file, then you need to add it there
as in that case the ``~/.profile`` won't be read.

**3)** Create a virtual env

    mkvirtualenv \
        --system-site-packages \
        --python=/usr/bin/python3 \
        raspberry-charlcd-menu-ui

Note: We are allowing system site python packages to be available in our
virtual env here.

**When you are ready to work** on the new virtual env

    workon raspberry-charlcd-menu-ui

**Once you are done** deactivate the virtual env

    deactivate


Troubleshooting
===============

List devices available on I2C bus and their addresses:

    i2cdetect -y 1
