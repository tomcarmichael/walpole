import requests
from datetime import date
from config import ADMIRALTY_API_KEY
from functions import shift_time

# Today's date to be used by several functions - but may not be necessary - check when implementation complete
todays_date = date.today().isoformat()


def tides():
    # Location ID: "MARGATE"
    location_id = "0103"
    # Documentation: https://admiraltyapi.portal.azure-api.net/docs/services/uk-tidal-api/operations/TidalEvents_GetTidalEvents?
    # No of days to fetch tidal data for:
    days = 1
    try:
        url = f"https://admiraltyapi.azure-api.net/uktidalapi/api/V1/Stations/{location_id}/TidalEvents?{days}"
        response = requests.get(url, headers={"Ocp-Apim-Subscription-Key": ADMIRALTY_API_KEY})
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
    

# Takes the array of dicts returned by tides() & calculates times when it's NOT possible to swim in the Tidal Pool
def no_swim_times(tides):
    # Check whether a string has been passed to method, indicating a Request Exception in Admiralty API request:
    if (isinstance(tides, str)):
        return
    # Create 2D array to store start and end times of no swim periods that occur twice daily around high tide
    no_swim_periods = []
    # Check each dictionary in the array for High Tide entries
    for dict in tides:
        if dict["EventType"] == "High Tide":
            # Using shift_time defined in functions.py
            no_swim_periods.append([shift_time(dict["Time"], -2), shift_time(dict["Time"], 2)])
    return no_swim_periods




