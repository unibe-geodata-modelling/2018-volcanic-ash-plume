import numpy as np
from matplotlib import pyplot as plt
import matplotlib as m
from matplotlib.pyplot import colorbar
from netCDF4 import *
import math
import matplotlib.colors as mcolors
from mpl_toolkits.basemap import  Basemap


# This model calculates 2D ash plume dispersion
# 03.07.2018, Author: benjamin.schuepbach@students.unibe.ch
# 25.07.2018, Author: christoph.vonmatt@students.unibe.ch

''' First Section___________________________________________
 
 In this first section the preliminary parameters are established. This includes the read-in of wind data,
 specification of volcanic eruption type.
 This can either be user input or stored eruption characteristics (Eyjafjallajökull 2010 eruption).
 Wind data has to be provided by the user in all scenarios.
 Currently only supported data-format for the wind is NetCDF.
 '''

# Decide whether test is run or simulation based on own provided wind fields is executed
print("Choose if you want to run:\n"
      "1 Test \n"
      "2 Simulation")
test = 0
while test < 1 or test > 2:
    test = int(input("Type your choice:"))

if test == 2:
    test = False
else:
    test = True

if not test:
    # Wind Datasets for April 2010
    u_windFile_apr = Dataset("ERAInterim_April2010.nc")
    v_windFile_apr = Dataset("ERAInterim_April2010.nc")

    # Wind Datasets for May 2010
    u_windFile_mai = Dataset("ERAInterim_May2010.nc")
    v_windFile_may = Dataset("ERAInterim_May2010.nc")

    # Specify here the wind file used in the simulation
    u_windFile = u_windFile_apr
    v_windFile = v_windFile_apr

    # Pre-Processing of wind-data
    print(u_windFile.variables.keys())
    print(v_windFile.variables.keys())
    keys_u = u_windFile.variables.keys()
    keys_v = v_windFile.variables.keys()

    lon_key = "longitude"
    lat_key = "latitude"
    time_key = "time"
    u_key = "u"
    v_key = "v"

    # Retrieving longitude, latitude and timesteps
    lon1 = u_windFile.variables[lon_key]
    lat1 = u_windFile.variables[lat_key]

    lon = np.array(u_windFile.variables[lon_key])
    lon = lon - 180
    lat = np.array(u_windFile.variables[lat_key])
    dim_lon = len(lon)
    dim_lat = len(lat)

    time_u = u_windFile.variables[time_key][:]
    time_v = v_windFile.variables[time_key][:]
    # convert time to date-format
    time_units = u_windFile.variables[time_key].units
    time_calender = u_windFile.variables[time_key].calendar
    time_converted = num2date(time_u, time_units, calendar=time_calender)

    timesteps = len(time_converted)
    # number of days (4 timesteps each day)
    days = len(time_converted) / 4

    # Manual specification of the days which should be used!
    try:
        print("Your wind dataset contains {} timesteps (equals {} days).".format(timesteps, int(days)))
        start = int(input("Type here the start day of the analysis: (If empty all steps are used!)")) - 1
        end = int(input("Type here the end day of the analysis:")) - 1
        if start < 0:
            start = 0
        start = start * 4
        end = end * 4 + 4
    except ValueError:
        print("All timesteps will be used.")
        start = 0
        end = timesteps

    # Wind-Data (for all timesteps)
    u_wind = u_windFile.variables[u_key]
    v_wind = v_windFile.variables[v_key]

    # Adjust length according to timesteps
    # u_wind = u_wind[start:end,:,:]
    # v_wind = v_wind[start:end,:,:]


# Defines the model resolution
resolution = 80

# Calculating Distance for Diagonal transport: with cosinus(45°)
resolution_extended = resolution / math.cos(0.785398)

# hourly resolution of the model
hourly_res = 6

# User input for ash plume characteristics
# ash plume characteristics are: Mass eruption rate (MER), plume height, eruption durance, percentage of ash particles
# <63 micrometer
# Note: The height parameter won't be used unless there are several wind fields at different heights available
#       (Requiring feature add by yourself)
# Mode 1: lets the user choose the input parameter itself
# Mode 2: Eyjafjallajökull 2010 characteristics

mode = 0
while mode == 0 or mode >= 3:
    print("Mode description: \n"
          + "1 manual inputs \n"
          + "2 Eyjafjallajökull 2010 scenario")
    mode = int(input("Please chose mode:"))

# TODO: convert the following lines to a switch and define for each mode seperate functions! (each returning a list of
# Input parameters

if mode == 1:
    print("Manual mode")
    print("___________")
    # Specification of the volcano coordinates
    # Conventions: coordinates: North = +, South = -, East = +, West = -
    lon_vol = float(input("Type the longitude of the volcano (decimal degrees):"))
    lat_vol = float(input("Type the latitude of the volcano (decimal degrees):"))

    # Specification of the plume height
    height = -1
    while height <= 0 or height >= 15001:
        height = int(input("Please specify your plume height (m, 0-15000): "))

    # Specification of the eruption durance
    durance = 0
    while durance <= 0:
        durance = int(input("Please specify the eruption durance:"))

    # Specification of the ash particle fraction below 63 microns
    ash_fraction = float(input("Type in the m63-mass fraction (fraction < 63 micrometer) (value 0-1):"))
    while ash_fraction < 0 or ash_fraction > 1:
        print("Value was not between 0 and 1!")
        ash_fraction = float(input("Type in the m63-mass fraction (fraction < 63 micrometer) (value 0-1):"))

    # Specification of the mass and volume rates
    mass_rate = 0
    volume_rate = 0
    while (mass_rate <= 0) or (volume_rate <= 0):
        print("Both volume rate and mass rate must be greater than zero!")
        if mass_rate <= 0:
            mass_rate = int(input("Type in the mass rate (g/s):"))
        if volume_rate <= 0:
            volume_rate = int(input("Type in the volume rate (m^3/s):"))

    # Print a summary
    print("You have chosen the following parameters:")
    print("Height: {}".format(height))
    print("Durance: {}".format(durance))
    print("Ash-Fraction: {}".format(ash_fraction))
    print("Mass rate: {}".format(mass_rate))
    print("Volume rate: {}".format(volume_rate))

    # Ash concentration calculation # TODO: maybe apply adjustments according to Gudmundsson-Formula!
    concentration = np.array(mass_rate) * ash_fraction / np.array(volume_rate) / (resolution * resolution)

    concentration = 400 #TODO: CHANGE BACK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


if mode == 2:
    # here the specific characteristics of the Eyjafjallajökull eruption are specified.
    print("Mode 2: Eyjafjallajökull 2010 eruption characteristics.")

    lon_vol = -19.625
    lat_vol = 63.625

    height =  [0, 0, 5, 7.5, 5.5, 5.5, 5.5, 3, 4, 3.5, 5,
              5, 6, 7, 6, 5, 5.5, 5, 3, 2.5, 2.5, 2.5, 2.5, 2.5, 3, 2.5, 2.5, 2.5, 3, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 3,
              3, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 3.5, 3, 2, 3, 5, 5, 5, 4.5, 4.5, 4, 3.5, 3.5, 3, 2.5, 2.5, 7.5, 4.5, 5,
              5.5, 4, 3, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 4.5, 3.5, 3, 4, 5,
              5.5, 5.5, 5.5, 6, 6, 5, 5, 5.5, 5, 5, 5, 5, 5, 4, 4.5, 4, 4.5, 4.5, 4, 4.5, 4.5, 4.5, 4, 3, 4, 5, 4.5,
              4.5, 4, 4.5, 5, 5, 5, 5.5, 8, 8, 5, 5, 5, 5, 5, 5, 5, 5.5, 5.5, 6, 7, 7, 6, 5.5, 7, 5.5, 5, 4.5, 5, 5,
              4.5, 4.5, 4.5, 3.5, 3, 4, 3.5, 4, 4, 3, 3, 2.5, 2.5, 2.5, 2.5, 2.5]

    durance = len(height)

    # Tephra mass rate (in g/s)
    mass_rate = [0, 0, 550000000, 1000000000,  700000000, 100000000, 100000000, 50000000, 50000000, 100000000,
                 500000000, 550000000, 550000000, 550000000, 500000000, 100000000, 400000000, 400000000, 50000000,
                 50000000, 50000000, 0, 50000000, 50000000, 50000000, 0, 50000000, 50000000, 50000000, 0, 50000000, 0,
                 50000000, 50000000, 50000000, 0, 50000000, 50000000, 0, 0, 50000000, 50000000, 0, 0, 100000000,
                 100000000, 100000000, 100000000, 50000000, 0, 0, 50000000, 0, 0, 500000000, 100000000, 100000000,
                 300000000, 50000000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 50000000, 0, 0, 0, 0, 0, 0, 50000000, 50000000,
                 50000000, 50000000, 50000000, 200000000, 100000000, 150000000, 350000000, 850000000, 50000000,
                 50000000, 150000000, 50000000, 50000000, 50000000, 50000000, 50000000, 50000000, 50000000, 50000000,
                 50000000, 50000000, 50000000, 50000000, 50000000, 50000000, 50000000, 50000000, 50000000, 50000000,
                 50000000, 50000000, 50000000, 50000000, 50000000, 250000000, 150000000, 50000000, 50000000, 50000000,
                 50000000, 50000000, 250000000, 300000000, 550000000, 500000000, 250000000, 50000000, 250000000,
                 50000000, 250000000, 300000000, 300000000, 350000000, 400000000, 450000000, 300000000, 300000000,
                 400000000, 300000000, 50000000, 50000000, 100000000, 50000000, 50000000, 50000000, 50000000, 50000000,
                 0, 50000000, 0, 50000000, 50000000, 50000000, 50000000, 0, 0, 0, 0, 0]

    volume_rate = [100, 100, 300, 400, 300, 100, 100, 100, 100, 100, 200, 300, 300, 300, 200, 100, 200, 200, 100, 100,
                   100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
                   100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200, 100, 100, 200, 100, 100,
                   100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
                   100, 100, 100, 200, 400, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
                   100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200,
                   300, 200, 100, 100, 100, 100, 100, 200, 200, 200, 200, 200, 200, 200, 200, 200, 100, 100, 100, 100,
                   100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]

    ash_fraction = 0.5
    # TODO: check the formula for concentration retrieval in Gudmundsson et al. 2012; S.7 (Ash generation..."
    concentration = np.array(mass_rate) * ash_fraction / np.array(volume_rate) / (resolution * resolution)

""" Actual Eruption model implementation starts here (physics)

For the dispersal we tried to use a simplification of the advection-dispersial equations and implemented them as far
as possible. The wind advection was fully implemented.
However, the dispersion factor and the sink term was more or less estimated. Therefore a sensitivity analysis and
a comparison with the more complex models should be done to evaluate if the model results reached by this model are
sufficiently."""

# Creates a test wind field (only for plausibility testing)
# There is no option to choose the test run in the automated program
# The test wind dataset has to be assigned to u_wind and / or v_wind variable manually
if test:
    # Create Coordinate variables
    lon = np.arange(0, 360, 0.75) - 180
    lat = np.arange(-90,90.25, 0.75)

    dim_lon = len(lon)
    dim_lat = len(lat)

    # Creates Array with no wind, lat and lon
    test_wind_u = np.array((0,dim_lat, dim_lon))
    test_wind_v = np.array((0, dim_lat, dim_lon))

    # Create wind fields
    # U wind / V wind
    u_test = np.ones((dim_lat, dim_lon))
    v_test = np.ones((dim_lat, dim_lon))

    u_test[u_test == 1] = 25
    v_test[v_test == 1] = 0
    # TODO: assign here to u_wind and v_wind if necessary

    # How many timesteps
    start = 0 * 4
    end = int(input("How many timesteps do you want to model? (Wind field will not change!)"))


# Specify the eruption / volcano source cell
lat_pos = lat[np.where(abs(lat - lat_vol) == min(abs(lat - lat_vol)))][0]
lon_pos = lon[np.where(abs(lon - lon_vol) == min(abs(lon - lon_vol)))][0]
# Get index of closest lat and lon values
lat_index = int(np.where(lat == lat_pos)[0])
lon_index = int(np.where(lon == lon_pos)[0])

# Creating a raster with zero values for the dimensions of the given wind data field
particles = np.zeros((dim_lat, dim_lon,))

# Defining the row and col numbers (equals to dimensions of lon and lat)
rows = int(np.shape(particles)[0])
cols = int(np.shape(particles)[1])

timesteps = np.arange(start, end, 1)

# Creates figure list
figures = []

# 1/24 reasons in the fact that fine ash can persist for several days in the air.
# We assumed here that it can stay almost 6 days in the air without major fallout. (6*4 steps = 24)
# Modelling fall out is generally complex and was simplified here
fall_out = 1-1/float(24)
fall_out = 0.9

# According to a neutrally stable atmosphere D, horizontal diffusion coefficient
# Gaussian Plume Model -->consider this could not be valid for synoptic scale?!
diff_coeff = 68*(resolution**0.894)
diff_perc = float(100) / (resolution*1000) * float(diff_coeff / 100)

diff_perc = 0.04
# TODO: one could here add a specific diffusion coefficient for the diagonal (extended) propagation too...

# Variable to sum up total erupted material
eruption_sum = 0

print("Modeling process initiated, going through {} iterations.".format(len(timesteps)))

# for-loop to go through specified amount of timesteps
for n in timesteps:

    # create temporary array to save calculated time step
    temp_arr = np.zeros((rows, cols))

    # Setting the wind fields for each timestep
    # If it's a test - the same wind field for every timestep is used
    if not test:
        u = u_wind[n, :, :]
        v = v_wind[n, :, :]
    else:
        u = u_test
        v = v_test

    # Fall out of particles over the whole particles grid
    particles = particles * fall_out

    # POINT SOURCE INITIALISATION
    if mode == 2:
        if n - min(timesteps) < len(concentration):
            if np.isnan(particles[lat_index, lon_index]):
                particles[lat_index, lon_index] = concentration[n - min(timesteps)]
            else:
                particles[lat_index, lon_index] += concentration[n - min(timesteps)]

            eruption = concentration[n - min(timesteps)]
            eruption_sum += eruption
        else:
            eruption = 0
    if mode == 1:
        if np.isnan(particles[lat_index, lon_index]):
            particles[lat_index, lon_index] = concentration
        else:
            particles[lat_index, lon_index] += concentration

        eruption = concentration
        eruption_sum += eruption


    print("..." * 10)
    print("..." * 10)
    print("timestep {}, erupting {} g/m^3".format(n + 1, eruption))

    # go through every pixel and evaluate its next time step, then save to temp_arr
    # TODO: Handle the OutOfBoundsError
    # TODO: Handle it such that overflow will be added behind! like when -180 is reached then +180 / 179 entering
    # TODO: How to handle the test situation versus the real run!

    # Adjustment for temporal resolution of wind data
    if test:
        res_correction = np.zeros((1,))
    else:
        res_correction = np.arange(0, hourly_res, 1)

    for k in res_correction:
        i = 0
        while i < rows:
            j = 0

            while j < cols:
                # to check if it works correctly:
                # print("going trough pixel at {},{}".format(i, j))

                # Array for stepwise calculation
                # steps = np.zeros((rows, cols))

                # Calculation of the particle advection and diffusion for each time step
                # Retrieving u and v wind value
                wind_u = u[i, j]
                wind_v = v[i, j]

                # wind in km/h
                wind_u = wind_u * 3.6
                wind_v = wind_v * 3.6 #* -1

                # Classification of Advection transport - measured for 1h and depending on model resolution!
                v_dir = abs(wind_v)
                u_dir = abs(wind_u)

                # TODO: can be adjusted! to Adjust when only one component is present!
                if u_dir != 0.0 and v_dir != 0.0:
                    diag = math.sqrt(v_dir ** 2 + u_dir ** 2)
                else:
                    diag = max(u_dir*0.1, v_dir*0.1)

                # Defining percentage contribution of individual winds
                wind_sum = u_dir + v_dir + diag
                u_per = 100 / wind_sum * u_dir / 100
                v_per = 100 / wind_sum * v_dir / 100
                diag_per = 100 / wind_sum * diag / 100

                if wind_v == 0.0:
                    wind_sum = u_dir + 2 * diag
                    u_per = 100 / wind_sum * u_dir / 100
                    diag_per = 100 / wind_sum * diag / 100
                if wind_u == 0.0:
                    wind_sum = v_dir + 2 * diag
                    v_per = 100 / wind_sum * v_dir / 100
                    diag_per = 100 / wind_sum * diag / 100

                # Define how much mat should be transported - 100% if wind reaches "resolution" km/h
                u_transport_perc = 0

                max_uv = max(u_dir, v_dir)

                if max_uv >= (resolution - 5) :
                    transport_perc = 1
                if (resolution - 5) > max_uv >= resolution * 0.8 - 5:
                    transport_perc = 0.95 #0.8
                if resolution * 0.8 - 5 > max_uv >= resolution * 0.6 - 5:
                    transport_perc = 0.9 #0.6
                if resolution * 0.6 - 5 > max_uv:
                    transport_perc = 0.85 #0.4

                if max(max_uv, diag) != max_uv:
                    if diag >= resolution_extended - 5:
                        transport_perc = 1
                    if resolution_extended - 5 > diag >= resolution_extended * 0.8 - 5:
                        transport_perc = 0.95 # 0.8
                    if resolution_extended * 0.8 - 5 > diag >= resolution_extended * 0.6 - 5:
                        transport_perc = 0.9 # 0.6
                    if resolution_extended * 0.6 - 5 > diag:
                        transport_perc = 0.85 # 0.4

                try:
                    # receiving concentrations from all grid cells
                    x_origin = particles[i, j]
                    x1 = particles[i - 1, j]
                    x2 = particles[i - 1, j + 1]
                    x3 = particles[i, j + 1]
                    x4 = particles[i + 1, j + 1]
                    x5 = particles[i + 1, j]
                    x6 = particles[i + 1, j - 1]
                    x7 = particles[i, j - 1]
                    x8 = particles[i - 1, j - 1]

                    in_x1 = 0
                    in_x2 = 0
                    in_x3 = 0
                    in_x4 = 0
                    in_x5 = 0
                    in_x6 = 0
                    in_x7 = 0
                    in_x8 = 0

                    # calculate the gradients
                    grad_x1 = (x1 - x_origin) / resolution
                    grad_x2 = (x2 - x_origin) / resolution_extended
                    grad_x3 = (x3 - x_origin) / resolution
                    grad_x4 = (x4 - x_origin) / resolution_extended
                    grad_x5 = (x5 - x_origin) / resolution
                    grad_x6 = (x6 - x_origin) / resolution_extended
                    grad_x7 = (x7 - x_origin) / resolution
                    grad_x8 = (x8 - x_origin) / resolution_extended

                    if not x_origin == 0:
                        if wind_u > 0 and wind_v > 0:
                            # calculate the advection rates
                            adv_x1 = x_origin * transport_perc * v_per
                            adv_x2 = x_origin * transport_perc * diag_per
                            adv_x3 = x_origin * transport_perc * u_per

                            # Calculate inputs (model = 6 hourly)
                            in_x1 = adv_x1
                            in_x2 = adv_x2
                            in_x3 = adv_x3

                        if wind_u > 0 and wind_v < 0:
                            # calculate the advection rates
                            adv_x3 = x_origin * transport_perc * u_per
                            adv_x4 = x_origin * transport_perc * diag_per
                            adv_x5 = x_origin * transport_perc * v_per

                            # Calculate inputs (model = 6 hourly)
                            in_x3 = adv_x3
                            in_x4 = adv_x4
                            in_x5 = adv_x5

                        if wind_u < 0 and wind_v < 0:
                            # calculate advection rate
                            adv_x5 = x_origin * transport_perc * v_per
                            adv_x6 = x_origin * transport_perc * diag_per
                            adv_x7 = x_origin * transport_perc * u_per

                            # Calculate inputs (model = 6 hourly)
                            in_x5 = adv_x5
                            in_x6 = adv_x6
                            in_x7 = adv_x7
                            # TODO: keep in mind that temperature is conservative while ash is not!
                            # TODO: thus the areal dispersion must be accounted! (everything / 3) because 3 cell distribution

                        if wind_u < 0 and wind_v > 0:
                            # calculate the advection rates
                            adv_x7 = x_origin * transport_perc * u_per
                            adv_x8 = x_origin * transport_perc * diag_per
                            adv_x1 = x_origin * transport_perc * v_per

                            # Calculate inputs (model = 6 hourly)
                            in_x7 = adv_x7
                            in_x8 = adv_x8
                            in_x1 = adv_x1

                        if wind_u > 0 and wind_v == 0.0:
                            # calculate the advection rates
                            adv_x2 = x_origin * transport_perc * diag_per
                            adv_x3 = x_origin * transport_perc * u_per
                            adv_x4 = x_origin * transport_perc * diag_per #TODO: correct to diagonal

                            # Calculate inputs (model = 6 hourly)
                            in_x3 = adv_x3
                            if n % 4 == 0: #and (lat_index - 4< i < lat_index + 4) and (lon_index - 4 < j < lon_index + 4):
                                in_x4 = adv_x4
                                in_x2 = adv_x2

                        if wind_u < 0 and wind_v == 0.0:
                            # calculate the advection rates
                            adv_x6 = x_origin * transport_perc * diag_per
                            adv_x7 = x_origin * transport_perc * u_per
                            adv_x8 = x_origin * transport_perc * diag_per

                            # Calculate inputs (model = 6 hourly)
                            in_x7 = adv_x7
                            if n % 4 == 0:
                                in_x8 = adv_x8
                                in_x6 = adv_x6

                        if wind_u == 0.0 and wind_v > 0:
                            # calculate the advection rates
                            adv_x8 = x_origin * transport_perc * diag_per
                            adv_x1 = x_origin * transport_perc * v_per
                            adv_x2 = x_origin * transport_perc * diag_per

                            # Calculate inputs (model = 6 hourly)
                            in_x1 = adv_x1
                            if n % 4 == 0:
                                in_x2 = adv_x2
                                in_x8 = adv_x8

                        if wind_u == 0.0 and wind_v < 0:
                            # calculate the advection rates
                            adv_x4 = x_origin * transport_perc * diag_per
                            adv_x5 = x_origin * transport_perc * v_per
                            adv_x6 = x_origin * transport_perc * diag_per

                            # Calculate inputs (model = 6 hourly)
                            in_x5 = adv_x5
                            if n % 4 == 0:
                                in_x6 = adv_x6
                                in_x4 = adv_x4

                        # Adjust ash concentration from origin cell to the losses
                        updated = x_origin - in_x1 - in_x2 - in_x3 - in_x4 - in_x5 - in_x6 - in_x7 - in_x8
                        if updated < 0:
                            temp_arr[i, j] = 0
                        else:
                            temp_arr[i, j] = x_origin - in_x1 - in_x2 - in_x3 - in_x4 - in_x5 - in_x6 - in_x7 - in_x8

                        # Add the losses to the corresponding cells
                        temp_arr[i - 1, j] += in_x1
                        temp_arr[i - 1, j + 1] += in_x2
                        temp_arr[i, j + 1] += in_x3
                        temp_arr[i + 1, j + 1] += in_x4
                        temp_arr[i + 1, j] += in_x5
                        temp_arr[i + 1, j - 1] += in_x6
                        temp_arr[i, j - 1] += in_x7
                        temp_arr[i - 1, j - 1] += in_x8

                    gradients = [grad_x1, grad_x2, grad_x3, grad_x4, grad_x5, grad_x6, grad_x7, grad_x8]

                    if any(n < 0 for n in gradients):

                        # DIFFUSION PART
                        x_origin = particles[i, j]
                        diff_amount = x_origin * diff_perc

                        # TODO: KEEP IN MIND THAT WIND DATA IS 6-HOURLY
                        # TODO: Possible solution: do the movement 6 times before moving to the next iteration step!
                        # TODO: (would mean 6 times with the same wind field!)
                        # TODO: But then plot only each 3th or 6th hour???!

                        # TODO: SCHAUEN DASS KEINE ZELLE WENIGER ALS 0 oder NaN haben kann!!

                        no_cells = sum(n < 0 for n in gradients)

                        # Diffusion Component
                        # assign each surrounding pixel of end-of-timestep-target pixel the diffusion value
                        if grad_x1 < 0:
                            temp_arr[i - 1, j] += diff_amount / no_cells
                        if grad_x2 < 0:
                            temp_arr[i - 1, j + 1] += diff_amount / no_cells
                        if grad_x3 < 0:
                            temp_arr[i, j + 1] += diff_amount / no_cells
                        if grad_x4 < 0:
                            temp_arr[i + 1, j + 1] += diff_amount / no_cells
                        if grad_x5 < 0:
                            temp_arr[i + 1, j] += diff_amount / no_cells
                        if grad_x6 < 0:
                            temp_arr[i + 1, j - 1] += diff_amount / no_cells
                        if grad_x7 < 0:
                            temp_arr[i, j - 1] += diff_amount / no_cells
                        if grad_x8 < 0:
                            temp_arr[i - 1, j - 1] += diff_amount / no_cells

                        temp_arr[i, j] = temp_arr[i, j] - diff_amount

                except IndexError:
                    # this is to prevent the program from collapsing in case one of the above conditions tries to
                    # access a pixel outside of the range of a numpy array, like a pixel with index particles[-10,
                    # -10] in that case the program should just pass the condition and move on
                    pass

                # Adding the stepwise calculations to the temporary array
                # temp_arr = temp_arr + steps

                # iterating through columns
                j += 1

            # iterating through rows
            i += 1

        # diffusion = np.zeros((rows, cols))
        # p = 0
        # while p < rows:
        #
        #     o = 0
        #     while o < cols:
        #         # to check if it works correctly:
        #         # print("going trough pixel at {},{}".format(i, j))
        #
        #         # Array for stepwise calculation
        #         # steps = np.zeros((rows, cols))
        #
        #         # Calculation of the particle advection and diffusion for each time step
        #         # Retrieving u and v wind value
        #         wind_u = u[p, o]
        #         wind_v = v[p, o]
        #
        #         # wind in km/h
        #         wind_u = wind_u * 3.6
        #         wind_v = wind_v * 3.6 * -1
        #
        #         # Classification of Advection transport - measured for 1h and depending on model resolution!
        #         v_dir = abs(wind_v)
        #         u_dir = abs(wind_u)
        #
        #         # TODO: can be adjusted! to Adjust when only one component is present!
        #         if u_dir != 0.0 and v_dir != 0.0:
        #             diag = math.sqrt(v_dir ** 2 + u_dir ** 2)
        #         else:
        #             diag = max(u_dir * 0.3, v_dir * 0.3)
        #
        #         # Defining percentage contribution of individual winds
        #         wind_sum = u_dir + v_dir + diag
        #         u_per = 100 / wind_sum * u_dir / 100
        #         v_per = 100 / wind_sum * v_dir / 100
        #         diag_per = 100 / wind_sum * diag / 100
        #
        #         if wind_v == 0.0:
        #             wind_sum = u_dir + 2 * diag
        #             u_per = 100 / wind_sum * u_dir / 100
        #             diag_per = 100 / wind_sum * diag / 100
        #         if wind_u == 0.0:
        #             wind_sum = v_dir + 2 * diag
        #             v_per = 100 / wind_sum * v_dir / 100
        #             diag_per = 100 / wind_sum * diag / 100
        #
        #         # Define how much mat should be transported - 100% if wind reaches "resolution" km/h
        #         u_transport_perc = 0
        #         v_transport_perc = 0
        #         diag_transport_perc = 0
        #
        #         if u_dir >= (resolution - 5):
        #             u_transport_perc = 1
        #         if (resolution - 5) > u_dir >= resolution * 0.8 - 5:
        #             u_transport_perc = 0.8
        #         if resolution * 0.8 - 5 > u_dir >= resolution * 0.6 - 5:
        #             u_transport_perc = 0.6
        #         if resolution * 0.6 - 5 > u_dir:
        #             u_transport_perc = 0.4
        #
        #         if v_dir >= (resolution - 5):
        #             v_transport_perc = 1
        #         if (resolution - 5) > v_dir >= resolution * 0.8 - 5:
        #             v_transport_perc = 0.8
        #         if resolution * 0.8 - 5 > v_dir >= resolution * 0.6 - 5:
        #             v_transport_perc = 0.6
        #         if resolution * 0.6 - 5 > v_dir:
        #             v_transport_perc = 0.4
        #
        #         if diag >= (resolution_extended - 5):
        #             diag_transport_perc = 1
        #         if (resolution_extended - 5) > diag >= resolution_extended * 0.8 - 5:
        #             diag_transport_perc = 0.8
        #         if resolution_extended * 0.8 - 5 > diag >= resolution_extended * 0.6 - 5:
        #             diag_transport_perc = 0.6
        #         if resolution_extended * 0.6 - 5 > diag:
        #             diag_transport_perc = 0.4
        #
        #         try:
        #             # receiving concentrations from all grid cells
        #             x_origin = temp_arr[p, o]
        #             x1 = temp_arr[p - 1, o]
        #             x2 = temp_arr[p - 1, o + 1]
        #             x3 = temp_arr[p, o + 1]
        #             x4 = temp_arr[p + 1, o + 1]
        #             x5 = temp_arr[p + 1, o]
        #             x6 = temp_arr[p + 1, o - 1]
        #             x7 = temp_arr[p, o - 1]
        #             x8 = temp_arr[p - 1, o - 1]
        #
        #             in_x1 = 0
        #             in_x2 = 0
        #             in_x3 = 0
        #             in_x4 = 0
        #             in_x5 = 0
        #             in_x6 = 0
        #             in_x7 = 0
        #             in_x8 = 0
        #
        #             # calculate the gradients
        #             grad_x1 = (x1 - x_origin) / resolution
        #             grad_x2 = (x2 - x_origin) / resolution_extended
        #             grad_x3 = (x3 - x_origin) / resolution
        #             grad_x4 = (x4 - x_origin) / resolution_extended
        #             grad_x5 = (x5 - x_origin) / resolution
        #             grad_x6 = (x6 - x_origin) / resolution_extended
        #             grad_x7 = (x7 - x_origin) / resolution
        #             grad_x8 = (x8 - x_origin) / resolution_extended
        #
        #         except IndexError:
        #             # this is to prevent the program from collapsing in case one of the above conditions tries to
        #             # access a pixel outside of the range of a numpy array, like a pixel with index particles[-10,
        #             # -10] in that case the program should just pass the condition and move on
        #             pass
        #
        #         gradients = [grad_x1, grad_x2, grad_x3, grad_x4, grad_x5, grad_x6, grad_x7, grad_x8]
        #
        #         if any(n < 0 for n in gradients):
        #
        #             # DIFFUSION PART
        #             x_origin = temp_arr[p, o]
        #             diff_amount = x_origin * diff_perc
        #
        #             # TODO: KEEP IN MIND THAT WIND DATA IS 6-HOURLY
        #             # TODO: Possible solution: do the movement 6 times before moving to the next iteration step!
        #             # TODO: (would mean 6 times with the same wind field!)
        #             # TODO: But then plot only each 3th or 6th hour???!
        #
        #             # TODO: SCHAUEN DASS KEINE ZELLE WENIGER ALS 0 oder NaN haben kann!!
        #
        #             no_cells = sum(n < 0 for n in gradients)
        #
        #             # Diffusion Component
        #             # assign each surrounding pixel of end-of-timestep-target pixel the diffusion value
        #             if grad_x1 < 0:
        #                 diffusion[p - 1, o] += diff_amount / no_cells
        #             if grad_x2 < 0:
        #                 diffusion[p - 1, o + 1] += diff_amount / no_cells
        #             if grad_x3 < 0:
        #                 diffusion[p, o + 1] += diff_amount / no_cells
        #             if grad_x4 < 0:
        #                 diffusion[p + 1, o + 1] += diff_amount / no_cells
        #             if grad_x5 < 0:
        #                 diffusion[p + 1, o] += diff_amount / no_cells
        #             if grad_x6 < 0:
        #                 diffusion[p + 1, o - 1] += diff_amount / no_cells
        #             if grad_x7 < 0:
        #                 diffusion[p, o - 1] += diff_amount / no_cells
        #             if grad_x8 < 0:
        #                 diffusion[p - 1, o - 1] += diff_amount / no_cells
        #
        #             diffusion[p, o] = temp_arr[p, o] - diff_amount
        #
        #         o += 1
        #     p += 1



    # saving temp_arr as the new particles for the next time-step, also saving a snapshot from each
    # timestep to a folder for GIF-creation later
    particles = temp_arr

    figures.append(particles)

    # TODO: Eruption sum can be stated as finish statement (see end of Version B. Schuepbach!)

    # Set all zero values to 'nan'
    # particles[particles == 0.00000000000000000000000000000000000000000000000000000000000000000000000000000000] = np.nan
    # plt.imsave("Ash_Plumes\Ash_Plume{}".format(n), particles, cmap='gray')

    plt.imshow(particles)

    # Colormap (same as MeteoSwiss)
    # minus values = tricks: basemap would be better option (package basemap) -->more complicated
    clevs = [0, 10**-4, 10**-3, 10**-2, 10**-1, 10**0, 10**1, 10**2, 10**3, 10**4, 10**42]
    cmap_cols = [(255,255,255),
                 (0, 191, 255),
                 (28,134,238),
                 (16,78,139),
                 (0,0,128),
                 (178,58,238),
                 (104,34,139),
                 (238,18,137),
                 (0,0,0),
                 (35,35,40)]

    cmap_data = np.array(cmap_cols) / 255.0
    cmap = mcolors.ListedColormap(cmap_data, 'concentrations')

    norm = m.colors.BoundaryNorm(clevs, ncolors=cmap.N, clip=True)

    plt.imshow(particles, cmap=cmap)

    plt.imsave("Ash_Plumes\Ash_Plume{}".format(n), particles, cmap=cmap)

    plt.contourf(lon, lat, particles, levels=clevs, cmap=cmap, vmax=100, vmin=0, norm= norm)

    mbase = Basemap(projection='mill', lat_0=45, lon_0=lon_vol, resolution='l')
    lon2, lat2 = np.meshgrid(lon, lat)
    x, y = mbase(lon2, lat2)


    # BASEMAP TRY
    for n in timesteps:
        fig = plt.figure(figsize=(30, 30))
        # m.fillcontinents(color='gray',lake_color='gray')
        mbase.drawcoastlines()
        mbase.drawparallels(np.arange(-80., 81., 20.))
        mbase.drawmeridians(np.arange(-180., 181., 20.))
        mbase.drawmapboundary(fill_color='white')
        # cs = mbase.imshow(particles, cmap=cmap, norm=norm)
        # cs = mbase.contourf(x, y, particles[:,:], levels=clevs, cmap=cmap, norm=norm) # cmap = cmap passt
        cs = mbase.contourf(x, y, figures[n - min(timesteps)], levels=clevs, cmap=cmap, norm=norm)
        plt.title(' SAT on January 1')
        plt.colorbar();
        fig.savefig("Test_{}".format(n - min(timesteps)))
        plt.close(fig)
        # TODO: Create a own plotting function that plots the input raster!


















''' REFERENCES on which this model relies on _______________________________________________________________________

Mastin, L.G., Guffanti, M., Servranckx, R., Webley, P., Barsotti, S., Dean, K., Durant, A, Ewert, J.W., Neri, A.,
              Rose, W.I., Schneider, D., Siebert, L., Stunder, B., Swanson, G., Tupper, A., Volentik, A.,
              Waythomas, C.F. (2009): A multidisciplinary effort to assign realistic source parameters to models of
              volcanic ash-cloud transport and dispersion during eruptions.
              In: Journal of Volcanology and Geothermal Research 186: 10-21.
              DOI: 10.1016/j.jvolgeores.2009.01.008
              
Folch, A. (2012): A review of tephra transport and dispersal models: Evolution, current status, and future perspectives.
              In: Journal of Volcanology and Geothermal Research 235-236: 96-115.
              DOI: 10.1016/j.jvolgeores.2012.05.020
              



'''
