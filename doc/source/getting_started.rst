Getting yaupon
==============

Yaupon depends on Python 2.5 or higher. Here's how to download and 
install Yaupon.

Debian flavors of Linux
~~~~~~~~~~~~~~~~~~~~~~~

sudo apt-get install python
sudo apt-get install python-setuptools
(if you want to run tests, do "sudo easy_install py" for py.test) 
(if you want sphinx, then do "sudo easy_install Sphinx")
sudo apt-get install mercurial

Add your development path to the python search path, for example:

sudo echo "/home/aaron/development" > /usr/local/lib/python2.6/dist-packages/yaupon.pth