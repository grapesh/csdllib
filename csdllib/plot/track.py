"""
@author: grapesh@gmail.com
"""
import numpy as np

#==============================================================================
def add (ax, T, color='k',linestyle='-',markersize=1,zorder=1, fs=5):
    """
    Adds track to the current axis 'ax'
    """   
    ax.plot (T['lon'],T['lat'], color=color, linestyle=linestyle, \
              markersize=markersize,zorder=zorder)

    for n in range(len(T['lon'])):
              ax.text (T['lon'][n], T['lat'][n],str(int(T['vmax'][n])), \
                          color=color, fontsize=fs)
    return ax
                          
#==============================================================================
def quadrants (ax, T, neq, color='k', zorder=1):
    """
    Adds depiction of storm isotachs to current axis 'ax'
    """
    
    da = np.pi/180.  #  
    R  = 6370.       # Mean Earth Radius in km

    for n in range(len(T['lon'])):
        x = T['lon'][n]
        y = T['lat'][n]

        if T[neq][n] is not None:

            #Convert Quadrant values to km
            ne = T[neq][n][0]*1.852
            se = T[neq][n][1]*1.852
            sw = T[neq][n][2]*1.852
            nw = T[neq][n][3]*1.852

            label = neq
            if neq == 'rmax':
                label = str (int(T['vmax'][n]))           
           
            xiso = []
            yiso = []
            for a in np.arange(0.,        0.5*np.pi, da):
                
                dx = 180./(np.pi*R)*ne/np.cos( np.radians(y))
                dy = 180./(np.pi*R)*ne
                xiso.append( x + dx*np.cos(a)  )
                yiso.append( y + dy*np.sin(a)  )
                
            ax.text(x + dx + 0.05*dx, y, label, color=color, fontsize=7)
 
            for a in np.arange(0.5*np.pi,    np.pi, da):
                dx = 180./(np.pi*R)*nw/np.cos( np.radians(y))
                dy = 180./(np.pi*R)*nw
                xiso.append( x + dx*np.cos(a)  )
                yiso.append( y + dy*np.sin(a)  )                

            for a in np.arange(np.pi,    1.5*np.pi, da):
                dx = 180./(np.pi*R)*sw/np.cos( np.radians(y))
                dy = 180./(np.pi*R)*sw
                xiso.append( x + dx*np.cos(a)  )
                yiso.append( y + dy*np.sin(a)  )                

            for a in np.arange(1.5*np.pi, 2.*np.pi, da):
                dx = 180./(np.pi*R)*se/np.cos( np.radians(y))
                dy = 180./(np.pi*R)*se
                xiso.append( x + dx*np.cos(a)  )
                yiso.append( y + dy*np.sin(a)  )                
            
            ax.plot(xiso, yiso, color=color, zorder=zorder)
            ax.plot((xiso[0],xiso[-1]), (yiso[0],yiso[-1]), color=color, zorder=zorder)

    return ax        
