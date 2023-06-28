# Walpole Bay Tidal Pool community resource website

A website for sea swimmers who use the Walpole Bay Tidal Pool in Margate, Kent. Built to address the problem of needing to visit multiple different websites to check the tide times, weather conditions, and water pollution levels on any given day before heading out for a swim.

Built using Python and [Flask](https://flask.palletsprojects.com/en/2.2.x/), with the [Bootstrap](https://getbootstrap.com/) framework for styling.

![Walpole Bay Tidal Pool](https://haeckels.co.uk/wp-content/uploads/2018/07/walpole.haeckels-768x553.jpg)

## Getting started

`git clone https://github.com/tomcarmichael/walpole.git`

Activate the virtual environment:

`source ./venv/bin/activate`

Install dependencies:

`pip install -r requirements.txt`

To start the development server:

`flask run`

Alternatively to start the gunicorn server for deployment:

`gunicorn app:app`

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

## sample_classification.py

Defines the `classify_sample` function, which is passed data received from the Bathing Water API relating to the most recent water quality tests carried out by the Environment Agency. These tests are conducted regularly from the *start of May* till the *end of September*. The function determines and returns the correct classification for the water quality based on the Ecoli and intestinal Enterococci count as per the [Enviroment Agency's specifications](https://environment.data.gov.uk/bwq/profiles/help-understanding-data.html).

## tides.py

Queries the [UK Tidal API](https://admiraltyapi.portal.azure-api.net/docs/services/uk-tidal-api/operations/Stations_GetStation), filtering the returned JSON data to contain only the tidal information for today's date. The `no_swim_times` function calculates at what times during the day the Walpole Bay Tidal Pool will be inaccessable, because between approximately 2 hours before and after high tide, the water level comes over the walls of the pool.

## forecast.py

Queries the [meteomatics weather API](https://www.meteomatics.com/en/api/available-parameters/#api-basic) and filters the returned JSON data to ascertain, for today's date, the sunrise and sunset times, temperature, weather symbols, wind speeds and wind directions throughout the day. The wind speeds are used to render a graph on the home page of the website. The `calcuate_cardinal_direction` function in `forecast.py` returns a string indicating if the wind is, on average, mostly 'North' / 'South' / 'South-East' / etc. facing throughout the day. Walpole Bay Tidal Pool is on a North-facing part of the coastline and so is most exposed to wind blowing in a Southern direction. This is reflected on the home page of the website with a message giving information to the user about the likely impact of the wind speed and direction that day for swimmers.

Weather symbol codes that are provided by the meteomatics API are used to render corresponding images that are stored in [./static/images/symbols](static/images/symbols).

## functions.py

Defines some general purpose functions for use throughout the application including using the [Matplotlib](https://matplotlib.org/) Python library to generate a graph of the windspeed in MPH over the course of the day, a function to reformat the date from US formatting to UK formatting, and a function to check whether today's date is within the annual testing season for water quality samples, as explained above.

## app.py

Contains some configuration for the Flask app, makes calls to the functions defined in the aforementioned files and defines two routes, passing the data returned from the function calls to the `/` route. The `/resources` route renders a static page containing relevant links to other websites.

## templates/index.html

Implements Jinja logic to display the weather and tidal data to the user. Data related to in-season water quality testing is only displayed if the user is visiting the website during the testing season.

> Dependencies are specified in `./requirements.txt`.
> 
> See `./bathing-water-quality.ttl` for more information on the data provided by the UK Gov Environment Agency regarding water quality.
> 
> Bootstrap files for styling are included within `./static`

# Reflections on design and implementation

Though only comprising of a front end, this was the first substantial website that I built from scratch, as my final project for Harvard University's [CS50x course](https://cs50.harvard.edu/x/2023/). My knowledge of Python, and of writing high quality code more generally, was very limited compared to where it is now (approximately six months on from when I first created the website). Functions are long, there is no use of OOP, and too much commenting. Were I to begin this project again, I would look to improve upon its design, using OOP principles, and to write more concise and self-documenting functions.
