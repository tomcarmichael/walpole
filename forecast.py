import requests
from datetime import date
from config import METEOMATICS_USERNAME, METEOMATICS_PWORD

todays_date = date.today().isoformat()
# Walpole Bay tidal pool longditude and latitude:
COORIDINATES = "51.3926103,1.3933696"


def calcuate_cardinal_direction(direction_in_degrees):
    # Wind direction is given in degrees from North. Eg. 45 == wind is coming from the Northeast.
    if direction_in_degrees in range(22,67):
        return "North East"
    elif direction_in_degrees in range(67,112):
        return "East"
    elif direction_in_degrees in range(112,157):
        return "South East"
    elif direction_in_degrees in range(157,202):
        return "South"
    elif direction_in_degrees in range(202,247):
        return "South West"
    elif direction_in_degrees in range(247,292):
        return "West"
    # Else, between 337.5 and 360 or between 0 and 22.5 == North
    else:
        return "North"


# Reference: https://www.meteomatics.com/en/api/getting-started/
def forecast():
    # If later adding functionality to do the same for 24 hours from now use:
    # tomo_to_last_hour = (datetime.now() + timedelta(hours=24)).replace(second=0, microsecond=0, minute=0).strftime("%Y-%m-%dT%H:%M:%S")
    # Querying for weather info on today's date 04:00 to 23:59 to cover all likely swim times:
    url = f"https://api.meteomatics.com/{todays_date}T04:00:00.000+00:00--{todays_date}T22:59:00.000+00:00:PT1H/wind_speed_10m:ms,wind_dir_10m:d,sunrise:sql,sunset:sql,weather_symbol_1h:idx,t_2m:C/{COORIDINATES}/json?model=mix"
    try:
        response = requests.get(url, auth=(METEOMATICS_USERNAME, METEOMATICS_PWORD))
    except requests.RequestException:
        return None

# Retrieving wind speed data:
    try:
        # "data" contains an array of the dfferent weather parameters in the order they were given in request URL
        # Save only the relevant data from request (an array of dictionaries):
        data = response.json()["data"]
    except (KeyError, TypeError, ValueError):
        return "JSON error - main request"

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

    # Initialise list to store wind direction values from throughout the day:
    wind_directions = []
    try:
        # Retrieve wind direction data, index [1] derived from position of paramter in request URL:
        for dict in data[1]["coordinates"][0]["dates"]:
            wind_directions.append(dict['value'])
        # Calculate the average windspeed over the given time period:
        avg_wind_direction = sum(wind_directions) / len(wind_directions)
    except (KeyError, TypeError, ValueError):
        return "JSON error"
    
    # Convert from an int (degrees from North) to a string of the cardinal direction eg. "East"
    wind_direction = calcuate_cardinal_direction(avg_wind_direction)

    # Retrieve today's sunrise time:
    try:
        sunrise = data[2]["coordinates"][0]["dates"][0]["value"][11:16]
    except (KeyError, TypeError, ValueError):
        return "JSON error"

    # Retrieve today's sunset time:
    try:
        sunset = data[3]["coordinates"][0]["dates"][0]["value"][11:16]
    except (KeyError, TypeError, ValueError):
        return "JSON error"

    # Weather symbol codes correspond to the file names of images in ./static/images/symbols/
    # Each index of the list corresponds to a subsequent hour of the day
    symbols = []
    try:
        # Rename "date" key to "time" and format it as such:
        for dict in data[4]["coordinates"][0]["dates"]:
            dict['symbol'] = dict.pop('value')
            # Convert from int to string and append to symbols list:
            symbols.append(str(dict['symbol']))
    except (KeyError, TypeError, ValueError):
        return "JSON error"

    # Retrieve temperatures at hourly intervals throught the day
    # Each index of the list corresponds to a subsequent hour of the day
    temperatures = []
    try:
        # Rename "date" key to "time" and format it as such:
        for dict in data[5]["coordinates"][0]["dates"]:
            dict['temp'] = dict.pop('value')
            temperatures.append(dict['temp'])
    except (KeyError, TypeError, ValueError):
        return "JSON error"

    hourly_forecast = [times, speeds, symbols, temperatures]
    return  hourly_forecast, wind_direction, sunrise, sunset
