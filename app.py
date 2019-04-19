from flask import Flask, render_template, request
from yeelight import *
from tide_scraper import *
import datetime
import time
import httplib2
import re

app = Flask(__name__, static_url_path='/static')
app.config["TEMPLATES_AUTO_RELOAD"] = True
http = httplib2.Http()


@app.route('/', methods=['GET', 'POST'])
def index():
    bulbs = discover_bulbs()
    devices = []
    for bulb in bulbs:
        devices.append(bulb['capabilities'].get('id'))

    us_regions = []
    local_stations = get_stations_dict()
    for region in get_regions():
        # TODO: Iterate through an array of all the locations we want to skip
        # We don't need tide data for the great lakes
        if 'Great Lakes' not in region.text:
            us_regions.append(region.text)

    # Get current time
    weekday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    current_weekday = weekday[datetime.datetime.today().weekday()]
    current_date = str(datetime.datetime.today().month) + '/' + str(datetime.datetime.today().day)

    # A tidal station was selected
    if request.method == 'POST':
        test_val = request.json['test_val']
        station_url = 'https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id=%s' % test_val
        times = get_tide_data(station_url)
        simple_flow(times)

    return render_template('index.html', us_regions=us_regions,
                           local_stations=local_stations, devices=devices,
                           current_weekday=current_weekday, current_date=current_date)


@app.route('/get-stations')
def get_stations(region):
    local_stations = get_stations(region)
    return render_template('index.html', local_stations=local_stations)


# Turn the light on
@app.route('/turn-on')
def turn_on():
    bulbs = discover_bulbs()
    if len(bulbs) is 0:
        return render_template('index.html')

    my_bulb = Bulb(bulbs[0].get("ip"))
    my_bulb.turn_on()
    return render_template('index.html')


# Turn the light off
@app.route('/turn-off')
def turn_off():
    bulbs = discover_bulbs()
    if len(bulbs) is 0:
        return render_template('index.html')

    my_bulb = Bulb(bulbs[0].get("ip"))
    my_bulb.turn_off()
    return render_template('index.html')


# TODO: Add delayed thread for
#  tidal highs and lows
def simple_flow(times):
    split_times = list()

    # split_times, contains elements in the form:
    # e.g., ['2:51 ', 'AM', 'high 1.62 ft.']
    for time in times:
        high_low = re.split('([AP]M)', time)
        split_times.append(high_low)

    # Get current time in seconds
    current_time = datetime.datetime.today()
    tide_times = split_times_to_datetimes(split_times)

    # Get data points (prev tide time, current time, next tide time)
    # Data points are converted to datatime objects
    data_points = get_data_points(current_time, tide_times)

    # Get bulb intensity as a percent.  Bulb gets brighter as it gets closer to next tide time.
    # Use fake times as a test.  Replace with data_points. 
    test = fake_times()
    light_intensity = get_light_intensity(test)
    print(light_intensity)



    bulbs = discover_bulbs()
    if len(bulbs) is 0:
        return False

    my_bulb = Bulb(bulbs[0].get("ip"))
    transitions = [
        TemperatureTransition(1700, duration=1000),
        SleepTransition(duration=1000),
        TemperatureTransition(6500, duration=1000),
        TemperatureTransition(500, 500),
    ]

    flow1 = Flow(
        count=4,
        action=Flow.actions.recover,
        transitions=transitions
    )

    my_bulb.start_flow(flow1)

def split_times_to_datetimes(split_times):
    results = []
    current_time = datetime.datetime.today()
    for time in split_times:
        test_time = str(current_time.year) + " " + str(current_time.month)+ " " + str(current_time.day)+ " " + str(time[0]) + str(time[1])
        dateobj = datetime.datetime.strptime(test_time, '%Y %m %d %I:%M %p')
        results.append([dateobj, time[2].split(' ')[0]])

    return results

def get_data_points(current_time, tide_times):
    results = []
    prev_time = None
    next_time = None
    last_item = None
    #Compare current time with tide times
    for time in tide_times:
        if time[0] < current_time:
            last_item = time[0]
        else:
            prev_time = last_item
            next_time = time[0]
            results.extend(prev_time, current_time, next_time)
    return results

def get_light_intensity(data_points):
    # Get fraction of tide
    # light_intensity = time.mktime(data_points[0][0].timetuple())
    prev_time = data_points[0]
    current_time = data_points[1]
    next_time = data_points[2]

    prev_time_seconds = float(time.mktime(prev_time.timetuple()))
    current_time_seconds = float(time.mktime(current_time.timetuple()))
    next_time_seconds = float(time.mktime(next_time.timetuple()))

    numerator = (next_time_seconds - prev_time_seconds)/10
    denomenator = current_time_seconds - prev_time_seconds
    light_intensity = (numerator/denomenator) * 100

    return light_intensity

def fake_times():

    conversion_format = '%b %d %Y %I:%M%p'

    prev_date_time = 'Apr 19 2019 3:32PM'
    prev_date_obj = datetime.datetime.strptime(prev_date_time, conversion_format)

    current_date_time = 'Apr 19 2019 5:14PM'
    current_date_obj = datetime.datetime.strptime(current_date_time, conversion_format)

    next_date_time = 'Apr 19 2019 10:05PM'
    next_date_obj = datetime.datetime.strptime(next_date_time, conversion_format)

    fake_times = [prev_date_obj, current_date_obj, next_date_obj]
    return fake_times




if __name__ == '__main__':
    app.run(debug=True)
