from pyicloud import PyiCloudService
from geopy.distance import vincenty
import ConfigParser
import ast, sys, time, requests, base64, logging

logging.basicConfig(filename='iLocatorLog.log',level=logging.DEBUG, format='%(asctime)s %(message)s')
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
		logging.info('Configuration loaded')
	except:
		print('Exception! Please check the log')
		logging.error('\r\nNo configuration avaialble. Please see https://github.com/trusk89/iLocatorBridge for configuration')
		sys.exit(0)
	
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
			print('Exception! Please check the log')
			logging.error('exception on %s!' % option)
			sys.exit(0)
	logging.info('Configuration %s parsed' % (section))
	return dict
	
def getDeviceCoordinates():
	global gConfigurationiCloud
	global gConfigurationGeofence

	try:
		gRequester = PyiCloudService(gConfigurationiCloud['username'], gConfigurationiCloud['password'])
		deviceList = gRequester.devices
		locationDictionary = (gRequester.devices[gConfigurationiCloud['deviceid']].location())
	except Exception, e:
		print('Exception! Please check the log')
		logging.error('Could not get device coordinates')
		sys.exit(0)
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
	try:
		req = requests.put(url, data=state, headers=basic_header())
		if req.status_code != requests.codes.ok:
			req.raise_for_status()
		logging.info('Update posted to OpenHab')
	except Exception, e:
		print('Exception! Please check the log. Will continue execution.')
		logging.error('Could not post update to OpenHab')

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
			logging.info('User is in Geofence')
			postUpdate('ON')
		else:
			print('NO')
			logging.info('User is outside of Geofence')
			postUpdate('OFF')
		time.sleep(60)
