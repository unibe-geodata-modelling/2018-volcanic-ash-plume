*2018-volcanic-ash-plume*

# Modelling Eyjafjallajökull Volcanic Ash Plume of 2010

Authors:

_Christoph von Matt, 13-105-358, christoph.vonmatt@students.unibe.ch_

_Benjamin Schuepbach, 14-100-564, benjamin.schuepbach@students.unibe.ch_




## About Our Model

This project is our homework submission for the seminar  _438745-FS2018-0- Geodata analysis and modeling_ at the University of Bern in Switzerland. We built a model of [the ash plume dispersion after the eruption of Eyjafjallajökull in 2010](https://en.wikipedia.org/wiki/2010_eruptions_of_Eyjafjallaj%C3%B6kull).

To build our model we worked with Python v2.7.0 by using a Conda Environment.

The model dynamics is inspired by the many different particle-transport-models that exist and which often base on the advection-diffusion equation (as described in e.g. _Folch 2012_).
We decided however to implement simplified transport-diffusion dynamics.
The transport of the particles is determined by wind direction and wind speed.
Therefore, we classified the surrounding cells according to the wind-direction.
Depending on the wind speed, different percentages of the cells concentration are transported.

For further information on the transport and diffusion process, please consider the explanations below.

---

### Model Settings

Our model can be run with different settings:

**Test or Simulation**: Choices related to wind field initialisation

The **Test** mode initializes constant wind fields with constant wind speed and wind direction. In this mode the wind field
does not change during the whole modeling process. As indicated this mode is primarily for (functionality) testing purposes.
Wind speeds for U-wind and V-wind components can be specified by the user.
As the wind fields are created artificially, the user can specify the model resolution too.

The **Simulation** mode initializes wind fields out of NetCDF-wind files provided by the user. The user has to provide two
NetCDF-files, one for each wind component. It is very important that all variables, except the ones for U- and V-wind components are identical!

_Attention: The only supported data format is the NetCDF-format!_


**Manual Parametrisation or Eyjafjallajökull Parametrisation:** Choices related to eruption characteristics

The **Manual** mode allows the complete specification of all parameters needed to calculate the erupted ash concentration.
This includes the _geographic location_ of the volcano, the _plume height_, the _durance_ of the eruption, the _mass fraction_
of the particles (<63 micrometers), as well as tephra _mass_ and tephra _volume rates_. This results in one single concentration value which
is erupted for the specified durance. Again, this mode is primarily for testing purposes.

In the **Eyjafjallakökull** mode the erupted ash concentration is calculated with predefined values for all needed parameters.
We therefore use literature based values for the Eyjafjallajökull eruption event back in 2010. The result is an available eruption concentration sequence of 156 values (6-hourly-resolution) starting from the 14th April 2010 until the 22th May 2010.

We obtained the Eyjafjallajökull 2010 concentration by using the following literature:

- Plume height, eruption durance, (tephra) mass rate, (tephra) volume rate  &rarr; (*Gudmundsson et al. 2012*)
- Ash mass fraction &rarr; (*Mastin et al. 2009*)

---


### Input Parameters / Model Components:
In the following all needed input parameters are listed and shortly explained. Depending on the chosen model settings
the user may be prompted to provide input values.

Required parameters and components are:



+ **Wind Data**

     In the **Simulation** mode the user has to provide 2 NetCDF-filenames (ending in ".nc") for both U-wind and
     V-wind components. It is very important that all variables, except the ones for U- and V-wind components are identical!
     
     In the **Test** mode the user can specify the constant wind speeds for both wind-components.
     
     In both cases the initialised wind fields consist of two rasters with one containing the values for the U-wind component
     and the other for the V-wind component.


+ **Timesteps**

   Time is defined as steps, which in turn represent iterations.
   
   In the **Simulation** mode the user can choose for which available time period (in days) the simulation should run.
   The amount of days is calculated from available timesteps and temporal resolution. The number of timesteps is then
   adjusted according to the chosen period length.
   
   In the **Test** mode the hourly resolution is by default 1 hour. Thus, the user input equals directly the timesteps
   executed.


+ **Resolution**
   
   * Spatial Resolution
      
      In the **Simulation** mode the user has to specify the spatial resolution such that it equals the one of the provided
      wind datasets.
      
      In the **Test** mode the spatial resolution can be chosen arbitrary. To not obtain non-sense results both, the resolution
      in kilometers as well as the resolution in degrees should be chosen interdependently.
      
   * Temporal Resolution
   
      In the **Simulation** mode the user has to specify the temporal resolution (in hours) such that it equals the one of the
      provided wind datasets.
      
      In the **Test** mode the temporal resolution cannot be changed and is by default 1 hour.
   


+ **Location of Volcano**

   In the **Manual** mode the user can specify arbitrary *longitude* and *latitude* values for the volcano 
   (point source) location. 
   
   In the **Eyjafjallakökull** mode the location of the volcano is specified as follows:
   
   &rarr; *Longitude:* -19.625 
   <br> &rarr; *Latitude:* 63.625.
   
   *Attention: Be aware that the model uses decimal coordinate values!*
   
+ **Particle fall-out**
     
     The particle *fall-out* parameter describes what amount of particles falls out of the system by each timestep. <br>
     The particle fall-out can be specified by the user in all model settings and should be given as **1 - percent** value
     [0-1].
     
     The default fall-out was determined by the idea that the finer particles can remain in the air for several days without
     major fall-out. The default fall-out assumes that this durance is 6 days.
     
+ **Diffusion**
     
     * Diffusion coefficient
          
          The *diffusion coefficient* was calculated according to a Gaussian plume model and was calculated as follows
          (assuming a neutrally stable atmosphere): <br>
          <br>**Diffusion coefficient = 68 x resolution^0.894**  &rarr; (*Cimbala 2018*)
          
     * Diffusion Percentage
          
          The *diffusion percentage* determines how much of the ash concentration is diffused.
          
          
          For the calculation of the default diffusion percentage the diffusion coefficient is used.
          As the Gaussian Plume model may not be accurate for synoptic scale dispersion / diffusion the user can also
          choose an arbitrary diffusion percentage in the range between 0 and 1.
          
     * Diffusion Type
          
          We implemented two different *diffusion types* in our model (see Section "What our Model does (How to Volcano)").
          
          The choices are as follows:<br>
          1 - Diffusion in all directions **(Choice: 0)**<br>
          2 - Gradient-dependent diffusion **(Choice: 1)**<br>
          3 - no diffusion **(Choice: any other number)**


+ **Ash Plume height**
     
     The *ash plume height* specifies the height of the erupted ash cloud in kilometers.
     
     As already declared above, in the **Manual** mode the user can specify the ash plume height, while in the
     **Eyjafjallajökull** mode predefined values (according to *Gudmundsson et al. 2012*) are used.

   
+  **Mass- and Volume Rates**
     
     The *mass-* and *volume rates* specify the erupted rates of tephra mass (in g/m^3) and tephra volume (in m^3/s).
     
     As with the plume height, the user can specify the mass- and volume rates manually in the **Manual** mode while 
     predefined values are used in the **Eyjafjallajökull** mode (according to *Gudmundsson et al. 2012*).
     
+ **Ash Fraction**
     
     The *ash fraction* defines the percentage of particles smaller than 63 micrometers.<br>
     
     The erupted tephra mass is multiplied by this factor to obtain only the fine ash fraction, which potentially
     can be transported over large distances.
     
     In the **Manual** mode the user can specify the mass fraction value arbitrary between 0 and 1.
     
     In the **Eyjafjallakökull** mode the ash mass fraction is predefined as **0.5** (according to *Mastin et al. 2009*).
     
+ **Ash Concentration**
     
     The erupted *ash concentration* is calculated as follows:
     
     **concentration = mass rate * ash fraction / volume rate / resolution^2**
     
     The final division with the squared resolution accounts for the issue that the spatial resolution of the model is
     almost all cases much larger than volcanic eruption area (point source!). The consideration of this areal difference 
     therefore slightly reduces the ash concentration in the model.
     

---


### What our Model does (How to Volcano)

#### Raster Calculations

After the initialisation of all required input parameters the model performs more or less raster calculations.

The two most important rasters are:<br>
1) U- and V-wind speed rasters
2) Particle concentration raster

The **particle concentration raster** stores the different ash concentration distributions for each timestep.

#### Basic Principles (A typical model run)

**1) Eruption is happening!**
     
  By its initialisation the **particle concentration raster** is empty. Thus, before transport and diffusion can happen an
  eruption has to happen. This is realized by adding the calculated concentration to the raster cell which is closest to the
  specified *geographic location* of the volcano.
  
**2) Transport of particles**

  After the eruption has happened, the ash can be transported by the wind.<br>
  The transport depends on both wind speed and wind direction.
  
  For each cell of the **particle concentration raster** the same procedure is performed:<br>
  
  **2.1)** First, the *wind direction* is calculated. This is done by calculating the angle resulting from both components.
  
  **2.2)** Second, the *maximal wind speed* between the individual components and also the resulting wind speed of both wind
  components together is calculated.

  **The transport mechanism works as follows (See Figures below):**<br>
  
  Say the model is processing the cell of the **particle concentration raster** with the given indices *i* (row) and *j*
  (column).<br>
  
  **Figure 1:**<br>
  Each surrounding cell is classified in the model starting by the index *i - 1*, *j* (Cell 1) proceeding clockwise till
  *i - 1*, *j - 1* <br>(Cell 8). Further, the cells are classified with respect to the 360° circle. We therefore divided the
  360° by the 8 surrounding cells, resulting in a classification where each surrounding cell falls between a 45° range.
  
  <img src="https://github.com/unibe-geodata-modelling/2018-volcanic-ash-plume/blob/Figures/Cell_classification.png" alt="Classification" width="400" height="350">
   Figure 1: Classification of the surrounding cells.<br>


  **Figures 2 and 3:**
  
  
<img src="https://github.com/unibe-geodata-modelling/2018-volcanic-ash-plume/blob/Figures/Wind_Field.png" width="400" height="350">
Figure 2: Wind field with constant wind speeds (25 m/s).<br>


Then, by the means of the calculated *wind direction angle* we then

The first iteration (put into words) would look something like this:

+ Read cell with index (0,0) of both wind rasters
+ Read cell with index (0,0) of the ash concentration raster

In order to check, based on wind direction, which cell needs to recieve the output of each calculation, we followed the same principle used in the ArcGIS Tool [_Flow Direction_](http://desktop.arcgis.com/en/arcmap/10.3/tools/spatial-analyst-toolbox/how-flow-direction-works.htm). This tool assigns each of the neighbouring 8 cells an individual value, where each value represents a direction:


![alt_text](https://github.com/unibe-geodata-modelling/2018-volcanic-ash-plume/blob/master/mediaResources/readme_resources/flow_acc.JPG)


In our case, we assigned each neighbouring cell a value between 0 and 7, starting from cell (x-1,y-1) with value 0 and then continuing to add 1 in a clockwise motion. Winds that go straight North would therefore have a value of 1 assigned in a particular cell.


+ Once wind direction is figured out, we calculate the percentage of the value in our ash concentration raster that should be
transported. This is dependent mostly on wind speed, diffusion as well as a constant fallout coefficient. We iterate over each cell
of all rasters like this, all the while saving the calculated values to our cache array. Calculation of all cells in the cache array
marks the end of one iteration of the main loop. At the end of each such iteration, the ash concentration raster will be overwritten
by the cache array. 

+ In order to simulate an eruption, cells at the pre-specified coordinates of the volcano are set to recieve an eruption value at each 
timestep, introducing ash into the system. These values are stored in a list.


Finally, our model outputs a fully drawn map for each iteration of the main loop. This is so in the end, results using this model can easily be displayed as a GIF file.


---


## Results we got


### Development Phase 1


In development phase 1 we tried to implement basic ash dispersion in a 2D environment with constant wind speeds. 
Afterwards, the only factors reducing the amount of ash in the air were our fallout constant as well as to some degree our 
diffusion constant (which only really thinned out ash pockets, not really leading to reduced amout of ash in the 'atmosphere')


Here are a few of our earliest results:
(Hover your mouse over the following pictures for explanations)

![alt text](https://github.com/unibe-geodata-modelling/2018-volcanic-ash-plume/blob/master/mediaResources/testruns_GIFs/test.gif "First implementation, only mass transport, no diffusion, no fallout")

![alt text](https://github.com/unibe-geodata-modelling/2018-volcanic-ash-plume/blob/master/mediaResources/testruns_GIFs/test_3.gif "Same as first one, although with 4 ash-source pixels instead of 1")

![alt_text](https://github.com/unibe-geodata-modelling/2018-volcanic-ash-plume/blob/master/mediaResources/testruns_GIFs/Ashplume2.gif "Ash plume with implemented diffusion- and fallout coefficients")


### Development Phase 2


In development phase 2 additional functionality such as different modes was added. At this stage we tried to implement the use of actual wind data and coordinates from the 2010 eruption. With the decision to go back to Anaconda Python 2.7 we could also have the result displayed on a basemap.

---


## Known Limitations // Bugs of our Model
+ OutOfBounds Error

+asf


---


## Aknowledgements
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





