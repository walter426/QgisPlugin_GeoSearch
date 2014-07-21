#GoogleMapsServiceParser.py

"""
/***************************************************************************
 Google Maps API
                                 A Python module
Provide Goole Maps API Web Service under Python 
                             -------------------
        begin                : 2014-02-14
        copyright            : (C) 2014 by Walter Tsui
        email                : waltertech426@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

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

import util



class ServiceParser:
    def __init__(self, service, result_name, domain='maps.googleapis.com', protocol='http',
                 client_id=None, secret_key=None):
        '''
        Initialize a Google maps web service.

        ''service'' required Google maps web service
        
        API authentication is only required for Google Maps Premier customers.

        ``domain`` should be the localized Google Maps domain to connect to. The default
        is 'maps.google.com', but if you're geocoding address in the UK (for
        example), you may want to set it to 'maps.google.co.uk' to properly bias results.

        ``protocol`` http or https.
        
        ``client_id`` Premier account client id.
        
        ``secret_key`` Premier account secret key.
        '''
        
        self.service = service
        self.result_name = result_name
        
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
                      'service': self.service, 'params': urlencode(params)}
                      
        secret = base64.urlsafe_b64decode(self.secret_key)
        url_params['url_part'] = (
            '/maps/api/%(service)s/json?%(params)s' % url_params)
        signature = hmac.new(secret, url_params['url_part'], hashlib.sha1)
        url_params['signature'] = base64.urlsafe_b64encode(signature.digest())

        return ('%(protocol)s://%(domain)s%(url_part)s'
                '&signature=%(signature)s' % url_params)

    def get_url(self, params):
        '''Returns a standard geocoding api url.'''
        return 'http://%(domain)s/maps/api/%(service)s/json?%(params)s' % (
            {'domain': self.domain, 'service': self.service, 'params': urlencode(params)})
    
    def GetService_url(self, url):
        '''Fetches the url and returns the result.'''
        page = urlopen(url)

        return self.parse_json(page)


    def parse_json(self, page):
        '''Returns json feed.'''
        if not isinstance(page, basestring):
            page = util.decode_page(page)
            
        self.doc = json.loads(page)
        results = self.doc.get(self.result_name, [])
    
        if not results:
            self.check_status(self.doc.get('status'))
            return None
            
            
        return results
            
            
    def check_status(self, status):
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

