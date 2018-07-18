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

""" Datacube processing functions
"""
from backend import logtool
from backend.helper import isdate

log = logtool.getLogger("db", "datacube_precesses")
# Make this configurable once the user can dymanically generate one's own datasets

# Accelerated LS8 ingested from S3 -- R,G,B,NIR
LS8 = {
    'env' : None,
    'product' : 'ls8_rgb_ndvi'
}

# Raw BOA S2 L2A from disk -- all bands, 2 years, less coverage
L2A = {
    'env' : 'l2a_safe',
    'product' : 's2a_sen2cor_granule'
}

# Raw TOA S2 L1C from disk -- all bands, all years, full coverage
L1C = {
    'env' : 'l1c_safe',
    'product' : 's2a_level1c_granule'
    # 'product' : 's2b_level1c_granule'
}

DATASET = L2A

def execute(params, fp=None):
    """Handles REST parameters and dispatches the right function
    :param Dictionary params: request parameters
    :param file object params: optional file object to save plots are other bulky files
    :return: raw HTTP response (json or image/*)
    """
    if not ('selection' in params) or not ('type' in params):
        return error("Both selection [line|rectangle] and type"
                     " [ndvi_transect|ndvi_time_series|time_series|...] need to be defined.")
    if params['selection'] == 'line':
        res = line(params, fp)
    if params['selection'] == 'rectangle':
        res = rectangle(params, fp)
    return res


def line(params, fp=None):
    """Handles line-based algorithms e.g. ndvi_transect and dispatches
    the right function.
    :param Dictionary params: dictionary with xmin,xmax,ymin,ymax,type
    :param file object params: optional file object to save plots are other bulky files
    :return: raw HTTP response (json or image/*)

    NOTE: line can potentially be any multipoint LINESTRING but we
    start with xmin,xmax,ymin,ymax
    """
    from datacube.utils import geometry

    if not ('xmin' in params) or not ('xmax' in params) \
       or not ('ymin' in params) or not ('ymax' in params):
            return error("Line requires xmin,xmax,ymin,ymax")
    xmin = float(params["xmin"])
    xmax = float(params["xmax"])
    ymin = float(params["ymin"])
    ymax = float(params["ymax"])
    # NOTE: you can use a line with multiple points here
    line = geometry.line([(xmin, ymin), (xmax, ymax)], 'EPSG:4326')
    if(line.type != 'LineString'):
        return error("ndvi_transect: line not LINESTRING")

    query = {
        'geopolygon': line
    }
    if ('time_begin' in params) and ('time_end' in params):
        if (not isdate(params['time_begin'])) or (not isdate(params['time_end'])):
            return error("Invalid time specified")
        query['time'] = (params['time_begin'], params['time_end'])
    if params['type'] == 'ndvi_transect':
        if not fp:
            return error("ndvi_transet needs a pre-allocated file")
        return ndvi_transect(query, fp)
    else:
        return error("Supported line-processing types: ndvi_transect")


def rectangle(params, fp=None):
    """Handles rectangle-based algorithms e.g. ndvi_time_series and dispatches
    the right function.
    :param Dictionary params: request parameters
    :param file object params: optional file object to save plots are other bulky files
    :return: raw HTTP response (json or image/*)
    """
    if not ('xmin' in params) or not ('xmax' in params) \
       or not ('ymin' in params) or not ('ymax' in params):
            return error("Rectangle requires xmin,xmax,ymin,ymax")
    xmin = float(params["xmin"])
    xmax = float(params["xmax"])
    ymin = float(params["ymin"])
    ymax = float(params["ymax"])
    query = {
        'x' : (xmin, xmax),
        'y' : (ymin, ymax)
        }
    if ('time_begin' in params) and ('time_end' in params):
        if (not isdate(params['time_begin'])) or (not isdate(params['time_end'])):
            return error("Invalid time specified")
        query['time'] = (params['time_begin'], params['time_end'])
    
    if not fp:
        return error("A pre-allocated file is currently mandatory for all operations")

    if params['type'] == 'ndvi_time_series':
        return ndvi_time_series(query, fp, std_dev=False)
    elif params['type'] == 'ndvi_std_dev':
        return ndvi_time_series(query, fp, std_dev=True)
    elif params['type'] == 'time_series':
        query["measurements"] = ['B04_10m', 'B03_10m', 'B02_10m']
        return time_series(query, fp)
    elif params['type'] == 'colour_infrared':
        query["measurements"] = ['B08_10m', 'B04_10m', 'B03_10m']
        return time_series(query, fp)
    elif params['type'] == 'colour_urban':
        query["measurements"] = ['B12_20m', 'B11_20m', 'B04_20m']
        return time_series(query, fp)
    #elif params['type'] == 'swir':
    #    query["measurements"] = ['B12_20m', 'B8A_20m', 'B04_20m']
    #    return time_series(query, fp)
    # Crops:bright green, non-crop vegetation: darker green, bare earth: shades of pink
    #elif params['type'] == 'agriculture':
    #    query["measurements"] = ['B11_20m', 'B8A_20m', 'B02_20m']
    #    return time_series(query, fp)
    # elif params['type'] == 'healthy_vegetation':
    #     query["measurements"] = ['B8A_20m', 'B11_20m', 'B02_20m']
    #     return time_series(query, fp)
    # elif params['type'] == 'atmo_penetration':
    #     query["measurements"] = ['B12_20m', 'B11_20m', 'B8A_20m']
    #     return time_series(query, fp)
    # elif params['type'] == 'land_water':
    #     query["measurements"] = ['B8A_20m', 'B11_20m', 'B04_20m']
    #     return time_series(query, fp)
    # elif params['type'] == 'scene_classifier':
    #    return l2a_scene_classifier(query, fp)
    else:
        return error("Please use a supported rectangle-processing type e.g. ndvi_time_series, colour_infrared etc.")

def time_series(query, fp):
    """Returns muliple images with R,G,B values mapped to measurements parameter
    :param dict query: x (or longitude), y (or latitude), time
    :param file object params: optional file object to save plots are other bulky files
    :return: raw HTTP response (json or image/*)
    """
    # keep those imports here to avoid breaking the rest of the file when these
    # libraries do not exist
    import matplotlib
    # pyplot will dry to plot on an X11 Display without this:
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import datacube
    from datacube.storage.masking import mask_invalid_data
    

    if 'granule' in DATASET['product']:
        query['resolution'] = (-0.000135, 0.000135)
        query['output_crs'] = 'EPSG:4326'
    
    dc = datacube.Datacube(env=DATASET['env'], app="ndvi_time_series")

    data = dc.load(DATASET['product'], **query)
    data = mask_invalid_data(data)
    rgb = data.to_array(dim='color')
    fake_saturation = 4000
    rgb = rgb.transpose(*(rgb.dims[1:]+rgb.dims[:1]))  # make 'color' the last dimension
    rgb = rgb.where((rgb <= fake_saturation).all(dim='color'))  # mask out pixels where any band is 'saturated'
    rgb /= fake_saturation  # scale to [0, 1] range for imshow
    try:
        rgb.plot.imshow(x=data.crs.dimensions[1], y=data.crs.dimensions[0],col='time', col_wrap=5)
    except Exception as err:
        return error("Plotting failed: {}".format(err))
    ############################
    # save to supplied file object:
    plt.savefig(fp, dpi=150, format='jpg')
    plt.gcf().clear()  # clear figure instead of combining new images with old
    size = fp.tell()
    return {'error': 0, 'mimetype': 'image/jpg', 'size': size}


def l2a_scene_classifier(query, fp):
    """Return a plot a scene classification according to SCL band in Sentinel2 L2A
    :param dict query: x (or longitude), y (or latitude), time
    :param file object params: optional file object to save plots are other bulky files
    :return: raw HTTP response (json or image/*)
    """
    # keep those imports here to avoid breaking the rest of the file when these
    # libraries do not exist
    import matplotlib
    # pyplot will dry to plot on an X11 Display without this:
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import datacube
    from datacube.storage.masking import mask_invalid_data
    

    if 'granule' in DATASET['product']:
        query['resolution'] = (-0.000135, 0.000135)
        query['output_crs'] = 'EPSG:4326'
    
    dc = datacube.Datacube(env=DATASET['env'], app="S2_scene_classifier")

    data = dc.load(DATASET['product'], measurements=['SCL_20m'], **query)
    scl = data.SCL_20m
    colors=["xkcd:charcoal", "#3498db", "xkcd:green", "xkcd:white", "xkcd:dark green", "xkcd:white", "xkcd:deep blue", "xkcd:dark brown","xkcd:white","xkcd:white"]
    
    try:
        scl.plot(col='time', col_wrap=3, levels=[0,1,2,3,4,5,6,7,8,9,10], colors = colors)
    except Exception as err:
        return error("Plotting failed: {}".format(err))
    ############################
    # save to supplied file object:
    plt.savefig(fp, dpi=150, format='jpg')
    plt.gcf().clear()  # clear figure instead of combining new images with old
    size = fp.tell()
    return {'error': 0, 'mimetype': 'image/jpg', 'size': size}


def ndvi_transect(query, fp):
    """Return ndvi_transect as image
    :param dict query: x (or longitude), y (or latitude), time
    :param File fp: file pointer to save resulting plot
    :return: raw HTTP response (json on success or image on error)

    NOTE: line can potentially be any multipoint LINESTRING but we
    start with xmin,xmax,ymin,ymax
    """
    # keep those imports here to avoid breaking the rest of the file when these
    # libraries do not exist
    import matplotlib
    # pyplot will dry to plot on an X11 Display without this:
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    import xarray
    import datacube

    line = query['geopolygon']
    
    query.update({
        'resolution': (-0.00027, 0.00027), # ADJUST THIS FOR QUALITY (in WPS84 degrees) -- can run out of memory ;)
        'output_crs': 'EPSG:4326'
    })
    
    dc = datacube.Datacube(env=DATASET['env'], app='ndvi-transect')
    nired = dc.load(product='safe_10m', measurements=['B04_10m', 'B08_10m'],
                    group_by='solar_day', **query)
    # Return error message if we find no data instead of crashing
    if (len(nired.data_vars) == 0):
        error("Didn't find any index/ingested data in selected area at {}".format(DATASET))
    #### interpolation -- calculate all values along the line according to resolution
    try:
        resolution = abs(nired.affine.a)
        line = line.to_crs(nired.crs)
        dist = np.arange(0, line.length, resolution)
        points = [line.interpolate(d).coords[0] for d in dist]
        indexers = {
            nired.crs.dimensions[0]: [p[1] for p in points],
            nired.crs.dimensions[1]: [p[0] for p in points]
        }
        trans = nired.sel_points(xarray.DataArray(dist, name='distance', dims=['distance']),
                                 method='nearest',
                                 tolerance=None,
                                 **indexers)
        ####
        nir = trans.B08_10m.where(trans.B08_10m != trans.B08_10m.attrs['nodata'])
        red = trans.B04_10m.where(trans.B04_10m != trans.B04_10m.attrs['nodata'])
        ndvi = ((nir - red) / (nir + red))
        # For transect just choose cloud-free images for now
        #good_data = datacube.storage.masking.make_mask(trans.quality, cloud=0)
        # drop N/A values
        #ndvi_cloud_free = ndvi.where(good_data).dropna('time', how='all')
        #ndvi_cloud_free.plot()
        #ndvi.plot()
        # reverse Y,X and use custom cmap:
        ndvi.plot(x='distance', y='time', cmap='RdYlGn')
    except Exception as err:
        return error("Plotting failed: {}".format(err))
    ############################
    # save to supplied file object:
    plt.savefig(fp, dpi=150, format='jpg')
    plt.gcf().clear()  # clear figure instead of combining new images with old
    size = fp.tell()
    return {'error': 0, 'mimetype': 'image/jpg', 'size': size}


def ndvi_time_series(query, fp, std_dev=False):
    """Return ndvi time series as a big image of smaller images
    :param dict query: x (or longitude), y (or latitude), time
    :param File fp: file pointer to save resulting plot
    :param std_dev Bool: If True then plot ndvi std deviation over period
    :return: raw HTTP response (json on success or image on error)
    """
    # keep those imports here to avoid breaking the rest of the file when these
    # libraries do not exist
    import matplotlib
    # pyplot will dry to plot on an X11 Display without this:
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import datacube
    
    if 'granule' in DATASET['product']:
        query['resolution'] = (-0.000135, 0.000135)
        query['output_crs'] = 'EPSG:4326'
    
    dc = datacube.Datacube(env=DATASET['env'], app="ndvi_time_series")
    nired = dc.load(product=DATASET['product'], measurements=['B04_20m', 'B8A_20m', 'SCL_20m'], group_by='solar_day', **query)
    nir = nired.B8A_20m.where(nired.B8A_20m != nired.B8A_20m.attrs['nodata'])
    red = nired.B04_20m.where(nired.B04_20m != nired.B04_20m.attrs['nodata'])
    ndvi = ((nir - red) / (nir + red))

    # Return error message if we find no data instead of crashing
    if (len(nired.data_vars) == 0):
        error("Didn't find any index/ingested data in selected area at {}".format(DATASET))
    try:
        cloud = datacube.storage.masking.make_mask(nired.SCL_20m, sca="snow")
        ndvi_cloud_free = ndvi.where(~cloud).dropna('time', how='all')
        if ( std_dev ):
            ndvi_cloud_free.std(dim='time').plot()
        else:
            ndvi_cloud_free.plot(col='time', col_wrap=3, cmap='RdYlGn')
    except Exception as err:
        return error("Plotting failed: {}".format(err))
    ############################
    # save to supplied file object:
    plt.savefig(fp, dpi=150, format='jpg')
    plt.gcf().clear()  # clear figure instead of combining new images with old
    size = fp.tell()
    return {'error': 0, 'mimetype': 'image/jpg', 'size': size}


def error(message):
    return {"error": 1, "msg": message}


def success(message):
    return {"error": 0, "msg": message}

################### MAIN #######################


if __name__ == "__main__":
    import sys
    # test error json
    print(logtool.pp(execute({'selection': 'line', 'type': 'ndvi_transect'})))

    ## create params
    params = {
        'xmin' : -4.037846435,
        'ymin' : 52.51647802,
        'xmax' : -3.970512503,
        'ymax' : 52.56521060,
        'time_begin' : '2018-2-1',
        'time_end' : '2018-6-1',
        'product' : 'sentinel'
    }
    # Agriculture
    with open('agriculture.jpg', 'wb+') as out:
        params['selection'] = 'rectangle'
        params['type'] = 'agriculture'
        img = execute(params, fp=out)
        print("Saved {}".format(str(img)))
    sys.exit(0)
    # Scene classifier
    with open('scene_classifier.jpg', 'wb+') as out:
        params['selection'] = 'rectangle'
        params['type'] = 'scene_classifier'
        img = execute(params, fp=out)
        print("Saved {}".format(str(img)))
    sys.exit(0)
    # false-color-infrared
    with open('colour_infrared.jpg', 'wb+') as out:
        params['selection'] = 'rectangle'
        params['type'] = 'colour_infrared'
        img = execute(params, fp=out)
        print("Saved {}".format(str(img)))
    sys.exit(0)
    # NDVI TIME SERIES
    with open('test_ndvi_time_series.jpg', 'wb+') as out:
        params['selection'] = 'rectangle'
        params['type'] = 'ndvi_time_series'
        img = execute(params, fp=out)
        print("Saved {}".format(str(img)))
    #sys.exit(0)
    # NDVI STD DEV
    with open('test_ndvi_std_dev.jpg', 'wb+') as out:
        params['selection'] = 'rectangle'
        params['type'] = 'ndvi_std_dev'
        img = execute(params, fp=out)
        print("Saved {}".format(str(img)))
    sys.exit(0)
    # TIME SERIES
    with open('test_time_series.jpg', 'wb+') as out:
        params['selection'] = 'rectangle'
        params['type'] = 'time_series'
        img = execute(params, fp=out)
        print("Saved {}".format(str(img)))
    sys.exit(0)
    # NDVI TRANSECT
    with open('test_ndvi_transect.jpg', 'wb+') as out:
        params['selection'] = 'line'
        params['type'] = 'ndvi_transect'
        img = execute(params, fp=out)
        print("Saved {}".format(str(img)))
    sys.exit(0)
