"""
@author: grapesh@gmail.com
"""
import os
import glob

#==============================================================================
def findLatestCycle (dirMask):
    
    dirs = glob.glob(dirMask+'*')
    latestDir = max(dirs, key=os.path.getctime)    
    D = os.path.basename(latestDir).split('.')[-1]

    files = glob.glob(latestDir + '/*.points.cwl.nc')
    latestFile = max(files)

    F = os.path.basename(latestFile)
    latestCycle =  D + F[F.find('.t')+2:F.find('z.')]

    return latestCycle
