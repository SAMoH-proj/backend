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
          
from tempfile import NamedTemporaryFile
from os.path import basename
from bottle import static_file

from backend import helper, logtool
from backend.db import landsat, sentinel, datacube_processes
log = logtool.getLogger("GeoRest", "backend")


class GeoRest(object):
    """REST request handler object. Return values should be direct json"""

    def __init__(self, request, response):
        self.request = request
        self.response = response

    def landsat_coverage(self):
        """ Execure landsat.get_coverage for all dataset that contain lon, lat
            Mandatory GET Args:
                lon: Longitude
                lat: Latitude
            Returns:
                Relevant Landsat datasets entries as an array of JSON objects
        """
        log.debug('CALL: {}'.format(self.request.url))
        params = helper.httprequest2dict(self.request)
        if not ('lat' in params) or not ('lon' in params):
            return self.error("Both lat and lon need to be defined")
        coverage = landsat.get_coverage(params["lon"], params["lat"])
        return self.success(coverage)

    def sentinel_coverage(self):
        """ Execure sentinel.get_coverage for all dataset that contain lon, lat
            Mandatory GET Args:
                lon: Longitude
                lat: Latitude
            Returns:
                Relevant Sentinel datasets entries as an array of JSON objects
        """
        log.debug('CALL: {}'.format(self.request.url))
        params = helper.httprequest2dict(self.request)
        if not ('lat' in params) or not ('lon' in params):
            return self.error("Both lat and lon need to be defined")
        coverage = sentinel.get_coverage(params["lon"], params["lat"])
        return self.success(coverage)


    def datacube_selection(self):
        """ Execute a datacube action on selection
            Mandatory GET Args:
                selection: "rectangle" or "line"
                type: type of processing e.g. "ndvi_transect", "digest". Check
                      implementation at db.datacube
            Returns:
                Varies -- image/jpeg, image/png or JSON
        """
        log.debug('CALL: {}'.format(self.request.url))
        params = helper.httprequest2dict(self.request)
        # the `delete` flag will delete file when it is closed. Disable to debug
        with NamedTemporaryFile(delete=True, prefix='tmp_plot_') as temp_fp:
            plot = datacube_processes.execute(params, temp_fp)
            if plot["error"] == 1:
                return plot
            if plot["error"] == 0:
                log.debug("Got {} plot named {} size {}".format(plot["mimetype"],
                                                                temp_fp.name,
                                                                plot["size"]))
                temp_fp.flush()
                # there are strong effiency reasons we are not returning the
                # contents of the fp directly but create a temp file instead.
                # s.a. static_file documentation (chunked downloading,
                # content-type, content-length, debugging)
                return static_file(basename(temp_fp.name), root='/tmp',
                                   mimetype=plot["mimetype"], download=False)
        return self.error("Temporary file creation for plotting failed")

    def help(self):
        log.debug('CALL: {}'.format(self.request.url))
        return {"landsat": ["GET", "lat(float): latitude", "lon(float):longitude"]}

    def error(self, message):
        return {"error": 1, "msg": message}

    def success(self, message):
        return {"error": 0, "msg": message}
