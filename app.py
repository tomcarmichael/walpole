from flask import Flask, render_template
from tides import tides, no_swim_times
from forecast import forecast
from water_quality import water_quality
from functions import plotView, check_if_in_season
from datetime import date

# Configure application
app = Flask(__name__)
# Ensure templates are auto-reloaded when running flask app and making changes on the fly
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Return weather forecast info, format= [hourly_forecast=[times, speeds, symbols, temperatures], wind_direction, sunrise, sunset]]
weather_info = forecast()


@app.route("/")
def index():
    tide_info = tides()
    pollution = water_quality()
    # If weather_info has not returned an error message:
    if not (isinstance(weather_info, str)):
        # Retrieve wind speed at 13:00 as indicator for the day
        wind_speed_int = int(weather_info[0][1][9])
        # Generate graph with time in hours, speeds in MPH, taking every other value (every 2 hours)
        wind_plot = plotView(weather_info[0][0][::2], weather_info[0][1][::2])
    # Check if today's date is in season for regular water quality testing, returned as a bool:
    in_testing_season = check_if_in_season(date.today())
    return render_template("index.html", tides=tide_info, swim_times=no_swim_times(tide_info), wind_plot=wind_plot, wind_speed_int=wind_speed_int,
    weather_info=weather_info, pollution=pollution, in_testing_season=in_testing_season)


@app.route("/resources")
def resources():
    return render_template("resources.html")