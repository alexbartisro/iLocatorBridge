from pyicloud import PyiCloudService
from geopy.distance import vincenty
import ConfigParser
import ast, sys, time, requests, base64

gConfig = ConfigParser.ConfigParser()
gConfigurationiCloud = {}
gConfigurationGeofence = {}
gConfigurationOH = {}

def configurationManager():
	global gConfigurationiCloud
	global gConfigurationGeofence
	global gConfigurationOH

	try:
		gConfig.read('configuration.ini')
	except:
		print('\r\nNo configuration avaialble. Please see https://github.com/trusk89/iLocatorBridge for configuration')
	gConfigurationiCloud = configSectionMap('iCloud') 
	gConfigurationGeofence = configSectionMap('Geofence')
	gConfigurationOH = configSectionMap('OpenHab')

def configSectionMap(section):
	dict = {}
	options = gConfig.options(section)
	for option in options:
		try:
			dict[option] = gConfig.get(section, option)
		except:
			print('exception on %s!' % option)
			dict[option] = None
	return dict
	
def getDeviceCoordinates():
	global gConfigurationiCloud
	global gConfigurationGeofence

	gRequester = PyiCloudService(gConfigurationiCloud['username'], gConfigurationiCloud['password'])
	deviceList = gRequester.devices
	locationDictionary = (gRequester.devices[gConfigurationiCloud['deviceid']].location())
	return float(locationDictionary['latitude']), float(locationDictionary['longitude'])

def calculateDistance(lat, longitude):
	global gConfigurationGeofence

	currentLocation = (lat, longitude)
	homeLocation = (('%.6f' % float(gConfigurationGeofence['homelatitude'])), ('%.6f' %  float(gConfigurationGeofence['homelongitude'])))
	if gConfigurationGeofence['distanceunit'] == 'm':
		distance = (vincenty(currentLocation, homeLocation).meters)
	else:
		distance = (vincenty(currentLocation, homeLocation).feet)
	if int(distance) <= int(gConfigurationGeofence['geofenceradius']):
		return True
	else:
		return False

def postUpdate(state):
	global gConfigurationOH

	url = '%s/rest/items/%s/state' % (gServer, gConfigurationOH['ohitem'])
	req = requests.put(url, data=state, headers=basic_header())
	if req.status_code != requests.codes.ok:
		req.raise_for_status()
        

def basic_header():
	global gConfigurationOH

	auth = base64.encodestring('%s:%s'
                       %(gConfigurationOH['ohusername'], gConfigurationOH['ohpassword'])
                       ).replace('\n', '')
	return {
            "Authorization" : "Basic %s" %auth,
            "Content-type": "text/plain"}


if __name__ == "__main__":
	configurationManager()
	while 1:
		lat, long = getDeviceCoordinates()
		if calculateDistance(lat, long) == True:
			print ('YES')
			# postUpdate('ON')
		else:
			print('NO')
			# postUpdate('OFF')
		time.sleep(60)
