from __future__ import division
from operator import attrgetter
from numpy.random import rand
from numpy import average, std, sqrt
import random
import copy
from admin import beginning, init
from engine import Runsim, makeComb, act_user, init_stat
import admin
import engine
from graph import init_graph
from visualization import visualization, Trend



# Define state constant
begin = 1
finished = 0

# Define the list to store the statistical of the system
against_ratio=[]
int_percentages=[]
population=[]

# Define function CI
# This function calculate the confidence interval of the statistics
# Input from system calculation
def CI(data):

	# Due to the lack of library on PACE, we set the number of sample as 200
	# With confidence = 0.95
    t = 1.971956544249395
          
    n = len(data)
    m = average(data)
    std_err = std(data, ddof=1)

    h = std_err * t / sqrt(n)

    start = m - h

    end = m + h

    return m, std_err, h, start, end

# Ask the user for the inputs
while (1):
	print('initial number of S?')
	init_S=int(input())
	if init_S>=0:
		break
	else:
		print("try again")

while (1):
	print('initial number of T?')
	init_T=int(input())
	if init_T>=0:
		break
	else:
		print("try again")

sample = 0

while (1):
	print('The credibility of the rumor?')
	cred = float(input())
	if 0<=cred<=1:
		break
	else:
		print("try again")

while (1):	
	print('Which allocation?')
	alloc = int(input())
	if alloc in [1,2,3]:
		break
	else:
		print("try again")

while (1):
	print('Open or Restricted system? 0 for Restricted, simulation time for Open')
	sim_time = int(input())
	if sim_time >= 0:
		break
	else:
		print("try again")

if sim_time == 0:
	while (1):
		print('Size of the system?')
		global size
		size = int(input())
		if size > 0:
			break
		else:
			print("try again")
else:
	size = 0

# run the simulation 200 times
for n in range(200):

	# Indicate the number of the iteration
	print("#",n," iteration")

	# Initialize the user list and intimacy map coordinates
	init()
	init_graph()
	init_stat()

	# Initialize users
	beginning(init_S, init_T, alloc, cred, size)

	# Plot the initial snapshot of the system
	visualization('Begin.pdf')

	# Schedule interactions for all active users
	makeComb()
	# Run the simulation
	Runsim(sim_time) # The time of simulation can be adjusted

	# Derive the statistics of the network (to be extended after the checkpoint)
	untouched = 0
	touched = 0
	numS = 0
	numT = 0
	num_all = len(admin.all_user)
	for i in admin.all_user:
		if i.value == 0:
			untouched += 1
		if i.value != 0:
			touched += 1
		if i.Type == 'S' or i.Type == 'RS':
			numS += 1
		if i.Type == 'T' or i.Type == 'RT':
			numT += 1

	# Calculate the interacted 
	int_percentage = float(touched / num_all)
	if numT == 0:
		against_rat = "inf"
	else:
		against_rat = numS/numT

	# Print the result of every simulation run
	print("Now we have "+ str(num_all) + " persons\n" + str(touched) + " have been interacted\n"
		+ str(untouched) + " haven't been interacted")
	print(str(int_percentage*100)+"% people have been in an interaction")
	if numT != 0:
		print("S/T ratio is: "+str(against_rat))
	
	# Add the results into the result list for later analysis
	population.append(num_all)
	against_ratio.append(against_rat)
	int_percentages.append(int_percentage)

	# Plot the changing trend in the system
	if n > sample:
		Trend(n, engine.ratio, "interacted_percentage")
		Trend(n, engine.num_sp, "num_spreader")
		Trend(n, engine.num_tr, "num_truther")
		Trend(n, engine.num_st, "num_stifler")
		Trend(n, engine.num_touched, "num_touched")
		sample += 40

	# Plot the initial snapshot of the system
	visualization('End.pdf')

# Calculate the statistics of the simulation
m, std_err, h, start, end = CI(population)
print("Statistical results: population of this network:")
print(("mean: %3f; std_err: %3f; zeta: %3f; CI_min: %3f; CI_max: %3f; zeta/mean: %3f")%
	(m, std_err, h, start, end, h/m))

m, std_err, h, start, end = CI(against_ratio)
print("Statistical results: against_ratio of this network:")
print(("mean: %3f; std_err: %3f; zeta: %3f; CI_min: %3f; CI_max: %3f; zeta/mean: %3f")%
	(m, std_err, h, start, end, h/m))

m, std_err, h, start, end = CI(int_percentages)
print("Statistical results: int_percentages of this network:")
print(("mean: %3f; std_err: %3f; zeta: %3f; CI_min: %3f; CI_max: %3f; zeta/mean: %3f")%
	(m, std_err, h, start, end, h/m))

# Store the output for future analysis
filename = "{0}S{1}T_population.txt".format(init_S,init_T)
with open(filename, "w") as output:
	output.write(str(population))

filename = "{0}S{1}T_against_ratio.txt".format(init_S,init_T)
with open(filename, "w") as output:
	output.write(str(against_ratio))

filename = "{0}S{1}T_against_int_percentage.txt".format(init_S,init_T)
with open(filename, "w") as output:
	output.write(str(int_percentages))

