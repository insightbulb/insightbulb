from flask import Flask, render_template
from yeelight import *

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


# Turn the light on
@app.route('/toggle-on/', methods=['POST'])
def turn_on():
    bulbs = discover_bulbs()
    if bulbs.__len__() == 0:
        return render_template('index.html')

    my_bulb = Bulb(bulbs[0].get("ip"))
    my_bulb.turn_on()
    return render_template('index.html')


# Turn the light off
@app.route('/toggle-off/', methods=['POST'])
def turn_off():
    bulbs = discover_bulbs()
    if bulbs.__len__() == 0:
        return render_template('index.html')

    my_bulb = Bulb(bulbs[0].get("ip"))
    my_bulb.turn_off()
    return render_template('index.html')


# This is a simple example of a flow event
@app.route('/toggle-flow/', methods=['POST'])
def simple_flow():
    bulbs = discover_bulbs()
    if bulbs.__len__() == 0:
        return render_template('index.html')

    my_bulb = Bulb(bulbs[0].get("ip"))
    transitions = [
        TemperatureTransition(1700, duration=1000),
        SleepTransition(duration=1000),
        TemperatureTransition(6500, duration=1000)
    ]

    flow1 = Flow(
        count=2,
        action=Flow.actions.recover,
        transitions=transitions
    )

    my_bulb.start_flow(flow1)
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
