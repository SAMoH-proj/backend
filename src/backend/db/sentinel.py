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

""" Sentinel specific functions
"""
from backend.db import spatialite
from backend import logtool

log = logtool.getLogger("db", "sentinel")


def get_coverage(lon, lat):
    """ Find all indexed Landsat dataset entries that contain lon, lat
        Args:
            lon: Longitude
            lat: Latitude
        Returns:
            All return rows as an array of dictionaries
    """
    point = 'POINT({} {})'.format(lon, lat)
    # check cloudCover!=-1 and big differences in lat / lon as mercator border data
    res = spatialite.execute("""
            SELECT productName, timestamp, epoch, cloudCover,
                   utmZone || latitudeBand || gridsquare as grid , min_lat, min_lon, max_lat, max_lon,
                   'https://sentinel-s2-l1c.s3.amazonaws.com/' ||path || '/preview.jpg' as download_url
            FROM s2_l1c_extent
            WHERE within(GeomFromText(?,4326),geometry) AND
                  (cloudCover != -1)  AND (max_lat-min_lat)<50 AND (max_lon-min_lon)<50
            ORDER BY epoch DESC;
            """, (point,))
    # convert 2d array to an array of dictionaries. This will be returned
    # as JSON to make life easier for the web developer.
    resdict = []
    for row in res:
        d = {}
        d["productId"] = row[0]
        d["entityId"] = row[0]
        d["acquisitionDate"] = row[1]
        d["epoch"] = row[2]
        d["cloudCover"] = row[3]
        d["processingLevel"] = "L1C"
        d["grid"] = row[4]
        d["min_lat"] = row[5]
        d["min_lon"] = row[6]
        d["max_lat"] = row[7]
        d["max_lon"] = row[8]
        d["download_url"] = row[9]
        resdict.append(d)
    return resdict


################### MAIN #######################
if __name__ == "__main__":
    print(logtool.pp(get_coverage(-3.35, 55.95)))
