from operator import attrgetter
import numpy as np
from numpy.random import rand
import random
import copy
from admin import User, beginning, makeComb, act_user, schedule, FEL, rest, Pr, Ps, Pt
import admin
import graph
import heapq

# Define state constant
begin = 1
finished = 0

# Define the time constant
Now = 0.0

# Define function init_stat
# This function initialize lists to store time-related statistics
def init_stat():
    global ratio 
    ratio = []
    global num_sp 
    num_sp = []
    global num_tr
    num_tr = []
    global num_st 
    num_st = []
    global num_touched
    num_touched = []

# Define function Runsim
# variate time from manually input
# Drive the simulation to run by popping and parsing event from FEL
def Runsim(time):
    # Define the list to store time-related statistics
    cp = 10
    print("Initial event list:")
    while len(FEL)!=0:
        PrintList()
        event = FEL.pop(0)

        # Uncomment the following section to simulate an open system
        if (time!=0):
            if(event.timestamp > time):
                break
        
        global Now   
        Now = event.timestamp
        print("Now is "+ str(Now))

        # Record the current state of the system
        num_user=len(admin.all_user)
        if Now > cp:
            touched = 0
            nS = 0
            nT = 0
            nR = 0
            for i in admin.all_user:
                if i.value != 0:
                    touched += 1 
                if i.Type == 'S':
                    nS += 1
                if i.Type == 'T':
                    nT += 1
                if i.value == -1:
                    nR += 1  
            ratio.append([Now, touched/num_user])
            num_touched.append([Now, touched])
            num_sp.append([Now, nS])
            num_tr.append([Now, nT])
            num_st.append([Now, nR])
            cp += 10
        eventhandler(event)
    print("End time: ", Now)

# Define function Printlist
# Print out all the events in the FEL with their information
def PrintList():
    print("Future Events")
    for i in FEL:
        if(i.Type):
            state = "beginning"
            # Invalidate the event whose talker already converted to a stifler
            if(i.talker.value != 1):
            	print("(invalid event)")
        else:
            state = "finished"

        # Print the both sides of the talk if the action is "begin"
        if(i.oriR == None):
            print(str(i.talker.Type) + " (ID:" + str(i.talker.ID) + ") " + "interaction " + state + " with " 
            + str(i.receiver.Type) + " (ID:" + str(i.receiver.ID) + ") ")
            print("@ " + str(i.timestamp) + "\n")
        # Print the original both sides of the talk if the action is "finished"
        else:
            print(str(i.oriT.Type) + " (ID:" + str(i.oriT.ID) + ") " + "interaction " + state + " with " 
                + str(i.oriR.Type) + " (ID:" + str(i.oriR.ID) + ") ")
            print("@ " + str(i.timestamp) + "\n")

# Define function CurrentTime
# CurrentTime returns Now, which is "current time"
def CurrentTime():
	return Now

# Define function eventhandler
# The input event comes from function Runsim
# The eventhandler makes who in "begin" action interact or wait
# and makes who in "finished" action find a new talk or go to the subsequent talk
def eventhandler(Event):

    # Print out the current event
    print("Now processing")
    if(Event.Type):
        state = "beginning"
        print(str(Event.talker.Type) + " (ID:" + str(Event.talker.ID) + ") " + "interaction " + state + " with " 
            + str(Event.receiver.Type) + " (ID:" + str(Event.receiver.ID) + ") " + "\n@ " + str(Event.timestamp))
    else:
        state = "finished"  
        print(str(Event.oriT.Type) + " (ID:" + str(Event.oriT.ID) + ") " + "interaction " + state + " with " 
            + str(Event.oriR.Type) + " (ID:" + str(Event.oriR.ID) + ") " + "\n@ " + str(Event.timestamp)+", result: ")
        print(str(Event.talker.Type) + " (ID:" + str(Event.talker.ID) + ") " + ", and " 
            + str(Event.receiver.Type) + " (ID:" + str(Event.receiver.ID) + ") \n")

    # Process the "begin" action
    if Event.Type == begin:

        # Invalidate the current event if the talker is stifled beforehead
        if Event.talker.value != 1:
        	print("This event is invalid")
        	Event.talker.wait_num = 0
        	Event.receiver.wait_num -= 1
        	Event.talker.occupy = 0
        	Event.receiver.occupy = 0
        	return

        # Have the both sides wait if one of them or both in a conversation
        # until both of them finish current talking
        if Event.talker.wait_num != 0 and Event.talker.occupy == 1:
            if Event.talker.freetime > Event.receiver.freetime:
            	ts = Event.talker.freetime + rest()
            else:
            	ts = Event.receiver.freetime + rest()
            schedule(None, None, Event.talker, Event.receiver, ts, begin)
        elif Event.receiver.wait_num != 0 and Event.receiver.occupy == 1:
            if Event.talker.freetime > Event.receiver.freetime:
            	ts = Event.talker.freetime + rest()
            else:
            	ts = Event.receiver.freetime + rest()
            schedule(None, None, Event.talker, Event.receiver, ts, begin)
        # Make them interact if both are not occupied
        else:
            interact(Event.talker, Event.receiver)

    #Process the "finished" action
    else:        
        # Substract 1 from the waiting number
        if Event.talker.wait_num != 0:
        	Event.talker.wait_num -= 1
        if Event.receiver.wait_num != 0:
        	Event.receiver.wait_num -= 1
        
        # Mark the talker and receiver as unoccupied
        Event.talker.occupy = 0
        Event.receiver.occupy = 0
        # Invalidate a previously stifled talker
        # and invalidate all its related events in advance
        if Event.talker.value == -1:
        	Event.talker.wait_num = 0

        # Assign the active talker a new interaction
        if Event.talker.wait_num == 0:
            if Event.talker.value == 1:
                act_user.append(Event.talker)
                makeComb()
        # Assign the active receiver a new interaction
        if Event.receiver.wait_num == 0:
            if Event.receiver.value == 1:
                act_user.append(Event.receiver)
                makeComb()

# Define function interact
# The both sides of interaction are from eventhandler
# This function makes both sides parsed to this function interact
# and change their type according to their type with probability
def interact(talker, receiver):

    # Copy the original users in this interaction for later description
    originT = copy.copy(talker)
    originR = copy.copy(receiver)
    
    # Mark both ones as occupied
    talker.occupy = 1
    receiver.occupy = 1

    # Generate random number for deciding the result
    r_s = rand(1)
    r_rt = rand(1)
    r_rr = rand(1)
    # Generate interact time from function interval
    delta_time = interval()
    # Set the time for "finished" action
    ts = float(Now + delta_time)

    # P_s, P_rt, P_rr = conversion(dists, talker, receiver)
    talker.P = [Ps(talker.ID, graph.dists), Pt(talker.ID, graph.dists), Pr(talker.ID, graph.dists)]
    receiver.P = [Ps(receiver.ID, graph.dists), Pt(receiver.ID, graph.dists), Pr(receiver.ID, graph.dists)]

    if talker.Type == 'S':
        index_p = 0
    else:
        index_p = 1
    # Process case where two active users interact
    if talker.value+receiver.value == 2:

        # Random probability distribution for deciding conversion
        if talker.Type == receiver.Type:            
            if r_rr < receiver.P[2]:
                receiver.P[0] = Ps(receiver.ID, graph.dists)
                receiver.P[1] = Pt(receiver.ID, graph.dists)
                receiver.Type = 'R' + receiver.Type
                receiver.value = -1
                receiver.P[2] = 1

            if r_rt < talker.P[2]:
                talker.P[0] = Ps(talker.ID, graph.dists)
                talker.P[1] = Pt(talker.ID, graph.dists)
                talker.Type = 'R' + talker.Type
                talker.value = -1
                talker.P[2] = 1
        else:           
            if r_s < receiver.P[index_p]:
                receiver.Type = talker.Type
                receiver.value = 1
                receiver.P[index_p] = 1
                receiver.P[(2**index_p)%2] = 0
            if r_rr < receiver.P[2]:
                receiver.Type = 'R' + receiver.Type
                receiver.value = -1
                receiver.P[0] = Ps(receiver.ID, graph.dists)
                receiver.P[1] = Pt(receiver.ID, graph.dists)
                receiver.P[2] = 1
            if r_rt < talker.P[2]:
                talker.Type = 'R' + talker.Type
                talker.value = -1
                talker.P[0] = Ps(talker.ID, graph.dists)
                talker.P[1] = Pt(talker.ID, graph.dists)
                talker.P[2] = 1

    # Process case where an active user interacts with an ignorant
    elif talker.value+receiver.value == 1:

        # Random probability distribution for deciding conversion
        if r_s < receiver.P[index_p]:
            receiver.value = talker.value
            receiver.Type = talker.Type
            receiver.P[index_p] = 1
            receiver.P[(2**index_p)%2] = 0
        else:
            receiver.value = -1
            receiver.Type = 'R' + talker.Type
            receiver.P[2] = 1
        if r_rt < talker.P[2]:
            talker.Type = 'R' + talker.Type
            talker.value = -1
            talker.P[0] = Ps(talker.ID, graph.dists)
            talker.P[1] = Pt(talker.ID, graph.dists)
            talker.P[2] = 1

    # Process case where an active user interacts with a stifler
    elif talker.value+receiver.value == 0:

        # Random probability distribution for deciding conversion
        if r_s < receiver.P[index_p]:
            receiver.value = talker.value
            receiver.Type = talker.Type
            receiver.P[index_p] = 1
            receiver.P[(2**index_p)%2] = 0
            receiver.P[2] = Pr(talker.ID, graph.dists)
        if r_rt < talker.P[2]:
            talker.value = -1
            talker.Type = 'R' + talker.Type
            talker.P[0] = Ps(talker.ID, graph.dists)
            talker.P[1] = Pt(talker.ID, graph.dists)
            talker.P[2] = 1

    # Schedule the "finished" event
    schedule(originT, originR, talker, receiver, ts, finished) 

# Define function interval
# Generate the time length for the conversation according to a reference
def interval():
	s = rand(1)

	if s < 0.116:
		var = rand(1)
		return (15*var)
	elif 0.116 <= s < 0.251:
		var = rand(1)
		return (15+22.5*var)
	elif 0.251 <= s < 0.419:
		var = rand(1)
		return (37.5+22.5*var)
	elif 0.419 <= s < 0.728:
		var = rand(1)
		return (60+60*var)
	elif 0.728 <= s < 0.835:
		var = rand(1)
		return (120+60*var)
	elif 0.835 <= s < 0.868:
		var = rand(1)
		return (180+60*var)
	elif 0.868 <= s < 0.945:
		var = rand(1)
		return (240+60*var)
	elif 0.945 <= s < 0.986:
		var = rand(1)
		return (300+300*var)
	elif 0.986 <= s < 0.994:
		var = rand(1)
		return (600+600*var)
	else:
		var = rand(1)
		return (1200 + 2400*var)
