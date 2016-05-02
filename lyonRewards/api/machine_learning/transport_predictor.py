#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
import os
import msvcrt as m
from datetime import datetime
from sets import Set
from math import *
import cPickle

DATALOC = u"../dataset"
DATALYON = u"../datalyon"

TRANSPORT = {
	"unknown" : -1,
	"walk" : 0.0,
	"bike" : 1.0,
	"car" : 2.0,
	"taxi" : 2.0,
	"bus" : 3.0
}

TRANSPORT_LYON = {
	"walk" : 0.0,
	"bike" : 1.0,
	"bus" : 2.0,
	"tram" : 3.0,
	"car" : 4.0
}

REVERSE = ["walk", "bike", "car", "bus"]
REVERSE_LYON = ["walk", "bike", "bus", "tram", "car"]

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

#Haversine FTW
def dist_lyon(gps1, gps2):
	dlon = radians(gps2["longitude"] - gps1["longitude"])
	dlat = radians(gps2["latitude"] - gps1["latitude"])
	a = (sin(dlat/2))**2 + cos(radians(gps1["latitude"])) * cos(radians(gps2["latitude"])) * (sin(dlon/2))**2 
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

# ------------------------------------------------------------
# 						PRODUCTION - LYON
# ------------------------------------------------------------

#Speed unit mode is eitheir m/s or km/h
def compute_features(gps_log, accel_log, speed_unit_mode):
	#1st feature : average speed
	speeds = [0.0] * len(gps_log)
	speed_sum = 0.0
	for index in range(1, len(gps_log)):
		if(gps_log[index]["speed"]=="NA"):
			if((gps_log[index]["timestamp"] - gps_log[index-1]["timestamp"]).total_seconds())==0:
				speeds[index] = 0
			else:
				speeds[index] = 3.6 * dist_lyon(gps_log[index], gps_log[index-1])/ \
								((gps_log[index]["timestamp"] - gps_log[index-1]["timestamp"]).total_seconds())
		else:
			speeds[index] = float(gps_log[index]["speed"])
			if(speed_unit_mode=="m/s"):
				speeds[index] = 3.6 * speeds[index]
		speed_sum += speeds[index]
	avg_speed = speed_sum / (len(gps_log)-1)
	return [avg_speed]

def train():
	subpath = DATALYON + "/logs"
	logs = os.listdir(subpath)

	with open(DATALYON + "/modes.txt") as flabel:
		for line in flabel:
			attributes = line.rstrip().split("=")
			label_dict[attributes[0]] = TRANSPORT_LYON[attributes[1]]

	for logpath in logs:
		with open(subpath + "/" + logpath) as fdata:
			column_mode = -1
			speed_unit_mode = "?"
			gps_log = []
			accel_log = []
			for line_number, line in enumerate(fdata):

				if line_number==1:
					names = line.rstrip().split(";")
					column_mode = len(names)
					detect_speed_unit = line.find("LOCALISATION Vitesse")
					if(detect_speed_unit==-1):
						detect_speed_unit = line.find("LOCATION Speed") + len("LOCATION Speed")
					else:
						detect_speed_unit += len("LOCALISATION Vitesse")
					if(line[detect_speed_unit+3]=="m"):
						speed_unit_mode = "m/s"
					else:
						speed_unit_mode = "km/h"

				elif line_number>1:
					attributes = line.rstrip().split(";")
					if(column_mode==13):
						#If low on satellites, skip object
						nb_satellites = int(attributes[10].split("/")[0])
						if(nb_satellites==0):
							continue
						gps_object = {
							"latitude" : float(attributes[3]),
							"longitude" : float(attributes[4]),
							"speed" : "NA" if attributes[7] == "" else attributes[7],
							"timestamp" : datetime.strptime(attributes[12][:-4], "%Y-%m-%d %H:%M:%S")
						}
						accel_object = {
							"x" : attributes[0],
							"y" : attributes[1],
							"z" : attributes[2],
							"timestamp" : datetime.strptime(attributes[12][:-4], "%Y-%m-%d %H:%M:%S")
						}
						gps_log.append(gps_object)
						accel_log.append(accel_object)
					elif(column_mode==22):
						#If low on satellites, skip object
						nb_satellites = int(attributes[19].split("/")[0])
						if(nb_satellites==0):
							continue
						gps_object = {
							"latitude" : float(attributes[12]),
							"longitude" : float(attributes[13]),
							"speed" : "NA" if attributes[16] == "" else attributes[16],
							"timestamp" : datetime.strptime(attributes[21][:-4], "%Y-%m-%d %H:%M:%S")
						}
						accel_object = {
							"x" : attributes[0],
							"y" : attributes[1],
							"z" : attributes[2],
							"timestamp" : datetime.strptime(attributes[21][:-4], "%Y-%m-%d %H:%M:%S")
						}
						gps_log.append(gps_object)
						accel_log.append(accel_object)

			#Remove 10% unsure data from each side
			gps_log = gps_log[len(gps_log)/10:(len(gps_log)-(len(gps_log)/10))]
			accel_log = accel_log[len(accel_log)/10:(len(accel_log)-(len(accel_log)/10))]

			#File eaten in gps_log and accel_log, now we can compute features
			features = compute_features(gps_log, accel_log, speed_unit_mode)
			print features[0], " km/h is mode ", REVERSE_LYON[int(label_dict[logpath[:-4]])]
			X.append(features)
			Y.append(label_dict[logpath[:-4]])

	#Now train the model !
	forest = RandomForestClassifier(n_estimators = 100)
	forest.fit(X,Y)
	Yresult = forest.predict(X)
	counter = 0
	for index in range(0, len(Yresult)):
		if(Yresult[index] == Y[index]):
			counter = counter + 1
	print "Done training the forest !"
	print "Statistics, success : ", counter, " / ", len(Yresult)
	print "-----------------------------------------------------"
	with open('rf.pkl', 'wb') as f:
		cPickle.dump(forest, f)

def predict(data):
	Xdata = []
	with open('rf.pkl', 'rb') as f:
		forest = cPickle.load(f)
	speed_unit_mode = "m/s"
	gps_log = data["gps"]
	accel_log = data["accel"]
	total_km = 0.0

	#Data needs some adaptation dude
	for accel_object in accel_log:
		accel_object["timestamp"] = datetime.fromtimestamp(float(accel_object["timestamp"]))

	for index in range(len(gps_log)):
		if(gps_log[index]["speed"] == "-1"):
			gps_log[index]["speed"] = "NA"
		gps_log[index]["latitude"] = float(gps_log[index]["latitude"])
		gps_log[index]["longitude"] = float(gps_log[index]["longitude"])
		gps_log[index]["timestamp"] = datetime.fromtimestamp(float(gps_log[index]["timestamp"]))
		if(index>0):
			total_km += (dist_lyon(gps_log[index], gps_log[index-1]))/1000

	Xdata.append(compute_features(gps_log, accel_log, speed_unit_mode))
	result = {
		"type" : REVERSE_LYON[int(forest.predict(Xdata))],
		"distance" : total_km
	}
	print result
	return result


# ------------------------------------------------------------
# 						CHINA TRAINING
# ------------------------------------------------------------

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
	train()
	#Demo
	predict(
		{
			"gps" : [
				{
					"latitude" : "45.50",
					"longitude" : "4.50",
					"speed" : "45.50",
					"timestamp" : "1462212262"
				},
				{
					"latitude" : "45.80",
					"longitude" : "4.50",
					"speed" : "45.50",
					"timestamp" : "1462212266"
				}
			],
			"accel" : [
				{
					"x" : "1.59849",
					"y" : "2.54949",
					"z" : "7.595495949",
					"timestamp" : "1462212262"
				},
				{
					"x" : "4.5997877",
					"y" : "8.54949",
					"z" : "0.59949",
					"timestamp" : "1462212266"
				}
			]
		}
	)
	""" OLD : TRAIN WITH CHINA DATA
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
	"""

if __name__ == "__main__":
	main()