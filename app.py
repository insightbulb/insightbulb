from flask import Flask, render_template, request
from yeelight import *
from tide_scraper import *
from datetime import datetime
from tide_data import split_times_to_datetimes, get_data_points

import httplib2
import re

app = Flask(__name__, static_url_path='/static')
app.config["TEMPLATES_AUTO_RELOAD"] = True
http = httplib2.Http()
current_times = list()
station_name = []


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
    current_weekday = weekday[datetime.today().weekday()]
    current_date = str(datetime.today().month) + '/' + str(datetime.today().day)

    # A tidal station was selected
    if request.method == 'POST':
        station_data = request.json['station_data']
        station_url = 'https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id=%s' % station_data[0]
        times = get_tide_data(station_url)
        current_times.clear()
        extrema = simple_flow(times)
        station_name.clear()
        station_name.append(station_data[1])
        print("HERE!!", station_data)
        for extreme in extrema:
            current_times.append(extreme)

    return render_template('index.html', us_regions=us_regions,
                           local_stations=local_stations, devices=devices,
                           current_weekday=current_weekday, current_date=current_date,
                           tide_times=current_times, station_name=station_name)


@app.route('/show-tide-extrema')
def update_tide_times():
    return render_template('index.html', tide_times=current_times)


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
    for tide in times:
        high_low = re.split('([AP]M)', tide)
        split_times.append(high_low)

    # Get current time in seconds
    current_time = datetime.today()
    tide_times = split_times_to_datetimes(split_times)

    # Get data points (prev tide time, current time, next tide time)
    # Data points are converted to datatime objects
    data_points = get_data_points(current_time, tide_times)

    bulbs = discover_bulbs()
    if len(bulbs) is 0:
        return split_times

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

    return split_times


if __name__ == '__main__':
    app.run(debug=True)
