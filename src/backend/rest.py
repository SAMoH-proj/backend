from tempfile import NamedTemporaryFile
from os.path import basename
from bottle import static_file

from backend import helper, logtool
#from backend.db import xxx

log = logtool.getLogger("GeoRest", "backend")


class GeoRest(object):
    """REST request handler object. Return values should be direct json"""

    def __init__(self, request, response):
        self.request = request
        self.response = response

    def operation1(self):
        """ Execure operation1 blah blah
            Mandatory GET Args:
                param1: first parametre
                param2: second parametre
            Returns:
                something useful
        """
        log.debug('CALL: {}'.format(self.request.url))
        params = helper.httprequest2dict(self.request)
        # example mandatory parametre checks
        if not ('param1' in params) or not ('param2' in params):
            return self.error("Both param1 and param2 need to be defined")
        return self.success("returned value")

    def operation2(self):
        """ Execure operation2 blah blah
            Mandatory GET Args:
                param1: first parametre
                param2: second optional parametre
            Returns:
                something useful
        """
        log.debug('CALL: {}'.format(self.request.url))
        params = helper.httprequest2dict(self.request)
        # example mandatory parametre checks
        if not ('param1' in params):
            return self.error("Both param1 need to be defined")
        return self.success("returned value")

    def help(self):
        log.debug('CALL: {}'.format(self.request.url))
        return {"operation1": ["GET", "param1(float): first parametre", "param2(float): second parametre"]}

    def error(self, message):
        return {"error": 1, "msg": message}

    def success(self, message):
        return {"error": 0, "msg": message}
