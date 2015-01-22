import bluetooth
from sys import byteorder
import wave
import alsaaudio
import mutagen
import mutagen.mp3
from mutagen.id3 import ID3, TPE2, TCMP, APIC, TAL, TRCK
import time
import sys
import socket
import os
import eyed3
from ftplib import FTP
import time
from threading import Thread
import cPickle as pickle

TEST = False

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


#CONFIGURATIONS FOR RECORDING(DO NOT CHANGE)
#DEFAULT CONFIGURATIONS
RATE = 44100
NO_CHANNELS = 1
SAMPLE_WIDTH = 2
CHUNK_SIZE = 1024

#CONFIGURATIONS FOR ALSA
inp = None
if TEST is False:
    card = 'sysdefault:CARD=Mic'
else:
    card = 'sysdefault:CARD=Generic_1'
    
#OTHER CONFIGURATIONS
FOUND = False
FILENAME = None
ENTER = False
MACID = "None"
NOT_FOUND_COUNT = 0
CHECK_DEVICE = False

MIN_RECORD_TIME *= 60

def configure_alsa():

    global card, inp, NO_CHANNELS, RATE, CHUNK_SIZE    
    
    inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, 0, card)
    inp.setchannels(NO_CHANNELS)
    inp.setrate(RATE)
    inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
    inp.setperiodsize(CHUNK_SIZE)
    
def record():

    global MIN_RECORD_TIME, p, RATE, FOUND, COPY_COUNT, COPY_LIMIT, CHECK_DEVICE, index_of_device, FILENAME
    
    print "recording ..."
    w = wave.open(FILENAME, 'w')
    w.setnchannels(NO_CHANNELS)
    w.setsampwidth(SAMPLE_WIDTH)
    w.setframerate(RATE)
    
    record_limit = MIN_RECORD_TIME
    past_time = time.time()
    delta_time = 0    
    
    past_time = time.time()
    delta_time = 0
    while delta_time < record_limit:
        delta_time = int(time.time() - past_time)
        l, data = inp.read()
        w.writeframes(data)
    w.close()

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
    macid_string = unicode(' , '.join(macids))

    audiofile = eyed3.load(FILENAME)
    
    #set the tags of the metadata
    audiofile.tag.artist = unicode(present_time)
    audiofile.tag.album = unicode(CARE_HOME)
    #audiofile.tag.genre = unicode(RESIDENT_ID + "," + macid_string)
    audiofile.tag.genre = unicode(macid_string)
    audiofile.tag.description = unicode(RESIDENT_ID)
    audiofile.tag.save()
    
    MACID = "None"
    
    print "Done adding metadata.."
    
def main():
    
    global FOUND, MACID, FILENAME, p
    print "Now Starting operations"
    configure_alsa()
    while True:
        present_time = time.strftime("%d-%m-%Y_%H:%M:%S")
        FILENAME = RESIDENT_ID + present_time + ".mp3"
        record()
        print "Finished recording"
        add_metadata(MACID, present_time)
        print "PRESS ctrl+z NOW"
        break

main()
