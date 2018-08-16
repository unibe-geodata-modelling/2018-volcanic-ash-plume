## 2018-volcanic-ash-plume

# Modelling Eyjafjallajökull Volcanic Ash Plume of 2010

Authors:

_Christoph von Matt, matr.n, uni-email_

_Benjamin Schuepbach, 14-100-564, benjamin.schuepbach@students.unibe.ch_




#### About our Model

This project is our homework submission for the seminar  _438745-FS2018-0- Geodatenanalyse und Modellierung_ at the University of Bern in Switzerland. We intended to create a python model of [the ash plume dispersion after the eruption of Eyjafjallajökull in 2010](https://en.wikipedia.org/wiki/2010_eruptions_of_Eyjafjallaj%C3%B6kull).


**Testing & Simulation Modes**

Our Model has different modes. There is a manual mode, where the user can input their own input parameters. There is also a simulation mode, where predefined input parameters (representing the Eyjafjallajökull eruption of 2010) are used.


---


## Input Parameters:
We used the following input parameters in our model:


+ **Wind Data**

   Wind Data is fed into our model in raster format and taken from [here](insert link here!).  
   We used two seperate Inputs, one for lat(u)-winds and one for lng(v)-winds.  


+ **Time**

   Time is defined as steps, which in turn represent iterations. Each step represents 6 hours and one model iteration.  
   This was derived from how often atmospheric winds are measured, which is in 6-hour intervalls.  


+ **Resolution**

   With this parameter, the pixel-resolution (in km units) of our model can be changed.  


+ **Location of Volcano**

   The location of a volcano can be entered here.  
   This parameters takes coordinates in the lng/lat format (in decimal degrees).  


+ **Ash Plume height**

   asdfasdf.  
   asdfasdf.  

+ **Mass- and Volume Rates & Ash Fraction**

   asdfasdf.  
   asdfasdf.  


---


## What our Model does (How to Volcano)
asdf

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


## Known Limitations of our Model
asdf


---


## Aknowledgements






