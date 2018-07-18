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

## Execute this at .backends/data/ to create extents.db
# Download index from amazon
wget http://landsat-pds.s3.amazonaws.com/c1/L8/scene_list.gz
gzip -d scene_list.gz
# create spatialite metadata in a fresh database. Much faster than `SELECT InitSpatialMetaData()'
spatialite extents.db
# import csv to sqlite3
sqlite3 -csv extents.db ".import scene_list landsat_extent"
# create a an extra column with Unix Epoch instead of Date time to ease processing
sqlite3 extents.db "ALTER TABLE landsat_extent ADD COLUMN epoch DATETIME;"
sqlite3 extents.db "UPDATE landsat_extent SET epoch = strftime('%s',datetime(acquisitionDate))"
# generate spatialite metadata
spatialite extents.db "SELECT AddGeometryColumn('landsat_extent','geom',4326,'POLYGON','XY')"
# generate polygon extents from min/max lon/lat columns
spatialite extents.db "UPDATE landsat_extent SET geom = GeomFromText('POLYGON(('||min_lon||' '||min_lat||','||max_lon||' '||min_lat||','||max_lon||' '||max_lat||','||min_lon||' '||max_lat||','||min_lon||' '||min_lat||'))',4326);"

# To test the above -- fetch all landsat coverages at a sample point:
# select * from landsat_extent where within(GeomFromText('POINT(-3.35 55.95)'),geom);
