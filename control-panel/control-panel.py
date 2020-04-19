import os
import argparse
from time import sleep
from threading import Thread, Event
import urllib.request
import dbus
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

parser = argparse.ArgumentParser(description='patchOS control panel')
parser.add_argument('--port', dest='port', type=int, default=80)
args = parser.parse_args()

bus = dbus.SystemBus()
systemd = bus.get_object(
    'org.freedesktop.systemd1',
    '/org/freedesktop/systemd1'
)

manager = dbus.Interface(
    systemd,
    'org.freedesktop.systemd1.Manager'
)

jackService = bus.get_object(
    'org.freedesktop.systemd1',
    object_path=manager.GetUnit('jack@jack.service')
)

jacktripServerService = bus.get_object(
    'org.freedesktop.systemd1',
    object_path=manager.GetUnit('jacktrip-server.service')
)

jacktripClientService = bus.get_object(
    'org.freedesktop.systemd1',
    object_path=manager.GetUnit('jacktrip-client.service')
)

jackServiceInterface = dbus.Interface(
    jackService,
    dbus_interface='org.freedesktop.DBus.Properties'
)

jacktripServerServiceInterface = dbus.Interface(
    jacktripServerService,
    dbus_interface='org.freedesktop.DBus.Properties'
)

jacktripClientServiceInterface = dbus.Interface(
    jacktripClientService,
    dbus_interface='org.freedesktop.DBus.Properties'
)

externalIp = urllib.request.urlopen('https://ident.me').read().decode('utf8')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = True

socketio = SocketIO(app, async_mode=None, logger=True, engineio_logger=True)

thread = Thread()
thread_stop_event = Event()

def getJackServiceStatus():
    return jackServiceInterface.Get('org.freedesktop.systemd1.Unit', 'ActiveState')


def getJacktripServiceStatus():
    serverStatus = jacktripServerServiceInterface.Get('org.freedesktop.systemd1.Unit', 'ActiveState')
    clientStatus = jacktripClientServiceInterface.Get('org.freedesktop.systemd1.Unit', 'ActiveState')

    if serverStatus == 'inactive' and clientStatus == 'inactive':
        return 'inactive'

    if serverStatus != 'inactive':
        return serverStatus

    if clientStatus != 'inactive':
        return clientStatus


def checkStatusLoop():
    while not thread_stop_event.isSet():
        socketio.emit('status', {'data': {'jack': getJackServiceStatus(), 'jacktrip': getJacktripServiceStatus()}})
        socketio.sleep(5)


@app.route("/")
def index():
    templateData = {}

    return render_template('index.html', **templateData)


@app.route("/jacktrip/start", methods=['POST'])
def jacktripStart():
    return jsonify({'externalIp': externalIp})


@app.route("/jacktrip/start-client", methods=['POST'])
def jacktripStartClient():
    print(request.json['serverIp'])
    os.environ['JACKTRIP_SERVER_IP'] = request.json['serverIp']

    # TODO: Check if jacktrip-server/jacktrip-client services are running
    # TODO: Stop running services
    # TODO: Start jacktrip-client service

    try:
        manager.StartUnit('jacktrip-client.service', 'replace')
        return jsonify({'status': getJacktripServiceStatus()})
    except dbus.exceptions.DBusException as error:
        response = jsonify({'error': error})
        response.status_code = 500

        return response


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
    emit('status', {'data': {'jack': getJackServiceStatus(), 'jacktrip': getJacktripServiceStatus()}})


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=args.port)
