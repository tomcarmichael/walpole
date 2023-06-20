# Walpole Bay Tidal Pool community resource website

A website for sea swimmers who use the Walpole Bay Tidal Pool in Margate, Kent.

Built using Python and [Flask](https://flask.palletsprojects.com/en/2.2.x/), with the [Bootstrap](https://getbootstrap.com/) framework.

![Walpole Bay Tidal Pool](https://haeckels.co.uk/wp-content/uploads/2018/07/walpole.haeckels-768x553.jpg)

## Getting started

`git clone https://github.com/tomcarmichael/walpole.git`

Activate the virtual environment:

`source ./venv/bin/activate`

Install dependencies:

`pip install -r requirements.txt`

Start the development server:

`flask run`

Open the link to the local server displayed in the terminal in your browser.

[./forecast.py](./forecast.py) uses the [meteomatics weather API](https://www.meteomatics.com/en/api/available-parameters/#api-basic) (the basic, free tier).

The API key for this is stored in `./config.py`, which is included in [.gitignore](.gitignore), so it is necessary to [register for a free tier meteomatics API account](https://www.meteomatics.com/en/sign-up-weather-api-free-basic-account/), run:

`touch ./config.py`

And add your username and password to config.py using the format:

``` python
# Meteomatics API login information - basic free tier account
METEOMATICS_USERNAME = ""
METEOMATICS_PWORD = ""
```

[./tides.py](./tides.py) uses the free [UK Tidal API - Discovery](https://admiraltyapi.portal.azure-api.net/docs/services/uk-tidal-api/operations/Stations_GetStation) from the UK Hydrographic Office's Admiralty website. This is limited to 10,000 calls per month.

It will be neccesary to [create an account](https://admiraltyapi.portal.azure-api.net/) and sign up for the Discovery level UK Tidal API on the Admiralty website, then add the your API key to config.py as follows:

```
# Admiralty API Key for tidal info:
ADMIRALTY_API_KEY = ""
```

## water_quality.py

Pulls water quality / pollution data from the UK Gov Environment Agency's free [Bathing Water API](https://environment.data.gov.uk/doc/bathing-water/ukj4210-12630.json)

## sample_classification.py

Defines the `classify_sample` function, which is passed data received from the Bathing Water API relating to the most recent water quality tests carried out by the Environment Agency. These tests are conducted regularly from the *start of May* till the *end of September*. 

index.html implements Jinja logic to display data related to in season testing only if the user is visiting the website during the season.

> See `./bathing-water-quality.ttl` for more information on the data provided by the UK Gov Environment Agency regarding water quality.

## functions.py

Defines some general purpose functions for use throughout the application including using the Matplotlib Python library to generate a graph of the windspeed in MPH over the course of the day, a function to reformat the date from US formatting to UK formatting, and a function to check whether today's date is within the annual testing season, as explained above. 

**bootstrap files for styling are included within ./static**