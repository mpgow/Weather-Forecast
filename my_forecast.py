import requests
import pandas as pd
import sqlite3

url = "https://api.open-meteo.com/v1/forecast"
api_key = None # no API key in this case, but not always true
params = {}
params["hourly"] = ["temperature_2m", "precipitation"]
# params["hourly"] = ["temperature_2m", "broken_precipitation_argument"] # For HTTP testing
params["current"] = ["temperature_2m"]

print("Let's get some basic temperature and precipitation facts for your location!\n")
units = input("Fahrenheit or Celsius?: {F | C}: ")
while not units or units not in ["F", "C"]:
    units = input("Fahrenheit or Celsius?: {F | C}: ")
if units == "F":
    params["temperature_unit"] = "fahrenheit"
coords = input("Enter latitude and longitude as {±XX.XX} {±XXX.XX} or leave blank for San Diego: ")
if not coords:
    params.update({
        "latitude" : 32.7,
        "longitude" : -117.16
    })
else:
    try:
        coords = coords.split()
        params.update({
            "latitude" : float(coords[0]),
            "longitude" : float(coords[1])
        })
    except:
        print(f"No correction implemented, failed on input: {coords}")

try:
    responses = requests.get(url, params=params, timeout=5)
    responses.raise_for_status() # need to call for HTTP Error to be raised for 4XX/5XX errors
except requests.exceptions.HTTPError as errorHTTP: # TODO: catching other error types that exist
    print(f"Request failed. Error Code: {errorHTTP.args[0]}")
    exit()
if responses.status_code == 200: # redundant but successful 200 code, HTTP's 4XX codes are client-side errors
    
    # Exploring data from get call

    print(f"url: {responses.url} \n")
    print(f"status code: {responses.status_code} \n")
    # print(f"text {responses.text[:]}\n")
    print(f"directory: {dir(responses)} \n") # prints out the accessible API variables, but doesn't distinguish attr or methods
    jason = responses.json() # method, callable(responses.json) == True, returns a dict
    # print(f"raw data: {jason}\n")
    # text = responses.text # atrribute, returns a string
    # print(text,"\n")
    keys = jason.keys()
    print(f" keys: {list(keys)} \n")
    current = jason["current"]
    current_units = jason["current_units"]
    hourly = jason["hourly"]
    hourly_units = jason["hourly_units"]
    print(f"current: {current} \n{current_units} \n")
    print(f"hourly: {hourly} \n{hourly_units} \n")

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
        tagged_rows.append([params["latitude"], params["longitude"], row[0], row[1], row[2]])

    # Need OR REPLACE to avoid crashing caused by UNIQUE constraints of primary key
    cursor.executemany("""INSERT OR REPLACE INTO weather (latitude, longitude, time, temperature_2m, precipitation) VALUES (?, ?, ?, ?, ?)""", tagged_rows)
    cnxn.commit()

    print(cnxn.execute("SELECT COUNT(*) FROM weather").fetchone())
    for row in cnxn.execute("SELECT * FROM weather ORDER BY RANDOM() LIMIT 67"):
        print(row)
    cnxn.close()
else:
    print(f"Request failed. Error Code: {responses.status_code}")

# Error handling tests conducted:

# Tested incorrect parameters caused HTTP Error 400
# Tested running on the same location replaces old rows isntead of appending duplicates
# Tested running multiple new locations adds new rows to the same target database, without wiping previous query results
    # Note that sequential queries should all request to use the same unit of temperature for posterity


