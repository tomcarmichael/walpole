"""
UK Environment Agency water quality classifications are as follows =>
Excellent	EC: ≤250 cfu/100ml ; IE: ≤100 cfu/100ml (95th percentile)
Good	EC: ≤500 cfu/100ml ; IE: ≤200 cfu/100ml (95th percentile)
Sufficient	EC: ≤500 cfu/100ml ; IE: ≤185 cfu/100ml (90th percentile)
Poor	means that the values are worse than the sufficient
https://environment.data.gov.uk/bwq/profiles/help-understanding-data.html
"""

# Takes Ecoli count and intestinal Enterococci count as ints, qualififers as a str either '<' '=' or '>'
def classify_sample(ec_count, ec_qualifier, ie_count, ie_qualifier):
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