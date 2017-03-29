<span class="badge-paypal"><a href="https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=F5UAFVHBPQWXQ" title="Donate to this project using Paypal"><img src="https://img.shields.io/badge/paypal-donate-yellow.svg" alt="PayPal donate button" /></a></span>
<span class="badge-bitcoin"><a href="http://i.imgur.com/wGR65b3.png" title="Donate once-off to this project using Bitcoin"><img src="https://img.shields.io/badge/bitcoin-donate-yellow.svg" alt="Bitcoin donate button" /></a></span>


# iLocatorBridge

Bridge between iCloud location and OpenHAB

Install:

1. Download and install (Needed for connecting to iCloud) https://github.com/picklepete/pyicloud
 
2. Edit configuration.ini to provide:
    - iCloud credentials & device(s), under the [iCloud] section
    - Geofence settings, under the [Geofencexxx] section
    - OpenHAB credentials & item(s), under the [OpenHAB] section
    
3. Run python iLocator.py



Notes regarding configuration.ini:

1. Support has been added for additional units of measure. You may now choose between m (meters), km (Kilometers), ft (feet), mi (miles) or nm (nautical miles).

2. Dynamic/Adaptive polling has been added for each Geofence.  You provide a polling map that defines the polling rate within set distances from the POI.  As your location changes, the poll time will adjust.  The map is a comma-seperated key-value pair in the format "distance1=interval1,distance2=interval2, etc", beginning with the shortest distance first. An example polling map would be 100=300,1000=10,1001=60 which translates to (within 100 ft poll @ 300 sec, else within 1000ft poll @ 10 sec, else poll at 60 sec).  See configuration.ini for additional examples.
    * If you do NOT want to take advantage of adaptive polling, you can simply enter 0=60 to poll every 60 seconds, or 0=300 to poll every 5 minutes, etc.
    * Polling maps are provided at the Geofence level so if you have more than one Geofence configured, the bridge will compare the polling maps for the current distance and use the lesser of all the polling intervals.  This ensures that the shortest interval is enforced.

3. In addition to updating a "Presence" item in OpenHAB, the bridge now provides functionality for posting additional information back to OpenHAB including Current Distance, Current Polling Rate & Next Poll Time.  All three of these are optional and do not need to be confiugured if you shoose not to use them.

    - OHItem & OHItem_Presence are configured inside the Geofence settings as these are specific to each Geofence.
    - OHItem_PollingRate & OHItem_NextPollTime are configured inside the OpenHAB settings as these are global and apply to all Geofences.
