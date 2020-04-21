"""
@author: Sergey.Vinogradov@noaa.gov
"""
from datetime import datetime
import numpy as np
from csdllib import oper

#==============================================================================
def getData (stationID,  dateRange, 
             product='waterlevelrawsixmin', datum='MSL', units='meters', verbose=False):
    
    """ 
    Allows for downloading the observations from NOAA's 
    Center for Operational Oceanographic Products and Services (COOPS)
    via OpenDAP server    http://opendap.co-ops.nos.noaa.gov .
    
    Args:
        stationID (str):              7 character-long CO-OPS station ID.
        dateRange (datetime, datetime): start and end dates of retrieval.
    
    Optional Args:        
        'product' (str):             
            WATER LEVEL: 
            'waterlevelrawsixmin' (=default), 'waterlevelrawonemin',
            'waterlevelverifiedsixmin',  'waterlevelverifiedhourly',
            'waterlevelverifiedhighlow', 'waterlevelverifieddaily', 
            'waterlevelverifiedmonthly',
            'highlowtidepredictions', 'predictions', 
            'harmonicconstituents',    'datums',             
            METEOROLOGY: 
            'barometricpressure', 'wind'. 
            
        'datum' (str): 'MSL' (=default), 'NAVD', 'IGLD', 'MTL',
            'station datum', 'MHW','MHHW','MLLW', 'MLW'.
        
        'units' (str): 'meters','feet', 'm/sec', 'knots','miles/hour'
        
        'tideFreq' (str): '6' (=default), '60'
        
    Returns:
        ('dates' (datetime), 'values' (float)): 
            retrieved time series record of observations.
            Note: for the 'wind' product, 'values' consist of 
            wind speed, wind direction and wind gust.
            
    Examples:
        now   = datetime.now()
        dates = (now-dt(days=3), now)
        tides = getdata('8518750', dates, product='predictions')        
        retrieves tidal water levels at The Battery, NY over the last 3 days.
        
    """
    # TODO:
    # Check dateRange
    # 'waterlevel*'       : months=12
    # 'waterlevelverifiedhighlow' : months=5*12
    # 'waterlevel*sixmin' : months=1
    # ''
    # If needed call sub-function to split dateRange into proper chunks
    # and call getdata recursively and concatenate the outputs
    
    ## Formulate, print and send the request
    serverSide  = 'https://opendap.co-ops.nos.noaa.gov/axis/webservices/'
    timeZoneID  = '0'

    unitID      = '1'  # feet, or knots
    if units   == 'meters' or units == 'm/sec':
        unitID  = '0'    
    elif units == 'miles/hour':
        unitID  = '2'

    tideFreq    = '6'  # use 60 for hourly tides
    tideFreqStr = ''
    if product == 'predictions':
        tideFreqStr = '&dataInterval=' + tideFreq
        
    request = ( serverSide + product + '/plain/response.jsp?stationId=' + 
               stationID + 
               '&beginDate=' + dateRange[0].strftime("%Y%m%d") + 
               '%20' + dateRange[0].strftime("%H:%M") + 
               '&endDate='   + dateRange[1].strftime("%Y%m%d") +
               '%20' + dateRange[1].strftime("%H:%M") + 
               '&datum=' + datum + '&unit=' + unitID + 
               '&timeZone=' + timeZoneID + tideFreqStr + 
               '&Submit=Submit')
    oper.sys.msg( 'i','Downloading ' + request)
           
    lines = oper.transfer.readlines_ssl (request, verbose)
    
    ## Parse the response
    dates  = []
    values = []   
    for line in lines:
        if ('waterlevel' in product):
            try:
                dates.append  (datetime.strptime(line[13:29],'%Y-%m-%d %H:%M'))
                values.append (float(line[31:38]))
            except:
                pass
        elif product == 'predictions':
            try:
                dates.append  (datetime.strptime(line[ 9:25],'%m/%d/%Y %H:%M'))
                values.append (float(line[26:]))
            except: 
                pass
        elif product == 'barometricpressure':
            try:
                dates.append  (datetime.strptime(line[13:29],'%Y-%m-%d %H:%M'))
                values.append (float(line[30:37]))
            except: 
                pass
        elif product == 'wind':
            try:
                dates.append  (datetime.strptime(line[13:29],'%Y-%m-%d %H:%M'))
                values.append ([float(line[30:37]),
                                float(line[38:45]),
                                float(line[46:53])])
            except: 
                pass
        else:
            oper.sys.msg( 'e','Product [' + product + '] is not yet implemented!')
            break
        
    return {'dates' : dates, 'values' : values}       

#==============================================================================
def readData (xmlFile):
    """
    Reads data from xmlFile instead from OpenDAP server (getData)
    Args:
        xmlFile (str): full path to xml data file
    Returns:
        ('dates' (datetime), 'values' (float)):
            parsed time series record of observations.
    """
   ## Parse the file
    dates  = []
    values = []
    lines = open(xmlFile).readlines()
    for line in lines:
        try:
            dates.append  (datetime.strptime(line[13:29],'%Y-%m-%d %H:%M'))
            values.append (float(line[30:38]))
        except:
            pass

    return {'dates' : dates, 'values' : values}

#==============================================================================
def writeData (data, outFile):
    """
    Writes data to outFile 
    Args:
        data (dict): 'dates' (datetime), 'values' (float)
        outFile (str): full path to xml data file
    """
    dates  = data['dates']
    values = data['values']
    with open(outFile,'w') as f:
        for n in range(len(dates)):
            line = " "*13 + \
                datetime.strftime(dates[n], '%Y-%m-%d %H:%M') + ' '+ \
                str(values[n]) + '\n'
            f.write (line)

#==============================================================================
def getStationInfo (stationID):
    
    """
    Downloads geographical information for a CO-OPS station
    from http://tidesandcurrents.noaa.gov
    
    Args:
        stationID (str):              7 character-long CO-OPS station ID
    
    Returns:
        'info' (dict): ['name']['state']['lon']['lat']
    Examples:
        & getStationInfo('8518750')['name']
        & 'The Battery'
    """
    request = ( 'https://tidesandcurrents.noaa.gov/stationhome.html?id=' +
               stationID )

    lines = oper.transfer.readlines (request)    
    
    try:
        for line in lines:
            if 'var station_name'  in line:
                stationName  = line.split('"')[1]
            if 'var station_state' in line:
                stationState = line.split('"')[1]
            if 'var lat'           in line:
                lat          = float(line.split('"')[1])
            if 'var lon'           in line:
                lon          = float(line.split('"')[1])           
        
        return {'name'  : stationName, 
                'state' : stationState,
                'lon'   : lon, 
                'lat'   : lat }
    except:
        oper.sys.msg( 'e','Cannot get info for  ' + stationID)
        return None


#==============================================================================
def getActiveStations (request = 'https://access.co-ops.nos.noaa.gov/nwsproducts.html?type=current'):
    """
    Downloads and parses the list of CO-OPS active tide gauges.
    """
    if 'http' in request:
        lines = oper.transfer.readlines (request)
    else:
        lines = open(request).readlines()

    active = dict()
    active['nos_id'] = []
    active['nws_id'] = []
    active['lon']    = []
    active['lat']    = []
    for line in lines:
        if line[0:4] == '<br>':
            try:
                active['nos_id'].append(int(line[5:12]))
                active['nws_id'].append(line[13:18])
                active['lon'].append(float(line[65:76]))
                active['lat'].append(float(line[38:49]))
            except:
                pass
    return active

#==============================================================================
def getNOSID (string):
    """
    Parses 7-digit NOS ID from the string (usually, a station description)
    """
    nosid = '0000000'
    st = string.split()
    for s in st:
        if len(s) == 7 and s.isdigit():
            nosid = s
    return nosid

#==============================================================================
def createAnomalyTable (csvFile, dates):
    """
    Reads all active CO-OPS stations via openDAP, computes anomaly(bias)
    and writes into a file in comma-delimited format
    """
    rightNow = datetime.utcnow()    

    f = open(csvFile,'w')
    header = 'NOS-ID, NWS-ID, lon, lat, Bias MSL (meters), Length of record (days),' + \
              datetime.strftime(dates[0],'%Y%m%d') +'--' + \
              datetime.strftime(dates[1],'%Y%m%d') + '\n'
    f.write(header)

    active = getActiveStations()

    for count in range(len(active['nos'])):
        
        nos_id = str(active['nos'][count])
        nws_id = str(active['nws'][count])        
        
        try:
            info = getStationInfo (nos_id)
            wlv  = getData(nos_id, dates, product='waterlevelrawsixmin')
            bias = np.mean(wlv['values'])
            if not np.isnan(bias):
                N    = len(wlv['values'])
                line = nos_id + ',' + nws_id + ','
                line = line + str(info['lon']) + ','
                line = line + str(info['lat']) + ','
                line = line + str(bias) + ','
                line = line + str(N/240.) + '\n'
                f.write(line)                    
        except:
            oper.sys.msg( 'warn','Failed to read ' + str(nos_id))
            
    f.close()
    oper.sys.msg( 'i','Elapsed time: ' +(datetime.utcnow()-rightNow).seconds +' sec')
    
