import sys
import time
import json
import threading
import ble_scan_core as ble
import bluetooth._bluetooth as bluez


class BLE_Listen(object):

    def __init__(self, dev_id):
        """ Constructor"""

        self.dev_id = dev_id

        thread = threading.Thread(target=self.run, args=(self.dev_id,))
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self, dev_id):
        """ Method that runs forever """
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
            print json.dumps(l)

if __name__ == '__main__':
    example = BLE_Listen(0)
    time.sleep(3)
    while True:
        print "Main Thread is executing"
        time.sleep(10)
