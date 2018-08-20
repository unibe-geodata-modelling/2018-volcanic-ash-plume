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


**Manual Parameterisation or Eyjafjallajökull Parameterisation:** Choices related to eruption characteristics

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

  **The transport mechanism works as follows (see Figures below):**<br>
  
  Say the model is processing the cell of the **particle concentration raster** with the given indices *i* (row) and *j*
  (column).<br>
  
  **Figure 1:**<br>
  Each surrounding cell is classified in the model starting by the index *i - 1*, *j*  (Cell 1) proceeding clockwise till
  *i - 1*, *j - 1* <br>(Cell 8). Further, the cells are classified with respect to the 360° circle. We therefore divided the
  360° by the 8 surrounding cells, resulting in a classification where each surrounding cell falls between a 45° range.
  
  <img src="https://github.com/unibe-geodata-modelling/2018-volcanic-ash-plume/blob/Figures/Cell_classification.png" alt="Classification" width="400" height="350">
   Figure 1: Classification of the surrounding cells.
   <br>
   <br>


  **Figures 2 and 3:**
  
  *Figure 2* shows an example wind field with constant wind field with only U-wind components as it could typically be
  running the model in the **Test** mode.
  
  The calculated *wind direction angle* in this example would be **90°** as there is only a U-wind component present in the
  two *wind rasters*. By the means of this angle and the explained cell classification (*see Figure 1*) the receiving wind
  transport direction cell would therefore be **Cell 3** (*see Figure 3*).
  
  As mentionned before, the particle transport depends not only on wind direction, but on wind speed too. That is were
  the *maximal wind speed* and the *spatial model resolution* comes into play:
  
  Let's assume that the spatial model resolution is **80 km**. If the calculated *maximal wind speed* exceeds the spatial
  model resolution (here 80 km/h) then **100% (1.0)** of the ash concentration in the Cell ( *i* , *j* ) is transported to 
  Cell 3.
  Hence, if the maximal wind speed is lower than 80 km/h, then only a predefined proportion of less than 100% (< 1.0) of 
  the ash concentration will be freighted to Cell 3.
  
  That is actually not the whole story. What is with the diffusion ash concentration part?<br> 
  The amount of ash concentration dedicated to diffusion is subtracted before the transport process takes place.
  So, in the example only **1.0 * (total ash concentration - diffusion concentration amount)** is transported to Cell 3.
  
  *Attention: Please remember that in the model the U- and V-wind component are stored in separate rasters!*
  
<img src="https://github.com/unibe-geodata-modelling/2018-volcanic-ash-plume/blob/Figures/Wind_Field.png" width="400" height="350">
Figure 2: Wind field with constant wind speeds (25 m/s).<br>

<img src="https://github.com/unibe-geodata-modelling/2018-volcanic-ash-plume/blob/Figures/Transport_model.png" width="350" height="325">
  Figure 3: Particle transport according to wind field in Figure 2.
  <br>
  <br>

**3) Diffusion of particles**
  
  After the particle transport mechanism has been completed, the diffusion part begins.
  
  Our model provides two different diffusion types: one in all directions and a gradient-dependent one. 
  The amount of ash concentration which is diffused, depends
  on the initially defined *diffusion percentage*.
  
  Continuing the above example, the Cell *i* , *j* contains now the ash concentration of the diffusion part (which was not
  transported) and a possible transported part from neighbouring cells.<br>
  The current concentration in Cell *i* , *j* is thus:<br>
  
  **current concentration = 1 - 1.0 * (total ash concentration - diffusion concentration amount) + transported concentration**
  
  which is equal to
  
  **current concentration =** (remaining) **diffusion concentration amount + transported concentration** (in this cell).
  
  Before diffusion can take place - just like in the transport mechanism - the *diffusion concentration amount* has to be
  specified again. The available ash concentration for diffusion is therefore **current concentration * diffusion percentage**.
  
  Let's now look at the different diffusion types!
  <br>
  <br>
  
  **3.1) Diffusion in all directions**
  
  In this diffusion type the *diffusion concentration amount* is equally distributed to all 8 surrounding cells. Each cell
  receives therefore an ash concentration of **diffusion concentration amount / 8** (*see Figure 4*). <br>
   
<img src="https://github.com/unibe-geodata-modelling/2018-volcanic-ash-plume/blob/Figures/Diff_all.png" width="350" height="325">
  Figure 4: Diffusion-Type: All directions.
  <br>
  <br>
  
  **3.2) Gradient-dependent diffusion**
  
  The second diffusion type is slightly more complex.
  
  As a first step, the concentrations of all surrounding cells are retrieved. Then the 
  **difference with respect to the Cell *i* , *j*** is
  calculated. Then, these differences are divided by the distance separating each cell from the Cell *i* *j*.<br>
  This is done with the *spatial model resolution*. The differences then become **gradients**.
  
  An example calculation for Cell 3 looks like:
  <br>
  **gradient = (concentration Cell 3 - concentration Cell *i*, *j* ) / 80 km**
  <br>
  
  *Note: The diagonally situated cells 2, 4, 6, 8 require a corrected distance. This is realized using simple trigonometry.*
  
  In the next step the available ash concentration for diffusion is **equally distributed to the cells showing a negative
  gradient** with respect to Cell *i* , *j* (*see Figure 5*).
  
  Thus each receiving cell gets the following concentration:
  
  **diffusion concentration amount / Number of cells with negative gradient**.
  
  With this diffusion type, the diffusion distributes the *diffusion concentration amount* only towards lower ash
  concentrations.
  
  <img src="https://github.com/unibe-geodata-modelling/2018-volcanic-ash-plume/blob/Figures/Diff_grad.png" width="400" height="300">
  Figure 5: Diffusion-Type: Gradient-dependent.
  <br>
  <br>
  
 **4) Particle Fall-out**
 
   As last step, before the whole transport diffusion loop starts all over again, the particle fall-out takes place.
   
   To model the particle fall out, the initially specified **fall-out percentage** is applied over the whole 
   **particle concentration raster**. Every cell of this raster looses the same percentage of ash concentration with each
   timestep. Thus, cells with higher concentrations lose a proportionally higher amount of ash particles.
  <br>
  <br>

Finally, our model outputs three fully drawn maps for each iteration of the transport and diffusion loop. So in the end, 
the model results can easily be displayed as a GIF file.


---


### Control Mechanism

To guarantee that the model does correct calculations and that no mass is created or disappearing mysteriously, we implemented
a control mechanism in our model.

**Principle:**<br>
With each timestep the fall-out is summed-up and stored. After the transport and diffusion procedure is complete, all
concentrations of the very last **particle concentration raster** are summed-up and added to the summed-up fall-out.<br>
Simultaneously, each eruption of ash concentration is summed-up as well.

In the end **sum of eruptions** has to be equal to the sum of **Sum final particle raster + Sum fall-out**.


---


## Results

As mentionned in the "What Our Model does (How to Volcano)" section, our model generates three different maps. All maps are
realized with the **Basemap** package.

The colouring and spacing of the colorbars is strongly inspired by the [EUMETRAIN's Volcanic Ash Training Module](http://eumetrain.org/data/1/144/navmenu.php?page=4.0.0).

All the specified (and relevant) parameters used in a specific model run are visible on the individual plots and are
updated automatically if different model settings and input parameters are used.

For the **Eyjafjallajökull simulation** mode we use 500hPa ERA-Interim wind data of April 2010 which we directly obtained from
the [ECMWF](https://www.ecmwf.int/en/forecasts/datasets/archive-datasets/reanalysis-datasets/era-interim) website.

In this section we present some of our results we got from our model runs.<br>
A validation was not yet performed and thus the adequacy of the model for the **Eyjafjallajökull eruption 2010** will not be
discussed here.<br>
A possible validation strategy could be a comparison with other transport-dispersion models, such as the visualisation
on the [EUMETRAIN's Volcanic Ash Training Module](http://eumetrain.org/data/1/144/navmenu.php?page=4.0.0).

### Figure 1 - World Map

This figure shows the model simulation on a global map.

The parameters for this model run are specified on the plot.


---


## Model Shortcomings and Outlook

We are fully aware that our model has several limitations and issues which are not solved yet. They shall be discussed in
this section.

### Dynamics related limitations

Limitations related to the model dynamics consists of issues related to spatial and temporal model resolution as well as to fall-out and dispersion.

#### Resolution-related issues

The first dynamics-related problem considering the model resolution is, that with each timestep the 
**maximal particle transport distance** is limited to the spatial resolution of the model. No matter whether maximum 
wind speeds are much higher than the distance to traverse a model cell, the particles will maximally be transported as far as the model resolution.

Example:<br>
With a *spatial resolution* of **80 km** and *maximum windspeeds* of **160 km/ h** the particles won't be transported further than 80 km although the potential transport is twice as far.

Another issue is the temporal resolution. The temporal resolution of the wind fields we used in the "Results" section is 
six-hourly. This means we have only one new wind field every six hours.<br>
Using one wind field per timestep would however not make sense as the spatial issue even aggravates as the particle transport
distance is heavily underestimated.

Our model attempts to reduce this temporal resolution issue by iterating with the unchanged wind fields for the durance of the model resolution.

#### Fall-out related issues

In addition to model resolution related issues, there are also limitation with the fall-out parameterisation

First, the ash can sometimes stay in air for several days without any major fall-out. This is not considered in our model
as fall-out begins from the first iteration on. As we model only one specific level we neglect this issue.

Another fall-out issue is its constant parameterisation. Although we limited our simulation to particles smaller than
63 micrometers, the ash particle size can be still quite diverse. The constant fall-out does therefore not account for the
fall-out velocity of different particle size fractions. This is clearly a limitation of our model.

### Other issues

General issues consider some code functionality problems. These are not discussed in this documentation.

### Outlook

As our model operates almost exclusively with raster data we can imagine an implementation of this model in a geographic
information system. A combination with air space territories could be worth a try to detect flight zone restrictions due
to ash concentrations.



---
## Thanks

Thanks go to our instructors and supervisors during the semester, *Dr. Andreas Zischg (University of Bern)*, *Dr. Jorge Ramirez
(University of Bern)* and *Dr. Pascal Horton (University of Bern)* for their strong commitment to make the "Geodata analysis and modeling" lecture in its first realisation a full success. Thanks for the very informative and interesting lecture!

---


## Aknowledgements
                            
Cimbala, J. M. (2018): Gaussian Plume Model and Dispersion Coefficients. Pennsylvania State University.
              Latest revision: 30th January 2018.
              Available under: https://www.mne.psu.edu/cimbala/me433/Lectures/Tables_for_Gaussian_Plume_Model.pdf
              
Folch, A. (2012): A review of tephra transport and dispersal models: Evolution, current status, and future perspectives.
              In: Journal of Volcanology and Geothermal Research 235-236: 96-115.
              [DOI: 10.1016/j.jvolgeores.2012.05.020](https://www.sciencedirect.com/science/article/pii/S0377027312001588).
              
Gudmundsson, M.T., Thordarson, T., Hoeskuldsson, A., Larsen, G., Bjoernsson, H., Prata, F.J., Oddsson, B.,
             Magnusson, E., Hoegnadottir, T., Petersen, G.N., Hayward, C.L., Stevenson, J.A., Jonsdottir, I.
             (2012): Ash generation and distribution from the April-May 2010 eruption of Eyjafjallajoekull, Iceland.
             In: Scientific Reports 2:572: S.1-12.
             [DOI: 10.1038/srep00572](https://www.nature.com/articles/srep00572).
                      
Mastin, L.G., Guffanti, M., Servranckx, R., Webley, P., Barsotti, S., Dean, K., Durant, A, Ewert, J.W., Neri, A.,
              Rose, W.I., Schneider, D., Siebert, L., Stunder, B., Swanson, G., Tupper, A., Volentik, A.,
              Waythomas, C.F. (2009): A multidisciplinary effort to assign realistic source parameters to models of
              volcanic ash-cloud transport and dispersion during eruptions.
              In: Journal of Volcanology and Geothermal Research 186: 10-21.
              [DOI: 10.1016/j.jvolgeores.2009.01.008](https://www.sciencedirect.com/science/article/pii/S0377027309000146).





