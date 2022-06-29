import numpy as np
from matplotlib import pyplot as plt
import random
import cv2
import os

cwd = os.getcwd()
path = cwd+'/frames/'

totalSteps = 5000
L = 300 #dimension of lattice
lattice = np.zeros((L, L)) #generate lattice
seedX, seedY = 150, 150 #location of seed
radius = 148 #radius measured from seed location
num_particles = 5 #number of random walkers

#initialize
for row in range (0,L):
        for col in range (0,L):
            if row==seedY and col==seedX:
                lattice[row][col] = num_particles+1 #seed is planted
            elif np.sqrt((seedY - row)**2 + (seedX - col)**2) > radius:
                lattice[row][col] = 0

t = 0 #keep track of number of particles added to cluster
directions = ['N', 'S', 'W', 'E']
notComplete = True
alpha_list = [1, 1, 1, 1, 1] #sticking probability #can turn into list for each particle

stats = [] #collect ID of particles that got added to the cluster
randXList = []
randYList = []
for part in range(num_particles):
    r = radius+1
    while r>radius:
        randX = random.randint(0, L-1)
        randY = random.randint(0, L-1)
        r = np.sqrt((randX-seedX)**2+(randY-seedY)**2)
    randXList.append(randX) #randXlist and randYlist keep track of current particle position
    randYList.append(randY)

stick = False
saving_plots = False
moving = True

while notComplete:

    for part in range(num_particles):

        #get current position
        posX = randXList[part]
        posY = randYList[part]

        #now make a random move
        moving = True
        while moving:

            move = random.choice(directions)
            # now choose step to make
            if move == 'N':
                moveX, moveY = posX, posY + 1
            elif move == 'S':
                moveX, moveY = posX, posY - 1
            elif move == 'W':
                moveX, moveY = posX - 1, posY
            else:
                moveX, moveY = posX + 1, posY
            moving = False
        #calculate new distance from seedX. Generate new particle if beyond edge, at 0, stuck.
        r = np.sqrt((seedY - moveY) ** 2 + (seedX - moveX) ** 2)

        birthing = False
        if r == 0 or r>radius:
            birthing = True
        else:
            #should be within edge: Now see if it sticks to cluster or not
            if lattice[moveY + 1][moveX] != 0 \
                    or lattice[moveY - 1][moveX] != 0 \
                    or lattice[moveY][moveX + 1] != 0 \
                    or lattice[moveY][moveX - 1] != 0:
                k_stick = np.random.random_sample()
                if k_stick < alpha_list[part]:
                    lattice[moveY][moveX] = part+1
                    stats.append(part+1)
                    t += 1
                    print(t)
                    moving = False #no need to move any further. You are stuck.
                    birthing = True #need a new particle
                else: #keep moving because probability of sticking was too high!
                    moving = True
                    birthing = False
                if saving_plots:
                    filestr = 'step_{}.png'.format(t)
                    frame_normed = 255 * (lattice - lattice.min()) / (lattice.max() - lattice.min())
                    frame_normed = np.array(frame_normed, np.int)
                    cv2.imwrite(os.path.join(path, filestr), frame_normed)
                    cv2.destroyAllWindows
            else:
                randXList[part] = moveX
                randYList[part] = moveY
                # reminder to stop if total number of steps reached
                if t == totalSteps:
                    notComplete = False
                stick = False
                moving = True
                birthing = False

        while birthing:
            r = radius + 1
            while r > radius:
                randX = random.randint(0, L - 1)
                randY = random.randint(0, L - 1)
                r = np.sqrt((randX - seedX) ** 2 + (randY - seedY) ** 2)
            birthing = False
            randXList[part] = randX
            randYList[part] = randY

print(lattice)
fig, ax = plt.subplots()
plt.imshow(lattice, cmap = 'jet')
plt.title('num_part = 10, t = 10000')
plt.colorbar()
plt.show()
#plt.savefig('alpha = 0.25.png', dpi = 200)

#calculate fractal dimension and also calculate correlation
R = 9
N = 0 #number of particles inside radius
for row in range(0,L):
    for col in range(0,L):
        r = np.sqrt((seedY - row) ** 2 + (seedX - col) ** 2)
        if r<R:
            N += lattice[row][col]
print('(R,N) =', '(', R, N, ')')

#calculate correlation function for different distances r
C = 0 #correlation function
k = 0
rho = 10 #correlation lag
for row in range(0,L-rho):
    for col in range(0,L-rho):
        r = np.sqrt((seedY - row) ** 2 + (seedX - col) ** 2)
        C += (lattice[row][col] * lattice[row][col+rho] + \
              lattice[row][col] * lattice[row+rho][col])
        k += 1
#print('(rho,C(r)) =', '(', rho, 1/k * C, ')')

for part in range(num_particles):
    ID = part+1
#    print('Count of {}:'.format(ID), stats.count(ID))