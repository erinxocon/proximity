import json
import time
import sqlite3
import requests
from flask import Flask, request, g, jsonify, make_response

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
CP_LIVE = True
USERNAME = 'fourwinds'
PASSWORD = 'fourwinds'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def set_cm_variable(ip, d, user, pwd):
    string = ''
    for k, v in d.items():
        k, v = str(k), str(v)
        url = 'http://'+ip+':10561/player/command/RunScript?1=Player.SetVariable('+k+','+v+')'
        r = requests.get(url, auth=(user, pwd))
        if r.status_code == requests.codes.ok:
            string += 'Set variable '+k+' to '+v+'\n'
        else:
            string += 'Failed to set variable '+k+'\n'
    return string


def play_cm_content(ip, d, user, pwd):
    string = ''
    for k, v in d.items():
        k, v = str(k), str(v)
        url = 'http://'+ip+':10561/player/command/RunScript?1=Template.PlayContent('+k+','+v+')'
        r = requests.get(url, auth=(user, pwd))
        if r.status_code == requests.codes.ok:
            string += 'Played Content '+k+' in region '+v+'\n'
        else:
            string += 'Failed to play Content '+k+'\n'
    return string


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/subscribe', methods=['GET'])
def subscribe_player():
    origin = request.headers.get('X-Forwarded-For', request.remote_addr)
    t = (origin, 0)
    try:
        g.db.execute('INSERT INTO subscribers VALUES (?,?)', t)
        g.db.commit()
    except sqlite3.IntegrityError:
        return "You've already subscribed!"

    return jsonify(origin=origin)


@app.route('/flush', methods=['GET'])
def drop_subscribers():
    g.db.execute('DELETE FROM subscribers;')
    g.db.execute('VACUUM;')
    g.db.commit()
    return "subscribers table flushed"


@app.route('/devices', methods=['GET'])
def get_devices():
    l = []
    cur = g.db.execute('SELECT * FROM devices')
    for row in cur.fetchall():
        j = {"mac": str(row[0]), "uuid": str(row[1]), "majorid": row[2], "minorid": row[3], "rssi": row[4], "tx_calibrated": row[5], "isAcquired": row[6]}
        l.append(j)
    resp = make_response(json.dumps(l))
    resp.headers['Content-Type'] = 'text/json'
    return resp


@app.route('/acquireDevice', methods=['GET'])
def acquire_device():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    try:
        cur = g.db.execute('SELECT * from devices WHERE isAcquired = 0 ORDER BY rssi')
        row = cur.fetchone()
        d1 = {"mac": str(row[0]), "uuid": str(row[1]), "majorid": row[2], "minorid": row[3], "rssi": row[4], "tx_calibrated": row[5], "isAcquired": row[6]}
        d2 = {'BLE Data': 'Main'}
        if CP_LIVE:
            setVar = set_cm_variable(ip, d1, app.config['USERNAME'], app.config['PASSWORD'])
            playContent = play_cm_content(ip, d2, app.config['USERNAME'], app.config['PASSWORD'])
            return jsonify(variables=setVar, content=playContent)
        else:
            return jsonify(status='Check sqlite3 for results')
    except TypeError:
        d2 = {'Blank': 'Main'}
        playContent = play_cm_content(ip, d2, app.config['USERNAME'], app.config['PASSWORD'])
        return jsonify(status='Played Blank.')


@app.route('/engageDevice/<uuid>', methods=['GET'])
def engage_device(uuid):
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    g.db.execute('UPDATE devices SET isAcquired = 1 WHERE uuid = ?', (uuid,))
    g.db.execute('UPDATE subscribers SET hasAcquired = 1 WHERE ip = ?', (ip,))
    g.db.commit()
    return jsonify(status='Device is Engaged')


@app.route('/dropDevice/<uuid>', methods=['GET'])
def drop_device(uuid):
    ip = request.headers.get('X-Forwarded-For', request.remote_addr)
    time.sleep(10)
    g.db.execute('DELETE FROM devices WHERE uuid = ?', (uuid,))
    g.db.execute('UPDATE subscribers SET hasAcquired = 0 WHERE ip = ?', (ip,))
    g.db.commit()
    return jsonify(status='Device Dropped.')


@app.route('/newData', methods=['GET'])
def webhook():
    cur = g.db.execute('SELECT * FROM subscribers')
    for row in cur.fetchall():
        d = {'Blank': 'Control', 'CONTROL:AcquireDevice': 'Control'}
        play_cm_content(row[0], d, app.config['USERNAME'], app.config['PASSWORD'])
    return jsonify(status='Alerted subscribers to check for new data')

if __name__ == '__main__':
    app.debug = DEBUG
    app.run(host='0.0.0.0', port=80)
