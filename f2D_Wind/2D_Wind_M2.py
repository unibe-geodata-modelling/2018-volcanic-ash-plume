import numpy as np
from matplotlib import pyplot as plt


#This feature tries to model 2D Wind distribution of ash particles
#03.07.2018, Author: benjamin.schuepbach@students.unibe.ch


#-------------------------------DECLARING INPUT PARAMETERS----------------------------
#raster size (square)
rastersize = 20
#iteration parameter
iterate = 10
# volcanic ash in ppm that gets erupted with each timestep
eruption = [500000, 10000000, 5000000, 250000, 150000, 100000, 10000, 5000, 2000, 1000]
# placement of volcano
origin = [10,10]
#diffusion/fallout factor over time
loss = 0.9
#--------------------------------------------------------------------------------------
#Import actual wind-raster here
# BE AWARE diffusion should probably be taken into account as well...
wind = np.array([[3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],
                 [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],
                 [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
                 [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                 [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
                 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                 [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                 [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
                 [2,2,2,2,2,2,2,2,2,2,2,2,1,1,1,2,2,2,2,2],
                 [2,2,2,2,2,2,2,2,2,2,2,2,2,1,2,2,2,2,2,2],
                 [2,2,2,2,2,2,2,2,2,2,3,3,2,2,2,2,2,2,2,2],
                 [3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3,3],
                 [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],
                 [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],
                 [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],
                 [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],
                 [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],
                 [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],
                 [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5],
                 [5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5,5]])
w_direction = wind
#--------------------------------------------------------------------------------------

# setup
#w_direction = np.random.randint(low=0, high=8, size=(int(rastersize), int(rastersize)))
particles = np.zeros((int(rastersize), int(rastersize)))
iterations = range(0,int(iterate))

#just for testing purposes, make middle wind direction be all the same
#w_direction[4] = 3
#w_direction[5] = 3
#w_direction[6] = 3


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
        print("..." * 10)
        print("..." * 10)
        print("timestep {}, erupting {}".format(q+1, eruption[q]))

        #go through every pixel and evaluate its next time step, then save to temp_arr
        i = 0
        while i < rows:
            j = 0

            while j < cols:
                #to check if it works correctly:
                #print("going trough pixel at {},{}".format(i, j))

                try:
                    # this calculates the following per timestep:
                    # (old location of particles) * loss + (particles remaining at new location)
                    if direction[i, j] == 0:
                        # top left
                        temp_arr[i-1, j-1] = particles[i,j] * loss + particles[i-1,j-1]

                    elif direction[i, j] == 1:
                        # top middle
                        temp_arr[i - 1, j] = particles[i,j] * loss + particles[i-1,j]

                    elif direction[i, j] == 2:
                        # top right
                        temp_arr[i - 1, j + 1] = particles[i,j] * loss + particles[i-1,j+1]

                    elif direction[i, j] == 3:
                        # middle right
                        temp_arr[i, j + 1] = particles[i,j] * loss + particles[i,j+1]

                    elif direction[i, j] == 4:
                        # bottom right
                        temp_arr[i + 1, j + 1] = particles[i,j] * loss + particles[i+1,j+1]

                    elif direction[i, j] == 5:
                        # bottom middle
                        temp_arr[i + 1, j] = particles[i,j] * loss + particles[i+1,j]

                    elif direction[i, j] == 6:
                        # bottom left
                        temp_arr[i + 1, j - 1] = particles[i,j] * loss + particles[i+1,j-1]

                    elif direction[i, j] == 7:
                        # middle left
                        temp_arr[i, j - 1] = particles[i,j] * loss + particles[i,j-1]

                except IndexError:
                    pass

                j +=1
            i += 1
        #enabling iteration for the for loop
        q += 1

        #saving temp_arr as the new particles for the next time-step
        particles = temp_arr

    print("{}{} RESULTS {}{}".format("\n","---"*10,"---"*10, "\n"))
    print("Model ran {} timesteps with volcanic output of \n{}\n".format(iterate,eruption))
    print("Wind direction Raster: \n", w_direction, "\n")
    print("Model output: \n", np.rint(particles))

    #plt.imshow(w_direction, cmap='gray')
    #plt.imshow(particles, cmap='gray')
    plt.imsave("Wind_Direction", w_direction)
    plt.imsave("Ash_Plume", particles)
    return np.rint(particles)

partTransport(w_direction, particles, eruption, origin, loss)