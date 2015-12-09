from pyicloud import PyiCloudService
from geopy.distance import vincenty
import numpy as np
import ast, sys, time

gConfiguration = {}
gUsername = ""
gPassword = ""
gDeviceID = ""
gRequester = None
gLatitude = 0
gLongitude = 0
gGeofence = 300

def readingFile():
	global gConfiguration 
	global gUsername
	global gPassword
	global gDeviceID
	global gLatitude
	global gLongitude

	gConfiguration = np.load('configuration.npy').item()

	gUsername = gConfiguration['username']
	gPassword = gConfiguration['password']
	gDeviceID = gConfiguration['deviceID']
	gLatitude =float(gConfiguration['latitude'])
	gLongitude = float(gConfiguration['longitude'])
	print('\r\nSuccessfully loaded configuration\r\n')		

def requestCredentials():
	global gUsername
	global gPassword
	global gLatitude
	global gLongitude

	gUsername = raw_input('Please insert your Apple ID\r\n')
	gPassword = raw_input('Please insert your Apple ID password\r\n')
	gLatitude = raw_input('Please insert your latitude (like: 12.345678)\r\n')
	gLongitude = raw_input('Please insert your long (like: 12.345678)\r\n')
	writingFile(gUsername, gPassword, '', gLatitude, gLongitude)

def writingFile(user, passwd, devID, lat, long):
	global gConfiguration 

	gConfiguration = {'username':user,'password':passwd,'deviceID':devID, 'latitude':lat, 'longitude':long}
	np.save('configuration.npy', gConfiguration)

def configurationManager():
	try:
		readingFile()
	except:
		print('\r\nNo configuration avaialble. Let\'s set it up!')
		requestCredentials()
	
def getDeviceCoordinates():
	global gUsername
	global gPassword
	global gDeviceID
	global gRequester

	gRequester = PyiCloudService(gUsername, gPassword)
	deviceList = gRequester.devices

	if gDeviceID == '':
		print ('The device list is ')
		print (deviceList)
		gDeviceID = raw_input('Insert the ID of the device you want to localize\r\n')
		writingFile(gUsername, gPassword, gDeviceID, gLatitude, gLongitude)
	locationDictionary = (gRequester.devices[gDeviceID].location())
	return float(locationDictionary['latitude']), float(locationDictionary['longitude'])

def calculateDistance(lat, longitude):
	global gLatitude
	global gLongitude
	global gGeofence

	currentLocation = (lat, longitude)
	homeLocation = (('%.6f' % gLatitude), ('%.6f' %  gLongitude))
	distance = (vincenty(currentLocation, homeLocation).meters)
	if int(distance) <= gGeofence:
		return True
	else:
		return False


if __name__ == "__main__":
	configurationManager()	
	print('Requesting devices for username ' + gUsername + ' and password ' + gPassword)
	while 1:
		lat, long = getDeviceCoordinates()
		if calculateDistance(lat, long) == True:
			print ('Yey, I\'m home')
		else:
			print ('Not home yet')
		time.sleep(60)
