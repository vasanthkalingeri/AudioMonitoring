import fcntl
import struct
import array
import bluetooth
import bluetooth._bluetooth as bt

import time
import os
import datetime

def bluetooth_rssi(addr):
    # Open hci socket
    hci_sock = bt.hci_open_dev()
    hci_fd = hci_sock.fileno()

    # Connect to device (to whatever you like)
    bt_sock = bluetooth.BluetoothSocket(bluetooth.L2CAP)
    bt_sock.settimeout(10)
    result = bt_sock.connect_ex((addr, 1))	# PSM 1 - Service Discovery

    try:
        # Get ConnInfo
        reqstr = struct.pack("6sB17s", bt.str2ba(addr), bt.ACL_LINK, "\0" * 17)
        request = array.array("c", reqstr )
        handle = fcntl.ioctl(hci_fd, bt.HCIGETCONNINFO, request, 1)
        handle = struct.unpack("8xH14x", request.tostring())[0]

        # Get RSSI
        cmd_pkt=struct.pack('H', handle)
        rssi = bt.hci_send_req(hci_sock, bt.OGF_STATUS_PARAM,
                     bt.OCF_READ_RSSI, bt.EVT_CMD_COMPLETE, 4, cmd_pkt)
        rssi = struct.unpack('b', rssi[3])[0]

        # Close sockets
        bt_sock.close()
        hci_sock.close()

        return rssi

    except:
        return None



macid = bluetooth.discover_devices()
#macid = ['14:30:C6:EC:DF:39']
print "The device detected has", macid

assert len(macid) > 0

print "Now determining its proximity"
far_count = 0
while True:
    
    rssi = bluetooth_rssi(macid[0])
    print rssi,
    if rssi < 0:
        far_count += 1
    else:
        far_count = 0
    
    if far_count > 5:
        print "FAR"
    else:
        print "NEAR"
print rssi
