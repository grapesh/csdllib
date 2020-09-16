"""
@author: grapesh@gmail.com
"""
import csdllib as cs
from csdllib.methods.convert import ft2meters
import matplotlib
matplotlib.use('Agg',warn=False)
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.dates as mdates

import numpy as np
from datetime import timedelta as dt

#==============================================================================
def set (xlim, ylim, datums, floodlevels, zero='MSL',width=14, height=4.5):
    """
    stages the hydrograph plot with vertical datums and flood levels.
    Returns figure and axis handles.
    """
        
    fig, ax = plt.subplots(sharex=True, figsize=(width, height))
    ax2 = ax.twinx()
    ax.plot([],[])

    """
    TODO: Extract the below to addDatums() and addLevels()
    """
    if datums:

        datum_mhhw_ft = datums['datum_mhhw_ft']
        datum_mllw_ft = datums['datum_mllw_ft']
        datum_msl_ft  = datums['datum_msl_ft']
        datum_hat_ft  = datums['datum_hat_ft']

        shift = 0.
        datum_msl_m = 0
        if zero is 'MLLW':
            shift =  - datum_mllw_ft + datum_msl_ft
            datum_msl_m = ft2meters( datum_msl_ft )
    
    if floodlevels:

        fl_major_ft   = floodlevels['fl_major_ft']
        fl_moder_ft   = floodlevels['fl_moder_ft']
        fl_minor_ft   = floodlevels['fl_minor_ft']

        # Compute and plot minor flood level
        fl_minor_m = ft2meters( datum_mhhw_ft+fl_minor_ft-datum_msl_ft+shift ) 
        if not np.isnan(fl_minor_m) and fl_minor_m < ylim[1]:
            ax.plot(xlim[0], fl_minor_m, 'dr', markerfacecolor='r')
            ax.text(xlim[0], fl_minor_m,\
                    'Minor Flood: ' + str(np.round(fl_minor_m,2)),color='k',fontsize=7)
            p = patches.Rectangle((mdates.date2num(xlim[0]), fl_minor_m), \
                                mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                                ylim[1]-fl_minor_m, \
                                color='r',alpha=0.15)
            ax.add_patch(p)
                
        # Compute and plot moderate flood level
        fl_moder_m = ft2meters( datum_mhhw_ft+fl_moder_ft-datum_msl_ft+shift ) 
        if not np.isnan(fl_moder_m) and fl_moder_m < ylim[1]:
            ax.plot(xlim[0], fl_moder_m, 'dr', markerfacecolor='r')
            ax.text(xlim[0], fl_moder_m,\
                    'Moderate Flood: '+ str(np.round(fl_moder_m,2)),color='k',fontsize=7)
            p = patches.Rectangle((mdates.date2num(xlim[0]), fl_moder_m), \
                                mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                                ylim[1]-fl_moder_m, \
                                color='r',alpha=0.15)
            ax.add_patch(p)

        # Compute and plot major flood level
        fl_major_m = ft2meters( datum_mhhw_ft+fl_major_ft-datum_msl_ft+shift ) 
        if not np.isnan(fl_major_m) and fl_major_m < ylim[1]:
            ax.plot(xlim[0], fl_major_m, 'dr', markerfacecolor='r')
            ax.text(xlim[0], fl_major_m,\
                    'Major Flood: ' + str(np.round(fl_major_m,2)),color='k',fontsize=7)
            p = patches.Rectangle((mdates.date2num(xlim[0]), fl_major_m), \
                                mdates.date2num(xlim[1])-mdates.date2num(xlim[0]), \
                                ylim[1]-fl_major_m, \
                                color='r',alpha=0.15)
            ax.add_patch(p)

        # Compute and plot MHHW datum
        datum_mhhw_m = ft2meters( datum_mhhw_ft-datum_msl_ft+shift ) 
        if not np.isnan(datum_mhhw_m) and datum_mhhw_m < ylim[1]:
            ax.plot(xlim, [datum_mhhw_m, datum_mhhw_m], color='c')
            ax.plot(xlim[1], datum_mhhw_m, 'dc', markerfacecolor='c')
            ax.text(xlim[1] - dt(hours=6), 
                    datum_mhhw_m + 0.05, 'MHHW',color='c',fontsize=7)

        # Compute and plot MLLW datum
        datum_mllw_m = ft2meters( datum_mllw_ft-datum_msl_ft+shift ) 
        if not np.isnan(datum_mllw_m) and datum_mllw_m > ylim[0] and datum_mllw_m < ylim[1]:
            ax.plot(xlim, [datum_mllw_m, datum_mllw_m], color='c')
            ax.plot(xlim[1], datum_mllw_m, 'dc', markerfacecolor='c')
            ax.text(xlim[1] - dt(hours=6), 
                    datum_mllw_m + 0.05, 'MLLW',color='c',fontsize=7)

        # Compute and plot HAT datum
        datum_hat_m  = ft2meters( datum_hat_ft-datum_msl_ft+shift ) 
        if not np.isnan(datum_hat_m) and datum_hat_m < ylim[1]:
            ax.plot(xlim, [datum_hat_m, datum_hat_m], color='y')
            ax.plot(xlim[1], datum_hat_m, 'dy', markerfacecolor='y')
            ax.text(xlim[1] - dt(hours=6), 
                    datum_hat_m  + 0.05, 'HAT',color='y',fontsize=7)

        # Plot LMSL datum
        if not np.isnan(shift):
            ax.plot(xlim, [ft2meters(shift), ft2meters(shift)], color='k')
            ax.plot(xlim[1], ft2meters(shift), 'dk',color='k')
            ax.text(xlim[1] - dt(hours=6), 0.05+ft2meters(shift), 'LMSL',color='k',fontsize=7)

        # Plot 'now' line
        #ax.plot( [now, now], ylim, 'k',linewidth=1)
        #ax.text(  now + dt(hours=1),  ylim[1]-0.4,'N O W', color='k',fontsize=6, 
        #          rotation='vertical', style='italic')
    
    return fig, ax, ax2

#==============================================================================
def add (ax, dates, values, color='k',label='',lw=2):
    """
    Adds time series and its paraphernalia to the axis
    """
    ax.plot(dates, values, color=color, label=label,linewidth=lw)
    return ax

#==============================================================================
def addDatums(ax):
    """
    Adds vertical datums to the axis
    """
    cs.oper.sys.msg('e','function is not yet implemented')
    return ax

#==============================================================================
def addLevels(ax):
    """
    Adds (flood) levels to the plot
    """
    cs.oper.sys.msg('e','function is not yet implemented')
    return ax


