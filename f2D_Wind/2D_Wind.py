import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

#This feature tries to model 2D Wind
# 03.07.2018

#creating model variables wind strength, wind direction
#and amount of particles in the air
#w_strength = np.random.randint(100, size=(10,10))
w_direction = np.random.randint(low=0, high=8, size=(10,10))
particles = np.zeros((10,10))
iterations = 10
eruption = [50000, 100000, 50000, 25000, 15000, 10000, 1000, 500, 250, 100]



#just for testing purposes, make middle be all the same
w_direction[4] = 3
w_direction[5] = 3
w_direction[6] = 3

#w_strength[5:] = 100
#print(w_direction)
#print(w_strength)



#plt.imshow(w_strength)
#plt.imshow(w_direction)


def partTransport(direction, particles, eruption, q):
    ''' calculates transport of particles, this works fine'''

    rows = int(np.shape(particles)[0])
    cols = int(np.shape(particles)[1])

    #parTemp = np.array(int(cols),int(rows))

    i = 0
    j = 0

    while i < rows:
        # set origin of volcanic ash plume with amount of particles in air
        temp_particles = np.zeros((rows,cols))
        temp_particles[6, 6] = particles[6, 6] + int(eruption[q])
        print("Eruption value at iteration ", q + 1, " :",  int(eruption[q]))

        #maybe introduce temporary second array that saves calculated values


        while j < cols:

            if direction[i,j] == 0:
                #top left
                try:
                    temp_particles[i-1,j-1] = particles[i,j]*0.5
                    i += 1
                    j += 1
                except:
                    i += 1
                    j += 1

            elif direction[i,j] == 1:
                #top middle
                try:
                    temp_particles[i-1,j] = particles[i,j]*0.5
                    i += 1
                    j += 1

                except:
                    i += 1
                    j += 1



            elif direction[i,j] == 2:
                #top right
                try:
                    temp_particles[i-1,j+1] = particles[i,j]*0.5
                    i += 1
                    j += 1

                except:
                    i += 1
                    j += 1



            elif direction[i,j] == 3:
                #middle left
                try:
                    temp_particles[i,j+1] = particles[i,j]*0.5
                    i += 1
                    j += 1

                except:
                    i += 1
                    j += 1



            elif direction[i,j] == 4:
                #middle middle
                try:
                    temp_particles[i+1,j+1] = particles[i,j]*0.5
                    i += 1
                    j += 1

                except:
                    i += 1
                    j += 1



            elif direction[i,j] == 5:
                #middle right
                try:
                    temp_particles[i+1,j] = particles[i,j]*0.5
                    i += 1
                    j += 1

                except:
                    i += 1
                    j += 1



            elif direction[i,j] == 6:
                #bottom left
                try:
                    temp_particles[i+1,j-1] = particles[i,j]*0.5
                    i += 1
                    j += 1

                except:
                    i += 1
                    j += 1



            elif direction[i,j] == 7:
                #bottom middle
                try:
                    temp_particles[i,j-1] = particles[i,j]*0.5
                    i += 1
                    j += 1

                except:
                    i += 1
                    j += 1


    particles = temp_particles
    print(temp_particles)
    return particles

def model(direction, particles,iterations, eruption):
    ''' iterates over timesteps, works fine'''
    q = 0
    for v in range(0, iterations):
        try:
            partTransport(direction, particles, eruption, q)
            q += 1
        except:
            q += 1
            pass



    print(particles)
    return particles




model(w_direction, particles, iterations, eruption)
#print(particles)