from pyicloud import PyiCloudService
from math import radians, cos, sin, asin, sqrt
import ConfigParser
# import ast
import sys
import time
import requests
import base64
import logging

logging.basicConfig(filename='iLocatorLog.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
gConfig = ConfigParser.ConfigParser()
gConfigurationiCloud = {}
gConfigurationGeofence = {}
gConfigurationOH = {}
gRequester = None


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
    global gConfigurationOH
    global gRequester
    locationDictionary = None

    while locationDictionary is None:
        try:
            # deviceList = gRequester.devices
            locationDictionary = (gRequester.devices[gConfigurationiCloud['deviceid']].location())
        except Exception, e:
            print('Exception! Please check the log')
            logging.error('Could not get device coordinates. Retrying!: %s' % (e, ))
            time.sleep(int(gConfigurationOH['interval']))
        pass

    return float(locationDictionary['latitude']), float(locationDictionary['longitude'])


def calculateDistance(lat, longitude):
    global gConfigurationGeofence

    distance = haversine(gConfigurationGeofence['homelatitude'], lat, gConfigurationGeofence['homelongitude'], long)
    logging.info('Distance from POI is ' + str(distance))
    if gConfigurationGeofence['distanceunit'] == 'f':
        distance = distance * 3.28084
    if int(distance) <= int(gConfigurationGeofence['geofenceradius']):
        return True
    else:
        return False


def haversine(lat1, lat2, lon1, lon2):
    # Thanks for this Aaron D
    # http://stackoverflow.com/questions/15736995/how-can-i-quickly-estimate-the-distance-between-two-latitude-longitude-points
    lon1 = (float(lon1))
    lat1 = (float(lat1))
    lon2 = (float(lon2))
    lat1 = (float(lat2))
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * asin(sqrt(a))
    m = 6367 * c * 1000
    return m


def postUpdate(state):
    global gConfigurationOH

    url = '%s/rest/items/%s/state' % (gConfigurationOH['ohserver'], gConfigurationOH['ohitem'])
    try:
        req = requests.put(url, data=state, headers=basic_header())
        if req.status_code != requests.codes.ok:
            req.raise_for_status()
        logging.info('Update posted to OpenHab')
    except Exception, e:
        print('Exception! Please check the log. Will continue execution.')
        logging.error('Could not post update to OpenHab: %s' % (e, ))


def basic_header():
    global gConfigurationOH

    auth = base64.encodestring('%s:%s'
                               % (gConfigurationOH['ohusername'], gConfigurationOH['ohpassword'])
                               ).replace('\n', '')
    return {
        "Authorization": "Basic %s" % auth,
        "Content-type": "text/plain"}


if __name__ == "__main__":
    configurationManager()
    gRequester = PyiCloudService(gConfigurationiCloud['username'], gConfigurationiCloud['password'])

    while 1:
        lat, long = getDeviceCoordinates()
        if calculateDistance(lat, long) == True:
            logging.info('User is in Geofence')
            postUpdate('ON')
        else:
            logging.info('User is outside of Geofence')
            postUpdate('OFF')
        time.sleep(int(gConfigurationOH['interval']))
