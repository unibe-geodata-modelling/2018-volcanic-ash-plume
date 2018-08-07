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

    #TODO: print a review at the end of all chosen variables! Then ask user if he/she wants to change anything...

    # Print a summary
    print("You have chosen the following parameters:")
    print("Height: {}".format(height))
    print("Durance: {}".format(durance))
    print("Ash-Fraction: {}".format(ash_fraction))
    print("Mass rate: {}".format(mass_rate))
    print("Volume rate: {}".format(volume_rate))

    # Ash concentration calculation # TODO: maybe apply adjustments according to Gudmundsson-Formula!
    concentration = np.array(mass_rate) * ash_fraction / np.array(volume_rate) / (resolution * resolution)


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
    test_wind_u = np.array((0,dim_lat, dim_lon))        #TODO: decide wether creating a NetCDF File by scratch or introduce a test version
    test_wind_v = np.array((0, dim_lat, dim_lon))

    # Create wind fields
    # U wind / V wind
    u_test = np.ones((dim_lat, dim_lon))
    v_test = np.ones((dim_lat, dim_lon))

    u_test[u_test == 1] = 50
    v_test[v_test == 1] = -50
    # TODO: assign here to u_wind and v_wind if necessary

    # How many timesteps
    start = 0 * 4
    end = int(input("How many days do you want to model? (Wind field will not change!)"))


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

# Calculating Distance for Diagonal transport: with cosinus(45°)
resolution_extended = resolution / math.cos(0.785398)

# 1/24 reasons in the fact that fine ash can persist for several days in the air.
# We assumed here that it can stay almost 6 days in the air without major fallout. (6*4 steps = 24)
# Modelling fall out is generally complex and was simplified here
fall_out = 1-1/24

# According to a neutrally stable atmosphere D, horizontal diffusion coefficient
# Gaussian Plume Model -->consider this could not be valid for synoptic scale?!
diff_coeff = 68*(resolution**0.894)
diff_perc = float(100) / (resolution*1000) * float(diff_coeff / 100)
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

    # POINT SOURCE INITIALISATION
    if n - min(timesteps) < len(concentration):
        if np.isnan(particles[lat_index, lon_index]):
            particles[lat_index, lon_index] = concentration[n - min(timesteps)]
        else:
            particles[lat_index, lon_index] += concentration[n - min(timesteps)]

        eruption = concentration[n - min(timesteps)]
        eruption_sum += eruption
    else:
        eruption = 0

    print("..." * 10)
    print("..." * 10)
    print("timestep {}, erupting {} g/m^3".format(n + 1, eruption))

    # go through every pixel and evaluate its next time step, then save to temp_arr
    # TODO: Handle the OutOfBoundsError
    # TODO: Handle it such that overflow will be added behind! like when -180 is reached then +180 / 179 entering
    # TODO: How to handle the test situation versus the real run!
    i = 0
    while i < rows:
        j = 0

        while j < cols:
            # to check if it works correctly:
            # print("going trough pixel at {},{}".format(i, j))

            # Array for stepwise calculation
            steps = np.zeros((rows, cols))

            # Calculation of the particle advection and diffusion for each time step
            # Retrieving u and v wind value
            wind_u = u[i, j]
            wind_v = v[i, j]

            try:
                if not np.isnan(particles[i, j]):

                    origin = particles[i, j] * fall_out

                    diff_amount = origin * diff_perc

                    tot = ((abs(wind_u) + abs(wind_v)) * origin / resolution) + math.sqrt(wind_u ** 2 + wind_v ** 2)*origin / resolution_extended + diff_amount

                    # TODO: KEEP IN MIND THAT WIND DATA IS 6-HOURLY
                    # TODO: Possible solution: do the movement 6 times before moving to the next iteration step!
                    # TODO: (would mean 6 times with the same wind field!)
                    # TODO: But then plot only each 3th or 6th hour???!

                    # TODO: SCHAUEN DASS KEINE ZELLE WENIGER ALS 0 oder NaN haben kann!!

                    case = -1

                    x1 = 0
                    x2 = 0
                    x3 = 0
                    x4 = 0
                    x5 = 0
                    x6 = 0
                    x7 = 0
                    x8 = 0

                    if wind_u >= 0 and wind_v >= 0:
                        x1 += wind_v * origin / resolution  # 1
                        x2 += math.sqrt(wind_u ** 2 + wind_v ** 2) * origin / resolution_extended
                        x3 += wind_u * origin / resolution  # 3

                        case = 0

                    if wind_u >= 0 and wind_v <= 0:
                        x3 += wind_u * origin / resolution  # 3
                        x4 += math.sqrt(wind_u ** 2 + wind_v ** 2) * origin / resolution_extended
                        x5 += - wind_v * origin / resolution  # 5

                        case = 1

                    if wind_u <= 0 and wind_v <= 0:
                        x5 += - wind_v * origin / resolution  # 5
                        x6 += math.sqrt(wind_u ** 2 + wind_v ** 2) * origin / resolution_extended
                        x7 += - wind_u * origin / resolution  # 7

                        case = 2

                    if wind_u <= 0 and wind_v >= 0:
                        x7 += - wind_u * origin / resolution  # 7
                        x8 += math.sqrt(wind_u ** 2 + wind_v ** 2) * origin / resolution_extended
                        x1 += wind_v * origin / resolution  # 1

                        case = 3

                    if origin - tot < 0:
                        if case == 0:
                            sum = x1 + x2 + x3
                            x1 = (tot-diff_amount) * (100/sum * x1 / 100)
                            x2 = (tot-diff_amount) * (100/sum * x2 / 100)
                            x3 = (tot-diff_amount) * (100/sum * x3 / 100)

                            tot = origin - x1 - x2 -x3 -diff_amount

                        if case == 1:
                            sum = x3 + x4 + x5
                            x3 = (tot-diff_amount) * (100/sum * x3 / 100)
                            x4 = (tot-diff_amount) * (100/sum * x4 / 100)
                            x5 = (tot-diff_amount) * (100/sum * x5 / 100)

                            tot = origin - x3 -x4 -x5 - diff_amount
                        if case == 2:
                            sum = x5 + x6 + x7
                            x5 = (tot-diff_amount) * (100/sum * x5 / 100)
                            x6 = (tot-diff_amount) * (100/sum * x6 / 100)
                            x7 = (tot-diff_amount) * (100/sum * x7 / 100)

                            tot = origin -x5 -x6 -x7 - diff_amount
                        if case == 3:
                            sum = x7 + x8 + x1
                            x7 = (tot-diff_amount) * (100/sum * x7 / 100)
                            x8 = (tot-diff_amount) * (100/sum * x8 / 100)
                            x1 = (tot-diff_amount) * (100/sum * x1 / 100)

                            tot = origin - x7 - x8 - x1 - diff_amount



                    # Diffusion Component
                    # assign each surrounding pixel of end-of-timestep-target pixel the diffusion value
                    temp_arr[i - 1, j] += (x1 + diff_amount / 8)
                    temp_arr[i - 1, j + 1] += (x2 + diff_amount / 8)
                    temp_arr[i, j + 1] += (x3 + diff_amount / 8)
                    temp_arr[i + 1, j + 1] += (x4 + diff_amount / 8)
                    temp_arr[i + 1, j] += (x5 + diff_amount / 8)
                    temp_arr[i + 1, j - 1] += (x6 + diff_amount / 8)
                    temp_arr[i, j - 1] += (x7 + diff_amount / 8)
                    temp_arr[i - 1, j - 1] += (x8 + diff_amount / 8)

                    temp_arr[i, j] += (origin - tot)

            except IndexError:
                # this is to prevent the program from collapsing in case one of the above conditions tries to
                # access a pixel outside of the range of a numpy array, like a pixel with index particles[-10,
                # -10] in that case the program should just pass the condition and move on
                pass

            # Adding the stepwise calculations to the temporary array
            temp_arr = temp_arr + steps

            # iterating through columns
            j += 1

        # iterating through rows
        i += 1

    # saving temp_arr as the new particles for the next time-step, also saving a snapshot from each
    # timestep to a folder for GIF-creation later
    particles += temp_arr

    # Set all zero values to 'nan'
    # particles[particles == 0.00000000000000000000000000000000000000000000000000000000000000000000000000000000] = np.nan
    # plt.imsave("Ash_Plumes\Ash_Plume{}".format(n), particles, cmap='gray')

    plt.imshow(particles)

    # Colormap (same as MeteoSwiss)
    # minus values = tricks: basemap would be better option (package basemap) -->more complicated
    clevs = [0, 10**-4, 10**-3, 10**-2, 10**-1, 10**0, 10**1, 10**2, 10**3]
    cmap_cols = [(255,255,255),
                 (0, 191, 255),
                 (28,134,238),
                 (16,78,139),
                 (0,0,128),
                 (178,58,238),
                 (104,34,139),
                 (238,18,137)]

    cmap_data = np.array(cmap_cols) / 255.0
    cmap = mcolors.ListedColormap(cmap_data, 'concentrations')

    norm = m.colors.BoundaryNorm(clevs, ncolors=cmap.N, clip=True)

    plt.imshow(particles, cmap=cmap)

    plt.imsave("Ash_Plumes\Ash_Plume{}".format(n), particles, cmap=cmap)

    plt.contourf(lon, lat, particles, levels=clevs, cmap=cmap, vmax=100, vmin=0, norm= norm)


    # BASEMAP TRY
    mbase = Basemap(projection='mill', lat_0=45, lon_0=lon_vol, resolution='l')
    lon2, lat2 = np.meshgrid(lon, lat)
    x, y = mbase(lon2, lat2)
    fig = plt.figure(figsize=(30, 30))
    # m.fillcontinents(color='gray',lake_color='gray')
    mbase.drawcoastlines()
    mbase.drawparallels(np.arange(-80., 81., 20.))
    mbase.drawmeridians(np.arange(-180., 181., 20.))
    mbase.drawmapboundary(fill_color='white')
    cs = mbase.contourf(x, y, particles[:,:], levels=clevs, cmap=cmap, norm=norm) # cmap = cmap passt
    plt.title(' SAT on January 1')
    plt.colorbar();
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
