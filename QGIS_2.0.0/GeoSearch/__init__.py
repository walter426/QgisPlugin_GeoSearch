# -*- coding: utf-8 -*-
"""
/***************************************************************************
 GeoSearch
                                 A QGIS plugin
 Search location by words like google map; Calculate Distance between two points on mapCanvas.
                             -------------------
        begin                : 2013-07-10
        copyright            : (C) 2013 by Walter Tsui
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
 This script initializes the plugin, making it known to QGIS.
"""


def name():
    return "GeoSearch"


def description():
    return "Search location by words like google map; Calculate Distance between two points on mapCanvas."


def version():
    return "Version 0.05.04"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "2.0"

def author():
    return "Walter Tsui"

def email():
    return "waltertech426@gmail.com"

def classFactory(iface):
    # load GeoSearch class from file GeoSearch
    from geosearch import GeoSearch
    return GeoSearch(iface)
