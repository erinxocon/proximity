import sys
import time
import json
import ble_scan_core as ble
import bluetooth._bluetooth as bluez

from multiprocessing import Process, Pipe


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
            #print "JSON THREAD:", json.dumps(l)


def main(parent_conn):
    con = parent_conn
    while True:
        if con.poll(30):
            print "Main Thread is executing"
            d = con.recv()
            print json.dumps(d)
        else:
            print "no new data"


if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    example = BLE_Listen(0, child_conn)
    main(parent_conn)
