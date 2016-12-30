from pyicloud import PyiCloudService
import ConfigParser
import sys
import time
import argparse
import logging 
from iLocator import configurationManager, DEFAULT_LOGFILE, DEFAULT_CONFIG


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='iLocatorBridge - Bridge between iCloud location and OpenHAB')
    parser.add_argument(
        '-c', '--config', dest='config', default=DEFAULT_CONFIG,
        help='Config location (default: %s)' % (DEFAULT_CONFIG, ))
    parser.add_argument(
        '-v', '--verbose', dest='verbose', action='store_true',
        help='Be more verbose in the output')

    args = parser.parse_args()
    logging.basicConfig(
        filename=DEFAULT_LOGFILE, level=args.verbose and logging.DEBUG or logging.INFO,
        format='%(asctime)s %(message)s')

    gConfigurationiCloud, _, _ = configurationManager(args.config)
    api = PyiCloudService(gConfigurationiCloud['username'], gConfigurationiCloud['password'])

    if api.requires_2fa:
        print "Two-factor authentication required. Your trusted devices are:"

        devices = api.trusted_devices
        for i, device in enumerate(devices):
            print "  %s: %s" % (i, device.get('deviceName',
                "SMS to %s" % device.get('phoneNumber')))

        device = click.prompt('Which device would you like to use?', default=0)
        device = devices[device]
        if not api.send_verification_code(device):
            print "Failed to send verification code"
            sys.exit(1)

        code = click.prompt('Please enter validation code')
        if not api.validate_verification_code(device, code):
            print "Failed to verify verification code"
            sys.exit(1)
    else:
        print "2 Factor authentication not necessary"
    print "now run iLocator .. "



