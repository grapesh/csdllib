"""
@author: Sergey.Vinogradov@noaa.gov
"""

import numpy as np
import datetime
from datetime import timedelta
from csdllib import oper

#============================================================================== 
def nearest(items, pivot):
    """
    Finds an item in 'items' list that is nearest in value to 'pivot'
    """
    nearestVal = min(items, key=lambda x: abs(x - pivot))
    try:
        items = items.tolist()
    except:
        pass
    indx = items.index(nearestVal)
    return nearestVal, indx


#==============================================================================
def distanceMatrix(x0, y0, x1, y1):
    """
    Computes euclidean distance matrix, fast
    from <http://stackoverflow.com/questions/1871536>
    """    
    oper.sys.msg('i', 'Computing distance matrix...')
    obs    = np.vstack((x0, y0)).T
    interp = np.vstack((x1, y1)).T

    d0 = np.subtract.outer(obs[:,0], interp[:,0])
    d1 = np.subtract.outer(obs[:,1], interp[:,1])

    return np.hypot(d0, d1)

#==============================================================================
def shepardIDW(x, y, v, xi, yi, p=2):
    """
    Computes Shepard's invese distance weighted interpolation
    Args:
        x, y, v (float) : arrays for data coordinates and values
        xi,  yi (float) : arrays for grid coordinates
        p         (int) : scalar power (default=2)
    Returns:
        vi      (float) : array of v interpolated onto xi and yi
    """       
    dist = distanceMatrix(x, y, xi, yi)    

    oper.sys.msg( 'i','Computing IDW...')
    vi = np.zeros(len(xi), dtype=float)
    weights = 1.0/np.power(dist, p)
    
    #TODO: Optimize!
    for n in range(len(xi)):
        A = 0.
        B = 0.
        for j in range(len(x)):
            A = A + weights[j,n]*v[j]
            B = B + weights[j,n]
        vi[n] = A/B
    return vi


#==============================================================================
def taperLinear (z_full, z_zero, zg, vg):
    """
    Tapers the values of the field to zero in between the two specified depths
    Args:
        z_full (float) : depth at which the tapering starts 
        z_zero (float) : depth at which the field fully tapers to zero
        zg     (float) : array of depths (larger numbers are deeper)
        vg     (float) : array of values to taper        
    Returns:
        vg     (float) : tapered array
    """
    oper.sys.msg( 'i','Computing linear taper...')
    
    #TODO: Optimize
    for n in range(len(vg)):
        w = (zg[n]-z_zero)/(z_full-z_zero)
        vg[n] = w*vg[n]
    return vg

#==============================================================================
def taperExp (z_full, z_zero, zg, vg):
    """
    Tapers the values of the field to zero in between the two specified depths
    Args:
        z_full (float) : depth at which the tapering starts 
        z_zero (float) : depth at which the field fully tapers to zero
        zg     (float) : array of depths (larger numbers are deeper)
        vg     (float) : array of values to taper        
    Returns:
        vg     (float) : tapered array
    """
    oper.sys.msg( 'i','Computing exponential taper...')
    
    #TODO: Optimize
    for n in range(len(vg)):
        #w = (zg[n]-z_zero)/(z_full-z_zero)
        if zg[n]>z_full:
            w     = z_zero/(z_zero-z_full)*(z_full/zg[n]-1.0) + 1.0
            vg[n] = w*vg[n]
    return vg


#============================================================================== 
def retime (obsDates, obsVals, modDates, modValsMasked, refStepMinutes=6):
    """
    Projects two timeseries (obsDates, obsVals) and (modDates, modVals)
    onto a common reference time scale with a resolution defined by
    refStepMinutes. 
    Note: tolerance for dates projection is half of refStepMinutes.
    Args:
        obsDates (datetime np.array of length Lobs ) : dates  for timeseries 1
        obsVals  (np.array of length Lobs)           : values for timeseries 1
        modDates (datetime np.array of length Lmod ) : dates  for timeseries 2
        modVals  (np.array of length Lmod)           : values for timeseries 2
        refStepMinutes (int, default=6)              : projection time step.
    Returns:
        refDates    (datetime np.array)  : projection dates
        obsValsProj (np.array)           : projected values of timeseries 1
        modValsProj (np.array)           : projected values of timeseries 2
    """
    refDates    = []
    obsValsProj = []
    modValsProj = []

    #Sort by date
    obsDates  = np.array(obsDates)
    obsVals   = np.array(obsVals)
    ind       = np.argsort(obsDates)
    obsDates  = obsDates[ind]
    obsVals   = obsVals[ind]
    # Remove nans
    ind       = np.logical_not(np.isnan(obsVals))
    obsDates  = obsDates[ind]
    obsVals   = obsVals[ind]
        
    #Sort by date
    modVals   = np.ma.filled(modValsMasked, np.nan)
    modDates  =  np.array(modDates)
    modVals   =  np.array(modVals)
    ind       = np.argsort(modDates)
    modDates  = modDates[ind]
    modVals   = modVals[ind]
    # Remove nans
    #Rid of mask
    if hasattr(modVals,'mask'):
        np.ma.set_fill_value(modVals, np.nan)   
    
    ind       = np.logical_not(np.isnan(modVals))
    modDates  = modDates[ind]
    modVals   = modVals[ind]

    # Create reference time line
    refStart = np.maximum(np.min(obsDates), np.min(modDates))
    refEnd   = np.minimum(np.max(obsDates), np.max(modDates))
    refStep  = timedelta(minutes=refStepMinutes)
    prec     = timedelta(minutes=0.5*refStepMinutes)
   
    refDates = np.arange(refStart, refEnd, refStep).astype(datetime.datetime)

    # Project obs and model onto reference time line
    obsValsProj  = []    
    modValsProj  = []

    for t in refDates:
        #find t in obsDates within refStep
        nearestObsDate, idx = nearest(obsDates, t)
        if abs(nearestObsDate - t) < prec:
            nearestObsVal   = obsVals[idx]
            obsValsProj.append (nearestObsVal)
        else:
            obsValsProj.append (np.nan)

        nearestModDate, idx = nearest(modDates, t)
        if abs(nearestModDate - t) < prec:
            nearestModVal   = modVals[idx]
            modValsProj.append (nearestModVal)
        else:
            modValsProj.append (np.nan)

    return refDates, np.array(obsValsProj), np.array(modValsProj)

