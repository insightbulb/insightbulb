from flask import Flask, render_template, request
from yeelight import *
from tide_scraper import *
import datetime
import httplib2
import json
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
        # We don't need tide data for the great lakes
        if 'Great Lakes' not in region.text:
            us_regions.append(region.text)

    # Get current time
    weekday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    current_weekday = weekday[datetime.datetime.today().weekday()]
    current_date = str(datetime.datetime.today().month) + '/' + str(datetime.datetime.today().day)
    
    if request.method == 'POST':
        # print('HERE!!!', request.json['test_val'])
        test_val = request.json['test_val']

        station_url = 'https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id=%s' % test_val
        times = get_tide_data(station_url)
        simple_flow(times)

    # print(station_url)
    # response = http.request(station_url)

        # soup = BeautifulSoup(response, 'html.parser')
        # test = soup.findAll("div", attrs={'class': 'span3'})
        # print(test)

    return render_template('index.html', us_regions=us_regions, local_stations=local_stations, devices=devices,
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


# This is a simple example of a flow event
def simple_flow(times):
    split_times = list()

    for time in times:
        high_low = re.compile('[AM/PM]').split(time)
        split_times.append(high_low)

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
    # return split_times


if __name__ == '__main__':
    app.run(debug=True)
