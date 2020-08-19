#!/usr/bin/env python3
#IMPORTS
import requests
import argparse
import os
import csv
import errno
import time
import configparser
from random import seed
from random import randint
from datetime import date
from datetime import datetime

#---------------------------------
#FUNCTIONS

def randomget(debug,logging,shuffles): #retrieves the random numbers
    r = requests.get('https://www.random.org/integers/?num='+str(shuffles)+'&min=100&max=999&col=5&base=10&format=plain&rnd=new')
    ranlist = [0] * shuffles #generates an empty list of appropriate length
    if r.status_code == 200: #if retrieval is successful
        for line in r:
            randomread = str(line)
        if debug == True:
           print(randomread)
        for x in range (len(ranlist)):
            plusfactor = x*5 #this increments things appropriately to skip over the junk letters in the retrieved string
            ranlist[x] = int(randomread[2+plusfactor:5+plusfactor]) #converts the string into a list
        if debug == True:
            print(ranlist)
        if logging == True:
            log.write('Tarota successfully retrieved the following '+str(shuffles)+' random number seeds from random.org:\n')
            for x in range (len(ranlist)):
                log.write(str(ranlist[x])+' ')
            log.write('\n'+ ' ' + '\n')
    else: # this generates numbers using randint if the retrieval is not successful
        for x in range (len(ranlist)):
            seed(time.time()) #seeds the pseudo-random number generator with the epoch time
            ranlist[x] = randint(100,999)
        if logging == True:
            log.write('Tarota failed to retrieve random numbers from random.org. Instead the following random seeds were generated:\n')
            for x in range (len(ranlist)):
                log.write(str(ranlist[x])+' ')
            log.write('\n'+ ' ' + '\n')
    return ranlist

def shuffdeck(carddata,ranlist,shuffles,debug,logging,reverse): #this shuffles the deck
    shufflecount = 0  #used for the log
    totalshuffles = shuffles #used for the log
    while shuffles > 0: # the shuffling loop
        shuffcard = []
        while len(carddata) > 0:
            if reverse == True: #this statement reverses the cards randomly
                for n in range (len(carddata)):
                    seed(time.time())
                    coinflip = randint (1,2)
                    if coinflip == 1:
                        if carddata[n][0] == 'A':
                            carddata[n][0] = 'B'
                        elif carddata[n][0] == 'B':
                            carddata[n][0] = 'A'
                    else:
                        pass
            seed(ranlist[shuffles-1]*time.time()) #combines the random number from random.org with the epoch time
            select = randint(0, len(carddata)) #selects a card randomly
            transfer = carddata.pop(select-1) # removes that card from the card data list
            shuffcard.append(transfer) #adds that card to the shuffled list
        carddata = shuffcard
        shuffles -= 1
        shufflecount += 1
        if debug == True:
            print (carddata,shuffles)
        if logging == True:
            log.write('Cut '+str(shufflecount)+' of '+str(totalshuffles)+':\n')
            for w in range (len(carddata)):
                log.write (str(carddata[w][5]))
                if carddata[w][0] == 'B':
                    log.write(' (reversed)')
                else:
                    pass
                log.write(', ')
            log.write(' ' + '\n')
    return carddata

#---------------------------------
#MAIN PROGRAM

parser = argparse.ArgumentParser(prog="Tarota")
parser.add_argument("-d", "--debug", action='store_true', help = "runs in debug mode.")
parser.add_argument("-l", "--log", action='store_true', help = "saves a log")
parser.add_argument("-u", "--user", action='store_true', help = "uses user config settings")
parser.add_argument("-r", "--reverse", action='store_true', help = "includes reversed cards")
parser.add_argument("sig", nargs='+', help= "The number of the Significator card" )
args = parser.parse_args()
significator = args.sig
currentdir = os.getcwd() # retrieves the current directory in which the CSVreader.py script is running
today = str(date.today())
if args.log:
    now = datetime.now()
    smalltime = now.strftime("%H:%M:%S")
    try:
        os.makedirs((currentdir) + '/Logs/')
    except OSError as exc:  # handles the error if the directory already exists
        if exc.errno != errno.EEXIST:
            raise
        pass
    logincrement = 0
    while os.path.exists((currentdir) + '/Logs/log' + ' ' + (today) + ' ' + str(logincrement) + '.txt'):
        logincrement += 1
    log = open((currentdir) + '/Logs/log' + ' ' + (today) + ' ' + str(logincrement) + '.txt', "w")
    log.write ('Tarota log number ' +str(logincrement)+ '. Date: ' + (today) + '. Time: ' +(smalltime) + '\n')
    log.write(' ' + '\n')
    logging = True
else:
    logging = False
if args.debug:
    debug = True
else:
    debug = False
if args.reverse:
    reverse = True
    if logging == True:
        log.write('Reversed cards included.\n')
        log.write(' ' + '\n')
else:
    reverse = False
    if logging == True:
        log.write('Reversed cards not included.\n')
        log.write(' ' + '\n')
config = configparser.ConfigParser()
if args.user:
    configseg = 'CURRENT'
else:
    configseg = 'DEFAULT'
config.read('Settings/config.ini')
shuffles = int(config[(configseg)]['shuffles']) #gets the number of shuffles
pronouns = config[(configseg)]['pronouns'].split() #gets the pronouns
ranlist = randomget(debug,logging,shuffles) # retrieves the random numbers
carddata = []
csv.register_dialect('tarota', delimiter=",", quoting=csv.QUOTE_NONE)
with open ('Decks/RiderWaite/Arcana.csv', "r") as arcana:
    csvobject = csv.reader(arcana, dialect='tarota')  # creates a csv object
    for row in csvobject:  # reads over all rows
        carddata.append(row)  # adds all rows to the 'tabledata' list
significator = significator[0] # converts the significator from a list to a string
if significator.isdigit() == False or int(significator) > len(carddata):
    print('Invalid Significator. Choosing random Significator.')
    seed(time.time())
    significator = randint(0,len(carddata))
sigcard = carddata.pop(int(significator)) #this removes the significator card so it is not shuffled with the rest of the deck
if logging == True:
    log.write('------------------------------\n')
    log.write('RECORD OF SHUFFLES:\n')
for x in range (shuffles):
    if logging == True:
        log.write(' \n')
        log.write('Shuffle '+str(x+1)+'\n')
    carddata = shuffdeck(carddata,ranlist,shuffles,debug,logging,reverse)
carddata.append(sigcard) # this returns the significator card to the end of the card list
if debug == True:
    for x in range (len(carddata)):
        print (str(carddata[x][5]),end='')
        if carddata[x][0] == 'B':
            print (' (reversed) ',end='')
        else:
            pass
        print (', ',end='')
print ('Significator: '+str(carddata[-1][5]))
print ('This covers '+str(pronouns[0])+': '+str(carddata[0][5]),end='')
if carddata[0][0] == 'B':
    print (' (reversed)',end='')
print ('')
print ('This is '+str(pronouns[1])+' obstacles: '+str(carddata[1][5]),end='')
if carddata[1][0] == 'B':
    print (' (reversed)',end='')
print ('')
print ('This crowns '+str(pronouns[0])+': '+str(carddata[2][5]),end='')
if carddata[2][0] == 'B':
    print (' (reversed)',end='')
print ('')
print ('This is beneath '+str(pronouns[0])+': '+str(carddata[3][5]),end='')
if carddata[3][0] == 'B':
    print (' (reversed)',end='')
print ('')
print ('This is behind '+str(pronouns[0])+': '+str(carddata[4][5]),end='')
if carddata[4][0] == 'B':
    print (' (reversed)',end='')
print ('')
print ('This is before '+str(pronouns[0])+': '+str(carddata[5][5]),end='')
if carddata[5][0] == 'B':
    print (' (reversed)',end='')
print ('')
print ('This signifies '+str(pronouns[0])+'self: '+str(carddata[6][5]),end='')
if carddata[6][0] == 'B':
    print (' (reversed)',end='')
print ('')
print ('This signifies '+str(pronouns[1])+' house: '+str(carddata[7][5]),end='')
if carddata[7][0] == 'B':
    print (' (reversed)',end='')
print ('')
print ('This signifies '+str(pronouns[1])+' hopes and fears: '+str(carddata[8][5]),end='')
if carddata[8][0] == 'B':
    print (' (reversed)',end='')
print ('')
print ('This represents what will come: '+str(carddata[9][5]),end='')
if carddata[9][0] == 'B':
    print (' (reversed)',end='')
print ('')
if logging == True: #creates the log
    log.write(' \n')
    log.write('------------------------------\n')
    log.write('THE READING:\n')
    log.write(' \n')
    log.write('Significator: ' + str(carddata[-1][5])+'\n')
    log.write('This covers ' + str(pronouns[0]) + ': ' + str(carddata[0][5]))
    if carddata[0][0] == 'B':
        log.write(' (reversed)')
    log.write('\n')
    log.write('This is ' + str(pronouns[1]) + ' obstacles: ' + str(carddata[1][5]))
    if carddata[1][0] == 'B':
        log.write(' (reversed)')
    log.write('\n')
    log.write('This crowns ' + str(pronouns[0]) + ': ' + str(carddata[2][5]))
    if carddata[2][0] == 'B':
        log.write(' (reversed)')
    log.write('\n')
    log.write('This is beneath ' + str(pronouns[0]) + ': ' + str(carddata[3][5]))
    if carddata[3][0] == 'B':
        log.write(' (reversed)')
    log.write('\n')
    log.write('This is behind ' + str(pronouns[0]) + ': ' + str(carddata[4][5]))
    if carddata[4][0] == 'B':
        log.write(' (reversed)')
    log.write('\n')
    log.write('This is before ' + str(pronouns[0]) + ': ' + str(carddata[5][5]))
    if carddata[5][0] == 'B':
        log.write(' (reversed)')
    log.write('\n')
    log.write('This signifies ' + str(pronouns[0]) + 'self: ' + str(carddata[6][5]))
    if carddata[6][0] == 'B':
        log.write(' (reversed)')
    log.write('\n')
    log.write('This signifies ' + str(pronouns[1]) + ' house: ' + str(carddata[7][5]))
    if carddata[7][0] == 'B':
        log.write(' (reversed)')
    log.write('\n')
    log.write('This signifies ' + str(pronouns[1]) + ' hopes and fears: ' + str(carddata[8][5]))
    if carddata[8][0] == 'B':
        log.write(' (reversed)')
    log.write('\n')
    log.write('This represents what will come: ' + str(carddata[9][5]))
    if carddata[9][0] == 'B':
        log.write(' (reversed)')
    log.write('\n')
    log.close()