# Weather-Forecast
Practice using Open-Meteo's public API, returning live JSON forecast data

[Open Meteo](https://open-meteo.com/en/docs) offers "Seamless integration of high-resolution weather models with up 16 days forecast."

# Install
```bash
pip install openmeteo-requests
pip install requests-cache retry-requests numpy pandas
```

Caching not implemented (needs to use requests-cache) but usually:
Requests get stored in a sqlite database file called .cache.sqlite
* add files such as .cache.sqlite to git ignores if you generated them

# Notes
Time zones were not converted to local times, so they default to GMT as per Open-Meteo doc
Forecast data is instead stored in forecast.db naively

