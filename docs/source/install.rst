
o2r-meta Getting started
========================

o2r-meta requires Python > 3.6

Installation from source
-------------------------

* Install the required modules

::

   git clone https://github.com/o2r-project/o2r-meta.git
   cd o2r-meta
   pip install -r requirements.txt


Installing using Docker
---------------------------

Another way of installation is provided by the Dockerfile. Build it like this:

::

   git clone https://github.com/o2r-project/o2r-meta.git
   cd o2r-meta
   docker build -t meta .

And start a tool of o2r meta like this:

::

   docker run --rm -v $(pwd)/extract/tests/:/testdata:ro meta -debug extract -i /testdata -s

You can pass all options to the images as if running ``o2rmeta.py`` directly, but must naturally mount all required data into the container.

The container has a default user o2r (``UID: 1000``) to avoid permission issues when mounting directories, e.g.

::
	
   mkdir /tmp/testout
   docker run --rm -v $(pwd)/extract/tests/:/testdata:ro -v /tmp/testout:/testout:rw meta -debug extract -i /testdata -o /testout
   ls /tmp/testout

Note: if the directory does not exist before mounting it, then Docker will create it for the user root and permission errors will arise.


