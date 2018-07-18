# Copyright (c) 2012-2016 The University of Edinburgh
# Copyright (c) 2017 Michael Koutroumpas
# Copyright (c) 2018 Geo Smart Decisions
# All rights reserved.
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
# * Redistributions in binary form must reproduce the above copyright notice, this
#   list of conditions and the following disclaimer in the documentation and/or
#   other materials provided with the distribution.
# * Neither the name of the copyright holders nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific prior
#   written permission.
# THIS SOFTWARE IS PROVIDED BY THE ABOVE COPYRIGHT HOLDERS ''AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL EDINA BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
# OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE.

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


###  /ws/landsat/... landsat index support ###
@route('/ws/landsat', method=["GET", ])
def landsat():
    return GeoRest(request, response).landsat_coverage()


###  /ws/sentinel/... sentinel index support ###
@route('/ws/sentinel', method=["GET", ])
def sentinel():
    return GeoRest(request, response).sentinel_coverage()


###  /ws/datacube/... datacube access support ###
@route('/ws/datacube', method=["GET", ])
def datacube():
    return GeoRest(request, response).datacube_selection()


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
