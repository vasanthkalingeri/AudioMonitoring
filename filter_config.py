from bluetooth import *
ALLOW_FILENAME = "list.txt"

def macid_config():
 
    nearby_devices = discover_devices()
    print "found %d devices" % len(nearby_devices)

    print nearby_devices
    my_list = []
    for i in range (0, len(nearby_devices)):
        my_list.append(nearby_devices[i])

    f = open(ALLOW_FILENAME, "w")

    for item in my_list:
        print "item", item  
        f.write(str(item) + "\n")
    f.close()

macid_config()    
