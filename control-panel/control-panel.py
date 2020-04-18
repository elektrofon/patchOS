import argparse
# from pydbus import SessionBus
from flask import Flask, render_template, jsonify, request

parser = argparse.ArgumentParser(description='patchOS control panel')
parser.add_argument('--port', dest='port', type=int, default=80)
args = parser.parse_args()

# bus = SessionBus()
# systemd = bus.get(".systemd1")

# for unit in systemd.ListUnits():
#     print(unit)

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=args.port, debug=True)
