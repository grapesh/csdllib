# -*- coding: utf-8 -*-
"""
Created on Thu Mar 16 10:02:14 2017

@author: grapesh@gmail.com
"""
import os
import numpy as np
from datetime import datetime
from datetime import timedelta
import csdllib
import netCDF4
import csv 

#==============================================================================
def readStations (f, fields):
    """
    Reads nyhops stations
    """
    return csdllib.data.parse.csvTable (f, fields)

#==============================================================================
def readTimeSeries (ncFile, stationsList, stationsFields, ncVar = 'elev', verbose=1):
    """
    Reads time series of the variable stored in netCDF file.
    Requires 'stationsList' and 'stationsFields' lists, 
    as it is read by nyhops.readStations()
    """
    if verbose:
        csdllib.oper.sys.msg('i', 'Reading [' + ncVar + '] from ' + ncFile)
    if not os.path.exists (ncFile):
        csdllib.oper.sys.msg('e', 'File ' + ncFile + ' does not exist.')
        return
    
    nc  = netCDF4.Dataset( ncFile )
    fld = nc.variables[ncVar][:]
    tim = nc.variables['time'][:]    

    lon      = []
    lat      = []
    stations = []
    ids      = []
    for s in stationsList:
        lon.append ( float(  s [ stationsFields.index('lon') ]) )
        lat.append ( float(  s [ stationsFields.index('lat') ]) )
        stations.append ( s [ stationsFields.index('station_name') ] )
        ids.append ( s [ stationsFields.index('nosid') ] )
	
    baseDate = datetime.strptime(nc.variables['time'].base_date[0:19],
                                 '%Y-%m-%d %H:%M:%S')
    realtime = np.array([baseDate + 
                         timedelta(seconds=int(tim[i])) 
                         for i in range(len(tim))])
						 
    return  {'lat'       : lat, 
	         'lon'       : lon,
	         'time'      : realtime, 
             'base_date' : baseDate, 
             'zeta'      : fld,
             'stationIDs'    : ids,  
             'stationNames'  : stations }   


    


