from datetime import timedelta, datetime
import io, base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure


# Function that takes HH:MM formatted string and shifts it forward or back by given number of hours
# Use a positive int to shift forward, negative to shift back
def shift_time(intime, hours):
    outtime = datetime.strptime(intime, "%H:%M") + timedelta(hours=hours)
    return outtime.strftime("%H:%M")

# Takes a YYYY-MM-DD formatted string
def reformat(date):
    # Returns DD-MM-YYYY formatted string
    array = date.split('-')
    # Check to see if string has likely already been formatted:
    if len(array[-1]) == 4:
        return array
    else:
        array = array[::-1]
        fdate = '-'.join(array)
        return fdate


# Function to generate windspeed graph using MatplotLib
def plotView(hours, speeds):
    # Generate plot
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.set_title("Today's Wind Speed")
    axis.set_xlabel("Time")
    axis.set_ylabel("MPH")
    axis.grid()
    # Populate graph with time in hours, speeds in MPH
    axis.plot(hours, speeds)

    # Convert plot to PNG image
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    

    # Encode PNG image to base64 string
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')
    return pngImageB64String
