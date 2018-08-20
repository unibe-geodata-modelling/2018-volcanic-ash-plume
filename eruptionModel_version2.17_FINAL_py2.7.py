import numpy as np
from matplotlib import pyplot as plt
import matplotlib as m
from matplotlib import ticker, cm
from netCDF4 import *
import math
import matplotlib.colors as mcolors
from mpl_toolkits.basemap import  Basemap


"""
____________________________________Author Information___________________________________________
"""

_author_ = "Christoph von Matt  Benjamin Schüpbach"
_affiliation_ = "Institute of Geography, University of Bern"
_version_ = "2.17"
_email_ = "christoph.vonmatt@students.unibe.ch  benjamin.schuepbach@students.unibe.ch"
_semester_ = "Spring Semester 2018"
_date_ = "2018-08-18"

"""
_____________________________________General description__________________________________________

This model was created within the course "Geodata analysis and modelling" in its first realisation 
in the Spring Semester 2018.

The model describes a simplified dynamical particle-transport-diffusion model for modelling synoptic-scale features like
volcanic ash cloud dispersions.
Within this model we implemented the scenario for the Icelandic Eyjafjallaj%kull eruption back in 2010.

MODEL SECTIONS:
1) User's section
2) Auxiliary Functions
3) Initialisation of wind field related data
4) Initialisation of eruption characteristics
5) Transport-Diffusion modelling
6) Generating Plots
7) References

USER INPUTS:
- Choice of Test or Simulation

- Choice of mode (either predefined Eyjafjallaj%kull or manual inputs)
    Manual inputs will require:
        1) geographic (decimal degrees) location of point source (e.g. volcano)
        2) Plume height (km)
        3) Eruption durance (h)
        4) Tephra mass rate (g/s)
        5) Tephra volume rate (m^3/s)

- Choice simulation (own wind fields) or test (fixed wind fields)

- 2 Wind field datasets for u and v components (in NetCDF format!)
    -->Input = filename or directory
    ATTENTION: Files HAVE TO contain the same variable names except for the wind components!

- Specification of amount of simulation-timesteps

- Parametrization of: 
        1) diffusion (percent)
        2) diffusion type (0, 1 or no diffusion (any other number))
        3) spatial model resolution (km) 
        4) temporal model resolution (h) 
        5) degrees resolution (only in test case!) 
        6) test-wind field (u- and v-components, only in test case!)
        7) fall_out (1 - percent)
        8) File-Names ("xy.nc", only in simulation case!)
        
PREREQUISITES:
In order to be able to save the plots automatically you should create the following folders
in your Model.py-directory:
    1) Folder "WorldMap"
    2) Folder "EuropeZoom"
    3) Folder "EuropeFlyzone"


DYNAMICS:
Our model is inspired by the advection-diffusion equation (as described in Folch 2012). 
We decided however to implement simplified transport-diffusion dynamics.
The transport of the particles is determined by wind direction and wind speed.
Therefore, we classified the surrounding cells according to the wind-direction.
Depending on the wind speed, different percentages of the cells concentration are transported.

For the diffusion we implemented two options:
    1) All Directions:
        In all direction-diffusion each surrounding cell (8 cells) receives an eighth of the diffusion part.
    2) Gradient dependent
        In gradient dependent-diffusion we first calculate the gradients of each surrounding cell with respect
        to the source cell. Diffusion is then only happening in direction of negative gradients (this means in 
        direction of the lower concentrations).
        
For Further informations please consider the individual Section descriptions.
"""

"""
____________________________________First Section - User's Section_____________________________________________

In this first section, users find all parameters they can specify on their own.
Please consider the suggestions for the input parameter ranges!

Parameters to specify are:
 1) Wind-File names
    The wind-file names should end with ".nc" as only NetCDF-data is supported.
    Two wind-file names are required: one for the U-wind component and one for the
    V-wind component.
 2) Model resolutions
    - Spatial resolution of the model (km)
    - Degree resolution (e.g. 0.75; has only influence in test runs)
        -->PLEASE BE AWARE that for realistic results both parameters should be adjusted in a meaningful way
           (e.g. 80 km and 0.75 degrees and not 25 km and 0.75 degrees (wrong))!!
    - temporal resolution (in h)
 3) Wind speed of U- and V-wind components
    - has only influence in test run
 4) Amount of Fall-out (1 - percent)
 5) Diffusion Type
    - 0 for gradient dependent
    - 1 for all directions
    - any other number for no diffusion
 6) Diffusion Percentage
 7) Plot extent (for Zoom-Plot)
    - lon_eu1, lon_eu2, lat_eu1, lat_eu2

"""
# Parameters which can be specified__________________________________________________________________________________
u_windfile = "ERAInterim_April2010.nc"
v_windfile = "ERAInterim_April2010.nc"

# Defines the model resolution (km)
resolution = 80
# specifies the degree-resolution (only required for test case)
degree_res = 0.75
# hourly resolution of the model (only required / influence for simulation)
hourly_res = 1

# Wind speed of U-wind and V-wind components (in m/s)
test_u = 25
test_v = -25

# 1/24 reasons in the fact that fine ash can persist for several days in the air.
# We assumed here that it can stay several days (assumption here: 6 days) in the air without major fallout.
# Modelling fall out is generally complex and was simplified here
# Default fall out with 6 days (equals timesteps = 24 / hourly resolution * 6 days)
fall_out_default = 1-1/float(24/hourly_res*6)
# Specify here your own fall_out (1 - percent)
fall_out = 0.99

# Specifies the diffusion type
# 0 - gradient dependent  1 - all directions  any other number - no diffusion
diffusion_type = 1
# Specifies the diffusion percentage (Consider: diffusion will be smaller if wind is faster)
# According to a neutrally stable atmosphere D, horizontal diffusion coefficient
# Gaussian Plume Model -->cconsider this could not be valid for synoptic scale?!
# Source: Cimbala 2018 (Penn State University)
diff_coeff = 68 * (resolution ** 0.894)
diffusion_percent_default = float(100) / (resolution * 1000) * float(diff_coeff / 100)

# Specify your own diffusion percentage
diffusion_percent = 0.1

# ZOOM PLOT coordinates
# Extension Europe Longitude: -40 to 40 Latitude: 80 to 30
lat_eu1 = 31
lat_eu2 = 81
lon_eu1 = -41
lon_eu2 = 41

"""
----------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------
--------------------------------DO NOT CHANGE ANYTHING BELOW----------------------------------------------------
----------------------------------------------------------------------------------------------------------------
----------------------------------------------------------------------------------------------------------------
"""

"""
____________________________________Second Section - Auxiliary Functions_________________________________________

In this first section all Auxiliary Functions are defined.
This includes:
    - Choice between Simulation and Test
    - Choice between Eyjafjallaj%kull or own parametrisation
    - Concentration Generation Mechanism
    - Diverse String Generators for the Plot Generation
"""

# AUXILIARY FUNCTIONS_______________________________________________________________
# Function which specifies if simulation or test is run
def testORsimulation():
    print("Choose if you want to run:\n"
          "1 Test \n"
          "2 Simulation")
    test = 0
    while test < 1 or test > 2:
        try:
            test = int(input("Type your choice:"))
            if test < 1 or test > 2:
                print("Invalid choice!")
        except NameError:
            print("Invalid choice!")
            continue

    # Specifies test variable according to input
    if test == 2:
        test = False
    else:
        test = True

    return test

# Function prints all items in a list
def printVariables(list):
    i = 0
    string = ""
    for item in list:
        string += str(i) + ") " + str(item) + "  "
        i += 1
    print(string)

# Function which specifies if own scenario or Eyjafjallaj%kull scenario is run
def chooseMode():
    print("Mode description: \n"
          + "1 manual inputs \n"
          + "2 Eyjafjallajökull 2010 scenario")
    mode = 0
    while mode <= 0 or mode >= 3:
        try:
            mode = int(input("Please chose mode:"))
            if mode <= 0 or mode >= 3:
                raise AttributeError("Invalid choice!")
        except (AttributeError, NameError) as e:
            print("Invalid choice!")
            continue
    if mode == 1:
        return True
    else:
        return False

# Function which asks the user for eruption specific parameters
# returns an array with concentration value and durance
def getManualConcentration():
    print("")
    print("Mode 1: Manual mode")
    print("___________")

    executable = False
    which_failed = [0, 0, 0, 0, 0, 0, 0]
    fail = 0
    while not executable:
        try:
            if fail == 1:
                raw_input("Press enter to continue...")

            # Specification of the volcano coordinates
            # Conventions: coordinates: North = +, South = -, East = +, West = -
            print("Specification of the eruption characteristics!")
            # LONGITUDE
            if which_failed[0] == 0:
                lon_vol = float(input("Type the longitude of the volcano (decimal degrees, -180 to 180):"))
                if lon_vol > 180 or lon_vol < -180:
                    print("")
                    print("Invalid longitude value!")
                    raise AttributeError("Invalid input!")
                which_failed[0] = 1

            # LATITUDE
            if which_failed[1] == 0:
                lat_vol = float(input("Type the latitude of the volcano (decimal degrees, -90 to 90):"))
                if lat_vol < -90 or lat_vol > 90:
                    print("")
                    print("Invalid latitude value!")
                    raise AttributeError("Invalid input!")
                which_failed[1] = 1

            # PLUME HEIGHT (in m)
            if which_failed[2] == 0:
                height = int(input("Please specify your plume height (m, 0-15000): "))
                if height < 0 or height > 15000:
                    print("")
                    print("Invalid height value!")
                    raise AttributeError("Invalid input!")
                which_failed[2] = 1

            # ERUPTION DURANCE (in hours)
            if which_failed[3] == 0:
                durance = int(input("Please specify the eruption durance:"))
                if durance <= 0:
                    print("")
                    print("Invalid durance value!")
                    raise AttributeError("Invalid input!")
                which_failed[3] = 1

            # ASH FRACTION ( <63 micrometer )
            if which_failed[4] == 0:
                ash_fraction = float(input("Type in the m63-mass fraction (fraction < 63 micrometer) (value 0-1):"))
                if ash_fraction < 0 or ash_fraction > 1:
                    print("")
                    print("Invalid ash fraction value!")
                    raise AttributeError("Invalid input!")
                which_failed[4] = 1

            # MASS RATE (g/s)
            if which_failed[5] == 0:
                mass_rate = int(input("Type in the mass rate (g/s):"))
                if not mass_rate > 0:
                    print("")
                    print("Invalid mass rate value!")
                    raise AttributeError("Invalid input!")
                which_failed[5] = 1

            # VOLUME RATE (m^3/s)
            if which_failed[6] == 0:
                volume_rate = int(input("Type in the volume rate (m^3/s):"))
                if not volume_rate > 0:
                    print("")
                    print("Invalid volume rate value!")
                    raise AttributeError("Invalid input!")
                which_failed[6] = 1

            # Print a summary
            print("")
            print("You have chosen the following parameters:")
            print("Height: {}".format(height))
            print("Durance: {}".format(durance))
            print("Ash-Fraction: {}".format(ash_fraction))
            print("Mass rate: {}".format(mass_rate))
            print("Volume rate: {}".format(volume_rate))

            # Ash concentration calculation
            concentration = np.array(mass_rate) * ash_fraction / np.array(volume_rate) / (resolution * resolution)

            # Statement only reached if all conditions fulfilled
            executable = True

        except (AttributeError, NameError, SyntaxError) as e:
            print("Invalid input!")
            fail = 1
            continue

    print("")
    print("Eruption parametrisation complete.")

    return [lat_vol, lon_vol, concentration, durance]

# Function creates concentration specific to the 2010 Eyjafjallaj%kull eruption event
# returns concentration
def getEyjafjallaConcentration():
    # here the specific characteristics of the Eyjafjallajökull eruption are specified.
    print("")
    print("Mode 2: Eyjafjallajökull 2010 eruption characteristics.")
    print("_______________________________________________________")

    #LATITUDE AND LONGITUDE OUTSIDE OF FUNCTION!

    # PLUME HEIGHT (in km) (Gudmundsson et al. 2012)
    height = [0, 0, 5, 7.5, 5.5, 5.5, 5.5, 3, 4, 3.5, 5,
              5, 6, 7, 6, 5, 5.5, 5, 3, 2.5, 2.5, 2.5, 2.5, 2.5, 3, 2.5, 2.5, 2.5, 3, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5,
              3, 3, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 3.5, 3, 2, 3, 5, 5, 5, 4.5, 4.5, 4, 3.5, 3.5, 3, 2.5, 2.5, 7.5, 4.5,
              5, 5.5, 4, 3, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 2.5, 4.5, 3.5, 3, 4,
              5, 5.5, 5.5, 5.5, 6, 6, 5, 5, 5.5, 5, 5, 5, 5, 5, 4, 4.5, 4, 4.5, 4.5, 4, 4.5, 4.5, 4.5, 4, 3, 4, 5, 4.5,
              4.5, 4, 4.5, 5, 5, 5, 5.5, 8, 8, 5, 5, 5, 5, 5, 5, 5, 5.5, 5.5, 6, 7, 7, 6, 5.5, 7, 5.5, 5, 4.5, 5, 5,
              4.5, 4.5, 4.5, 3.5, 3, 4, 3.5, 4, 4, 3, 3, 2.5, 2.5, 2.5, 2.5, 2.5]

    # DURANCE (in hours)
    durance = len(height)

    # TEPHRA MASS RATE (in g/s)
    mass_rate = [0, 0, 550000000, 1000000000, 700000000, 100000000, 100000000, 50000000, 50000000, 100000000,
                 500000000, 550000000, 550000000, 550000000, 500000000, 100000000, 400000000, 400000000, 50000000,
                 50000000, 50000000, 0, 50000000, 50000000, 50000000, 0, 50000000, 50000000, 50000000, 0, 50000000,
                 0, 50000000, 50000000, 50000000, 0, 50000000, 50000000, 0, 0, 50000000, 50000000, 0, 0, 100000000,
                 100000000, 100000000, 100000000, 50000000, 0, 0, 50000000, 0, 0, 500000000, 100000000, 100000000,
                 300000000, 50000000, 0, 0, 0, 0, 0, 0, 0, 0, 0, 50000000, 0, 0, 0, 0, 0, 0, 50000000, 50000000,
                 50000000, 50000000, 50000000, 200000000, 100000000, 150000000, 350000000, 850000000, 50000000,
                 50000000, 150000000, 50000000, 50000000, 50000000, 50000000, 50000000, 50000000, 50000000,
                 50000000, 50000000, 50000000, 50000000, 50000000, 50000000, 50000000, 50000000, 50000000, 50000000,
                 50000000, 50000000, 50000000, 50000000, 50000000, 50000000, 250000000, 150000000, 50000000, 50000000,
                 50000000, 50000000, 50000000, 250000000, 300000000, 550000000, 500000000, 250000000, 50000000, 250000000,
                 50000000, 250000000, 300000000, 300000000, 350000000, 400000000, 450000000, 300000000, 300000000,
                 400000000, 300000000, 50000000, 50000000, 100000000, 50000000, 50000000, 50000000, 50000000,
                 50000000, 0, 50000000, 0, 50000000, 50000000, 50000000, 50000000, 0, 0, 0, 0, 0]

    # TEPHRA VOLUME RATE (m^3/s)
    volume_rate = [100, 100, 300, 400, 300, 100, 100, 100, 100, 100, 200, 300, 300, 300, 200, 100, 200, 200, 100,
                   100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
                   100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 200, 100, 100, 200, 100,
                   100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
                   100, 100, 100, 100, 200, 400, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
                   100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100,
                   200, 300, 200, 100, 100, 100, 100, 100, 200, 200, 200, 200, 200, 200, 200, 200, 200, 100, 100, 100,
                   100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100, 100]

    # ASH FRACTION ( <63 micrometer ) (Mastin et al. 2009)
    ash_fraction = 0.5

    # Ash concentration calculation
    concentration = np.array(mass_rate) * ash_fraction / np.array(volume_rate) / (resolution * resolution)

    print("")
    print("Eyjafjallajökull 2010 eruption parametrisation complete.")

    return concentration

# PLOT LABEL STRING FUNCTIONS
# Function creates the title string
def getTitleString(test, simulation, manual, eyjafjalla):
    title_string = ""
    if eyjafjalla and simulation:
        title_string = "Eyjafjallajoekull Eruption 2010"  # Todo: Add date time and eruption sum, diff_perc, fall_out,
        # Todo: hourly resolution resolution, diff_type
    if eyjafjalla and test:
        title_string = "Eyjafjallajoekull Test"  # Todo:ADD HERE WIND COMPONENTS
    if manual and simulation:
        title_string = "Manual Characteristics"  # Todo: Add time and date of wind_data
    if manual and test:
        title_string = "Manual Characteristics Test"

    return title_string

# Function creates the Diffusion string
# takes diffusion type and diffusion percent
def getDiffusionString(diffusion_type, diff_perc):
    diff_string = "Diffusion: " + str(diff_perc)
    if diffusion_type == 0:
        diff_string += "\n" + "Diffusion-Type: Gradients"
    elif diffusion_type == 1:
        diff_string += "\n" + "Diffusion-Type: All Directions"
    else:
        diff_string += "\n" + "Diffusion-Type: None"

    return diff_string

# Function creates the Resolution string
# takes spatial and temporal resolution
def getResolutionString(resolution, hourly_res):
    return "Spatial Resolution: " + str(resolution) + " km" + "\n" + "Temporal Resolution: " + str(
        hourly_res) + " h"


''' 
___________________________Third Section - Initialisation of wind field related data_________________________
 
 In this first section the preliminary wind-field-related parameters are initialised. 
 This includes:
 1) Specification of wind-field related parameters
    - wind-fields (u-component, v-component)
    - spatial resolution settings (longitude, latitude settings)
    - temporal resolution settings (hourly resolution, amount of modelling timesteps)
 
 Choice test:
    Test will initialize constant wind fields (u and v wind components (m/s))
 Choice simulation:
    Simulation will make use of provided wind datasets.
 
 ATTENTION: 
 Currently only supported data-format for the wind is NETCDF.
 Variable names HAVE TO BE identical in both files except for the wind-component variables!
 Wind speed HAS TO BE in m/s!
 '''

# Start of Model _______________________________________________________________________________________________
# Choice Test or Simulation
test = testORsimulation()
simulation = not test  #TODO: could be used whenever situation encounters simulation to make things clearer!

# Wind-field, Longitude, Latitude and Time initialization for the case of Simulation!
if simulation:

    print("")
    print("Simulation-Run")
    print("______________")
    # Wind Datasets used in the simulation (here for April 2010)
    u_windFile = Dataset(u_windfile)
    v_windFile = Dataset(v_windfile)

    # PRELIMINARY PROCESSING OF WIND-DATA
    # storage of NetCDF-variables
    keys_u = u_windFile.variables.keys()
    keys_v = v_windFile.variables.keys()

    # INITIALISATION
    executable = False
    which_failed = [0, 0, 0, 0, 0]
    fail = 0
    while not executable:
        if fail == 1:
            raw_input("Press enter to continue...")
            print("")

        try:
            # printing the available variables
            print("U-wind component variables:")
            printVariables(keys_u)
            print("")
            print("V-wind component variables:")
            printVariables(keys_v)
            print("")

            # Choose found variables for Longitude, Latitude, Time, U-wind component and V-wind component
            print("Choose now the variables by typing the corresponding number (see printed lists above)!")

            if which_failed[0] == 0:
                lon_key = str(keys_u[int(input("Longitude-Key:"))])
                # lon_key = "longitude"
            if which_failed[1] == 0:
                lat_key = str(keys_u[int(input("Latitude-Key:"))])
                # lat_key = "latitude"
            if which_failed[2] == 0:
                time_key = str(keys_u[int(input("Time-Key:"))])
                # time_key = "time"
            if which_failed[3] == 0:
                u_key = str(keys_u[int(input("U-wind component-Key:"))])
                # u_key = "u"
            if which_failed[4] == 0:
                v_key = str(keys_v[int(input("V-wind component-Key:"))])
                # v_key = "v"

            # Processing LONGITUDE and LATITUDE
            lon1 = u_windFile.variables[lon_key]
            if not "lon" in str(lon1._getname()).lower():
                print("")
                print("You chose the wrong longitude key!")
                raise AttributeError("Wrong variable choice!")
            which_failed[0] = 1

            lat1 = u_windFile.variables[lat_key]
            if not "lat" in str(lat1._getname()).lower():
                print("")
                print("You chose the wrong latitude key!")
                raise AttributeError("Wrong variable choice!")
            which_failed[1] = 1

            # Correction for longitude (degree east --> 0-360 to -180-180)
            lon = np.array(u_windFile.variables[lon_key])
            lon = lon - 180
            lat = np.array(u_windFile.variables[lat_key])
            dim_lon = len(lon)
            dim_lat = len(lat)

            # Processing TIME
            time_u = u_windFile.variables[time_key]
            if not "time" in str(time_u._getname()).lower():
                print("")
                print("You chose the wrong time key!")
                raise AttributeError("Wrong variable choice!")
            which_failed[2] = 1
            time_u = time_u[:]
            time_v = v_windFile.variables[time_key][:]
            time_calender = u_windFile.variables[time_key].calendar

            # convert time to date-format
            time_units = u_windFile.variables[time_key].units
            # The new print-format is: YEAR-MONTH-DAY HOUR:MINUTES:SECONDS
            time_converted = num2date(time_u, time_units, calendar=time_calender)
            timesteps = len(time_converted)
            # number of days (4 timesteps each day)
            days = len(time_converted) / (24 / hourly_res)

            # Retrieving U-WIND and V WIND-COMPONENTS
            u_wind = u_windFile.variables[u_key]
            if not " u" in " " + str(u_wind._getname()).lower():
                print("")
                print("You chose the wrong U-wind component-key!")
                raise AttributeError("Wrong variable choice!")
            which_failed[3] = 1

            v_wind = v_windFile.variables[v_key]
            if not " v" in " " + str(v_wind._getname()).lower():
                print("")
                print("You chose the wrong V-wind component-key!")
                raise AttributeError("Wrong variable choice!")
            which_failed[4] = 1

            # Statement is reached only if all statements are fulfilled!
            executable = True

        except AttributeError:
            fail = 1
            continue
        except (NameError, IndexError, SyntaxError) as e:
            print("")
            print("Invalid input!")
            fail = 1
            continue

    # Specification of SIMULATION STEPS
    executable = False
    which_failed = [0, 0]
    while not executable:
        try:
            print("Your wind dataset contains {} timesteps (equals {} days).".format(timesteps, int(days)))


            if which_failed[0] == 0:
                print("Type here the start day of the analysis:")
                start = int(raw_input("If empty all steps are used! Day 1 = 0"))
                if start < 0:
                    raise AttributeError("Invalid input")
                which_failed[0] = 1
            end = int(input("Type here the end day of the analysis:"))
            start = start * hourly_res
            if hourly_res != 1:
                end = end * hourly_res + 24 / hourly_res

            executable = True

        except ValueError:
            print("")
            print("All timesteps will be used.")
            start = 0
            end = timesteps
            executable = True
        except (SyntaxError, AttributeError) as e:
            print("")
            print("Invalid input!")
            continue

    print("")
    print("Your simulation starts on timestep " + str(start) + " and ends on timestep " + str(end) + ".")

    print("")
    print("Wind initialisation complete!")
    print("")


# Wind-field, Longitude, Latitude and Time initialization for the TEST-CASE!
# Creates an artificial wind field of constant U-wind and V-wind components.
# Dimensions are set according to initially specified degrees resolution.
# Time is initialized in one-hourly resolution (10 timesteps = 10 hours).
if test:
    print("")
    print("Test-Run")
    print("________")
    print("")
    # Create Coordinate variables
    lon = np.arange(0, 360, degree_res) - 180
    lat = np.arange(-90,90.25, degree_res)
    dim_lon = len(lon)
    dim_lat = len(lat)

    # Create wind fields
    # U wind / V wind
    u_test = np.ones((dim_lat, dim_lon))
    v_test = np.ones((dim_lat, dim_lon))
    # Specification of U-wind and V-wind components
    u_test[u_test == 1] = test_u
    v_test[v_test == 1] = test_v
    # TODO: assign here to u_wind and v_wind if necessary

    # Test hourly resolution
    hourly_res = 1

    # Specify Test-Run timesteps
    executable = False
    while not executable:
        try:
            start = 0
            end = int(input("How many timesteps do you want to model? (Wind field will not change!)"))
            if end < 0:
                raise AttributeError("Timesteps must be positive!")
            executable = True
        except (NameError, SyntaxError, AttributeError) as e:
            print("Invalid input!")
            print("")
    print("")
    print("Your simulation starts on timestep " + str(start) + " and ends on timestep " + str(end) + ".")


"""
____________________________Fourth Section - Initialisation of eruption characteristics_______________________

In this second section the eruption related parameters are initialised. 
 This includes:
 1) Specification of eruption related parameters
    - geographic location (latitude, longitude) of the eruption point source (in decimal degrees)
    - plume height (km)
    - eruption durance (h)
    - ash fraction (<63 micrometers, 0-1)
    - mass rate (g/s)
    - volume rate (m^3/s)
    
 Choice 1: Manual Mode
    Within the manual mode all the parameters are specified manually.
    The result is one specific concentration which will be constant over the whole simulation.
    The point source will therefore never stop to emit material.
    
 Choice 2: Eyjafjallaj%kull 2010 eruption parametrisation.
    The parametrization of the Eyjafjallaj%kull eruption is achieved using the following sources:
        - geographic location
        - plume height (Gudmundsson et al. 2012)
        - eruption durance (Gudmundsson et al. 2012)
        - ash fraction (Mastin et al. 2009)
        - tephra mass rate (Gudmundsson et al. 2012)
        - tephra volume rate (Gudmundsson et al. 2012)
    
ATTENTION:
The plume height has no influence in this model! It is initialised for the eventually future introduction of
new modelling features.
"""

# Specify the Mode
manual = chooseMode()
eyjafjalla = not manual

if manual:
    # Calls the Manual input auxiliary function
    manualParameters = getManualConcentration()
    lat_vol = manualParameters[0]
    lon_vol = manualParameters[1]
    concentration = manualParameters[2]
    durance = manualParameters[3]


if eyjafjalla:
    # Calls the Eyjafjallajökull concentration auxiliary function
    concentration = getEyjafjallaConcentration()
    # LONGITUDE AND LATITUDE
    lon_vol = -19.625
    lat_vol = 63.625


""" 
____________________________________Fifth Section - Transport-Diffusion-Modelling________________________________
DYNAMICS:
Our model is inspired by the advection-diffusion equation (as described in Folch 2012). 
We decided however to implement simplified transport-diffusion dynamics.
The transport of the particles is determined by wind direction and wind speed.
Therefore, we classified the surrounding cells according to the wind-direction.
Depending on the wind speed, different percentages of the cells concentration are transported.

For the diffusion we implemented two options:
    1) All Directions:
        In all direction-diffusion each surrounding cell (8 cells) receives an eighth of the diffusion part.
    2) Gradient dependent
        In gradient dependent-diffusion we first calculate the gradients of each surrounding cell with respect
        to the source cell. Diffusion is then only happening in direction of negative gradients (this means in 
        direction of the lower concentrations).
    
    NOTE: The diffusion is run AFTER the transport of every cell is completed.
        

PARTICULARITIES:
We tried to account for the different hourly resolutions.
If the temporal wind-field resolution is x > 1 hour the model loop will run x-times until a new wind-field is loaded.
The same holds for fall_out and eruption input.

"""

# Get the closest coordinates with respect to specified longitude and latitude values
lat_pos = lat[np.where(abs(lat - lat_vol) == min(abs(lat - lat_vol)))][0]
lon_pos = lon[np.where(abs(lon - lon_vol) == min(abs(lon - lon_vol)))][0]
# Get index of closest longitude and latitude values
lat_index = int(np.where(lat == lat_pos)[0])
lon_index = int(np.where(lon == lon_pos)[0])

# Zero-Raster for storage of particle concentration during the modelling
particles = np.zeros((dim_lat, dim_lon,))

# Calculating Distance for diagonal transport (with cosine of 45 degrees)
resolution_extended = resolution / math.cos(0.785398)

# Defining the row and col numbers
rows = dim_lat
cols = dim_lon

# Creates an array with integer values from the start to the (end - 1) value
timesteps = np.arange(start, end, 1)

# Empty list to store particles values of each timestep
# Used for plotting all frames in the end of the model run
figures = []
# Variable to sum up all fall_out
sum_fallout = 0

# Variable to sum up total erupted material
eruption_sum = 0

print("")
raw_input("Press enter to initiate the modeling process...")
print("")
print("Modeling process initiated, going through {} iterations.".format(len(timesteps)*hourly_res))

# for-loop to go through specified amount of timesteps
for n in timesteps:

    # Setting up the wind fields for each timestep
    # If it's a test - the same wind field for every timestep is used
    if not test:
        u = u_wind[n, :, :]
        v = v_wind[n, :, :]
    else:
        u = u_test
        v = v_test

    # POINT SOURCE INITIALISATION
    # At specified geographic location the eruption concentration at current timestep will be
    # added.
    if eyjafjalla:
        if n - min(timesteps) < len(concentration):
            if particles[lat_index, lon_index] != 0.0:
                particles[lat_index, lon_index] += concentration[n - min(timesteps)]
            else:
                particles[lat_index, lon_index] = concentration[n - min(timesteps)]

            eruption = concentration[n - min(timesteps)]
            eruption_sum += eruption
        else:
            eruption = 0
    if manual:
        if n - min(timesteps) < durance:
            if particles[lat_index, lon_index] == 0:
                particles[lat_index, lon_index] = concentration
            else:
                particles[lat_index, lon_index] += concentration

            eruption = concentration
            eruption_sum += eruption

    # go through every pixel and evaluate its next time step, then save to temp_arr
    # TODO: Handle the OutOfBoundsError
    # TODO: Handle it such that overflow will be added behind! like when -180 is reached then +180 / 179 entering

    # Adjustment for temporal resolution of wind data
    # if hourly_res = 6 hours the loop will run 6 times before changing the wind field
    res_correction = np.arange(0, hourly_res, 1)

    for k in res_correction:
        # create temporary array to save calculated time steps
        temp_arr = np.zeros((rows, cols))

        if k == 0:
            # summing up fall out for surveillance mechanism
            sum_fallout += sum(particles[particles > 0.0] * (1 - fall_out))

            # Fall-out processing
            particles = particles * fall_out

        # Save the very first figure without transport and diffusion
        if n - min(timesteps) == 0:
            figures.append(particles)

        print("..." * 10)
        print("..." * 10)
        if not test:
            print("timestep {}, erupting {} g/m^3".format(n*hourly_res + k + 1, eruption))
        if test:
            print("timestep {}, erupting {} g/m^3".format(n + 1, eruption))

        # TRANSPORT LOOP_______________________
        i = 0
        while i < rows:
            j = 0
            while j < cols:

                # Retrieving u and v wind speed value
                wind_u = u[i, j]
                wind_v = v[i, j]

                # Calculating absolute wind speeds and diagonal wind speed
                v_dir = abs(wind_v)
                u_dir = abs(wind_u)
                diag = math.sqrt(u_dir**2 + v_dir**2)

                # Determining the wind angle! (0-360)
                wind_dir_trig_to = math.atan2(wind_u / diag, wind_v / diag)
                degrees = wind_dir_trig_to * 180 / math.pi

                # Adjustment for angles < 0 (atan2 --> -180 to 180)
                if degrees < 0:
                    degrees += 360

                # Classification of transport receiving cell
                cell = np.nan

                if 337.5 < degrees or degrees <= 22.5:
                    cell = 1
                if 22.5 < degrees <= 67.5:
                    cell = 2
                if 67.5 < degrees <= 112.5:
                    cell = 3
                if 112.5 < degrees <= 157.5:
                    cell = 4
                if 157.5 < degrees <= 202.5:
                    cell = 5
                if 202.5 < degrees <= 247.5:
                    cell = 6
                if 247.5 < degrees <= 292.5:
                    cell = 7
                if 292.5 < degrees <= 337.5:
                    cell = 8

                # wind in km/h
                wind_u_km = wind_u * 3.6
                wind_v_km = wind_v * 3.6
                diag_km = diag * 3.6

                # Determining highest wind speed of u, v and diagonal wind
                max_wind = max(wind_u_km, wind_v_km, diag_km)

                # Optional: Diffusion adjustments according to different wind speeds
                if max_wind > 50:
                    diff_perc = 0
                else:
                    diff_perc = diffusion_percent
                diff_perc = diffusion_percent # TODO: cancel this line if diffusion should be adjusted to wind speed

                # Classification of how much concentration should be transported
                # 100% if wind reaches "resolution" km/h
                transport_perc = 0

                if max_wind >= (resolution - 5) :
                    transport_perc = 1
                if (resolution - 5) > max_wind >= resolution * 0.8 - 5:
                    transport_perc = 0.95 #0.8
                if resolution * 0.8 - 5 > max_wind >= resolution * 0.6 - 5:
                    transport_perc = 0.9 #0.6
                if resolution * 0.6 - 5 > max_wind:
                    transport_perc = 0.85 #0.4
                if max_wind == 0:
                    transport_perc = 0

                try:
                    # calculates diffusion part
                    diff_amount = particles[i, j] * diff_perc

                    # receiving concentrations from all grid cells
                    # x_origin - diff_amount = portion of transportable wind
                    x_origin = particles[i, j] - diff_amount

                    x1 = particles[i + 1, j]
                    x2 = particles[i + 1, j + 1]
                    x3 = particles[i, j + 1]
                    x4 = particles[i - 1, j + 1]
                    x5 = particles[i - 1, j]
                    x6 = particles[i - 1, j - 1]
                    x7 = particles[i, j - 1]
                    x8 = particles[i + 1, j - 1]

                    if not x_origin == 0.0:

                        # Concentration transport processing
                        if cell == 1:
                            temp_arr[i + 1, j] = x_origin * transport_perc # i-1, j
                        if cell == 2:
                            temp_arr[i + 1, j + 1] = x_origin * transport_perc # i-1, j+1
                        if cell == 3:
                            temp_arr[i, j + 1] = x_origin * transport_perc
                        if cell == 4:
                            temp_arr[i - 1, j + 1] = x_origin * transport_perc # i+1, j+1
                        if cell == 5:
                            temp_arr[i - 1, j] = x_origin * transport_perc # i + 1, j
                        if cell == 6:
                            temp_arr[i - 1, j - 1] = x_origin * transport_perc #i + 1, j - 1
                        if cell == 7:
                            temp_arr[i, j - 1] = x_origin * transport_perc
                        if cell == 8:
                            temp_arr[i + 1, j - 1] = x_origin * transport_perc # i-1, j-1

                        # Adjust ash concentration from origin cell to the losses
                        updated = x_origin - (x_origin * transport_perc)
                        if updated < 0.00000001:
                            temp_arr[i, j] += (0 + diff_amount)
                        else:
                             temp_arr[i, j] += (updated + diff_amount)

                except IndexError:
                    # this is to prevent the program from collapsing in case one of the above conditions tries to
                    # access a pixel outside of the range of a numpy array, like a pixel with index particles[-10,
                    # -10] in that case the program should just pass the condition and move on
                    # TODO: OutOfBounds-problem should get solved (transport poles to poles)
                    pass

                # iterating through columns
                j += 1

            # iterating through rows
            i += 1

        # DIFFUSION LOOP_____________________________________
        # temporary array to store diffusion process timesteps
        diffusion = np.zeros((dim_lat, dim_lon))
        p = 0
        while p < rows:
            o = 0
            while o < cols:

                # Retrieving u, v and diagonal wind speed value
                wind_u = u[p, o]
                wind_v = v[p, o]
                diag = math.sqrt(wind_u**2 + wind_v**2)

                # wind in km/h
                wind_u_km = wind_u * 3.6
                wind_v_km = wind_v * 3.6
                diag_km = diag * 3.6

                # Determining highest wind speed of u, v and diagonal wind
                max_wind = max(wind_u_km, wind_v_km, diag_km)

                # Optional: Diffusion adjustments according to different wind speeds
                if max_wind > 50:
                    diff_perc = 0
                else:
                    diff_perc = diffusion_percent
                diff_perc = diffusion_percent # TODO: cancel this line if diffusion should be adjusted to wind speed

                try:
                    # calculates diffusion part
                    diff_amount = temp_arr[p, o] * diff_perc

                    # receiving concentrations from all grid cells
                    # x_origin - diff_amount = portion of transportable wind
                    x_origin = temp_arr[p, o] - diff_amount

                    if x_origin != 0:
                        x1 = temp_arr[p + 1, o]
                        x2 = temp_arr[p + 1, o + 1]
                        x3 = temp_arr[p, o + 1]
                        x4 = temp_arr[p - 1, o + 1]
                        x5 = temp_arr[p - 1, o]
                        x6 = temp_arr[p - 1, o - 1]
                        x7 = temp_arr[p, o - 1]
                        x8 = temp_arr[p + 1, o - 1]

                        # calculate the gradients of all surrounding cells with respect to x_origin
                        # only used if diffusion-type = 0
                        grad_x1 = (x1 - x_origin) / resolution
                        grad_x2 = (x2 - x_origin) / resolution_extended
                        grad_x3 = (x3 - x_origin) / resolution
                        grad_x4 = (x4 - x_origin) / resolution_extended
                        grad_x5 = (x5 - x_origin) / resolution
                        grad_x6 = (x6 - x_origin) / resolution_extended
                        grad_x7 = (x7 - x_origin) / resolution
                        grad_x8 = (x8 - x_origin) / resolution_extended

                        # store all gradients
                        gradients = [grad_x1, grad_x2, grad_x3, grad_x4, grad_x5, grad_x6, grad_x7, grad_x8]

                        # DIFFUSION with respect to gradients
                        if diffusion_type == 0:

                            # only executed if any gradient is negative (lower concentration in destination cell)
                            if any(n < 0 for n in gradients):

                                no_cells = sum(n < 0 for n in gradients)

                                # Diffusion processing
                                # diffusion part / number of cells with negative gradient will be diffused
                                # to the corresponding destination cells
                                if grad_x1 < 0:
                                    diffusion[p + 1, o] += diff_amount / no_cells
                                if grad_x2 < 0:
                                    diffusion[p + 1, o + 1] += diff_amount / no_cells
                                if grad_x3 < 0:
                                    diffusion[p, o + 1] += diff_amount / no_cells
                                if grad_x4 < 0:
                                    diffusion[p - 1, o + 1] += diff_amount / no_cells
                                if grad_x5 < 0:
                                    diffusion[p - 1, o] += diff_amount / no_cells
                                if grad_x6 < 0:
                                    diffusion[p - 1, o - 1] += diff_amount / no_cells
                                if grad_x7 < 0:
                                    diffusion[p, o - 1] += diff_amount / no_cells
                                if grad_x8 < 0:
                                    diffusion[p + 1, o - 1] += diff_amount / no_cells

                                # Adjust x_origin after diffusion processing
                                diffusion[p, o] += temp_arr[p, o] - diff_amount

                        # DIFFUSION in all directions
                        if diffusion_type == 1:

                            # Diffusion processing
                            # diffusion part / 8 surrounding cells will be diffused
                            diffusion[p + 1, o] += diff_amount / 8
                            diffusion[p + 1, o + 1] += diff_amount / 8
                            diffusion[p, o + 1] += diff_amount / 8
                            diffusion[p - 1, o + 1] += diff_amount / 8
                            diffusion[p - 1, o] += diff_amount / 8
                            diffusion[p - 1, o - 1] += diff_amount / 8
                            diffusion[p, o - 1] += diff_amount / 8
                            diffusion[p + 1, o - 1] += diff_amount / 8

                            # Adjust x_origin after diffusion processing
                            diffusion[p, o] += temp_arr[p, o] - diff_amount

                        # if no diffusion is happening (e.g. diff_percent = 0)
                        # the diffusion array is set equal to the temporary array (after-transport-array)
                        empty = diffusion[diffusion > 0]
                        if empty.size == 0:
                            diffusion = temp_arr
                except IndexError:
                    # this is to prevent the program from collapsing in case one of the above conditions tries to
                    # access a pixel outside of the range of a numpy array, like a pixel with index particles[-10,
                    # -10] in that case the program should just pass the condition and move on
                    # TODO: OutOfBounds-problem should get solved (transport poles to poles)
                    pass
                o += 1
            p += 1

        # saving the diffusion array as the new particles for the next time-step
        particles = diffusion
        # Save figure of timestep
        figures.append(particles)

# FINAL EXECUTION STATEMENTS__________________

# Prints Eruption Execution Summary
print("{}{} RESULTS {}{}".format("\n", "---" * 10, "---" * 10, "\n"))
print("Model ran {} timesteps with total eruption output of {} g/m^3.".format(len(timesteps)*hourly_res, eruption_sum))

# Surveillance mechanism for MASS BALANCE check
sum_particles = sum(particles[particles != 0])
comparison_sum = round(sum_particles + sum_fallout)
if abs(round(eruption_sum) - comparison_sum) >= 1:
    print("")
    print("WARNING: MASS BALANCE WAS NOT FULFILLED!!!")
else:
    print("")
    print("MASS BALANCE FULFILLED!")

"""
____________________________________Sixth Section - Generating Plots_______________________________________________

In this fourth sections the visual products are generated.
This consists of the following outputs:
1) Whole World Extent Graph in "XY" Projection
2) Composition of two graphs of Europe
    2.1) Graph as in 1) but restricted to Europe
    2.2) Graph with contour levels
        --> 0 to 2*10^-4 g/m^3 (Open to air traffic)
        --> beginning at 2*10^-4 g/m^3 (Enhanced Procedure Zones)
        --> beginning at 2*10^-3 g/m^3 (No Fly Zone)
        
        The flight-zone concentrations are chosen following the Civil Aviation Authority (CAA)
        

The used colormap is inspired by the visualisation of EUMETRAIN's Volcanic Ash Training Module.
(see http://eumetrain.org/data/1/144/navmenu.php?page=4.0.0)
    
"""

# plt.imsave("Ash_Plumes\Ash_Plume{}".format(n), particles, cmap='gray')

# FIGURE 1
# Creating a color map
# minus values = tricks: basemap would be better option (package basemap) -->more complicated
clevs = [0, 10**-4, 10**-3, 10**-2, 10**-1, 10**0, 10**1, 10**2, 10**3, 10**4]
cmap_cols = [(255,255,255),
            (0, 191, 255),
            (28,134,238),
            (16,78,139),
            (0,0,128),
            (178,58,238),
            (104,34,139),
            (238,18,137),
            (0,0,0)]

cmap_data = np.array(cmap_cols) / 255.0
cmap = mcolors.ListedColormap(cmap_data, 'concentrations')
norm = m.colors.BoundaryNorm(clevs, ncolors=cmap.N, clip=True)


# mill, ortho, cyl, moll
mbase = Basemap(projection='cyl', lat_0=45, lon_0=lon_vol, resolution='l')
lon2, lat2 = np.meshgrid(lon, lat)
x, y = mbase(lon2, lat2)

title_string = getTitleString(test, simulation, manual, eyjafjalla)
diff_string = getDiffusionString(diffusion_type, diff_perc)
res_string = getResolutionString(resolution, hourly_res)


prints = np.arange(0, len(figures), 1)

# BASEMAP TRY
for n in prints:
    #fig, ax = plt.subplots()
    fig = plt.figure(figsize=(19.23, 9.93))
    # m.fillcontinents(color='gray',lake_color='gray')
    mbase.drawcoastlines()
    mbase.drawparallels(np.arange(-80., 81., 20.), labels=[1, 0, 0, 0])
    mbase.drawmeridians(np.arange(-180., 181., 20.), labels=[0, 0, 0, 1])
    mbase.drawmapboundary(fill_color='white')
    mbase.drawcountries()
    cs = mbase.contourf(x, y, figures[n], locator=ticker.LogLocator(), levels=clevs, cmap=cmap, norm=norm)
    plt.title(title_string, fontsize=20, pad=30) #20
    cbar = plt.colorbar(fraction=0.05, pad=0.07, shrink=0.82, aspect=20, extendrect=False);
    cbar.set_ticklabels(["0", r'$10^{-4}$', r'$10^{-3}$', r'$10^{-2}$', r'$10^{-1}$', r'$10^0$', r'$10^1$', r'$10^2$',
                         r'$10^3$', r'$10^4$'])
    cbar.ax.set_title("Concentration [g/$m^3$]", pad=20)

    if n == 0:
        time_string = "Initialisation"
        counter = 0
    elif test:
        time_string = "Timestep: " + "+ " + str(timesteps[n - 1] + 1) + " h"
    elif simulation:
        if hourly_res == 1:
            time_string = str(time_converted[n - 1])
        else:
            if (n-1) % hourly_res == 0 and (n-1) > 0:
                counter += 1
            time_string = str(time_converted[counter]) + " + " + str((n-1) % hourly_res) + " h"

    plt.text(x=90, y=94, s=diff_string, fontdict={'size': 12})
    plt.text(x=90, y=104, s=res_string, fontdict={'size': 12})
    plt.text(x=-200, y=94, s=time_string, fontdict={'size': 12})

    if test:
        plt.text(x=-200, y=100, s="U-component: " + str(test_u) + " m/s" + "\n" + "V-component: " + str(test_v) + " m/s",
                 fontdict={'size': 12})

    number = str(n)
    if int(number) < 10:
        number = "00" + number
    elif int(number) < 100:
        number = "0" + number

    fig.savefig("WorldMap\WorldMap_{}".format(number))
    plt.close(fig)

# FIGURE 2
# Creating two plots of Europe
# Plot 1: As before
# Plot 2: Flight restriction zones

# Get the closest coordinates with respect to specified longitude and latitude values
# Extent is defined by user!
lat_pos_eu1 = lat[np.where(abs(lat - lat_eu1) == min(abs(lat - lat_eu1)))][0]
lat_pos_eu2 = lat[np.where(abs(lat - lat_eu2) == min(abs(lat - lat_eu2)))][0]
lon_pos_eu1 = lon[np.where(abs(lon - lon_eu1) == min(abs(lon - lon_eu1)))][0]
lon_pos_eu2 = lon[np.where(abs(lon - lon_eu2) == min(abs(lon - lon_eu2)))][0]
# Get index of closest longitude and latitude values
lat_index_eu1 = int(np.where(lat == lat_pos_eu1)[0])
lat_index_eu2 = int(np.where(lat == lat_pos_eu2)[0])
lon_index_eu1 = int(np.where(lon == lon_pos_eu1)[0])
lon_index_eu2 = int(np.where(lon == lon_pos_eu2)[0])

lon_plot = lon[lon_index_eu1:lon_index_eu2]
lat_plot = lat[lat_index_eu1:lat_index_eu2]

# mill, ortho, cyl, moll
mbase2 = Basemap(projection='cyl', llcrnrlat=lat_eu1, urcrnrlat=lat_eu2, llcrnrlon=lon_eu1, urcrnrlon=lon_eu2,
                 resolution='l', )
lon_eu, lat_eu = np.meshgrid(lon_plot, lat_plot)
x2, y2 = mbase(lon_eu, lat_eu)


# EUROPE ZOOM
for n in prints:
    fig = plt.figure(figsize=(19.23,9.91))
    ash_picture = figures[n][lat_index_eu1:lat_index_eu2, lon_index_eu1:lon_index_eu2]
    plt.contourf(x2, y2, ash_picture, levels=clevs, cmap=cmap, norm=norm)
    mbase2.drawcoastlines()
    mbase2.drawparallels(np.arange(30., 81., 10.), labels=[1, 0, 0, 0])
    mbase2.drawmeridians(np.arange(-40., 41., 10.), labels=[0, 0, 0, 1])
    mbase2.drawmapboundary(fill_color='white')
    mbase2.drawcountries()

    plt.title(title_string, fontsize=20, pad=30)  # 20
    cbar = plt.colorbar(fraction=0.05, pad=0.07, shrink=1, aspect=20, extendrect=False);
    cbar.set_ticklabels(["0", r'$10^{-4}$', r'$10^{-3}$', r'$10^{-2}$', r'$10^{-1}$', r'$10^0$', r'$10^1$',
                         r'$10^2$', r'$10^3$', r'$10^4$'])
    cbar.ax.set_title("Concentration [g/$m^3$]", pad=20)

    if n == 0:
        time_string = "Initialisation"
        counter = 0
    elif test:
        time_string = "Timestep: " + "+ " + str(timesteps[n - 1] + 1) + " h"
    elif simulation:
        if hourly_res == 1:
            time_string = str(time_converted[n - 1])
        else:
            if (n - 1) % hourly_res == 0 and (n - 1) > 0:
                counter += 1
            time_string = str(time_converted[counter]) + " + " + str((n - 1) % hourly_res) + " h"

    plt.text(x=25, y=82, s=diff_string, fontdict={'size': 12})
    plt.text(x=25, y=85.75, s=res_string, fontdict={'size': 12})
    plt.text(x=25, y=84.5, s="Fall-out: " + str(1-fall_out), fontdict={'size': 12})
    plt.text(x=-41, y=82, s=time_string, fontdict={'size': 12})

    if test:
        plt.text(x=-41, y=83.5, s="U-component: " + str(test_u) + " m/s" + "\n" + "V-component: " + str(test_v) + " m/s",
                 fontdict={'size': 12})

    number = str(n)
    if int(number) < 10:
        number = "00" + number
    elif int(number) < 100:
        number = "0" + number

    fig.savefig("EuropeZoom\EuropeZOOM_{}".format(number))
    plt.close(fig)



# Creating a new color map for Flight Zones
clevs2 = [0, 2*10**-4, 2*10**-3,  10**4]
cmap_cols2 = [(255,255,255),
              (255,255,0),
              (255,0,0)]

cmap_data2 = np.array(cmap_cols2) / 255.0
cmap2 = mcolors.ListedColormap(cmap_data2, 'concentrations')
norm2 = m.colors.BoundaryNorm(clevs2, ncolors=cmap2.N, clip=True)

# EUROPE FLIGHT RESTRICTION ZONES
for n in prints:
    fig = plt.figure(figsize=(19.23,9.91))
    ash_picture = figures[n][lat_index_eu1:lat_index_eu2, lon_index_eu1:lon_index_eu2]
    plt.contourf(x2, y2, ash_picture, levels=clevs2, cmap=cmap2, norm=norm2)
    mbase2.drawcoastlines()
    mbase2.drawparallels(np.arange(30., 81., 10.), labels=[1, 0, 0, 0])
    mbase2.drawmeridians(np.arange(-40., 41., 10.), labels=[0, 0, 0, 1])
    mbase2.drawmapboundary(fill_color='white')
    mbase2.drawcountries()

    fig.subplots_adjust()

    plt.title(title_string, fontsize=20, pad=30)  # 20
    cbar = plt.colorbar(fraction=0.05, pad=0.07, shrink=0.95, aspect=20, extendrect=False);
    cbar.set_ticklabels(["0", r'$2*10^{-4}$', r'$2*10^{-3}$', r'$10^4$'])
    cbar.ax.set_title("Concentration [g/$m^3$]", pad=20)

    if n == 0:
        time_string = "Initialisation"
        counter = 0
    elif test:
        time_string = "Timestep: " + "+ " + str(timesteps[n - 1] + 1) + " h"
    elif simulation:
        if hourly_res == 1:
            time_string = str(time_converted[n - 1])
        else:
            if (n - 1) % hourly_res == 0 and (n - 1) > 0:
                counter += 1
            time_string = str(time_converted[counter]) + " + " + str((n - 1) % hourly_res) + " h"

    plt.text(x=25, y=82, s=diff_string, fontdict={'size': 12})
    plt.text(x=25, y=85.75, s=res_string, fontdict={'size': 12}) #25 84.5
    plt.text(x=25, y=84.5, s="Fall-out: " + str(1 - fall_out), fontdict={'size': 12})
    plt.text(x=-41, y=82, s=time_string, fontdict={'size': 12})

    if test:
        plt.text(x=41, y=83.5, s="U-component: " + str(test_u) + " m/s" + "\n" + "V-component: " + str(test_v) + " m/s",
                 fontdict={'size': 12})

    # plt.text(x=58, y=78, s="Flight Zones", fontdict={'weight':"bold"}, fontsize=14)
    plt.text(x=-39.5, y=37.5, s="Flight Zones", fontdict={'weight': "bold"}, fontsize=17, color="blue")
    plt.text(x=-39.5, y=32.5, s="1 Open to air traffic \n2 Enhanced Procedure Zone \n3 Restricted Zone", fontsize=15)

    plt.text(x=52, y=39.5, s="1", fontdict={'weight': "bold"}, fontsize=30, color="blue")
    plt.text(x=52, y=55, s="2", fontdict={'weight': "bold"}, fontsize=30, color="blue")
    plt.text(x=52, y=71, s="3", fontdict={'weight': "bold"}, fontsize=30, color="blue")

    # plt.text(x=43.5, y=39.5, s="1", fontdict={'weight': "bold"}, fontsize=30, color="blue")
    # plt.text(x=43.5, y=55, s="2", fontdict={'weight': "bold"}, fontsize=30, color="blue")
    # plt.text(x=43.5, y=71, s="3", fontdict={'weight': "bold"}, fontsize=30, color="blue")

    number = str(n)
    if int(number) < 10:
        number = "00" + number
    elif int(number) < 100:
        number = "0" + number

    fig.savefig("EuropeFlyzone\EuropeFLYZONES_{}".format(number))
    plt.close(fig)


''' 
____________________________________Seventh Section - References_________________________________________________

Mastin, L.G., Guffanti, M., Servranckx, R., Webley, P., Barsotti, S., Dean, K., Durant, A, Ewert, J.W., Neri, A.,
              Rose, W.I., Schneider, D., Siebert, L., Stunder, B., Swanson, G., Tupper, A., Volentik, A.,
              Waythomas, C.F. (2009): A multidisciplinary effort to assign realistic source parameters to models of
              volcanic ash-cloud transport and dispersion during eruptions.
              In: Journal of Volcanology and Geothermal Research 186: 10-21.
              DOI: 10.1016/j.jvolgeores.2009.01.008
              
Folch, A. (2012): A review of tephra transport and dispersal models: Evolution, current status, and future perspectives.
              In: Journal of Volcanology and Geothermal Research 235-236: 96-115.
              DOI: 10.1016/j.jvolgeores.2012.05.020
              
Cimbala, J. M. (2018): Gaussian Plume Model and Dispersion Coefficients. Pennsylvania State University.
              Latest revision: 30th January 2018.
              Available under: https://www.mne.psu.edu/cimbala/me433/Lectures/Tables_for_Gaussian_Plume_Model.pdf
              
Gudmundsson, M.T., Thordarson, T., Hoeskuldsson, A., Larsen, G., Bjoernsson, H., Prata, F.J., Oddsson, B.,
             Magnusson, E., Hoegnadottir, T., Petersen, G.N., Hayward, C.L., Stevenson, J.A., Jonsdottir, I.
             (2012): Ash generation and distribution from the April-May 2010 eruption of Eyjafjallajoekull, Iceland.
             In: Scientific Reports 2:572: S.1-12.
             DOI: 10.1038/srep00572
             
'''
