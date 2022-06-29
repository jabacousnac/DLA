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
radius = 149 #radius measured from seed location

#initialize
for row in range (0,L):
        for col in range (0,L):
            if row==seedY and col==seedX:
                lattice[row][col]=1 #seed is planted
            elif np.sqrt((seedY - row)**2 + (seedX - col)**2) > radius:
                lattice[row][col] = 0

t = 0 #number of steps
notComplete = True

# generate random point that diffuses randomly
randX = random.randint(0, L-1)
randY = random.randint(0, L-1)
r = np.sqrt((seedY - randY) ** 2 + (seedX - randX) ** 2)
directions = ['N', 'S', 'W', 'E']
move = random.choice(directions)
stick = False
r_b = 124 #birthing radius

phi_list = [] #use it to generate images of lattice
alpha = 1

saving_plots = False

while notComplete:

    while r > radius or r == 0 or stick: #either outside of radius, or at the seed
        
        #birth at some radius
        randtheta =  random.choice(np.linspace(0,2*np.pi,180))
        randX = seedX+int(r_b*np.cos(randtheta))
        randY = seedY+int(r_b*np.sin(randtheta))
        stick = False
        r = np.sqrt((seedY - randY) ** 2 + (seedX - randX) ** 2)

        #random birthing
        #randX = random.randint(0, L-1)
        #randY = random.randint(0, L-1)
        #stick = False
        #r = np.sqrt((seedY - randY) ** 2 + (seedX - randX) ** 2)

    moving = True
    while moving:
        #now choose step to make
        if move == 'N':
            moveX, moveY = randX, randY + 1
        elif move == 'S':
            moveX, moveY = randX, randY - 1
        elif move == 'W':
            moveX, moveY = randX - 1, randY
        else:
            moveX, moveY = randX + 1, randY
        #new move for next turn
        move = random.choice(directions)

        r = np.sqrt((seedY - moveY) ** 2 + (seedX - moveX) ** 2)

        if  r < radius: #within circle
            if lattice[moveY+1][moveX] == 1\
                    or lattice[moveY-1][moveX] == 1 \
                    or lattice[moveY][moveX+1] == 1 \
                    or lattice[moveY][moveX-1] == 1:

                k_stick = np.random.random_sample()
                if k_stick < alpha:
                    lattice[moveY][moveX] = 1
                    if (moveX - seedX) != 0:
                        phi = np.arctan((moveY-seedY)/(moveX-seedX))#absorption angle
                    else:
                        phi = np.pi/2
                    phi_list.append(phi)
                    frame = lattice
                    t+=1
                    print(t)
                    moving = False
                    stick = True
                else:
                    moving = True
                    stick = False

                if saving_plots:
                    filestr = 'step_{}.png'.format(t)
                    frame_normed = 255 * (frame - frame.min()) / (frame.max() - frame.min())
                    frame_normed = np.array(frame_normed, np.int)
                    cv2.imwrite(os.path.join(path , filestr), frame_normed)
                    cv2.destroyAllWindows

            else:
                randX = moveX
                randY = moveY
                #reminder to stop if total number of steps reached
                if t == totalSteps:
                    notComplete = False
                stick = False
                moving = True
        elif r == 0 or r==radius or r>radius: #reached center, or bounds
            randX = moveX
            randY = moveY
            moving = False #which means we have to generate point again
            stick = False

print(lattice)
fig, ax = plt.subplots()
plt.imshow(lattice, cmap = 'gray')
plt.show()
#plt.savefig('alpha = 0.25.png', dpi = 200)

#calculate fractal dimension and also calculate correlation
R = 4
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
print('(rho,C(r)) =', '(', rho, 1/k * C, ')')

#probability distribution of angles
plt.hist(phi_list, density=True, bins=20)
plt.show()




