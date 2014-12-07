import json
import sqlite3
from flask import Flask, request, g, jsonify, make_response

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


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
    try:
        g.db.execute('INSERT INTO subscribers (ip) VALUES (?)', (origin,))
        g.db.commit()
    except sqlite3.IntegrityError:
        return "You've already subscribed!"

    return jsonify(origin=request.headers.get('X-Forwarded-For', request.remote_addr))


@app.route('/flush', methods=['GET'])
def drop_subscribers():
    g.db.execute('DELETE FROM subscribers;')
    g.db.execute('VACUUM;')
    g.db.commit()
    return "subscribers table flushed"


@app.route('/devices')
def get_devices():
    l = []
    cur = g.db.execute('SELECT * FROM devices')
    for row in cur.fetchall():
        j = {"mac": str(row[0]), "uuid": str(row[1]), "majorid": row[2], "minorid": row[3], "rssi": row[4], "tx_calibrated": row[5]}
        l.append(j)
    resp = make_response(json.dumps(l))
    resp.headers['Content-Type'] = 'text/json'
    return resp

if __name__ == '__main__':
    app.debug = DEBUG
    app.run(host='0.0.0.0', port=80)
