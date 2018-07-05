import numpy as np
from matplotlib import pyplot as plt
import random


#This feature tries to model 2D Wind distribution of ash particles
#03.07.2018, Author: benjamin.schuepbach@students.unibe.ch


#-------------------------------DECLARING INPUT PARAMETERS----------------------------
#raster size (square)
rastersize = 100

# volcanic ash in ppm that gets erupted with each timestep
eruption = [10000,5000,2000,1500,1000,1000,1000,3000,2000,
            1000,1000,1000,1000,1000,1000,1000,200,200,200,200,100,100,100,100,100,100,100,100,100,
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

#iteration parameter
iterate = len(eruption)

# placement of volcanoes
origin = [98,58]
origin2 = [98,59]
origin3 = [97,58]
origin4 = [97,59]

#diffusion/fallout factor over time
loss = 0.89


#--------------------------------------------------------------------------------------
#Import actual wind-raster here
#Be aware, diffusion should probably be taken into account as well...
#Also be aware that using random wind directions can lead to winds cancelling each other out!
#using random wind directions only going South East (3,4,5)
#return random integers from low (inclusive) to high (exclusive)
w_direction = np.random.randint(low=0, high=4, size=(int(rastersize), int(rastersize)))
#--------------------------------------------------------------------------------------


# setup
particles = np.zeros((int(rastersize), int(rastersize)))
iterations = range(0,int(iterate))

def partTransport(direction, particles, eruption, origin, loss):
    ''' calculates transport of particles trough wind'''

    q = 0
    rows = int(np.shape(particles)[0])
    cols = int(np.shape(particles)[1])

    print("Modeling process initiated, goint through {} iterations".format(max(iterations)+1))

    #for-loop to go through specified amount of timesteps
    for n in iterations:

        #create temporary array to save calculated time step
        temp_arr = np.zeros((rows, cols))

        #dynamic particle generation at volcano
        particles[origin[0], origin[1]] = eruption[q]
        particles[origin2[0],origin2[1]] = eruption[q]
        particles[origin3[0], origin3[1]] = eruption[q]
        particles[origin4[0], origin4[1]] = eruption[q]

        print("..." * 10)
        print("..." * 10)
        print("timestep {}, erupting {}ppm".format(q+1, eruption[q]))

        #go through every pixel and evaluate its next time step, then save to temp_arr
        i = 0
        while i < rows:
            j = 0

            while j < cols:
                #to check if it works correctly:
                #print("going trough pixel at {},{}".format(i, j))

                try:
                    # this calculates the following per timestep:
                    # new location of particles [depending on wind] = sum((old location[s] of particles) * loss)
                    if direction[i, j] == 0:
                        # top left
                        temp_arr[i-1, j-1] += particles[i,j] * loss

                    elif direction[i, j] == 1:
                        # top middle
                        temp_arr[i - 1, j] += particles[i,j] * loss

                    elif direction[i, j] == 2:
                        # top right
                        temp_arr[i - 1, j + 1] += particles[i,j] * loss

                    elif direction[i, j] == 3:
                        # middle right
                        temp_arr[i, j + 1] += particles[i,j] * loss

                    elif direction[i, j] == 4:
                        # bottom right
                        temp_arr[i + 1, j + 1] += particles[i,j] * loss

                    elif direction[i, j] == 5:
                        # bottom middle
                        temp_arr[i + 1, j] += particles[i,j] * loss

                    elif direction[i, j] == 6:
                        # bottom left
                        temp_arr[i + 1, j - 1] += particles[i,j] * loss

                    elif direction[i, j] == 7:
                        # middle left
                        temp_arr[i, j - 1] += particles[i,j] * loss

                except IndexError:
                    pass

                j +=1
            i += 1
        # enabling iteration for the for loop
        q += 1

        # saving temp_arr as the new particles for the next time-step
        particles = temp_arr
        plt.imsave("Ash_Plumes\Ash_Plume{}".format(q), particles)

    print("{}{} RESULTS {}{}".format("\n","---"*10,"---"*10, "\n"))
    print("Model ran {} timesteps with volcanic output of \n{}\n".format(iterate,eruption))
    print("Wind direction Raster: \n", w_direction, "\n")
    print("Model output: \n", np.rint(particles))

    #plt.imshow(w_direction, cmap='gray')
    #plt.imshow(particles, cmap='gray')
    plt.imsave("Wind_Direction\Wind_Direction", w_direction)
    return np.rint(particles)

partTransport(w_direction, particles, eruption, origin, loss)