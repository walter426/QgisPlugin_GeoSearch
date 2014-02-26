#directions.py

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


class Directions(ServiceParser):
    '''Directions using the Google Maps v3 API.'''
    
    def __init__(self):
        ServiceParser.__init__(self, 'directions', 'routes')

    def GetDirections(self, origin, destination, sensor = False, mode = None, waypoints = None, alternatives  = None, avoid = None, language  = None, units = None,
                        region = None, departure_time  = None, arrival_time = None):
        '''Get Directions Service
        Pls refer to the Google Maps Web API for the details of the remained parameters
        '''
        
        params = {
            'origin': origin,
            'destination': destination,
            'sensor': str(sensor).lower()
        }

        
        if mode:
            params['mode'] = mode
            
        if waypoints:
            params['waypoints'] = waypoints
            
        if alternatives:
            params['alternatives'] = alternatives
            
        if avoid:
            params['avoid'] = avoid
            
        if language:
            params['language'] = language
            
        if units:
            params['units'] = units
            
        if region:
            params['region'] = region
            
        if departure_time:
            params['departure_time'] = departure_time
            
        if arrival_time:
            params['arrival_time'] = arrival_time
        
        
        if not self.premier:
            url = self.get_url(params)
        else:
            url = self.get_signed_url(params)

        return self.GetService_url(url)
        
            