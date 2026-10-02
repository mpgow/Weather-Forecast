import requests
# import pandas as pd # unused currently
import sqlite3
import sys

url = "https://api.open-meteo.com/v1/forecast"
api_key = None # no API key in this case, but not always true
params = {}
params["hourly"] = ["temperature_2m", "precipitation"]
# params["hourly"] = ["temperature_2m", "broken_precipitation_argument"] # For HTTP testing
params["current"] = ["temperature_2m"]

print("Let's get some basic temperature and precipitation facts for your location!\n")
units = input("Fahrenheit or Celsius?: {F | C}: ").upper()
while not units or units not in ["f", "c", "F", "C"]:
    units = input("Fahrenheit or Celsius?: {F | C}: ").upper()
if units == "F":
    params["temperature_unit"] = "fahrenheit"
while True:
    coords = input("Enter latitude and longitude as {±XX.XX} {±XXX.XX} or leave blank for San Diego: ")
# San Diego : (32.72, -117.16), McMurdo Station (Antarctica) : (-77.85, 166.67), Berkeley : (37.87, -122.27), Tokyo : (35.69, 139.69)
    if not coords:
        lat, lon = 32.72, -117.16
        params.update({
            "latitude" : lat,
            "longitude" : lon
        })
        break
    try:
        lat, lon = coords.split()
        lat, lon = float(lat), float(lon)
    except ValueError:
        print(f"please input a space separated pair of numbers; failed on input: {coords}")
        continue
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        print("Latitude must be -90 <= X <= 90 and longitude must be -180 <= Y <= 180")
        continue
    break

params.update({
    "latitude" : lat,
    "longitude" : lon
})

timeout_time = 5 # 5 seconds

try:
    responses = requests.get(url, params=params, timeout=timeout_time)
    responses.raise_for_status() # need to call for HTTP Error to be raised for 4XX/5XX errors
    jason = responses.json() # method, callable(responses.json) == True, returns a dict of the data
except requests.exceptions.HTTPError as errh: # following geeksforgeeks listed conventions
    print(f"HTTP Error: {errh.args[0]}") # full error message
    print(f"Status Code: {errh.response.status_code} {errh.response.text}")
    sys.exit(1) # signals an error occurred
except requests.exceptions.Timeout as errrt: # Timeout is parent of ConnectTimeout and ReadTimeout
    print(f"Timed out after {timeout_time} seconds")
    sys.exit(1)
except requests.exceptions.ConnectionError as conerr:
    print(f"Connection error, please check your internet access")
    sys.exit(1)
except requests.exceptions.JSONDecodeError:
    print("Server responded with invalid json data")
    sys.exit(1)
except requests.exceptions.RequestException as errex: # has to be last so more specific cases are caught first
    print(f"Exception request {errex}")
    sys.exit(1)


if responses.status_code == 200: # redundant but successful 200 code, HTTP's 4XX codes are client-side errors
    
    # Exploring data from get call

    print(f"url: {responses.url} \n")
    print(f"status code: {responses.status_code} \n")
    # print(f"text {responses.text[:]}\n")
    # print(f"directory: {dir(responses)} \n") # prints out the accessible API variables, but doesn't distinguish attr or methods

    # print(f"raw data: {jason}\n")
    # text = responses.text # atrribute, returns a string
    # print(text,"\n")
    try:
        keys = jason.keys()
        print(f" keys: {list(keys)} \n")
        hourly = jason["hourly"]
        hourly_units = jason["hourly_units"]
        current = jason["current"]
        current_units = jason["current_units"]
        API_lat, API_lon = jason["latitude"], jason["longitude"]
        print(f"current: {current} \n{current_units} \n")
        print(f"hourly: {hourly} \n{hourly_units} \n")
    except KeyError as e: # json mis-conversion is already handled above, so assume missing key
        print(f"Data is missing key: {e}")
        sys.exit(1)

    # basic data handling

    hourly_data = []
    for i in range(len(hourly["time"])):
        row = []
        for column in hourly.keys():
            row.append(hourly[column][i])
        hourly_data.append(row)

    # above is same as hourly data = [list(r) for r in zip(*hourly.values())]

    print(f"length of hourly data for 7 days of forecast: {len(hourly_data)} \n")
    print(f"first few hours: {hourly_data[0:5]}")
    print(f"values in order of: {list(hourly.keys())}")
    for time, temp, precip in hourly_data[:5]:
        print(f"time {time} temp {temp} precip {precip}")

    cnxn = None # Need to initialize cnxn so that if cnxn = sqlite.connect("...") fails, it doesn't crash at finally
    try: 
        cnxn = sqlite3.connect("forecast.db")
        cursor = cnxn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            time TEXT NOT NULL,
            temperature_2m REAL,
            precipitation REAL,
            PRIMARY KEY (latitude, longitude, time)
            )""")
        tagged_rows = []
        for row in hourly_data:
            tagged_rows.append([API_lat, API_lon, row[0], row[1], row[2]])
        # Need OR REPLACE to avoid crashing caused by UNIQUE constraints of primary key
        cursor.executemany("""INSERT OR REPLACE INTO weather (latitude, longitude, time, temperature_2m, precipitation) VALUES (?, ?, ?, ?, ?)""", tagged_rows)
        cnxn.commit()
        print(cnxn.execute("SELECT COUNT(*) FROM weather").fetchone())
        for row in cnxn.execute("SELECT * FROM weather ORDER BY RANDOM() LIMIT 67"):
            print(row)
    except sqlite3.Error as e:
        print(f"sqlite db error: {e}")
        sys.exit(1)
    finally:
        if cnxn: # if connect fails, nothing to close so exits normally
            cnxn.close()
else:
    print(f"Request failed. Error Code: {responses.status_code}")

# Error handling tests conducted:

# Tested incorrect parameters caused HTTP Error 400
# Tested running on the same location replaces old rows isntead of appending duplicates
# Tested running multiple new locations adds new rows to the same target database, without wiping previous query results
    # Note that sequential queries should all request to use the same unit of temperature for posterity


