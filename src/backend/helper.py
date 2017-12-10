"""Just some static utility functions that can't be grouped anywhere else"""


def strfilter(text, remove):
    """
    remove chars defined in "remove" from "text" e.g ('ab','blaaah') -> 'lh'
    """
    return ''.join([c for c in text if c not in remove])


def httprequest2dict(http_request):
    """Convert bottle http request object into a case sensitive param dictionary
    as follows:
    1. Join POST and GET K/V pairs
    2. Lower case keys -- no point in case-sensitive GET/POST requests

    :param http_request: a Bottle BaseHTTPRequest object
    :returns: A dictionary with all values
    """

    join = {}
    for k in http_request.GET.dict:
        join[k.lower()] = http_request.GET.dict[k][0]
    for k in http_request.POST.dict:
        join[k.lower()] = http_request.POST.dict[k][0]
    return join


def isdate(date):
    """ Check if string is a valid date in the YYYY-MM-DD format 
    :param date string: a string to check
    :return bool: True if valid date in the YYYY-MM-DD, False otherwise

    >>> isdate('2018-01-01')
    True
    >>> isdate('2018-01-41')
    False
    >>> isdate('2018-1-1')
    True
    """
    import datetime
    res = True
    try:
        datetime.datetime.strptime(date,"%Y-%m-%d")
    except ValueError:
        res = False
    return res

