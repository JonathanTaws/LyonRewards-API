#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from sklearn.ensemble import RandomForestClassifier 
import os
import msvcrt as m
from datetime import datetime
from sets import Set
from math import *

DATALOC = u"../dataset"
TRANSPORT = {
	"unknown" : -1,
	"walk" : 0.0,
	"bike" : 1.0,
	"car" : 2.0,
	"taxi" : 2.0,
	"subway" : 3.0,
	"bus" : 4.0
}

REVERSE = ["walk", "bike", "car", "subway", "bus"]

log_last = None
log_list = []
label_dict = {}
meta_counter = 0
modes = Set()

X = []
Y = []

#Haversine FTW
def dist(gps1, gps2):
	dlon = radians(gps2["lon"] - gps1["lon"])
	dlat = radians(gps2["lat"] - gps1["lat"])
	a = (sin(dlat/2))**2 + cos(radians(gps1["lat"])) * cos(radians(gps2["lat"])) * (sin(dlon/2))**2 
	c = 2 * atan2(sqrt(a), sqrt(1-a))
	d = 6372.8 * 1000 * c
	return d

#Great circle magic bearing formulas
def angle_to_north(gps1, gps2):
    dlon = radians(gps2["lon"] - gps1["lon"])
    y = sin(dlon) * cos(radians(gps2["lat"]))
    x = cos(radians(gps1["lat"])) * sin(radians(gps2["lat"])) - sin(radians(gps1["lat"]))*cos(radians(gps2["lat"]))*cos(dlon)
    brng = (degrees(atan2(y,x)) + 360) % 360
    return brng

def analyse_data():
	print "Data read successfully !"
	print "Total trajectories : ", len(log_list)
	print "Number of labelled parts : ", meta_counter
	print ("-"*60)
	for log in log_list:
		if(len(log["gps"]) < 3):
			continue

		#Compute features and feed vectors
		#print "Log ", len(X)+1, " : ", len(log["gps"]), "GPS points and mode = ", log["mode"]

		#1st feature : average speed
		speeds = [0] * len(log["gps"])
		speed_sum = 0.0
		for index in range(1, len(log["gps"])):
			speeds[index] = dist(log["gps"][index], log["gps"][index-1])/ \
							((log["gps"][index]["timestamp"] - log["gps"][index-1]["timestamp"]).total_seconds())
			speed_sum += speeds[index]
		avg_speed = 3.6 * speed_sum / (len(log["gps"])-1)
		#print "--- avg speed is ", avg_speed, " km/h"

		#2nd feature : average acceleration
		accel_sum = 0.0
		for index in range(2, len(log["gps"])):
			accel_sum += (speeds[index] - speeds[index-1]) / \
						 ((log["gps"][index]["timestamp"] - log["gps"][index-1]["timestamp"]).total_seconds())
		avg_accel = accel_sum / (len(log["gps"])-2)
		#print "--- avg accel is ", avg_accel

		#3rd feature : average heading change
		angle_sum = 0.0
		for index in range(1, len(log["gps"])):
			angle_sum += angle_to_north(log["gps"][index], log["gps"][index-1])
		avg_angle = angle_sum / (len(log["gps"])-1)
		#print "--- avg degree change is ", avg_angle

		X.append([avg_speed, avg_accel, avg_angle])
		Y.append(TRANSPORT[log["mode"]])

	print ("-"*60)
	Xtrain = X[len(X)/2:]
	Ytrain = Y[len(Y)/2:]
	Xtest = X[:len(X)/2]
	Ytest = Y[:len(Y)/2]
	forest = RandomForestClassifier(n_estimators = 100)
	forest.fit(Xtrain,Ytrain)
	Yresult = forest.predict(Xtest)
	counter = 0
	for index in range(0, len(Yresult)):
		#print Yresult[index], " --- VS --- ", Ytest[index]
		if(Yresult[index] == Ytest[index]):
			counter = counter + 1
	print "Done training the forest !"
	print "Statistics, success : ", counter, " / ", len(Yresult)

def parse_labels(flabel):
	#Get labels ready
	for line_number, line in enumerate(flabel):
		if line_number == 0:
			continue
		try:
			label_parts = line.rstrip().split('\t')
			key = datetime.strftime(datetime.strptime(label_parts[0], "%Y/%m/%d"), "%Y/%m/%d") + \
				"|" + datetime.strftime(datetime.strptime(label_parts[1], "%H:%M:%S"), "%H:%M:%S") + \
				"|" + datetime.strftime(datetime.strptime(label_parts[2], "%H:%M:%S"), "%H:%M:%S")
			label_dict[key] = label_parts[3]
			modes.add(label_parts[3])
		except ValueError:
			pass #Nothing to do, this label goes to waste
		except IndexError:
			pass #Nothing to do, this label goes to waste

def solve_label():
	global meta_counter
	key = datetime.strftime(log_last["start_time"], "%Y/%m/%d|%H:%M:%S|") + datetime.strftime(log_last["end_time"], "%H:%M:%S")
	if key in label_dict and label_dict[key] in TRANSPORT:
		meta_counter = meta_counter + 1
		log_last["mode"] = label_dict[key]
		log_list.append(log_last)
		return True
	else:
		return False

#Feed our data structure using opened files
def parse_file(fdata):
	#Feed log_list structure
	global log_last
	make_new = False
	for line_number, line in enumerate(fdata):
		if line_number < 6:
			continue
		attributes = line.rstrip().split(",")
		datestr = attributes[5] + "|" + attributes[6]
		timestamp = datetime.strptime(datestr, "%Y/%m/%d|%H:%M:%S")
		gpsobject = {
						"timestamp" : timestamp,
						"lat" : float(attributes[0]),
						"lon" : float(attributes[1]),
						"alt" : float(attributes[3]),
					}
		if(attributes[2] == '1' or make_new):
			if not (log_last is None):
				solve_label()
			log_last = {
				"start_time" : timestamp,
				"end_time" : timestamp,
				"gps" : [gpsobject],
				"mode" : TRANSPORT["unknown"]
			}
			make_new = False
		else:
			log_last["end_time"] = timestamp
			log_last["gps"].append(gpsobject)
			make_new = solve_label()
		
#Get all PLT logs and open them, along with the associated label file
def main():
	subdirs = os.listdir(DATALOC)
	for subpath in subdirs:
		subpath = DATALOC + "/" + subpath + "/"
		logs = os.listdir(subpath + "trajectory/")
		with open(subpath + "labels.txt") as flabel:
			parse_labels(flabel)
		for logpath in logs:
			with open(subpath + "trajectory/" + logpath) as fdata:
				parse_file(fdata)
		print "Subfolder eaten : ", subpath, " - current total : ", len(log_list), " - ", meta_counter
	analyse_data()

if __name__ == "__main__":
	main()