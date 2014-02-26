#geocode.py

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

from GoogleMapsServiceParser import *


class Geocoding(ServiceParser):
    '''Elevation using the Google Maps v3 API.'''
    
    def __init__(self, format_string = '%s'):
        ServiceParser.__init__(self, 'geocode', 'results')
        self.format_string = format_string
                
    def geocode(self, string, bounds=None, region=None,
                language=None, sensor=False):
        '''Geocode an address.
        Pls refer to the Google Maps Web API for the details of the parameters
        '''
        if isinstance(string, unicode):
            string = string.encode('utf-8')

        params = {
            'address': self.format_string % string,
            'sensor': str(sensor).lower()
        }

        
        if bounds:
            params['bounds'] = bounds
            
        if region:
            params['region'] = region
            
        if language:
            params['language'] = language
            

        if not self.premier:
            url = self.get_url(params)
        else:
            url = self.get_signed_url(params)

        return self.GetService_url(url)

        
    def reverse(self, point, language=None, sensor=False):
        '''Reverse geocode a point.
        Pls refer to the Google Maps Web API for the details of the parameters
        '''
        params = {
            'latlng': point,
            'sensor': str(sensor).lower()
        }
        
        if language:
            params['language'] = language

        if not self.premier:
            url = self.get_url(params)
        else:
            url = self.get_signed_url(params)

        return self.GetService_url(url)
        
            