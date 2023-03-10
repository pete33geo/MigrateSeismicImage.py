# -*- coding: utf-8 -*-
"""
MigrateSeismicImage_v0.1.py

Created on Tue Jan 31 2023

@author: pete33geo
https://github.com/pete33geo/MigrateSeismicImage.py
"""
import numpy as np
import sys
from PIL import Image,ImageShow
from scipy.interpolate import LinearNDInterpolator as interpolate_fn

def MigrateSeismicImage(vel_model,png,dimensions,cutoff=False,save=True,show=False):
    """Apply a 2D depth migration to a png image of seismic data with known x
    and time dimensions. Units must be consistent across inputs. The 32bit png
    should be clipped to the data extent.
    
    Parameters
    ----------
    vel_model: np.array
        3D array containing meshgrids of x, depth, and velocity ('xy' indexing)
        Units must be consistent
    png : str
        File name of 32bit png type image
    dimensions : tuple
        Maximum x [m or km] and time [TWT, msec or sec] dimension
    cutoff : int/float (optional)
        Depth to cut-off data output. Default 'False' is max depth in vel_model
    save : bool (optional)
        Use Pillow to save a png of the results. Default is 'True'
    show : bool (optional)
        Use Pillow to preview the result in a new window. Default is 'False'

    Returns
    -------
    3D numpy array of shape (rows,columns,rgba)
    """    
    # Convert velocity model to time domain (OWT)
    #==========================================================================
    x = vel_model[0].T #convert velocity model to 'ij' indexing
    z = vel_model[1].T
    v = vel_model[2].T
    
    z_interval = np.diff(z,axis=1)
    
    owt = np.zeros(z.shape)
    owt[:,1:] = np.cumsum(z_interval / v[:,1:], axis=1)
    
    # Load image as an array of shape (rows,columns,rgba), and dimensionalise
    #==========================================================================
    img = Image.open(png)
    
    if img.mode != 'rgba':
        print("\nError: Image must be a 32-bit png with rgba channels\n")
        sys.exit()
    
    img = np.asarray(img)
    xmax = dimensions[0]
    tmax_owt = dimensions[1] / 2 ##convert to OWT
        
    #create meshgrid of xz coords corresponding to the pixels
    xaxis = np.arange(0,img.shape[1]) * (xmax / img.shape[1])
    taxis = np.arange(0,img.shape[0]) * (tmax_owt / img.shape[0])
    
    #dimensionalised x,t coords. We now have arrays with x, t, and z values
    ximg,timg = np.meshgrid(xaxis,taxis)
    
    # Interpolate z at each image pixel location
    #==========================================================================
    #take the velocity model points, with associated z and t data
    migrate = interpolate_fn((x.flatten(),owt.flatten()),z.flatten(),fill_value=999)
    #interpolate z values at image pixel locations
    depths = migrate(ximg.flatten(),timg.flatten())
    depths = depths.reshape(ximg.shape)
   
    # Resample results onto a regular grid for conversion to image
    #==========================================================================
    if cutoff:
        zlim = cutoff
    else:
        zlim = z.max()
    
    xpixels = img.shape[1]
    ypixels = int(xpixels / xmax * zlim)
    pixel_y = np.arange(0,ypixels) * (zlim / ypixels)
    
    img_out = np.zeros((ypixels,xpixels,4))
    
    for rgba in range(4):
        for i in range(img.shape[1]):
            colour_value = img[:,i,rgba] # column of rgba value in input image        
            img_out[:,i,rgba] = np.interp(pixel_y,depths[:,i],colour_value)
    
    print("\nDepth migrated {fname}\n".format(fname=png) )
    
    # Write regular grid to png image
    #==========================================================================
    img_png = Image.fromarray(img_out.astype(np.uint8))
   
    if show:
        ImageShow.show(img_png)
    if save:
        file = png[:-4] + '_depth'
        img_png.save(file + '.png')
        print("\nSaved {fname}.png\n".format(fname=file))
    
    return img_png
