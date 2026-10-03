# Weather-Forecast
Practice using Open-Meteo's public API, returning live JSON forecast data

[Open Meteo](https://open-meteo.com/en/docs) offers "Seamless integration of high-resolution weather models with up [to] 16 days forecast."

This program accepts user input to select a location via Latitudinal and Longitudinal decimal coordinates. After inputs are verified, the program sends a GET request to Open-Meteo, handles if any errors, then passes on data to a SQLite database. Each row represents a temperature (stored in the user's preferred unit) and precipitation forecast, keyed by latitude, longitude, and time. For clarity, a random subset of rows are printed in the terminal so users may inspect the collected rows contain the desired query results.

# Install

Caching not implemented (needs to use requests-cache) but usually:
Requests get stored in a sqlite database file called .cache.sqlite
* add files such as .cache.sqlite to git ignores if you generated them

Not in use:
```bash
pip install openmeteo-requests
pip install requests-cache retry-requests numpy pandas
```

# Notes
Time zones were not converted to local times, so they default to GMT as per Open-Meteo doc
Forecast data is instead stored in forecast.db naively

If you select the wrong temperature, re-run the query with the correct units selected and it will overwrite the location's temperature values (keyed on the grid-locked coordinates that Open-Meteo returns in its response)

