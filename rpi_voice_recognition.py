#Python 2.x program for Speech Recognition
##Program uses Picovoice free triggerwords from Porcupine
##and google voice recognition--both are free
##Porcupine has ten free triggerwords including Jarvis, Terminator, Bumblebee, Porcupine, etc...

#imported libraries/modules for setup
# from selenium import webdriver
#***************************************************************************************
#SEARCH FOR LIBRARIES ONLINE IF THESE ARE DON'T WORK
import speech_recognition as sr #https://pypi.org/project/SpeechRecognition/2.1.3/
import webbrowser
import time
import RPi.GPIO as GPIO
from subprocess import call
from time import sleep
import os
import struct
import pyaudio #https://pypi.org/project/PyAudio/
import pvporcupine #https://pypi.org/project/pvporcupine/
import random
import alsaaudio #sudo -H pip3 install pyalsaaudio
from pynput.keyboard import Key, Controller #https://pypi.org/project/pynput/





#General Purpose Input Output (GPIO) pins setup
#Fan relay is connected to GPIO 20
#Speaker relay is connected to GPIO 21
#motor controller (L298) connected to GPIO 23,24,25
#led visual status light is connected to GPIO 4--let's you see if 'jarvis' is listening
Fan = 20

Speakers = 21

in1 = 24
in2 = 23
en = 25
led = 4
 
callState = False
speakerState = False
GPIO20_State = True
playstate = False
lidstate = False
browserstate = False
GPIO.setmode(GPIO.BCM)
#GPIO setup for LED listening state visual queue
GPIO.setup(led, GPIO.OUT)
#GPIO setup for fans and speakers using 5v relays
GPIO.setup(Fan, GPIO.OUT)
GPIO.setup(Speakers, GPIO.OUT)
#GPIO setup for lid motor using l298 motor driver
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
p=GPIO.PWM(en,1000)
p.start(50)


keyboard = Controller()
#enter the name of usb microphone that you found
#using lsusb
#the following name is only used as an example
mic_name = "default"

#Sample rate is how often values are recorded
sample_rate = 48000
#Chunk is like a buffer. It stores 2048 samples (bytes of data)
#here.
#it is advisable to use powers of 2 such as 1024 or 2048
chunk_size = 2048
#Initialize the recognizer
r = sr.Recognizer()

#generate a list of all audio cards/microphones
mic_list = sr.Microphone.list_microphone_names()

#the following loop aims to set the device ID of the mic that
#we specifically want to use to avoid ambiguity.
for i, microphone_name in enumerate(mic_list):
    print("*********************************************")
    print(microphone_name)
    print("*********************************************")
    if microphone_name == mic_name:
        device_id = i

currentvolume = '150'
porcupine = None
pa = None
audio_stream = None
m = alsaaudio.Mixer()
current_volume = m.getvolume()
#open lid function
def up():
    print('raising lid')
    for y in range(50,60,2):
        p.ChangeDutyCycle(y)
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.HIGH)
        sleep(.1)
       
    sleep(.9)
    for y in range(60,50,-2):
        p.ChangeDutyCycle(y)
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.HIGH)
        sleep(.1)
       
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.LOW)
#close lid function
def down():
    print('lowering lid')
    for y in range(50,60,2):
        p.ChangeDutyCycle(y)
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        sleep(.1)
       
    sleep(.3)
    for y in range(60,40,-5):
        p.ChangeDutyCycle(y)
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        sleep(.2)
       
    GPIO.output(in1,GPIO.LOW)
    GPIO.output(in2,GPIO.LOW)

#adjust function for lid
def adjust():
    if lidstate == False:
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        sleep(.3)
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.LOW)
    else:
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.HIGH)
        sleep(.3)
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.LOW)
       
#simple multiplication function-- Jarvis speaks the answer
def multiplyList(myList) :
     
    # Multiply elements one by one
    result = 1
    for x in myList:
         result = result * x
    return result
#Different responses for variety's sake
wake_response = [['espeak','-a15', '-s150', '-v', 'mb-en1', '-z','how can i be of service, sir?'],
                 ['espeak','-a15', '-s100', '-v', 'mb-en1', '-z','yes sir?'],
                 ['espeak','-a15', '-s150', '-v', 'mb-en1', '-z','hello? you said something'],
                 ['espeak','-a15', '-s170', '-v', 'mb-en1', '-z',"I'm listening"],
                 ['espeak','-a15', '-s170', '-v', 'mb-en1', '-z',"Yes lord robinson?"]
                 ]
status_response = [['espeak','-a15', '-s150', '-v', 'mb-en1', '-z','I am well, sir. Thank you for asking'],
                 ['espeak','-a15', '-s100', '-v', 'mb-en1', '-z','Good sir?'],
                 ['espeak','-a15', '-s150', '-v', 'mb-en1', '-z','Doing Great!'],
                 ['espeak','-a15', '-s150', '-v', 'mb-en1', '-z',"couldn't be better sir!  "],
                 ['espeak','-a15', '-s130', '-v', 'mb-en1', '-z',"Status: all systems running at optimal performance!"]
                 ]

sound_response = [['espeak','-a15', '-s125', '-v', 'mb-en1', '-z','it is nice to be heard, sir'],
                 ['espeak','-a15', '-s130', '-v', 'mb-en1', '-z','loud and clear!'],
                 ['espeak','-a15', '-s140', '-v', 'mb-en1', '-z','I can speak!'],
                 ['espeak','-a15', '-s140', '-v', 'mb-en1', '-z',"Ready to communicate!"],
                 ['espeak','-a15', '-s130', '-v', 'mb-en1', '-z',"Thank you for giving me a voice in this world sir"]
                 ]
genpurp_response = [['espeak','-a15', '-s150', '-v', 'mb-en1', '-z',"absolutely sir!"],
                 ['espeak','-a15', '-s140', '-v', 'mb-en1', '-z','Right away sir!'],
                 ['espeak','-a15', '-s140', '-v', 'mb-en1', '-z',"Yes sir! I'll attend to that directly!" ],
                 ['espeak','-a15', '-s140', '-v', 'mb-en1', '-z',"of course, right away!"],
                 ['espeak','-a15', '-s130', '-v', 'mb-en1', '-z',"As you wish sir"]
                 ]
try:
    porcupine = pvporcupine.create(keywords=["jarvis", "terminator", "bumblebee","porcupine"])

    pa = pyaudio.PyAudio()

    audio_stream = pa.open(
                    rate=porcupine.sample_rate,
                    channels=1,
                    format=pyaudio.paInt16,
                    input=True,
                    frames_per_buffer=porcupine.frame_length)
    while True:
        wake_resp = random.randint(0,len(wake_response)-1)
        stat_resp = random.randint(0,len(status_response)-1)
        sound_resp = random.randint(0,len(sound_response)-1)
        genpurp_resp = random.randint(0,len(genpurp_response)-1)
        pcm = audio_stream.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)

        keyword_index = porcupine.process(pcm)
        #Responds if keyword is said --Jarvis, terminator, bumblebee, or porcupine
        if keyword_index >= 0:
            if playstate == True:
                keyboard.press(Key.space)
                sleep(.3)
                keyboard.release(Key.space)
            callState = True
            GPIO.output(led,callState)
            time.sleep(.5)
            GPIO.output(led,False)
            call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
            call(wake_response[wake_resp])
            call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
            GPIO.output(led,callState)
           
               
            #use the microphone as source for input. Here, we also specify
            #which device ID to specifically look for incase the microphone
            #is not working, an error will pop up saying "device_id undefined"
            with sr.Microphone(device_index =  device_id, sample_rate = sample_rate, chunk_size = chunk_size) as source:
                #wait for a second to let the recognizer adjust the
                #energy threshold based on the surrounding noise level
                r.adjust_for_ambient_noise(source)
                print ("Say Something")
                #listens for the user's input
                audio = r.listen(source)
                try:
                    text = r.recognize_google(audio)
                    print ("you said: " + text)
                    ##turns fans on GPIO20 with relay
                    if('cool' == text or 'turn fans on' == text or 'turn cooling on' == text or 'turn on fans' == text or 'turn on the fans' == text  or 'turn the fans on' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         GPIO.output(Fan, True)
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                    #turns fans off GPIO20 -- with relay
                    elif('off' == text or 'turn off cooling' == text or 'turn off fans' == text or 'turn fans off' == text or 'turn off the fans' == text or 'turn the fans off' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         GPIO.output(Fan, False)
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                    elif('volume' == text or 'set volume' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(['espeak','-a15', '-s130', '-v', 'mb-en1', '-z',"what percent sir?"])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         with sr.Microphone(device_index =  device_id, sample_rate = sample_rate, chunk_size = chunk_size) as source:
                             #wait for a second to let the recognizer adjust the
                             #energy threshold based on the surrounding noise level
                             r.adjust_for_ambient_noise(source)
                             print ("Say Something")
                             #listens for the user's input
                             audio = r.listen(source)
                             try:
                                 text = r.recognize_google(audio)
                                 print(text)
                                 currentvolume = text
                                 call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                                 call(["espeak",'-a15', '-s130', '-v', 'mb-en1', '-z',"volume set to"+text])
                                 call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo',currentvolume+'%'])
                                 call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', text+'%'])
                                 callState = False
                                 GPIO.output(led,callState)
                                 
                                 if playstate == True:
                                    keyboard.press(Key.space)
                                    sleep(.3)
                                    keyboard.release(Key.space)
                             except sr.UnknownValueError:
                                 call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                                 call(["espeak",'-a15', '-s130', '-v', 'mb-en1', '-z',"invalid input"])
                                 call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo',currentvolume+'%'])
                                 callState = False
                                 GPIO.output(led,callState)
                                 if playstate == True:
                                    keyboard.press(Key.space)
                                    sleep(.3)
                                    keyboard.release(Key.space)
                    #turns speakers on --GPIO21 with relay 
                    elif('sound' == text or 'turn on sound' == text or 'sound on' == text or 'turn sound on' == text or 'speak up' == text or 'speak up man' == text or 'let me hear you' == text):
                         GPIO.output(Speakers, True)
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                    #does multiplication responds with the answer
                    elif(('what is' in text or 'how much' in text) and '*' in text):
                         print('caught it')  
                         numbers = []
                         for word in text.split():
                           if word.isdigit():
                              numbers.append(int(word))

                         product = multiplyList(numbers)
                         print(product)
                         answer = str(product)
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(['espeak','-a15', '-s150', '-v', 'mb-en1', '-z', answer])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                           
                    #opens projector lid  
                    elif('open projector' == text or 'open projector lid' == text or 'open lid' == text or 'open the projector lid' == text or 'open the projector' == text or 'open the lid' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                         if lidstate == False:
                            up()
                            lidstate = True
                    #closes projector lid
                    elif('close projector' == text or 'close projector lid' == text or 'close lid' == text or 'close the projector lid' == text or 'close the projector' == text or 'close the lid' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                         if lidstate == True:
                            down()
                            lidstate = False; 
                    #Adjusts projector lid in last direction... eg. if last direction was openning, this opens it a little bit more     
                    elif('adjust projector' == text or 'adjust projector lid' == text or 'adjust lid' == text or 'adjust' == text or 'adjust the projector' == text or 'adjust the lid' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                         adjust()
                    #Does nothing except respond 
                    elif('status' == text or 'how are you' == text or 'status report' == text or 'how are you doing' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(status_response[stat_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                    #does nothing except respond with "hi to you too"
                    elif('hi' == text or 'high' == text or 'hola' == text or 'jello' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(['espeak','-a15', '-s150', '-v', 'mb-en1', '-z','Hi to you too!'])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                    #uses keyboard commands to go to next song on youtue
                    elif('next' == text or 'next song' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                         with keyboard.pressed(Key.shift):
                            keyboard.press('n')
                            keyboard.release('n')

                    #uses keyboard commands to go to previous son on youtube
                    elif('previous' == text or 'previous song' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                         with keyboard.pressed(Key.shift):
                            keyboard.press('p')
                            keyboard.release('p')
                    
                    #
                    elif('pause' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                        
                    elif('play' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)  
                            keyboard.release(Key.space)
                    #Puts GPIO 21 low--> Relay connected to speaker system--Turns them off
                    elif('silence' == text or 'be quiet' == text or 'turn off sound' == text or 'sound off' == text or 'turn sound off' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         GPIO.output(Speakers, False)
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                    #opens project lid, fans on, opens browser to movie streaming website** 
                    elif('movie' == text or 'I want to watch a movie' == text or 'movie time' == text or 'show me a movie' == text):
                         GPIO.output(Fan, True)
                         GPIO.output(Speakers, True)
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         webbrowser.open("https://ww1.123moviesfree.net")
                         callState = False
                         GPIO.output(led,callState)
                         browserstate = True
                         playstate = True
                         if lidstate == False:
                            up()
                            lidstate = True
                    
                    #opens projector lid and turns on fans to play retropie games on second Rpi
                    elif('play time' == text or 'I want to play Nintendo' == text or 'Nintendo' == text):
                         GPIO.output(Fan, True)
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         playstate = True
                         if lidstate == False:
                            up()
                            lidstate = True

                    #closes current tab, turns off fans and closes projector lid
                    elif('goodbye' == text or 'shut down' == text or 'shutdown' == text or 'turn everything off' == text or 'turn off everything' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(['espeak','-a15', '-s130', '-v', 'mb-en1', '-z',"Goodbye"])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         GPIO.output(Fan, False)
                         callState = False
                         if browserstate == True:
                             os.system("pkill chromium")
                             browserstate = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                         if lidstate == True:
                            down()
                            lidstate = False
                    
                    #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
                    # the following commands open browser window and plays defined song as first song of playlist

                    elif("Jessie's Girl" == text or "I want Jessie's girl" == text or "play Jessie's Girl" == text):
                         call(genpurp_response[genpurp_resp])
                         webbrowser.open('https://www.youtube.com/watch?v=qYkbTyHXwbs&list=RDqYkbTyHXwbs&start_radio=1')
                         callState = False
                         GPIO.output(led,callState)
                         
                         playstate = True
                    elif("Stuck in the middle with you" == text or "play jokers to the right" == text or "Play Stuck In The Middle With You" == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         playstate = True
                         browserstate = True
                         webbrowser.open('https://www.youtube.com/watch?v=OMAIsqvTh7g&list=RDOMAIsqvTh7g&start_radio=1')
                   
                    elif("Vivaldi" == text or "play Vilvadi" == text or "Play Vilvadi" == text or "Four Seasons" == text or "play four seasons" == text or "classical" == text or "play classical" == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         playstate = True
                         webbrowser.open('https://www.youtube.com/watch?v=GRxofEmo3HA')
                    elif("the witch" == text or "play witchy woman" == text or "play the witch" == text or "give me the witch" == text):
                         call(genpurp_response[genpurp_resp])
                         callState = False
                         GPIO.output(led,callState)
                         browserstate = True
                         webbrowser.open('https://www.youtube.com/watch?v=eVXqocPAz1k&list=RDeVXqocPAz1k&index=1')
                         playstate = True
                    elif("the stones" == text or "play Rolling Stones" == text or "throw me some stones" == text or "show me some stones" == text or "give me something hard and fast" == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         browserstate = True
                         webbrowser.open('https://www.youtube.com/watch?v=O4irXQhgMqg&list=RDO4irXQhgMqg&start_radio=1')
                         playstate = True
                    elif("the chain" == text or "give me the chain" == text or "play the chain" == text or "chain" == text or "Fleetwood Mac" == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         browserstate = True
                         webbrowser.open('https://www.youtube.com/watch?v=JDG2m5hN1vo&list=RDJDG2m5hN1vo&start_radio=1')
                         playstate = True
                    elif("Pumped Up Kicks" == text or "play Pumped Up Kicks" == text or "outrun my gun" == text or "play outrun my bullets" == text or "outrun my bullets" == text or "outrun my bullets sucker" == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         browserstate = True
                         webbrowser.open('https://www.youtube.com/watch?v=SDTZ7iX4vTQ&list=RDSDTZ7iX4vTQ&start_radio=1')
                         playstate = True
                    #&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

                    #gives the current time
                    elif('time' == text or 'what time is it' == text or 'give me the time' == text):
                         t = time.localtime()
                         current_time = time.strftime("%H:%M:%S", t)
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(['espeak','-a15', '-s130', '-v', 'mb-en1', '-z',current_time])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                    #closes the current browser window
                    elif('close browser' == text or 'close all tabs' == text or 'close' == text or 'close the browser' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         os.system("pkill chromium")
                         callState = False
                         browserstate = False
                         GPIO.output(led,callState)
                         playstate = False
                    #cancels google ai listening mode and resets to pico-voice listening for trigger word
                    elif('cancel' == text or 'cancel that' == text or 'nevermind' == text):
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(["espeak",'-a15', '-s130', '-v', 'mb-en1', '-z',"cancelling"])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                    #opens Football streaming website--
                    elif('gametime' in text or 'football games today' in text or 'I want to watch the game' == text):
                         callState = False
                         GPIO.output(Fan, True)
                         GPIO.output(Speakers, True)
                         GPIO.output(led,callState)
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(genpurp_response[genpurp_resp])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         #footaball streaming website
                         webbrowser.open("https://playing.stream2watch.sx/football-1/")
                         playstate = True
                         browserstate = True
                         if lidstate == False:
                            up()
                            lidstate = True
                    else:
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                         call(["espeak",'-a15', '-s130', '-v', 'mb-en1', '-z',"I have no such command in my database!"])
                         call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                         callState = False
                         GPIO.output(led,callState)
                         if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
                #error occurs when google could not understand what was said
               
                except sr.UnknownValueError:
                        print("Google Speech Recognition could not understand audio")
                        call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo','150%'])
                        call(["espeak",'-a15', '-s130', '-v', 'mb-en1', '-z',"I am sorry, but I didn't understand!"])
                        call(['pactl','set-sink-volume', 'alsa_output.platform-soc_audio.analog-stereo', currentvolume+'%'])
                        callState = False
                        GPIO.output(led,callState)
                        if playstate == True:
                            keyboard.press(Key.space)
                            sleep(.3)
                            keyboard.release(Key.space)
##                except sr.RequestError as e:
##                        print("Could not request results from GoogleSpeech Recognition service; {0}".format(e)
finally:
    if porcupine is not None:
        porcupine.delete()

    if audio_stream is not None:
        audio_stream.close()

    if pa is not None:
            pa.terminate()
