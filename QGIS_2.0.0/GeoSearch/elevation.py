'''Google Maps V3 Elevation.

Largely adapted from the existing v2 elevation with modifications made where
possible to support the v3 api as well as to clean up the class without
breaking its compatibility or diverging its api too far from the rest of the
elevation classes.
'''

import base64
import hashlib
import hmac
from urllib import urlencode
from urllib2 import urlopen

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        from django.utils import simplejson as json

from geopy import util



class Elevation:
    '''Elevation using the Google Maps v3 API.'''
    
    def __init__(self, domain='maps.googleapis.com', protocol='http',
                 client_id=None, secret_key=None):
        '''Initialize a customized Google elevation.

        API authentication is only required for Google Maps Premier customers.

        ``domain`` should be the localized Google Maps domain to connect to. The default
        is 'maps.google.com', but if you're geocoding address in the UK (for
        example), you may want to set it to 'maps.google.co.uk' to properly bias results.

        ``protocol`` http or https.
        
        ``client_id`` Premier account client id.
        
        ``secret_key`` Premier account secret key.
        '''

        if protocol not in ('http', 'https'):
            raise ValueError, 'Supported protocols are http and https.'
        if client_id and not secret_key:
            raise ValueError, 'Must provide secret_key with client_id.'
        if secret_key and not client_id:
            raise ValueError, 'Must provide client_id with secret_key.'

        self.domain = domain.strip('/')
        self.protocol = protocol
        self.doc = {}

        if client_id and secret_key:
            self.client_id = client_id
            self.secret_key = secret_key
            self.premier = True
        else:
            self.premier = False

    def get_signed_url(self, params):
        '''Returns a Premier account signed url.'''
        params['client'] = self.client_id
        url_params = {'protocol': self.protocol, 'domain': self.domain,
                      'params': urlencode(params)}
        secret = base64.urlsafe_b64decode(self.secret_key)
        url_params['url_part'] = (
            '/maps/api/elevation/json?%(params)s' % url_params)
        signature = hmac.new(secret, url_params['url_part'], hashlib.sha1)
        url_params['signature'] = base64.urlsafe_b64encode(signature.digest())

        return ('%(protocol)s://%(domain)s%(url_part)s'
                '&signature=%(signature)s' % url_params)

    def get_url(self, params):
        '''Returns a standard geocoding api url.'''
        return 'http://%(domain)s/maps/api/elevation/json?%(params)s' % (
            {'domain': self.domain, 'params': urlencode(params)})
    
    def GetService_url(self, url, exactly_one=True):
        '''Fetches the url and returns the result.'''
        util.logger.debug("Fetching %s..." % url)
        page = urlopen(url)

        return self.parse_json(page, exactly_one)

    def GetElevation(self, LatLngSet, sensor = False, exactly_one = False):
        '''Get Elevation of input locations

        ``LatLngSet`` (required) Latitude and Longitude of one or more Locations

        ``sensor`` (required) Indicates whether or not the geocoding request
        comes from a device with a location sensor.
        This value must be either True or False.
        '''
        
        locations = []
        
        for [lat, lng] in LatLngSet:
            locations.append(str(lat) + "," + str(lng))
        
        locations = "|".join(locations)
        
        params = {
            'locations': locations,
            'sensor': str(sensor).lower()
        }

        if not self.premier:
            url = self.get_url(params)
        else:
            url = self.get_signed_url(params)

        return self.GetService_url(url, exactly_one)


    def parse_json(self, page, exactly_one=True):
        '''Returns location, (latitude, longitude) from json feed.'''
        if not isinstance(page, basestring):
            page = util.decode_page(page)
        self.doc = json.loads(page)
        results = self.doc.get('results', [])
    
        if not results:
            check_status(self.doc.get('status'))
            return None
            
        '''    
        elif exactly_one and len(results) != 1:
            raise ValueError(
                "Didn't find exactly one placemark! (Found %d)" % len(results))
        '''
        
        def parse_result(result):
            '''Get the components from a single json result.'''
            elevation = result['elevation']
            latitude = result['location']['lat']
            longitude = result['location']['lng']
            resolution = result['resolution']
            
            return (elevation, (latitude, longitude), resolution)
        
        if exactly_one:
            return parse_result(results[0])
        else:
            return [parse_result(result) for result in results]

            
def check_status(status):
    '''Validates error statuses.'''
    if status == 'ZERO_RESULTS':
        raise GoogleServiceResultError(
            'The Google service was successful but returned no results.')
            
    elif status == 'OVER_QUERY_LIMIT':
        raise GoogleServiceResultError(
            'The given key has gone over the requests limit in the 24'
            ' hour period or has submitted too many requests in too'
            ' short a period of time.')
            
    elif status == 'REQUEST_DENIED':
        raise GoogleServiceResultError(
            'Your request was denied, probably because of lack of a'
            ' sensor parameter.')
            
    elif status == 'INVALID_REQUEST':
        raise GoogleServiceResultError('Probably missing address or latlng.')
        
    else:
        raise GoogleServiceResultError('Unkown error.')

         
class GoogleServiceResultError(Exception):
    pass

