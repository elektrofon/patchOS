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
    object_path = manager.GetUnit('jack@jack.service')
)

jacktripServerService = bus.get_object(
    'org.freedesktop.systemd1',
    object_path = manager.GetUnit('jacktrip-server.service')
)

jacktripClientService = bus.get_object(
    'org.freedesktop.systemd1',
    object_path = manager.GetUnit('jacktrip-client.service')
)

jackServiceInterface = dbus.Interface(
    jackService,
    dbus_interface = 'org.freedesktop.DBus.Properties'
)

jacktripServerServiceInterface = dbus.Interface(
    jacktripServerService,
    dbus_interface ='org.freedesktop.DBus.Properties'
)

jacktripClientServiceInterface = dbus.Interface(
    jacktripClientService,
    dbus_interface = 'org.freedesktop.DBus.Properties'
)


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
        return {'status': 'inactive', 'mode': 'undefined'}

    if serverStatus != 'inactive':
        return {'status': serverStatus, 'mode': 'server'}

    if clientStatus != 'inactive':
        return {'status': clientStatus, 'mode': 'client'}


def checkStatusLoop():
    while not thread_stop_event.isSet():
        status = getJacktripServiceStatus()
        socketio.emit('status', {'jack': getJackServiceStatus(), 'jacktrip': status['status'], 'jacktripMode': status['mode']})
        socketio.sleep(5)


@app.route("/")
def index():
    templateData = {}

    return render_template('index.html', **templateData)


@socketio.on('jacktrip-start-server')
def jacktripStart():
    manager.StartUnit('jacktrip-server.service', 'replace')


@socketio.on('jacktrip-start-client')
def jacktripStartClient(serverIp):
    serverIpFile = open('server-ip', 'w')
    serverIpFile.write('JACKTRIP_SERVER_IP=' + serverIp)
    serverIpFile.close()
    # os.environ['JACKTRIP_SERVER_IP'] = serverIp;

    manager.StartUnit('jacktrip-client.service', 'replace')


@socketio.on('jacktrip-stop')
def jacktripStop():
    manager.ResetFailedUnit('jacktrip-server.service')
    manager.ResetFailedUnit('jacktrip-client.service')
    manager.StopUnit('jacktrip-server.service', 'replace')
    manager.StopUnit('jacktrip-client.service', 'replace')


@socketio.on('connect')
def onConnect():
    global thread

    if not thread.isAlive():
        thread = socketio.start_background_task(checkStatusLoop)


@socketio.on('status?')
def queryStatus():
    status = getJacktripServiceStatus()

    emit('status', {'jack': getJackServiceStatus(), 'jacktrip': status['status'], 'jacktripMode': status['mode']})


@socketio.on('externalIp?')
def queryExternalIp():
    emit('externalIp', urllib.request.urlopen('https://ident.me').read().decode('utf8'))


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=args.port)
