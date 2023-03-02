from datetime import timedelta, datetime


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
