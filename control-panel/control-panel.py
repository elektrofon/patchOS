import os
import sys
from subprocess import call
import argparse
import time
from time import sleep
from threading import Thread, Event
import urllib.request
import dbus
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit

debug = False

firstRunTimestamp = str(int(time.time()))

if os.path.isfile('has-run-before'):
    with open('has-run-before', 'r') as f:
        firstRunTimestamp = f.read()
else:
    with open('has-run-before', 'w+') as f:
        f.write(firstRunTimestamp)

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

clientCount = 0

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.config['DEBUG'] = debug

socketio = SocketIO(app, async_mode=None, logger=debug, engineio_logger=debug)

thread = Thread()
thread_stop_event = Event()

def getJackServiceStatus():
    status = 'inactive'

    try:
        jackService = bus.get_object(
            'org.freedesktop.systemd1',
            object_path = manager.GetUnit('jack.service')
        )

        jackServiceInterface = dbus.Interface(
            jackService,
            dbus_interface = 'org.freedesktop.DBus.Properties'
        )

        status = jackServiceInterface.Get('org.freedesktop.systemd1.Unit', 'ActiveState')
    except:
        pass

    return status

def getJacktripServiceStatus():
    serverStatus = 'inactive'
    clientStatus = 'inactive'

    try:
        jacktripServerService = bus.get_object(
            'org.freedesktop.systemd1',
            object_path = manager.GetUnit('jacktrip-server.service')
        )

        jacktripClientService = bus.get_object(
            'org.freedesktop.systemd1',
            object_path = manager.GetUnit('jacktrip-client.service')
        )

        jacktripServerServiceInterface = dbus.Interface(
            jacktripServerService,
            dbus_interface ='org.freedesktop.DBus.Properties'
        )

        jacktripClientServiceInterface = dbus.Interface(
            jacktripClientService,
            dbus_interface = 'org.freedesktop.DBus.Properties'
        )

        serverStatus = jacktripServerServiceInterface.Get('org.freedesktop.systemd1.Unit', 'ActiveState')
        clientStatus = jacktripClientServiceInterface.Get('org.freedesktop.systemd1.Unit', 'ActiveState')
    except:
        pass

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
    externalIp = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    lastConnectedIp = '0.0.0.0'

    if os.path.isfile(os.path.join(sys.path[0], 'server-ip')):
        with open(os.path.join(sys.path[0], 'server-ip'), 'r') as f:
            lastConnectedIp = f.read().replace('JACKTRIP_SERVER_IP=', '')

    templateData = {
        'version': firstRunTimestamp,
        'lastConnectedIp': lastConnectedIp,
        'externalIp': externalIp
    }

    return render_template('index.html', **templateData)


@socketio.on('jacktrip-start-server')
def jacktripStart():
    manager.StartUnit('jacktrip-server.service', 'replace')


@socketio.on('jacktrip-start-client')
def jacktripStartClient(serverIp):
    with open(os.path.join(sys.path[0], 'server-ip'), 'w') as f:
        f.write('JACKTRIP_SERVER_IP=' + serverIp)

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
    global clientCount
    global thread_stop_event

    thread_stop_event.clear()

    clientCount += 1

    if not thread.is_alive():
        thread = socketio.start_background_task(checkStatusLoop)


@socketio.on('disconnect')
def onDisConnect():
    global thread
    global clientCount
    global thread_stop_event

    clientCount -= 1

    if clientCount <= 0:
        thread_stop_event.set()

@socketio.on('status?')
def queryStatus():
    status = getJacktripServiceStatus()

    emit('status', {'jack': getJackServiceStatus(), 'jacktrip': status['status'], 'jacktripMode': status['mode']})


@socketio.on('externalIp?')
def queryExternalIp():
    emit('externalIp', urllib.request.urlopen('https://ident.me').read().decode('utf8'))


@socketio.on('shutdown?')
def queryExternalIp():
    call("shutdown now", shell=True)


if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=args.port)
