from flask import Flask, render_template
from yeelight import *
from tide_scraper import *

app = Flask(__name__, static_url_path='/static')
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.route('/', methods=['GET'])
def index():
    # Get the region data on landing
    us_regions = []
    for region in get_regions():
        us_regions.append(region.text)

    stations = []
    for station in get_stations():
        stations.append(station.text)
    return render_template('index.html', us_regions=us_regions, stations=stations)


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
@app.route('/flow')
def simple_flow():
    bulbs = discover_bulbs()
    if len(bulbs) is 0:
        return render_template('index.html')

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
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
