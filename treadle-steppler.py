#!/usr/bin/python
import fileinput
import re
import sys
import os
import termios, fcntl

inWeftColors = 0
inTreadling  = 0
sequenceCnt  = 1
stepCnt      = 0
treadles     = []
weftColors   = {}
repeats      = 1
fileName     = ""
colorSet     = {0: 'ltGreen', 1: 'Blue', 2: 'Green', 3: 'Black'}

if len(sys.argv) - 1 == 2:  
    fileName     = sys.argv[1]
    repeats      = int(sys.argv[2])
elif len(sys.argv) - 1 == 1:
    fileName     = sys.argv[1] 
else:
    print "need a wif with optional repeats"
    exit()

def wait_key():
    ''' Wait for a key press on the console and return it. '''
    result = None
    if os.name == 'nt':
        import msvcrt
        result = msvcrt.getch()
    else:
        import termios
        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
    #print result
    return result

fileHandle = open(fileName, "r")

#for line in fileinput.input():
with open(sys.argv[1]) as fileHandle:
    for line in fileHandle:
        line = line.rstrip()
        if re.match("\[TREADLING\]",line):
            inWeftColors = 0
            inTreadling = 1
            continue
        elif re.match('\[WEFT COLORS\]',line):
            inWeftColors = 1
            inTreadling = 0
            continue
        if inTreadling == 1 and re.match('\d+=\d+',line):
            step, treadle = line.split('=')
            treadles.append(treadle.rstrip())
        elif inWeftColors == 1 and re.match('\d+=\d+',line):
            step, color = line.split('=')
            weftColors[int(step)] = color
            if not weftColors.get(0):
                weftColors[0] = color
        elif inTreadling == 1 and not re.match('\d+=\d+',line):
            inTreadling = 0
            inStep = 0
        elif inWeftColors == 1 and not re.match('\d+=\d+',line):
            inWeftColors = 0
            inStep = 0
#print weftColors

def treadleOut(thisTreadle, thisStep, nextTreadle, prevTreadle, thisColor, seq):
    # if thisColor == '26':
        # thisColor = 3
    # elif thisColor == 3:
        # thisColor = 2
    # elif thisColor == '1':
        # thisColor == 1
    # elif thisColor == '2':
        # thisColor = 2
        
#    print "    {}  step: {}    {} <- -> {} color: {}   sequence: {}".format(thisTreadle, thisStep, prevTreadle, nextTreadle, thisColor, seq)
    print "    {}  step: {}    {} <- -> {} color: {}   ".format(thisTreadle, thisStep, prevTreadle, nextTreadle, thisColor)
    # print "<html><body><table border=2><tr>"
    # print "<tr><th>Treadle</th><th>Step</th><th>Prev</th><th>Next</th><th>Color</th><th>Sequence</th></tr>"
    # print "<tr><td align=center><h2>{}</h2></td><td align=center>{}</td><td align=center>{}</td><td align=center>{}</td><td align=center>{}</td><td align=center>{}</td></tr>".format(thisTreadle, thisStep, prevTreadle, nextTreadle, thisColor, seq)
    # print "</table></body></html>"
    

def loop_treadles():
    stepCnt = len(treadles)
    doSteps = 1
    step = 0
    color = 0
    while doSteps == 1:
        if len(weftColors) == 0:
            color = 0
        elif len(weftColors) < len(treadles):
            color = 0
        else:
            color = weftColors[step]
        if weftColors.get(step+1):
            color = weftColors[step+1]
        else:
            if color == 0:
                color = 0
        if step == 0:
            treadleOut(treadles[0], step+1 , treadles[0], treadles[step+1], color, sequenceCnt)
            #print "    {}  step: {}          -> {} color: {} sequence: {}".format(treadles[0], step+1 , treadles[step+1], color, sequenceCnt)
        elif step > 0 and step < len(treadles)-1:
            treadleOut(treadles[step], step+1, treadles[step-1], treadles[step+1], color, sequenceCnt)
            #print "    {}  step: {}    {} <- -> {} color: {} sequence: {}".format(treadles[step], step+1, treadles[step-1], treadles[step+1], color, sequenceCnt)
        elif step == len(treadles)-1:
            treadleOut(treadles[step], step+1, treadles[step], treadles[step-1], color, sequenceCnt)
            #print "    {}  step: {}    {} <-       color: {} sequence: {} end of sequence".format(treadles[step], step+1, treadles[step-1], color, sequenceCnt)
            print
        theKey = wait_key()
        step += 1
        if step == stepCnt:
            doSteps = 0
        if theKey == 'b':
            step = step - 2
            if step < 0:
                step = 0
        elif theKey == 'q':
            exit()
            
        print


while True:
    loop_treadles()
    sequenceCnt += 1
    if sequenceCnt > repeats:
        exit()
