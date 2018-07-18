Backend
=======

This is a fork of the [lightweight backend](https://github.com/xmichael/backend) project to provide Landsat and Sentinel indexing support and to exposes OpenDataCube-backed functionality.

The original service is based on COBWEB project's [PCAPI](https://github.com/cobweb-eu/pcapi)

Installation
------------

1. `pip install --user git+https://github.com/SAMoH-proj/backend.git`
2. `backend`

Alternatively, one can use a WSGI server e.g. apache's mod_wsgi using *backend/server.py* as the point of entry.

By default _backend_ will store its default configuration and data file under *$HOME/.backend/*.

Dependencies
------------

 - python 3
 - libsqlite3-mod-spatialite (upstream debian)

Troubleshooting:
----------------

The easiest way to find what is wrong is to do the following:

1. Start the application from the command line locally by running `backend`. Look for error messages
2. `tail -f ~/.backend/logs/backend.log` (The actual location is specified in the configuration file)
3. Start issuing REST calls to localhost using a client like *curl* or *wget* e.g.

`curl http://localhost:8080/ws/operation?param1=<value1>&param2=<value2>`

### Sources:

* `./src/backend/`:
	* `server.py`: The main wsgi app. Start reading the source here.

	* `data`: default configuration file in .ini format. Configuration is copied to *~/.backend/* folder during installation.
* `./src/test/`: the test suite. To run it, cd inside that directory and execute: `python -munittest mytest`

### Database/Uploaded Files:

All files are under *~/.backend/* (unless overriden by +backend.ini+):

* `backend.ini`:
	        Default configuration file.
* `logs/backend.log`:
      		All log outputs as configured in +backend.ini+.

License
-------

[Modified BSD](./LICENSE)


See also individual file contents for additional copyrights.
