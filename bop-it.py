#!/use/bin/python3
import os,urllib,urllib2
import threading
import numpy as np
import RPi.GPIO as GPIO
import lcddriver
from time import time,sleep 
import random
 
 
#set up the GPIO pins
GPIO.setmode(GPIO.BOARD)
#buttons
GPIO.setup(11,GPIO.IN, pull_up_down=GPIO.PUD_UP) #start button
GPIO.setup(29,GPIO.IN,pull_up_down=GPIO.PUD_UP) # blue button
GPIO.setup(36,GPIO.IN,pull_up_down=GPIO.PUD_UP) #exit button
#rotary setup
input_A = 38
input_B = 40
GPIO.setup(input_A,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(input_B,GPIO.IN,pull_up_down=GPIO.PUD_UP)
old_a = True
old_b = True
#lcd screen object
lcd = lcddriver.lcd()
#varibles to send highscore tweet
BASE_URL = 'https://api.thingspeak.com/apps/thingtweet/1/statuses/update/'
KEY = 'T75CEW0C3H102J8Q'
 
 
 
#global varibiles 
 
start = False
game_start = True
gamemode = True
button1on = True
old_input = True
round = 1
 
#game speed and game level
speed = {0:1000,1:740,2:650,3:600,4:550,5:500}
level = {1 : 20, 2 : 15, 3: 10, 4 : 5 , 5 : 3} 
 
 
 
#scores
score = 0
final_score = 0
highscores = {1:[],2:[],3:[],4:[],5:[]} #dict for highscores
 
def send_tweet(score):
    status = 'Another player just played Bop Pi and scored: ' + str(score)
    data = urllib.urlencode({'api_key' : KEY, 'status': status})
    response = urllib2.urlopen(url=BASE_URL, data = data)
    print(response.read())
def gameover():
    global score
    lcd.lcd_clear()
    lcd.lcd_display_string("     Game Over", 1)
    lcd.lcd_display_string("   Final Score: " +str(score),2)
    sleep(3)
    lcd.lcd_clear()
    lcd.lcd_display_string(" Scores posted live", 1)
    lcd.lcd_display_string("     @BotPhrank    ",2)
    lcd.lcd_display_string("     On Twitter    ",3)
    send_tweet(score)
    sleep(4)
    lcd.lcd_clear()
    F = open("highscores.txt",'a')
    F.write(str(score) + '\n' )
    F.close()
    T = open("highscores.txt",'r')
    highscore = T.readline()
    for line in T.readlines():
        print(line)
        if line > highscore:
            highscore = line
    print(highscore)
    lcd.lcd_display_string("Highscore: " + highscore,2)
    sleep(5)
    game_start = False
    return
def get_encoder_turn():     
     # return -1, 0, or +1    
    global old_a, old_b
    result = 0
    new_a = GPIO.input(input_A)
    new_b = GPIO.input(input_B)
    if new_a != old_a or new_b != old_b :
        if old_a == 0 and new_a == 1 :
            result = (old_b * 2 - 1)
    elif old_b == 0 and new_b == 1:
        result = -(old_a * 2 - 1)
    old_a, old_b = new_a, new_b
    sleep(0.001)
    return result
 
def twistIt():
    while True:
        change = get_encoder_turn()
        if change != 0:
            print("Scored a point")
            sleep(0.2)
            return 1
         
 
def pushIt():
    while True:
        input_s = GPIO.input(11)
        if input_s == False:
            print("scored a point")
            sleep(0.2)
            return 1
 
def play_game(currtime):
    global score
    rand = random.randint(0,1)
    stime = currtime
    if(rand == 0):
        lcd.lcd_clear()
        lcd.lcd_display_string("Points:" + str(score) + "    Time:" + str(stime) ,1)
        lcd.lcd_display_string("      PUSH IT!", 2)
    #GPIO.remove_event_detect(11)
        score = score + pushIt()
    return score
        lcd.lcd_clear()
    if(rand == 1):
        lcd.lcd_clear()
        lcd.lcd_display_string("Points:" + str(score)+ "   Time:" + str(stime),1)
        lcd.lcd_display_string("      TWIST IT!",2)
        #GPIO.remove_event_detect(input_A)
        score = score + twistIt()
    return score
        lcd.lcd_clear()
def game(start, game_start):
    global score
    global round
    while game_start:
        lcd.lcd_display_string(" Hello! Welcome to ",1)
            lcd.lcd_display_string("     Bop Pi", 2)
            sleep(3)
            lcd.lcd_clear()
            lcd.lcd_display_string("   Press the start",1)
            lcd.lcd_display_string("   button to begin",2)
        while True:
            button1 = GPIO.input(29) #start
            button2 = GPIO.input(36) #exit
            if button1 == False: #if the start button is pushed, begin the gam
                lcd.lcd_clear()
                lcd.lcd_display_string("Round: " + str(round),2)
                sleep(1.5)
                lcd.lcd_clear()
                lcd.lcd_display_string("Amount of time:" + str(level[round]) +"sec",2)
                sleep(1.5)
                start = True
                            sleep(0.5)
                begin = time()
            if button2 == False:
                lcd.lcd_clear()
                lcd.lcd_display_string("Thanks for playing!!",2)
                sleep(3)
                lcd.lcd_clear()
                return
 
            while start:
                currtime = time() - begin
                score = play_game(int(currtime))
                print(int(currtime))
                if int(currtime) >= level[round] :
                    gameover()
                    score = 0
                    lcd.lcd_clear()
                    lcd.lcd_display_string("Next Round      Quit",1)
                        lcd.lcd_display_string(" |                |",2)
                    lcd.lcd_display_string(" V                V ",3)
                    begin = 0
                    round = round + 1
                    start = False
 
#start game
game(start,game_start)
