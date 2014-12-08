import sys
import time
import json
import sqlite3
import ble_scan_core as ble
import bluetooth._bluetooth as bluez


from multiprocessing import Process, Pipe

DATABASE = '/tmp/flaskr.db'


class BLE_Listen(object):

    def __init__(self, dev_id, child_conn):
        """ Constructor """

        self.dev_id = dev_id
        self.child_conn = child_conn

        thread = Process(target=self.run, args=(self.dev_id, self.child_conn))
        thread.daemon = True
        thread.start()

    def run(self, dev_id, child_conn):
        """ Daemon = True makes this run forever """
        con = self.child_conn

        try:
            sock = bluez.hci_open_dev(dev_id)
            print "ble thread started"
        except:
            print "error accessing bluetooth device..."
            sys.exit(1)

        ble.hci_le_set_scan_parameters(sock)
        ble.hci_enable_le_scan(sock)
        print "scan mode acquired"
        while True:
            l = ble.parse_events(sock, 10)
            con.send(l)
            time.sleep(2)
            #print "BLE THREAD:", json.dumps(l)


def main(parent_conn):
    con = parent_conn
    db = connect_db()
    while True:
        if con.poll(5):
            print "Main Thread is executing"
            d = con.recv()
            print json.dumps(d)
            for k in d.keys():
                t = (k, d[k]['uuid'], d[k]['majorid'], d[k]['minorid'], d[k]['rssi'], d[k]['calibratedtx'], 0)
                try:
                    db.execute('DELETE FROM devices WHERE isAcquired = 0;')
                    db.execute('VACUUM;')
                    db.execute('INSERT INTO devices VALUES (?,?,?,?,?,?,?)', t)
                    db.commit()
                except sqlite3.IntegrityError:
                    db.rollback()
        else:
            print "no new data"
            db.execute('DELETE FROM devices;')
            db.execute('VACUUM;')


def connect_db():
    return sqlite3.connect(DATABASE)


if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    example = BLE_Listen(0, child_conn)
    main(parent_conn)
