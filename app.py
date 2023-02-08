from flask import Flask, render_template
import io, base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from functions import tides, forecast, swim_times, water_quality

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded when running flask app and making changes on the fly
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Return weather forecast info, format= [hourly_forecast=[times, speeds, symbols, temperatures], wind_direction, sunrise, sunset]]
weather_info = forecast()


# Function to generate windspeed graph using MatplotLib
@app.route("/mysuperplot", methods=["GET"])
def plotView():

    # Generate plot
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Today's Wind Speed")
    axis.set_xlabel("Time")
    axis.set_ylabel("MPH")
    axis.grid()
    # Populate graph with time in hours, speeds in MPH, taking every other value (every 2 hours)
    # axis.plot(weather_info[0][0], weather_info[0][1])
    axis.plot(weather_info[0][0][::2], weather_info[0][1][::2] )

    # Convert plot to PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)

    # Encode PNG image to base64 string
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')

    # return render_template("image.html", image=pngImageB64String)
    return pngImageB64String


@app.route("/")
def index():
    # Retrieve wind speed at 13:00 as indicator for the day
    wind_speed_int = int(weather_info[0][1][9])
    tide_info = tides()
    wind_plot = plotView()
    # water_quality() returns a dict containing 'risk_prediction', 'heavy_rain_warning', 'latest_compliance_assessment'
    # TO DO = update this after adding "latestSampleAssessment" as rtn value in functions.py
    pollution = water_quality()

    return render_template("index.html", tides=tide_info, swim_times=swim_times(tide_info), wind_plot=wind_plot, wind_speed_int=wind_speed_int,
    weather_info=weather_info, pollution=pollution)


@app.route("/resources")
def resources():
    return render_template("resources.html")