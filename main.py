TEST_RECORD = False  #This tests only recording functionality
TEST_BLUETOOTH = False

import bluetooth
import time
from sys import byteorder
import wave
import alsaaudio
import mutagen
import mutagen.mp3
from mutagen.id3 import ID3, TPE2, TCMP, APIC, TAL, TRCK
import sys
import socket
import os

if TEST_RECORD is False:
    import eyed3
    
from ftplib import FTP
from threading import Thread
import cPickle as pickle


#TO BE USER DEFINED
#The index of the mic connected to the PI
index_of_device = 1

#Change this value to change the minimum record time
MIN_RECORD_TIME = 0.1 #This is in minutes


#change these to alter the metadata tags as per your needs
RESIDENT_ID = "287A"
CARE_HOME = "RodwellFarm"
SERVER = "ftp.rodwellfarm.co.uk"
USERNAME = "rodwca450762"
PASSWORD = "ROd$g20{{rd3("
DIRECTORY = "resilink/am" #This is the directory where everything should go to in the server
ALLOW_FILENAME = "list.txt"
ALLOWED = open(ALLOW_FILENAME).readlines()
ALLOWED = [i.strip() for i in ALLOWED]

#CONFIGURATIONS FOR RECORDING(DO NOT CHANGE)
#DEFAULT CONFIGURATIONS
RATE = 44100
NO_CHANNELS = 2
SAMPLE_WIDTH = 2
CHUNK_SIZE = 1024


#CONFIGURATIONS FOR ALSA
#inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE)
if TEST_RECORD is True:
    card = 'sysdefault:CARD=Generic_1'#Mic'
else:
    card = 'sysdefault:CARD=Mic'
inp = None

def configure_alsa():

    global card, inp, NO_CHANNELS, RATE, CHUNK_SIZE    
    
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, 0, card)
    inp.setchannels(NO_CHANNELS)
    inp.setrate(RATE)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(CHUNK_SIZE)

#OTHER CONFIGURATIONS
FOUND = False
FILENAME = None
ENTER = False
MACID = []
NOT_FOUND_COUNT = 0
CHECK_DEVICE = False
RSSI = 0 #Low value indicates device is far

MIN_RECORD_TIME *= 60

def nearby(mac):
    
    """Returns True if the device is nearby, the distance is set based on RSSI"""    
    rssi = bluetooth_rssi(mac)
    if rssi >= RSSI:
        return True
    else:
        return False
            
def scan():
    
    global FOUND, MACID, NOT_FOUND_COUNT, MIN_RECORD_TIME, CHECK_DEVICE, ALLOWED
    print "Scanning for nearby devices..."
    FOUND = False
    NOT_FOUND_COUNT = 0
    i = 0
    while True:
        i += 1
        if TEST_RECORD is True:
            FOUND = True
            time.sleep(4)
        else:            
            try:
                macid = bluetooth.discover_devices()
                
#                print macid
                NOT_FOUND_COUNT = 1
                for mac in macid:
                    if mac in ALLOWED and near(mac):
                        MACID.append(mac)
                        NOT_FOUND_COUNT = 0
                        print "Device found"
                        FOUND = True
                        break
                if NOT_FOUND_COUNT != 0:
                    print "Device out of range", NOT_FOUND_COUNT
                    FOUND = False
                    NOT_FOUND_COUNT += 1
                    MACID = []
            except:
                print "Bluetooth device is not connected correctly, please connect it within 10 seconds"
                time.sleep(15)
                continue
            print "searching, ", i

    return

def record():

    global MIN_RECORD_TIME, p, RATE, FOUND, COPY_COUNT, COPY_LIMIT, CHECK_DEVICE, index_of_device, FILENAME, MACID
    
    print "recording ..."
    w = wave.open(FILENAME, 'wb')
    w.setnchannels(NO_CHANNELS)
    w.setsampwidth(SAMPLE_WIDTH)
    w.setframerate(RATE)
    
    record_limit = MIN_RECORD_TIME
    
    macids = MACID #This is the macids for which the recording is being made
    
    while FOUND is True:
        past_time = time.time()
        delta_time = 0
        while delta_time <= record_limit:
            delta_time = int(time.time() - past_time)
            l, data = inp.read()
            w.writeframes(data)
        print "done", FOUND
        if TEST_RECORD is True:
            FOUND = False
    w.close()
    return macids
#    inp.close()

def add_metadata(macids, present_time):
    
    global FILENAME, CARE_HOME, MACID
    print "Adding metadata"
    
    #create all the id3 tags to attach metadata
    id3 = ID3()
    id3.add(TPE2(encoding=3, text="title"))
    id3.add(TPE2(encoding=3, text="artist"))
    id3.add(TPE2(encoding=3, text="album"))
    id3.add(TPE2(encoding=3, text="genre"))
    id3.add(TPE2(encoding=3, text="description"))
    id3.save(FILENAME)
    
    present_time = unicode(present_time)
    macids = ','.join(macids)
    macid_string = unicode(macids)

    if TEST_RECORD is False:    
        audiofile = eyed3.load(FILENAME)
        
        #set the tags of the metadata
        audiofile.tag.artist = unicode(present_time)
        audiofile.tag.album = unicode(CARE_HOME)
        #audiofile.tag.genre = unicode(RESIDENT_ID + "," + macid_string)
        audiofile.tag.genre = unicode(macid_string)
        audiofile.tag.description = unicode(RESIDENT_ID)
        audiofile.tag.save()
        
        MACID = []
    
    print "Done adding metadata.."
    
def send_mp3_file(server, username, password):
    
    global FILENAME
    print "Sending the mp3 file to the server..."
    ftp = None
    try:
        ftp = FTP(server)
    except:
        print "SERVER SEEMS TO BE INVALID/ SERVER NOT FOUND"
        return
    try:
        ftp.login(username, password)
    except:
        print "WRONG USERNAME OR PASSWORD"
        return
    try:
        ftp.cwd(DIRECTORY)
        ftp.storbinary('STOR ' + FILENAME, open(FILENAME, 'rb'))
        ftp.close()
    except:
        print "NO SUCH DIRECTORY IN THE SERVER"
        return
    os.remove(FILENAME)
    print "Done sending data"
    return
    
def main():
    
    global FOUND, MACID, FILENAME, p
    t = Thread(target=scan)
    t.start()
    time.sleep(4)
    print "Now Starting operations"
    configure_alsa()
    if TEST_BLUETOOTH:
        return
        
    while True:
        if FOUND is True:
            present_time = time.strftime("%d-%m-%Y_%H:%M:%S")
            FILENAME = RESIDENT_ID + present_time + ".mp3"
            macids = record()
            print "Finished recording"
            add_metadata(macids, present_time)
            
            if TEST_RECORD is False:
                print """Now we send the file across server"""
                nt = Thread(target=send_mp3_file, args=(SERVER, USERNAME, PASSWORD))
                nt.start()
            else:
                print "Press Ctrl+Z"
                break

main()
