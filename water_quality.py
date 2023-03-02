import requests
from sample_classification import classify_sample
from functions import reformat


def water_quality():
    # No API key required
    url = "https://environment.data.gov.uk/doc/bathing-water/ukj4210-12630.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return "Request Exception"
    try:
        # Create dictionary with only the relevant data
        data = response.json()["result"]["primaryTopic"]
        # A reference to the most recently available short-term pollution risk:
        risk_prediction = data["latestRiskPrediction"]['riskLevel']['name']['_value']
        # Associated expiry date for risk prediction as "YYYY-MM-DD":
        risk_prediction_expiry = data["latestRiskPrediction"]["expiresAt"]['_value'][0:10]
        # A boolean valued indicator of whether water quality is adversely affected by heavy rainfall:
        heavy_rain_warning = data["waterQualityImpactedByHeavyRain"]
        # The most recent annual compliance assessment - either "excellent", "good", "sufficient" or "poor"
        latest_compliance_assessment = data["latestComplianceAssessment"]['complianceClassification']['name']['_value']
        # To access date of last annual compliance assessment...
        # ... "_about" key stores a URL to another API request
        compliance_date_api = data["latestComplianceAssessment"]["_about"]
        compliance_date_response = requests.get(f"{compliance_date_api}.json")
        # Date returned as YYYY-MM-DD
        latest_compliance_date = compliance_date_response.json()["result"]["primaryTopic"]["finalSampleDate"]["_value"]
        # Retrieve information relating to latest in-season water sample taken by the Environment Agency:
        # "latestSampleAssessment" key returns a URL to another API request
        latest_sample_api = data["latestSampleAssessment"]
        latest_sample_response = requests.get(f"{latest_sample_api}.json")
        # Returns dictionary containing levels of Ecoli and intestinal Enterococci:
        latest_sample_data = latest_sample_response.json()["result"]["primaryTopic"]
        # Date of the most recent water sample in question as "YYYY-MM-DD":
        latest_sample_date = latest_sample_data["sampleDateTime"]["inXSDDateTime"]["_value"][0:10]

        # Returned from API as an int:
        ec_count = latest_sample_data["escherichiaColiCount"]
        # Returned from API as a string either '<' '=' '>'
        ec_qualifier = latest_sample_data["escherichiaColiQualifier"]["countQualifierNotation"]
        # Returned from API as an int:
        ie_count = latest_sample_data["intestinalEnterococciCount"]
        # Returned from API as a string either '<' '=' '>'
        ie_qualifier = latest_sample_data["intestinalEnterococciQualifier"]["countQualifierNotation"]
        # Calculate the classification of the latest water quality sample:
        latest_sample_classification = classify_sample(ec_count, ec_qualifier, ie_count, ie_qualifier)

    except (KeyError, TypeError, ValueError):
        return "JSON error"

    # Return dict, values are strings. Dates reformatted to UK format with reformat() defined in functions.py
    water_quality = {"risk_prediction": risk_prediction, "risk_prediction_expiry": reformat(risk_prediction_expiry), 
    "heavy_rain_warning": heavy_rain_warning, "latest_compliance_assessment": latest_compliance_assessment,
    "latest_compliance_date": reformat(latest_compliance_date), "latest_sample_date": reformat(latest_sample_date),
    "latest_sample_classification": latest_sample_classification}
    return water_quality