import requests

"""
Water quality classifications =>
Excellent	EC: ≤250 cfu/100ml ; IE: ≤100 cfu/100ml (95th percentile)
Good	EC: ≤500 cfu/100ml ; IE: ≤200 cfu/100ml (95th percentile)
Sufficient	EC: ≤500 cfu/100ml ; IE: ≤185 cfu/100ml (90th percentile)
Poor	means that the values are worse than the sufficient
https://environment.data.gov.uk/bwq/profiles/help-understanding-data.html
"""

# Takes ec_count and ie_count as integers, qualififers as a str either '<' '=' or '>'
def latest_sample_class(ec_count, ec_qualifier, ie_count, ie_qualifier):
    # Evaluate E Coli level classification
    if ec_qualifier == '<':
        if ec_count <= 250:
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
        if ec_count <= 250:
            ec = "Excellent"
        elif ec_count <= 500:
            ec = "Good or Sufficient"
        else:
            ec = "Poor"
    # Evaluate intestinal Enterococci level classification
    if ie_qualifier == '<':
        if ie_count <= 100:
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
        if ie_count <= 100:
            ie = "Excellent"
        elif ie_count <= 200:
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