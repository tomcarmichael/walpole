import requests
from datetime import date
from config import METEOMATICS_USERNAME, METEOMATICS_PWORD

todays_date = date.today().isoformat()
# Tidal pool longditude and latitude
COORIDINATES = "51.3926103,1.3933696"

def forecast():
    # If later adding functionality to do the same for 24 hours from now:
    # tomo_to_last_hour = (datetime.now() + timedelta(hours=24)).replace(second=0, microsecond=0, minute=0).strftime("%Y-%m-%dT%H:%M:%S")
    # Querying for wind info on today's date 04:00 to 23:59. Returns in metres/second
    url = f"https://api.meteomatics.com/{todays_date}T04:00:00.000+00:00--{todays_date}T22:59:00.000+00:00:PT1H/wind_speed_10m:ms,wind_dir_10m:d,sunrise:sql,sunset:sql,weather_symbol_1h:idx,t_2m:C/{COORIDINATES}/json?model=mix"
    try:
        response = requests.get(url, auth=(METEOMATICS_USERNAME, METEOMATICS_PWORD))
    except requests.RequestException:
        return None

# Retrieving wind speed data
    try:
        # "data" contains an array where each element contains the info for a dfferent weather parameter...
        # ...in the order they were given in URL request
        # Save only the relevant data from API request (returns an array of dictionaries)
        data = response.json()["data"]
    except (KeyError, TypeError, ValueError):
        return "JSON error - whole request"

    times = []
    speeds = []
    try:
        # Rename "date" key to "time" and format it as such
        for dict in data[0]["coordinates"][0]["dates"]:
            dict['time'] = dict.pop('date')[11:16]
            # Rename "value" to "speed" and convert metres/second to MPH
            dict['wind speed'] = round(dict.pop('value') * 2.23694, 2)
            times.append(dict['time'])
            speeds.append(dict['wind speed'])

    except (KeyError, TypeError, ValueError):
        return "JSON error - time and wind speed"

    # Wind direction given in degrees from North. Eg. a direction of 45 degrees means that wind is coming from the Northeast.
    avg_wind_direction = 0

    try:
        # Retrieving wind direction data which is at ["data"][1]
        for dict in data[1]["coordinates"][0]["dates"]:
            # Would execution time be more optimised by adding these to an empty array so that counting the length of that array is quicker (doesn't include datetime keys/values?)
            avg_wind_direction += dict['value']
        # Calculate the average windspeed over the given time period
        avg_wind_direction /= len(data)

    except (KeyError, TypeError, ValueError):
        return "JSON error"

    # If between 22.5 and 67.5 = North East. 67.5 and 112.5 = East 112.5 and 157.5 = South East . 157.5 and 202.5 = South.
    # 202.5 and 247.5 = South West. 247.5 and 292.5 = West 292.5 and 337.5 = North West 337.5 and 360 = North AND 0 and 22.5 = North
    if avg_wind_direction in range(22,67):
        wind_direction = "North East"
    elif avg_wind_direction in range(67,112):
        wind_direction = "East"
    elif avg_wind_direction in range(112,157):
        wind_direction = "South East"
    elif avg_wind_direction in range(157,202):
        wind_direction = "South"
    elif avg_wind_direction in range(202,247):
        wind_direction = "South West"
    elif avg_wind_direction in range(247,292):
        wind_direction = "West"
    else:
        wind_direction = "North"

    try:
        sunrise = data[2]["coordinates"][0]["dates"][0]["value"][11:16]
    except (KeyError, TypeError, ValueError):
        return "JSON error"

    try:
        sunset = data[3]["coordinates"][0]["dates"][0]["value"][11:16]
    except (KeyError, TypeError, ValueError):
        return "JSON error"

    symbols = []
    try:
        # Rename "date" key to "time" and format it as such
        for dict in data[4]["coordinates"][0]["dates"]:
            dict['symbol'] = dict.pop('value')
            symbols.append(str(dict['symbol']))

    except (KeyError, TypeError, ValueError):
        return "JSON error"

    temperatures = []
    try:
        # Rename "date" key to "time" and format it as such
        for dict in data[5]["coordinates"][0]["dates"]:
            dict['temp'] = dict.pop('value')
            temperatures.append(dict['temp'])

    except (KeyError, TypeError, ValueError):
        return "JSON error"

    hourly_forecast = [times, speeds, symbols, temperatures]
    return  hourly_forecast, wind_direction, sunrise, sunset
