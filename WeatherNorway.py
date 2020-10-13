#/usr/bin/python3
import requests
import pandas as pd
from xml.dom import minidom
import prettytable
from io import StringIO

# Configuration
searchname = "Inner Oslofjord"
lat = "60.10"
lon = "9.58"

# API Endpoint 1 - textforecast

url = "https://api.met.no/weatherapi/textforecast/2.0/coast_en"

response = requests.request("GET", url)

weatherdata = response.text.encode('utf8')

"""
Example XML
<textforecast xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="https://schema.api.met.no/schemas/textforecast-0.3.xsd">
<meta licenseurl="https://www.met.no/en/free-meteorological-data/Licensing-and-crediting"/>
<time from="2020-10-13T18:00:00" to="2020-10-14T00:00:00">
<forecasttype name="normal">
<location name="Outer Skagerrak" id="0818">Northeast force 6. Mainly dry and good. Significant wave height: 1-2 m.</location>
<location name="Inner Skagerrak" id="0817">Northeast force 5. Dry. Good. Significant wave height: 0,5-1,5 m.</location>
</forecasttype>
<forecasttype name="normal">
<location name="Inner Oslofjord" id="0816">North and northeast force 1 to 4. Much fair weather. Good. Significant wave height: Insignificant.</location>
<location name="Swedish border - Lyngoer" id="51699">North and northeast up to force 5. Much fair weather. Good. Significant wave height: 0,5-1 m.</location>
"""

# https://stackoverflow.com/questions/45603446/how-to-get-inner-content-as-string-using-minidom-from-xml-dom
def getText(nodelist):
    # Iterate all Nodes aggregate TEXT_NODE
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
        else:
            # Recursive
            rc.append(getText(node.childNodes))
    return ''.join(rc)

xmldoc = minidom.parseString(weatherdata)

# Read date_time from XML
nodelist = xmldoc.getElementsByTagName("time")
for node in nodelist:
    date_time = node.getAttribute("from")
    print("Weather forecast - Based on data from MET Norway")
    print("Date/Time: " + date_time)
    break

# Read forecast for area named 'searchname'
nodelist = xmldoc.getElementsByTagName("location")
for node in nodelist:
    location_name = node.getAttribute("name")
    if location_name == searchname:
        print("Location: " + location_name)
        print("Forecast: " + getText(node.childNodes))
        break

# API Endpoint 2 - Weather at location

url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat="+lat+"&lon="+lon

response = requests.request("GET", url)

"""
Example JSON
{
	"type": "Feature",
	"geometry": {
		"type": "Point",
		"coordinates": [
			9.58,
			60.1,
			496
		]
	},
	"properties": {
		"meta": {
			"updated_at": "2020-10-12T16:51:07Z",
			"units": {
				"air_pressure_at_sea_level": "hPa",
				"air_temperature": "celsius",
				"cloud_area_fraction": "%",
				"precipitation_amount": "mm",
				"relative_humidity": "%",
				"wind_from_direction": "degrees",
				"wind_speed": "m/s"
			}
		},
		"timeseries": [
			{
				"time": "2020-10-12T16:00:00Z",
				"data": {
					"instant": {
						"details": {
							"air_pressure_at_sea_level": 1012.5,
							"air_temperature": 6.5,
							"cloud_area_fraction": 10.7,
							"relative_humidity": 94.5,
							"wind_from_direction": 55.4,
							"wind_speed": 0.9
						}
					},
"""

#read JSON data. Print Time and current weather details

weatherdata = response.json()["properties"]["timeseries"][0]
date_time = weatherdata["time"]
print()
print("Detailed forecast")
print("Time: " + date_time)
print("Latitude: " + lat)
print("Longitude: " + lon)

df = pd.json_normalize(weatherdata["data"]["instant"]["details"])

# https://stackoverflow.com/questions/18528533/pretty-printing-a-pandas-dataframe
output = StringIO()
df.to_csv(output)
output.seek(0)
print(prettytable.from_csv(output))
