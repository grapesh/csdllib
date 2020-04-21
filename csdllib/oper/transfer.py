"""
@author: Sergey.Vinogradov@noaa.gov
"""
import os
from urllib.request import urlopen
import uuid
import ssl
from csdllib.oper.sys import msg

#==============================================================================
def download (remote, local):
    """
    Downloads remote file (using urllib2) if it does not exist locally.
    """
    if not os.path.exists(local):
        msg ('info','Downloading ' + remote + ' as ' + local)
        try:
            f = urlopen(remote)
            data = f.read()
            with open(local, "wb") as code:  #Python3 required b option now!
                code.write(data)
            f.close()
        except:
            msg ('warn', 'file ' + remote + ' was not downloaded. trying to cp...')
            try:
                os.system('cp ' + remote + ' ' + local)
            except:
                msg ('warn', 'file ' + remote + ' could not be copied')
            
    else:
        msg('warn','file ' + local + ' exists, skipping.')

#==============================================================================
def refresh (remote, local):
    """
    Downloads remote file (using urllib2), overwrites local copy if exists.
    """
    if not os.path.exists(local):
        msg('info', 'downloading ' + remote + ' as ' + local)
    else:
        msg ('info', 'overwriting ' + local + ' file with ' + remote)
    try:
        f = urllib2.urlopen(remote)
        data = f.read()
        with open(local, "wb") as code:
            code.write(data)
    except:
        msg('warn', 'file ' + remote + ' was not downloaded. trying to cp...')
        try:
            os.system('cp ' + remote + ' ' + local)
        except:
            msg('warn', 'file ' + remote + ' could not be copied')

#==============================================================================
def readlines (remote, verbose=False, tmpDir=None, tmpFile=None):
    """
    1. Downloads remote into temporary file
    2. Reads line by line
    3. Removes temporary file
    """
    
    if tmpFile is None:
        tmpFile  = str(uuid.uuid4()) + '.tmp' # Unique temporary name
    if tmpDir is not None:
        tmpFile = os.path.join(tmpDir, tmpFile)

    if verbose:
        msg('info','downloading ' + remote + ' as temporary ' + tmpFile)

    f        = open( tmpFile, 'wb' )
    response = urlopen(remote)
    f.write ( response.read() )
    f.close ()
 
    lines  = open(tmpFile).readlines()
    os.remove( tmpFile )
        
    return lines

#==============================================================================
def readlines_ssl (remote, verbose=False, tmpDir=None, tmpFile=None):
    """
    Deals with expired SSL certificate issue.
    1. Downloads remote into temporary file
    2. Reads line by line
    3. Removes temporary file
    """
    lines = []

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode    = ssl.CERT_NONE 
 
    if tmpFile is None:
        tmpFile  = str(uuid.uuid4()) + '.tmp'
    if tmpDir is not None:
        tmpFile = os.path.join(tmpDir, tmpFile)

    if verbose:
        msg ('info', 'downloading ' + remote + ' as temporary ' + tmpFile)

    f = open( tmpFile, 'wb' )
    try:
        response = urlopen(remote, context = ctx)
        f.write( response.read() )     
    except:
        msg ('error', response)       
    f.close ()

    lines  = open(tmpFile).readlines()
    os.remove( tmpFile )

    return lines

#==============================================================================
def upload(localFile, userHost, remoteFolder):
    cmd = 'scp -q ' + localFile + ' ' + userHost + ':' + remoteFolder
    if os.system(cmd) == 0:
        msg('info', 'executed ' + cmd)
    else:
        msg('error', 'failed to execute ' + cmd)
        
#==============================================================================
def cleanup (tmpDir='.', tmpExt='.tmp'):
    """
    Removes files with extension tmpExt from the tmpDir.
    """
    files = os.listdir(tmpDir)
    for file in files:
        if file.endswith(tmpExt):
            os.remove(os.path.join(tmpDir,file))