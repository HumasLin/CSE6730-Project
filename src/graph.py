import heapq
import random
import math
from numpy.random import rand

# Define the User class
class User:
    def __init__(self,ID,value,Type,wait_num,freetime,occupy,numFriend):
        self.ID=ID
        self.value=value
        self.Type=Type
        self.wait_num=wait_num
        self.freetime=freetime 
        self.occupy=occupy
        self.numFriend=numFriend
        self.P = P;

# Define function init_graph
# Initialize the intimacy map and conversation record
def init_graph():
    global dists
    dists = []
    global record
    record = []

# Define function createDist
# This function creates coordinates for every user
def createDist(User):
    # For original active users, create them on the opposite quadrant
    if User.ID == -1:

        if User.freetime == 1:
            # implement allocation 1
            x = 3*rand(1)[0]
            y = math.sqrt(9-x*x)
            sign_x = rand(1)
            sign_y = rand(1)
            x = x*(-1)**(sign_x-0.5>0)
            y = y*(-1)**(sign_y-0.5>0)

        elif User.freetime == 2:
            # implement allocation 2
            x = User.numFriend
            y = User.value * 3

        else:
            # implement allocation 3
            x = 3*(math.cos(2*User.numFriend*math.pi))
            y = 3*(math.sin(2*User.numFriend*math.pi))
        a = [x, y]
        dists.append(a)
    # For introduced ignorants, they are near to their friends with distance = 1
    else:
        d_x = rand(1)[0]
        d_y = math.sqrt(1-d_x*d_x)

        r_x = d_x
        r_y = d_y
        
        sign_x = rand(1)
        if sign_x < 0.5:
            x_new = r_x+dists[User.ID][0]
        else:
            x_new = -r_x+dists[User.ID][0]
        sign_y = rand(1)
        if sign_y < 0.5:
            y_new = r_y+dists[User.ID][1]
        else:
            y_new = -r_y+dists[User.ID][1]
        a = [x_new, y_new]
        dists.append(a)

# Define function kClosest
# Input parameters coming from function makeComb
def kClosest(points, User):
    # Get the points closest to the User
    closest_cor = heapq.nsmallest(User.numFriend+1,points,key=lambda p:(p[0]-dists[User.ID][0])*(p[0]-dists[User.ID][0])
        +(p[1]-dists[User.ID][1])*(p[1]-dists[User.ID][1]))
    # Choose randomly from the User's friends that haven't been interacted with him
    while len(closest_cor) != 0:
        chosen = random.randint(0, len(closest_cor)-1)
        result = closest_cor[chosen]
        closest_cor.pop(chosen)
        closestID = dists.index([float(result[0]),float(result[1])])     
        if closestID not in record[User.ID] and closestID != User.ID:
            return closestID
    return -1