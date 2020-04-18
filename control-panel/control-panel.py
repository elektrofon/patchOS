import argparse
from time import sleep
from threading import Thread, Event
# from pydbus import SessionBus
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

parser = argparse.ArgumentParser(description='patchOS control panel')
parser.add_argument('--port', dest='port', type=int, default=80)
args = parser.parse_args()

# bus = SessionBus()
# systemd = bus.get(".systemd1")

# for unit in systemd.ListUnits():
#     print(unit)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

thread = Thread()
thread_stop_event = Event()

def checkStatusLoop():
    while not thread_stop_event.isSet():
        socketio.emit('status', {'data': {'jack': 'running', 'jacktrip': 'stopped'}})
        socketio.sleep(5)


@app.route("/")
def index():
    templateData = {}

    return render_template('index.html', **templateData)


@app.route("/jacktrip/start", methods=['POST'])
def jacktripStart():
    return jsonify(request.json)


@app.route("/jacktrip/stop", methods=['POST'])
def jacktripStop():
    return jsonify(request.json)


@socketio.on('connect')
def onConnect():
    global thread

    if not thread.isAlive():
        thread = socketio.start_background_task(checkStatusLoop)


@socketio.on('status?')
def queryStatus():
    emit('status', {'data': {'jack': 'running', 'jacktrip': 'stopped'}})


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=args.port)
