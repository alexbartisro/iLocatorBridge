from pyicloud import PyiCloudService
import numpy as np
import ast
import sys

gConfiguration = {}
gUsername = ""
gPassword = ""
gDeviceID = ""
gRequester = None

def readingFile():
	global gConfiguration 
	global gUsername
	global gPassword
	global gDeviceID

	gConfiguration = np.load('configuration.npy').item()
	print(gConfiguration)

	gUsername = gConfiguration['username']
	gPassword = gConfiguration['password']
	gDeviceID = gConfiguration['deviceID']

	print('\r\nSuccessfully loaded configuration\r\n')		

def requestCredentials():
	global gUsername
	global gPassword

	gUsername = raw_input('Please insert your Apple ID\r\n')
	gPassword= raw_input('Please insert your Apple ID password\r\n')
	writingFile(gUsername, gPassword, '')

def writingFile(user, passwd, devID):
	global gConfiguration 

	gConfiguration = {'username':user,'password':passwd,'deviceID':devID}
	np.save('configuration.npy', gConfiguration)

def configurationManager():
	try:
		readingFile()
	except:
		print('\r\nNo configuration avaialble. Let\'s set it up!')
		requestCredentials()
	
def getDevice():
	global gUsername
	global gPassword
	global gDeviceID
	global gRequester

	print('Requesting devices for username ' + gUsername + ' and password ' + gPassword)
	gRequester = PyiCloudService(gUsername, gPassword)
	deviceList = gRequester.devices

	if gDeviceID == '':
		print ('The device list is ')
		print (deviceList)
		gDeviceID = raw_input('Insert the ID of the device you want to localize\r\n')
		writingFile(gUsername, gPassword, gDeviceID)
	print(deviceList)
	locationDictionary = (gRequester.devices[gDeviceID].location())
	print(locationDictionary['latitude'] + " " + locationDictionary['longitude'])

def main():
	global gConfiguration
	global gDeviceID
	global gRequester

	configurationManager()
	getDevice()

main()
