# MigrateSeismicImage.py
Apply a 2D depth migration to a .png image of seismic data with known x and time dimensions.

## Data inputs
- A png (32bit with rgba channels) image clipped to the data extent
- 2D velocity model as a 3D array, consisting x, depth, and velocity (2D meshgrids with 'xy' indexing)
- Note that inputs must be in consistent units

## Dependencies
- Standard python libraries (Numpy and Scipy)
- Image loading and saving requires [Pillow](https://pillow.readthedocs.io/en/stable/)
## Example: Depth migrate an image of seismic data using a velocity model
```
import numpy as np

#example velocity model structure 
x = np.arange(0,1000,0.1)
z = np.arange(0,10,0.1)

x,z = np.meshgrid(x,z, indexing='xy')
vel = z / 2 + 2 #seismic velocities with same dimensions as x and z

velocity_model = np.array([x,z,vel])

MigrateSeismicImage(vel_model=velocity_model,
                    png='your_data.png',
                    dimensions=(5,1000),
                    cutoff=5,
                    save=True,
                    show=True)
```
