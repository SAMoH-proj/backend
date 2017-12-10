"""
################ ROUTES ####################

#######################################################
###  Maps HTTP/REST requests to python functions    ###
###  They can all be tested ith wget/curl           ###
#######################################################
"""

import bottle
from bottle import route, request, response, static_file, hook
## backend imports
from backend import logtool
from backend import config

from backend.rest import GeoRest

log = logtool.getLogger("backend")


###  /ws/operation1/... operation1 ###
@route('/ws/operation1', method=["GET", ])
def operation1():
    return GeoRest(request, response).operation1()


###  /ws/operation2/... operation2 index support ###
@route('/ws/operation2', method=["GET", ])
def operation2():
    return GeoRest(request, response).operation2()


### Optional: STATIC FILES (html/css/js etc.). Reserved for future deployments
def init_static_routes():
    """Call this function to setup static routes using the documentroot defined
    in config.ini"""
    root = config.getStaticHTML()

    @route('/<filename:re:(?!ws/).*>')
    def serve_static(filename):
        return static_file(filename, root=root, download=False)

    @route('/')
    def default_static():
        return static_file('index.html', root=root, download=False)

########## CORS ##################


@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, OPTIONS, DELETE'
    response.headers['Access-Control-Allow-Headers'] = 'Origin, X-Requested-With, Content-Type, Accept'


### Error pages ###
@bottle.error(404)
def error404(error):
    return ['NO BACKEND endpoint at requested URL: {}\n'.format(request.url)]
