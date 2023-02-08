
import requests
from datetime import date, timedelta, datetime
from dotenv import load_dotenv
import os

# Load hidden API Keys
load_dotenv()

# Today's date to be used by several functions - but may not be necessary - check when implementation complete
todays_date = date.today().isoformat()

# Tidal pool longditude and latitude
COORIDINATES = "51.3926103,1.3933696"


def tides():
    # Location ID: "MARGATE"
    location_id = "0103"
    # Documentation: https://admiraltyapi.portal.azure-api.net/docs/services/uk-tidal-api/operations/TidalEvents_GetTidalEvents?
    # No of days to fetch tidal data for:
    days = 1
    try:
        url = f"https://admiraltyapi.azure-api.net/uktidalapi/api/V1/Stations/{location_id}/TidalEvents?{days}"
        response = requests.get(url, headers={"Ocp-Apim-Subscription-Key":os.getenv("ADMIRALTY_API_KEY")})
        response.raise_for_status()
    except requests.RequestException:
        return "Request Exception"

    try:
        full_json = response.json()
        tides = []
        # Iterate through the array of dictionaries returned in JSON format
        for dict in full_json:
            # Select those that match today's date (should be 2 high tides & 2 low tides)
            if dict["Date"][0:10] == todays_date:
                # Reformat DateTime to HH:MM and copy to new key Time
                dict["Time"] = dict["DateTime"][11:16]
                # Delete unnecessary key/value pairs
                del dict["IsApproximateTime"], dict["Height"], dict["IsApproximateHeight"], dict["Filtered"], dict["Date"], dict["DateTime"]
                # Rename Tide Types to more readable names
                if dict["EventType"] == "LowWater":
                    dict["EventType"] = "Low Tide"
                elif dict["EventType"] == "HighWater":
                    dict["EventType"] = "High Tide"
                tides.append(dict)
        return tides
    except (KeyError, TypeError, ValueError):
        return "JSON error"


# Function that takes HH:MM formatted string and shifts it forward or back by given number of hours
# Use a positive int to shift forward, negative to shift back
def shift_time(intime, hours):
    outtime = datetime.strptime(intime, "%H:%M") + timedelta(hours=hours)
    return outtime.strftime("%H:%M")


# Function that takes the array of dictionaries returned by tides() and calculates times when it's NOT possible to swim in the Tidal Pool
def swim_times(tides):

    # Create 2D array store start and end times of no swimming periods that occur twice daily around high tide
    no_swim_periods = []
    # Check each dictionary in the array for High Tide entries
    for dict in tides:
        if dict["EventType"] == "High Tide":
            no_swim_periods.append([shift_time(dict["Time"], -2), shift_time(dict["Time"], 2)])
    return no_swim_periods


def forecast():
    # API: https://www.meteomatics.com/en/weather-api/#api-packages

    # Example API request URL = https://api.meteomatics.com/2023-01-31T11:40:00.000+00:00/t_2m:C/51.3926103,1.3933696/html?model=mix

    # Retrieve the current date and time, rounded down to the last hour, and format for API request
    # now_to_last_hour = datetime.now().replace(second=0, microsecond=0, minute=0).strftime("%Y-%m-%dT%H:%M:%S")

    # Do the same for 24 hours from now
    # tomo_to_last_hour = (datetime.now() + timedelta(hours=24)).replace(second=0, microsecond=0, minute=0).strftime("%Y-%m-%dT%H:%M:%S")

    # Querying for wind info on today's date 04:00 to 23:59. Returns in metres/second
    url = f"https://api.meteomatics.com/{todays_date}T04:00:00.000+00:00--{todays_date}T22:59:00.000+00:00:PT1H/wind_speed_10m:ms,wind_dir_10m:d,sunrise:sql,sunset:sql,weather_symbol_1h:idx,t_2m:C/{COORIDINATES}/json?model=mix"

    try:
        response = requests.get(url, auth=(os.getenv("METEOMATICS_USERNAME"), os.getenv("METEOMATICS_PWORD")))
    except requests.RequestException:
        return None

# Retrieving wind speed data
    try:
        # "data" contains an array where each element contains the info for a dfferent weather parameter, in the order they were given in URL request
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

    # Wind direction given in degrees from North. For example, a direction of 45 degrees means that the wind is coming from the Northeast.
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


def water_quality():
    url = "https://environment.data.gov.uk/doc/bathing-water/ukj4210-12630.json"
    # TO DO : add data["latestSampleAssessment"] - provides a string that is a link to another API, need to append with .json
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return "Request Exception"
    try:
        data = response.json()["result"]["primaryTopic"]
        risk_prediction = data["latestRiskPrediction"]['riskLevel']['name']['_value']
        heavy_rain_warning = data["waterQualityImpactedByHeavyRain"]
        latest_compliance_assessment = data["latestComplianceAssessment"]['complianceClassification']['name']['_value']
        # Retrieving the date of the latest annual water quality clsasification (excellent/good/sufficient) and adding to dict
        # "about" key stores link to another API requests
        compliance_date_api = data["latestComplianceAssessment"]["_about"]
        compliance_date_response = requests.get(f"{compliance_date_api}.json")
        latest_compliance_date = compliance_date_response.json()["result"]["primaryTopic"]["finalSampleDate"]["_value"]
    except (KeyError, TypeError, ValueError):
        return "JSON error"
    water_quality = {"risk_prediction": risk_prediction, "heavy_rain_warning": heavy_rain_warning, "latest_compliance_assessment": latest_compliance_assessment, "latest_compliance_date": latest_compliance_date}
    return water_quality

