from flask import Flask, render_template, request
from yeelight import *
from tide_scraper import *
from tide_data import split_times_to_datetimes, get_data_points, get_light_intensity


from datetime import datetime
from time import sleep

import threading
from multiprocessing import Process
import httplib2
import re

app = Flask(__name__, static_url_path='/static')
app.config["TEMPLATES_AUTO_RELOAD"] = True
http = httplib2.Http()
current_times = list()
station_name = []
lunar_data = []


@app.route('/', methods=['GET', 'POST'])
def index():
    bulbs = discover_bulbs()
    devices = []

    weekday = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    current_weekday = weekday[datetime.today().weekday()]
    current_date = str(datetime.today().month) + '/' + str(datetime.today().day)

    skip_regions = ['Great Lakes',
                    'Erie',
                    'Michigan',
                    'St. Clair',
                    'Niagara River',
                    'Lawrence',
                    'Caribbean',
                    'District of Columbia',
                    'Indian',
                    'New York',
                    'New Jersey',
                    'North Carolina',
                    'Pacific Islands',
                    'Portuguese Islands',
                    'Rhode Island',
                    'South Carolina']

    for bulb in bulbs:
        devices.append(bulb['capabilities'].get('id'))

    us_regions = [region.text for region in get_regions()]
    for skip in skip_regions:
        for region in us_regions:
            if skip in region:
                us_regions.remove(region)
    local_stations = get_stations_dict()

    # A tidal station was selected
    if request.method == 'POST':
        station_data = request.json['station_data']
        station_url = 'https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id=%s' % station_data[0]
        times = get_tide_data(station_url)
        current_times.clear()
        extrema = tidal_flow(times)
        station_name.clear()
        station_name.append(station_data[1])
        # For debugging
        print("STATION_DATA:", station_data)
        for extreme in extrema:
            current_times.append(extreme)

        ld = get_lunar_data(station_data[0])
        for data in ld:
            lunar_data.append(data)

    return render_template('index.html', us_regions=us_regions,
                           local_stations=local_stations, devices=devices,
                           current_weekday=current_weekday, current_date=current_date,
                           tide_times=current_times, station_name=station_name, lunar=lunar_data)


@app.route('/hawaii')
def hawaii():
    station_url = [
        'https://www.ndbc.noaa.gov/station_page.php?station=51211', 
        'https://www.ndbc.noaa.gov/station_page.php?station=51210',
        'https://www.ndbc.noaa.gov/station_page.php?station=51202',
        'https://www.ndbc.noaa.gov/station_page.php?station=51212',
        'https://www.ndbc.noaa.gov/station_page.php?station=51201', 
        'https://www.ndbc.noaa.gov/station_page.php?station=51213',
        'https://www.ndbc.noaa.gov/station_page.php?station=51205',
        'https://www.ndbc.noaa.gov/station_page.php?station=51206',
        'https://www.ndbc.noaa.gov/station_page.php?station=51208'
    ]

    pearl_harbor = get_wave_data(station_url[0])
    kaneohe_bay = get_wave_data(station_url[1])
    mokapu_point = get_wave_data(station_url[2])
    barbers_point = get_wave_data(station_url[3])
    waimea_bay = get_wave_data(station_url[4])
    kaumalapau = get_wave_data(station_url[5])
    pauwela = get_wave_data(station_url[6])
    hilo = get_wave_data(station_url[7])
    hanalei = get_wave_data(station_url[8])

    return render_template('hawaii.html', pearl_harbor=pearl_harbor, kaneohe_bay=kaneohe_bay, 
                            mokapu_point=mokapu_point, barbers_point=barbers_point, 
                            waimea_bay=waimea_bay, kaumalapau=kaumalapau, pauwela=pauwela, hilo=hilo, 
                            hanalei=hanalei)


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
    my_bulb.turn_on(effect="sudden")
    return render_template('index.html')


# Turn the light off
@app.route('/turn-off')
def turn_off():
    bulbs = discover_bulbs()
    if len(bulbs) is 0:
        return render_template('index.html')
    my_bulb = Bulb(bulbs[0].get("ip"))
    my_bulb.turn_off(effect="sudden")
    return render_template('index.html')


def tidal_flow(times):
    bulbs = discover_bulbs()
    split_times = list()

    # split_times contains elements in the form:
    # ['2:51 AM', 'high', '1.62 ft.']
    for tide in times:
        high_low = re.split('(low|high)', tide)
        split_times.append(high_low)

    if len(bulbs) is 0:
        return split_times

    # Notify when a station is selected
    my_bulb = Bulb(bulbs[0].get("ip"))
    station_select_pulse = [
        TemperatureTransition(1500, duration=500, brightness=50)]
    station_flow = Flow(
        count=2,
        transitions=station_select_pulse)
    my_bulb.start_flow(station_flow)

    # Apply the ambient alert notification using a delayed thread
    delayed_transitions = [
        TemperatureTransition(1500, duration=1000),
        SleepTransition(duration=1000),
        TemperatureTransition(1500, duration=1000),
        TemperatureTransition(500, duration=500)]
    delayed_alert_flow = Flow(
        count=2,
        action=Flow.actions.recover,
        transitions=delayed_transitions)

    # This is where the main ambient notifications take place, two thread are run
    # The first runs an infinite loop adjusting brightness to the tides
    # While the other runs a delayed thread to run a flow on the next extrema

    # Get current time in seconds, data points (prev tide time, current time, next tide time)
    # Data points are converted to datetime objects
    now = datetime.now()
    test_times = [['7:00 AM'], ['10:00 PM'], ['11:59 PM']]
    tidal_datetimes = split_times_to_datetimes(test_times)
    data_points = get_data_points(now, tidal_datetimes)
    print("DATA_POINTS", data_points)

    if len(data_points) > 0:
        print("GOT HERE!!")
        delay = (data_points.pop() - now).total_seconds()
        print("DELAY", delay)
        p1 = Process(target=threading.Timer, args=(delay, lambda: my_bulb.start_flow(delayed_alert_flow,)))
        p1.start()

        p2 = Process(target=continuous_tidal_brightness, args=(data_points, my_bulb, now,))
        p2.start()

        p1.join()
        p2.join()

    return split_times


def continuous_tidal_brightness(tide_delta, bulb, ref_time):
    while True:
        sleep(5)
        brightness = get_light_intensity(tide_delta, ref_time)
        print(brightness)
        bulb.set_brightness(brightness=brightness)


if __name__ == '__main__':
    app.run(debug=True)
