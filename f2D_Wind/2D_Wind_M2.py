import numpy as np
import matplotlib.pyplot as plt

#This feature tries to model 2D Wind distribution of ash particles
# 03.07.2018
#--------------------------------------------------------------------------------------
#DECLARING INPUT PARAMETERS
#raster size (square)
rastersize = 10
#iteration parameter
iterate = 10
# volcanic ash in ppm that gets erupted with each timestep
eruption = [50000, 100000, 50000, 25000, 15000, 10000, 1000, 500, 250, 100]
# placement of volcano
origin = [5,5]
#diffusion/fallout factor over time
loss = 0.25
#--------------------------------------------------------------------------------------

# setup
w_direction = np.random.randint(low=0, high=8, size=(int(rastersize), int(rastersize)))
particles = np.zeros((int(rastersize), int(rastersize)))
iterations = range(0,int(iterate))

#just for testing purposes, make middle wind direction be all the same
w_direction[4] = 3
w_direction[5] = 3
w_direction[6] = 3


def partTransport(direction, particles, eruption, origin, loss):
    ''' calculates transport of particles trough wind'''

    q = 0
    rows = int(np.shape(particles)[0])
    cols = int(np.shape(particles)[1])

    print("Modeling process initiated, goint through {} iterations".format(max(iterations)+1))

    #start for-loop here to iterate
    for n in iterations:
        i = 0

        #create temporary array to save calculated time step
        temp_arr = np.zeros((rows, cols))

        #dynamic particle generation at volcano
        particles[origin[0], origin[1]] = eruption[q]
        print("..." * 10)
        print("..." * 10)
        print("timestep {}, erupting {}".format(q+1, eruption[q]))



        #go through every pixel and evaluate its next time step, then save to temp_arr
        while i < rows:
            j = 0

            while j < cols:
                #to check if it works correctly:
                #print("going trough pixel at {},{}".format(i, j))

                try:
                    if direction[i, j] == 0:
                        # top left
                        temp_arr[i - 1, j - 1] = particles[i, j] * loss

                    elif direction[i, j] == 1:
                        # top middle
                        temp_arr[i - 1, j] = particles[i, j] * loss

                    elif direction[i, j] == 2:
                        # top right
                        temp_arr[i - 1, j + 1] = particles[i, j] * loss

                    elif direction[i, j] == 3:
                        # middle left
                        temp_arr[i, j + 1] = particles[i, j] * loss

                    elif direction[i, j] == 4:
                        # middle middle
                        temp_arr[i + 1, j + 1] = particles[i, j] * loss

                    elif direction[i, j] == 5:
                        # middle right
                        temp_arr[i + 1, j] = particles[i, j] * loss

                    elif direction[i, j] == 6:
                        # bottom left
                        temp_arr[i + 1, j - 1] = particles[i, j] * loss

                    elif direction[i, j] == 7:
                        # bottom middle
                        temp_arr[i, j - 1] = particles[i, j] * loss

                except IndexError:
                    pass

                j +=1
            i += 1
        #enabling iteration for the for loop
        q += 1

        #saving temp_arr as the new particles for the next time-step
        particles = temp_arr


    print(particles)
    return particles




plt.imshow(partTransport(w_direction, particles, eruption, origin, loss))

