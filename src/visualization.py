import numpy as np
# import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.use('Agg')

import matplotlib.pyplot as plt
import admin
import graph

# Define function visualization
# Input parameters coming from manual input
def visualization(name):
	num = 0
	for i in graph.dists:
		if admin.all_user[num].value == 1 and len(graph.record[admin.all_user[num].ID])>=admin.all_user[num].numFriend:
			admin.all_user[num].Type = 'R' + admin.all_user[num].Type
			admin.all_user[num].value = -1
		if admin.all_user[num].Type == 'S':
			plt.scatter(i[0],i[1],color='blue',marker='o',s=5)
		elif admin.all_user[num].Type == 'T':
			plt.scatter(i[0],i[1],color='red',marker='o',s=5)
		elif admin.all_user[num].Type == 'RS':
			plt.scatter(i[0],i[1],color='green',marker='o',s=5)
		elif admin.all_user[num].Type == 'RT':
			plt.scatter(i[0],i[1],color='orange',marker='o',s=5)
		num += 1

	plt.savefig(name)
	plt.clf()

# Define function Trend
# This function draws the changing trend of several parameters of our system
# Input parameters coming from the data collected in application.py
def Trend(iteration, data, g_type):

	graph = "{0}_#{1}".format(g_type, iteration)
	
	# Plot the interacted percentage changing with time
	pts=[]
	record=[]
	for i in data:
	    if i[0] not in record:
	        record.append(i[0])
	        pts.append(i[1])

	plt.ylabel(g_type)
	plt.xlabel("t")
	for i in range(len(pts)):
	    plt.scatter(record[i],pts[i],color='red',marker='o',s=5)
	plt.savefig(graph)
	plt.clf()

