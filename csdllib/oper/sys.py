"""
@author: Sergey.Vinogradov@noaa.gov
"""

import datetime
from configparser import ConfigParser
import io

#==============================================================================
def timeStamp():
    msg('time', str(datetime.datetime.utcnow()) + ' UTC')

#==============================================================================
def stampToDate (stamp):
    return datetime.datetime.strptime(stamp, "%Y%m%d")

#==============================================================================
def dateToStamp (date):
    YYYY = str(date.year).zfill(4)
    MM   = str(date.month).zfill(2)
    DD   = str(date.day).zfill(2)
    return YYYY+MM+DD

#==============================================================================
def msg (msgType, msge):
    '''
    Customize standard I/O here.
    '''
    #print ('')
    if msgType.lower().startswith('i'):
        print ('[Info]: ' + msge)
    elif msgType.lower().startswith('w'):
        print ('[Warn]: ' + msge)
    elif msgType.lower().startswith('e'):
        print ('[Error]: '+ msge)
    elif msgType.lower().startswith('t'):
        print ('[Time]: ' + msge)
    else:
        print ('[    ]: ' + msge)
    
#==============================================================================
def removeInlineComments(cfgparser, delimiter):
    '''
    Per https://stackoverflow.com/questions/9492430/inline-comments-for-configparser
    '''
    for section in cfgparser.sections():
        [cfgparser.set(section, item[0], item[1].split(delimiter)[0].strip()) for item in cfgparser.items(section)]
    return cfgparser

#==============================================================================
def config ( iniFile ): 
    """
    Loads configuration file
    """
    with open(iniFile) as f:
        sample_config = f.read()

    config = ConfigParser(allow_no_value=True)
    config.readfp( io.StringIO(sample_config) )
    config = removeInlineComments(config, '#') 

    dictionary = {}
    for section in config.sections():
        dictionary[section] = {}
        for option in config.options(section):
            dictionary[section][option] = config.get(section, option)

    return dictionary
