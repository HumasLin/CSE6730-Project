from operator import attrgetter
import numpy as np
from numpy.random import rand
import random
import copy
import heapq
from graph import createDist, kClosest
import graph

# Create lists storing active users, all uses and all events
act_user = list()
FEL = list()

# Create a numpy array for visualization
limit = list()

# Define state constant
begin = 1
finished = 0

# Define the time constant
Now = 0.0

# Define class User
# User includes its ID, value and Type according to its role
# wait_num for the number of people waiting to interact with him
# freetime for when the last one wanting to connect can begin
# occpy for indicating whether he's in a talk
# numFriend for the number of friends the user has
class User:
    def __init__(self,ID,value,Type,wait_num,freetime,occupy,numFriend,P):
        self.ID=ID
        self.value=value
        self.Type=Type
        self.wait_num=wait_num
        self.freetime=freetime 
        self.occupy=occupy
        self.numFriend=numFriend
        self.P = P;

# Define class Event
# Event includes its original talker and receiver for "finished" action
# talker and receiver for the result of the "finished" and the both sides for a "begin" action
# timestamp for when this event begins, Type for whether it's "begin" or "finished"
class Event:
    def __init__(self, oriT, oriR, talker, receiver, timestamp, Type):
        self.oriT = oriT
        self.oriR = oriR
        self.talker = talker
        self.receiver = receiver
        self.timestamp = timestamp
        self.Type = Type

# Define function init
# This function initialize the user list
def init():
    global all_user
    all_user = list()

# Define function beginning
# This function initializes the users in the network
# Spreader and Truther from manually input, indicating the number of members in two teams
def beginning(Spreader, Truther, alloc, cred, size):

    if len(limit)==0:
        limit.append(size)
    # Add Spreader first
    i = 0
    while i < Spreader:
        # Set his numFriend from function numFriends
        numFriends_S = numFriends()
        a=User(len(all_user),1,'S',0,0,0,numFriends_S,[1,0,0.5])
        if alloc == 3:
            void = User(-1,1,'S',i+1,3,0,(2*i)/(Spreader+Truther),[])
        else:
            void = User(-1,1,'S',i+1,alloc,0,-3+6*i/Spreader,[])
        # # Uncomment the following line to implement allocation 3
        # void = User(-1,1,'S',i+1,0,0,(2*i)/(Spreader+Truther),[])
        act_user.append(a)
        all_user.append(a)
        graph.record.append([])
        createDist(void)

        # Add his friends as ignorants and potential receivers
        for j in range(numFriends_S):
            if size != 0:
                if len(all_user) > size:
                    break
            numFriends_I = numFriends()
            createDist(a)
            bid = len(all_user)
            b=User(bid,0,'I',0,0,0,numFriends_I,[cred,1-cred,0.5])
            all_user.append(b)
            graph.record.append([])
        i += 1
            
    # Then add Truther
    i = 0
    while i < Truther:   
        # Set his numFriend from function numFriends  
        numFriends_T = numFriends()
        a=User(len(all_user),1,'T',0,0,0,numFriends_T,[0,1,0.5])
        if alloc == 3:
            void = User(-1,-1,'T',i,3,0,(2*i+1)/(Spreader+Truther),[])            
        else:
        # Uncomment the following line to implement allocation 3
            void = User(-1,-1,'T',i,alloc,0,-3+6*i/Truther,[])
        act_user.append(a)
        all_user.append(a)
        graph.record.append([])
        createDist(void)
        
        # Add his friends as ignorants and potential receivers
        for j in range(numFriends_T):
            if size != 0:
                if len(all_user) > size:
                    break
            numFriends_I = numFriends()
            bid = len(all_user)
            createDist(a)
            P = [0.5,0.5,0.5]
            b=User(bid,0,'I',0,0,0,numFriends_I,[cred,1-cred,0.5])            
            all_user.append(b)
            graph.record.append([])
        i += 1

# Define function makeComb
# This function makes combination of both sides in an intercation
def makeComb():
    # Make combination until no active users are available
    while len(act_user) != 0:
        talker = act_user.pop(0)
        # Skip the talkers not active anymore
        if talker.value != 1:
        	continue
        # Skip and stifle the talkers who finishes with all his friends
        if(len(graph.record[talker.ID]) >= talker.numFriend):
            talker.Type = 'R' + talker.Type
            talker.value = -1
            continue
        # Get the receiver for the talker according to their relative position
        receiverID = kClosest(graph.dists, talker)
        receiver = all_user[receiverID]

        # Record their interaction to avoid repeating interaction
        graph.record[receiverID].append(talker.ID)
        graph.record[talker.ID].append(receiverID)
        # Alter the wait_num for both sides and schedule if waiting is needed
        if(talker.wait_num != 0):
            talker.wait_num += 1
            receiver.wait_num += 1
            # Schedule the event until both are available
            if talker.freetime > receiver.freetime:
            	ts = talker.freetime + rest()
            else:
            	ts = receiver.freetime + rest()
            schedule(None, None, talker, receiver, ts, begin)  

        # Alter the wait_num for both sides and schedule if waiting is needed      
        elif(receiver.wait_num != 0):
            talker.wait_num += 1
            receiver.wait_num += 1
            # Schedule the event until both are available
            if talker.freetime > receiver.freetime:
            	ts = talker.freetime
            else:
            	ts = receiver.freetime
            schedule(None, None, talker, receiver, ts, begin)

        # Schedule the event until both are available
        else:
            if talker.freetime > receiver.freetime:
            	ts = talker.freetime
            else:
            	ts = receiver.freetime
            talker.wait_num += 1
            receiver.wait_num += 1
            schedule(None, None, talker, receiver, ts, begin)
            
        # Introduce new friends if the receiver is picked for the first time
        if(receiver.Type=='I'):        
            j=1
            while(j<=receiver.numFriend):
                if len(limit) != 0:
                    if len(all_user) > limit[0]:
                        break
                numFriends_I = numFriends()
                aid = len(all_user)
                createDist(receiver)
                a=User(aid,0,'I',0,receiver.freetime,0,numFriends_I,
                    [receiver.P[0],receiver.P[1],receiver.P[2]])
                all_user.append(a)
                graph.record.append([])
                j += 1

# Define the function schedule
# This function schedule events to FEL and change participator's freetime
def schedule(oriT, oriR, talker,receiver,ts,Type):
    # Change the freetime for both sides as the time when they are both available
    if ts > talker.freetime:
        talker.freetime = ts
        all_user[talker.ID].freetime = ts
    if ts > receiver.freetime:
        receiver.freetime = ts
        all_user[receiver.ID].freetime = ts

    # Schedule events to the FEL
    FEL.append(Event(oriT, oriR, talker, receiver, ts, Type))
    FEL.sort(key=attrgetter('timestamp', 'Type'), reverse=False)

# Define function numFriends
# Generate the time length for the conversation according to a reference
def numFriends():
	s = rand(1)

	if s < 0.002:
		return 0
	elif 0.02 <= s < 0.08:
		return 1
	elif 0.08 <= s < 0.16:
		return 2
	elif 0.16 <= s < 0.27:
		return 3
	elif 0.27 <= s < 0.38:
		return 4
	elif 0.38 <= s < 0.55:
		return 5
	elif 0.55 <= s < 0.73:
		var = rand(1)
		return int(6+4*var)
	else:
		var = rand(1)
		return int(10+5*var)

# Define function rest
# Force available active users to rest for some time for the next talk
def rest():
	return 180

# Define function Ps
# Calculate the possibility that one will become a spreader
# Input parameters come from function interact
def Ps(ID, points):
    # Get the points closest to the User
    closest_cor = heapq.nsmallest(10,points,key=lambda p:(p[0]-graph.dists[ID][0])*(p[0]-graph.dists[ID][0])
        +(p[1]-graph.dists[ID][1])*(p[1]-graph.dists[ID][1]))
    closest_cor.pop(0)
    N = len(closest_cor)
    Ps = 0
    for i in closest_cor:
        neighborID = graph.dists.index([float(i[0]),float(i[1])])
        Ps += all_user[neighborID].P[0]
    Ps = Ps/N
    return Ps

# Define function Pt
# Calculate the possibility that one will become a truther
# Input parameters come from function interact
def Pt(ID, points):
    # Get the points closest to the User
    closest_cor = heapq.nsmallest(10,points,key=lambda p:(p[0]-graph.dists[ID][0])*(p[0]-graph.dists[ID][0])
        +(p[1]-graph.dists[ID][1])*(p[1]-graph.dists[ID][1]))
    closest_cor.pop(0)
    N = len(closest_cor)
    Pt = 0
    for i in closest_cor:
        neighborID = graph.dists.index([float(i[0]),float(i[1])])
        Pt += all_user[neighborID].P[1]
    Pt = Pt/N
    return Pt

# Define function Pr
# Calculate the possibility that one will become a stifler
# Input parameters come from function interact
def Pr(ID, points):
    # Get the points closest to the User
    closest_cor = heapq.nsmallest(10,points,key=lambda p:(p[0]-graph.dists[ID][0])*(p[0]-graph.dists[ID][0])
        +(p[1]-graph.dists[ID][1])*(p[1]-graph.dists[ID][1]))
    closest_cor.pop(0)
    N = len(closest_cor)
    Pr = 0
    for i in closest_cor:
        neighborID = graph.dists.index([float(i[0]),float(i[1])])
        Pr += all_user[neighborID].P[2]
    Pr = Pr/N
    return Pr
