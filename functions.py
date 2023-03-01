import requests
from datetime import date, timedelta, datetime
from config import ADMIRALTY_API_KEY, METEOMATICS_USERNAME, METEOMATICS_PWORD

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
    

"""
Excellent	EC: ≤250 cfu/100ml ; IE: ≤100 cfu/100ml (95th percentile)
Good	EC: ≤500 cfu/100ml ; IE: ≤200 cfu/100ml (95th percentile)
Sufficient	EC: ≤500 cfu/100ml ; IE: ≤185 cfu/100ml (90th percentile)
Poor	means that the values are worse than the sufficient

https://environment.data.gov.uk/bwq/profiles/help-understanding-data.html
"""

# Takes count as an int, qualififer as a str either '<' '=' '>'
def latest_sample_class(ec_count, ec_qualifier, ie_count, ie_qualifier):
    # Evaluate E Coli level classification
    if ec_qualifier == '<':
        if ec_count < 251:
            ec = "Excellent"
        # if ec count given as less than 251 we cannot be sure if it is excellent or good.
        else:
            ec = "Unknown"
    elif ec_qualifier == '>':
        if ec_count > 500:
            ec = "Poor"
        # if ec count given as greater than any number less than 500 we cannot be sure if it is poor or better.
        else:
            ec = "Unknown"
    else:
        if ec_count < 251:
            ec = "Excellent"
        elif ec_count < 501:
            ec = "Good or Sufficient"
        else:
            ec = "Poor"
    # Evaluate intestinal Enterococci level classification
    if ie_qualifier == '<':
        if ie_count < 101:
            ie = "Excellent"
        # if ie count given as less than 201 we cannot be sure if it is excellent or good.
        else:
            ie = "Unknown"
    elif ie_qualifier == '>':
        if ie_count > 185:
            ie = "Poor"
        # if ie count given as greater than any number less than 500 we cannot be sure if it is poor or better.
        else:
            ie = "Unknown"
    else:
        if ie_count < 101:
            ie = "Excellent"
        elif ie_count < 201:
            ie = "Good or Sufficient"
        else:
            ie = "Poor"
    # Evaluate the overall water quality classification
    if ec == "Poor" or ie == "Poor":
        return "Poor"
    elif ec == "Good or Sufficient" or ie == "Good or Sufficient":
        return "Good or Sufficient"
    elif ec == "Excellent" and ie == "Excellent":
        return "Excellent"
    else:
        return "Unknown"


def water_quality():
    # No API key required
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
        risk_prediction_expiry = data["latestRiskPrediction"]["expiresAt"]['_value'][0:10]
        # Return a boolean:
        heavy_rain_warning = data["waterQualityImpactedByHeavyRain"]
        latest_compliance_assessment = data["latestComplianceAssessment"]['complianceClassification']['name']['_value']
        # Retrieving the date of the latest annual water quality clsasification (excellent/good/sufficient/poor) and adding to dict
        # "about" key stores link to another API requests
        compliance_date_api = data["latestComplianceAssessment"]["_about"]
        compliance_date_response = requests.get(f"{compliance_date_api}.json")
        latest_compliance_date = compliance_date_response.json()["result"]["primaryTopic"]["finalSampleDate"]["_value"]
        #####
        # Retrieve infomration relating to latest in-season sample taken by Environment Agency
        # The key given as first argument returns a URL
        latest_sample_api = data["latestSampleAssessment"]
        latest_sample_response = requests.get(f"{latest_sample_api}.json")
        # latest_sample_data = latest_sample_response.json()["result"]["primaryTopic"]
        latest_sample_data = latest_sample_response.json()["result"]["primaryTopic"]
        # sampleDateTime given as "2022-09-22T12:06:00"
        latest_sample_date = latest_sample_data["sampleDateTime"]["inXSDDateTime"]["_value"][0:10]

        # Returned from API as an int
        ec_count = latest_sample_data["escherichiaColiCount"]
        # Returned from API as a string either '<' '=' '>'
        ec_qualifier = latest_sample_data["escherichiaColiQualifier"]["countQualifierNotation"]
        # Returned from API as an int
        ie_count = latest_sample_data["intestinalEnterococciCount"]
        # Returned from API as a string either '<' '=' '>'
        ie_qualifier = latest_sample_data["intestinalEnterococciQualifier"]["countQualifierNotation"]
        # Calculating the classification of the latest water quality sample
        latest_sample_classification = latest_sample_class(ec_count, ec_qualifier, ie_count, ie_qualifier)


    except (KeyError, TypeError, ValueError):
        return "JSON error"


    water_quality = {"risk_prediction": risk_prediction, "risk_prediction_expiry": risk_prediction_expiry, 
    "heavy_rain_warning": heavy_rain_warning, "latest_compliance_assessment": latest_compliance_assessment,
    "latest_compliance_date": latest_compliance_date, "latest_sample_date": latest_sample_date,
    "latest_sample_classification": latest_sample_classification}

    return water_quality

