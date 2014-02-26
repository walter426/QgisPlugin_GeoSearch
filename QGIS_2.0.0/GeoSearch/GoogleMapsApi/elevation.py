#elevation.py

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


class Elevation(ServiceParser):
    '''Elevation using the Google Maps v3 API.'''
    
    def __init__(self):
        ServiceParser.__init__(self, "elevation", 'results')

    def GetElevation(self, LatLngSet, sensor = False):
        '''Get Elevation of input locations
        LatLngSet: An coordinate array will be converted to proper location format here
        
        Pls refer to the Google Maps Web API for the details of the remained parameters
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

        return self.GetService_url(url)
        
            