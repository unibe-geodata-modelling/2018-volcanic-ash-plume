import numpy as np
from matplotlib import pyplot as plt

#This model calculates 2D ash plume dispersion
#03.07.2018, Author: benjamin.schuepbach@students.unibe.ch

#-------------------------------DECLARING INPUT PARAMETERS----------------------------
#raster size (square)
rastersize = 200

# volcanic ash in ppm that gets erupted with each timestep
eruption = [10000,5000,2000,1500,1000,1000,1000,3000,2000,
            1000,1000,1000,1000,1000,1000,1000,200,200,200,200,100,100,100,100,100,100,100,100,100,
            0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

#iteration parameter (also set up an ascending list with length of len(eruption)
#for use in later for-loop
iterate = len(eruption)
iterations = range(0,int(iterate))

# placement of volcanoes
origin1 = [198,158]
origin2 = [198,159]
origin3 = [197,158]
origin4 = [197,159]

#fallout factor over time
loss = 0.9

#diffusion facter for each timestep
diff_loss = 0.9

#Import actual wind-raster here
#Be aware, diffusion should probably be taken into account as well...
#Also be aware that using random wind directions can lead to winds cancelling each other out!
#using random wind directions only going North East (0,1,2)
#return random integers from low (inclusive) to high (exclusive)
w_direction = np.random.randint(low=0, high=3, size=(int(rastersize), int(rastersize)))

# set up empty np array representing clean air before eruption
particles = np.zeros((int(rastersize), int(rastersize)))
#--------------------------------------------------------------------------------------

def eruptionModel(direction, particles, eruption, origin1, origin2, origin3, origin4, loss, diff_loss):
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
        particles[origin1[0], origin1[1]] = eruption[q]
        particles[origin2[0], origin2[1]] = eruption[q]
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
                        temp_arr[i-1, j-1] += particles[i,j] * loss * (1-diff_loss)

                        #save indices to make further steps look more simple on paper
                        z = i-1
                        u = j-1

                        #assign each surrounding pixel of end-of-timestep-target pixel the diffusion value
                        temp_arr[z-1, u-1] += (particles[i,j] * loss * diff_loss) / 8
                        temp_arr[z-1, u] += (particles[i,j] * loss * diff_loss) / 8
                        temp_arr[z-1, u+1] += (particles[i,j] * loss * diff_loss) / 8
                        temp_arr[z, u+1] += (particles[i,j] * loss * diff_loss) / 8
                        temp_arr[z+1, u+1] += (particles[i,j] * loss * diff_loss) / 8
                        temp_arr[z+1, u] += (particles[i,j] * loss * diff_loss) / 8
                        temp_arr[z+1, u-1] += (particles[i,j] * loss * diff_loss) / 8
                        temp_arr[z, u-1] += (particles[i,j] * loss * diff_loss) / 8

                    elif direction[i, j] == 1:
                        # top middle
                        temp_arr[i - 1, j] += particles[i,j] * loss * (1-diff_loss)

                        # save indices to make further steps look more simple on paper
                        z = i - 1
                        u = j

                        # assign each surrounding pixel of end-of-timestep-target pixel the diffusion value
                        temp_arr[z - 1, u - 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z - 1, u] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z - 1, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u - 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z, u - 1] += (particles[i, j] * loss * diff_loss) / 8

                    elif direction[i, j] == 2:
                        # top right
                        temp_arr[i - 1, j + 1] += particles[i,j] * loss * (1-diff_loss)

                        # save indices to make further steps look more simple on paper
                        z = i - 1
                        u = j + 1

                        ##assign each surrounding pixel of end-of-timestep-target pixel the diffusion value
                        temp_arr[z-1, u-1] += (particles[i,j] * loss * diff_loss) / 8
                        temp_arr[z-1, u] += (particles[i,j] * loss * diff_loss) / 8
                        temp_arr[z-1, u+1] += (particles[i,j] * loss * diff_loss) / 8
                        temp_arr[z, u+1] += (particles[i,j] * loss * diff_loss) / 8
                        temp_arr[z+1, u+1] += (particles[i,j] * loss * diff_loss) / 8
                        temp_arr[z+1, u] += (particles[i,j] * loss * diff_loss) / 8
                        temp_arr[z+1, u-1] += (particles[i,j] * loss * diff_loss) / 8
                        temp_arr[z, u-1] += (particles[i,j] * loss * diff_loss) / 8

                    elif direction[i, j] == 3:
                        # middle right
                        temp_arr[i, j + 1] += particles[i,j] * loss * (1-diff_loss)

                        # save indices to make further steps look more simple on paper
                        z = i
                        u = j + 1

                        # assign each surrounding pixel of end-of-timestep-target pixel the diffusion value
                        temp_arr[z - 1, u - 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z - 1, u] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z - 1, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u - 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z, u - 1] += (particles[i, j] * loss * diff_loss) / 8

                    elif direction[i, j] == 4:
                        # bottom right
                        temp_arr[i + 1, j + 1] += particles[i,j] * loss * (1-diff_loss)

                        # save indices to make further steps look more simple on paper
                        z = i + 1
                        u = j + 1

                        # assign each surrounding pixel of end-of-timestep-target pixel the diffusion value
                        temp_arr[z - 1, u - 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z - 1, u] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z - 1, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u - 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z, u - 1] += (particles[i, j] * loss * diff_loss) / 8

                    elif direction[i, j] == 5:
                        # bottom middle
                        temp_arr[i + 1, j] += particles[i,j] * loss * (1-diff_loss)

                        # save indices to make further steps look more simple on paper
                        z = i + 1
                        u = j

                        # assign each surrounding pixel of end-of-timestep-target pixel the diffusion value
                        temp_arr[z - 1, u - 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z - 1, u] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z - 1, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u - 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z, u - 1] += (particles[i, j] * loss * diff_loss) / 8

                    elif direction[i, j] == 6:
                        # bottom left
                        temp_arr[i + 1, j - 1] += particles[i,j] * loss * (1-diff_loss)

                        # save indices to make further steps look more simple on paper
                        z = i + 1
                        u = j - 1

                        # assign each surrounding pixel of end-of-timestep-target pixel the diffusion value
                        temp_arr[z - 1, u - 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z - 1, u] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z - 1, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u - 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z, u - 1] += (particles[i, j] * loss * diff_loss) / 8

                    elif direction[i, j] == 7:
                        # middle left
                        temp_arr[i, j - 1] += particles[i,j] * loss * (1-diff_loss)

                        # save indices to make further steps look more simple on paper
                        z = i
                        u = j - 1

                        # assign each surrounding pixel of end-of-timestep-target pixel the diffusion value
                        temp_arr[z - 1, u - 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z - 1, u] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z - 1, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u + 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z + 1, u - 1] += (particles[i, j] * loss * diff_loss) / 8
                        temp_arr[z, u - 1] += (particles[i, j] * loss * diff_loss) / 8

                except IndexError:
                    #this is to prevent the program from collapsing in case one of the above conditions
                    #tries to access a pixel outside of the range of a numpy array, like a pixel with index particles[-10,-10]
                    #in that case the program should just pass the condition and move on
                    pass

                #iterating trhough columns
                j +=1

            #iterating through rows
            i += 1

        #iterating trough for-loop
        q += 1

        # saving temp_arr as the new particles for the next time-step, also saving a snapshot from each
        #timestep to a folder for GIF-creation later
        particles = temp_arr
        plt.imsave("Ash_Plumes\Ash_Plume{}".format(q), particles, cmap='gray')
        #todo: assure that colors always represent same number (vmin/vmax)

    print("{}{} RESULTS {}{}".format("\n","---"*10,"---"*10, "\n"))
    print("Model ran {} timesteps with volcanic output of \n{}\n".format(iterate,eruption))
    print("Wind direction Raster: \n", w_direction, "\n")
    print("Model output: \n", np.rint(particles))

    #plt.imshow(w_direction, cmap='gray')
    #plt.imshow(particles, cmap='gray')
    plt.imsave("Wind_Direction\Wind_Direction", w_direction)
    return np.rint(particles)

eruptionModel(w_direction, particles, eruption, origin1, origin2, origin3, origin4, loss, diff_loss)