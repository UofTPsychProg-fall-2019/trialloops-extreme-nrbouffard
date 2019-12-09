#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Trialloops extreme- collect responses and give feedback
@author: nrbouffard
"""
#%% Required set up 
# this imports everything you might need and opens a full screen window
# when you are developing your script you might want to make a smaller window 
# so that you can still see your console 
import numpy as np
import pandas as pd
import os, sys
from psychopy import visual, core, event, gui, logging


# global shutdown key for debugging!
event.globalKeys.add(key='q',func=core.quit)

# create a gui object
subgui = gui.Dlg()
subgui.addField("Subject ID:")
subgui.addField("Session Number:")

# show the gui
subgui.show()

# put the inputted data in easy to use variables
subjID = subgui.data[0]
sessNum = subgui.data[1]

#%% prepare output

outputFileName = 'data' + os.sep + 'sub' + subjID + '_sess' + sessNum + '.csv'
if os.path.isfile(outputFileName) :
    sys.exit("data for this session already exists")

outVars = ['subj', 'trial', 'face', 'object', 'sceneFace', 'color', 'rating', 'rt','trialStart', 'trialEnd', 'val']    
out = pd.DataFrame(columns=outVars)

# create output file now, to append to as the experiment progresses
out['subj'] = subjID
out.to_csv(outputFileName,index = False)

# instruction file
instFile = 'instructions.jpeg'

# open a white full screen window
win = visual.Window(fullscr=True, allowGUI=False, color='white', units='height') 

# initialize clocks
trialClock = core.Clock() 
expClock = core.Clock() 
stimClock = core.Clock()
fbClock = core.Clock()

# read in experiment info
trialInfo = pd.read_csv('objectConds.csv')

# initialize rating scale
myScale = visual.RatingScale(win, low=1, high=7, marker='triangle',
    tickMarks=[1,2,3,4,5,6,7],markerStart=None,markerColor='black',pos = (0,-.6))

# feedback
bigFeedback = visual.TextStim(win, text='Very Vivid', pos=(0,0), height=.05, color = 'red')
smallFeedback = visual.TextStim(win, text='Not Vivid', pos=(0,0), height=.05,color = 'red')
neutFeedback = visual.TextStim(win, text='Kind of Vivid', pos=(0,0), height=.05,color = 'red')

# randomize trials
trialInfo = trialInfo.sample(frac=1)
trialInfo = trialInfo.reset_index()

# set stimulus times in seconds
isiDur = 1
stimDur = 5
fbDur = 1.5

# set number of trials
nTrials = len(trialInfo)

# prepare image for display
instr = visual.ImageStim(win, image="instructions.jpg", size = .9)

# draw image to window buffer
instr.draw()
# flip window to reveal image
event.clearEvents() # this clears any prior button presses
win.flip()

# don't do anything until a key is pressed
event.waitKeys()

# make your loop
for t in np.arange(0,nTrials) :
    
    trialClock.reset()
    
    objectLeft = visual.ImageStim(win, image =trialInfo.loc[t,'object'] , pos= (-0.5,0.2))
    faceRight = visual.ImageStim(win, image = trialInfo.loc[t,'face'],pos= (0.5,0.2))
    myText = visual.TextStim(win, text = 'vividness', pos = (0,-.25), color = 'black', height = .10) 

    # then draw all stimuli
    objectLeft.draw() 
    faceRight.draw()
    myScale.draw()
    myText.draw()

    # record trial prarameters
    out[t,'subj'] = subjID
    out.loc[t,'object'] = trialInfo.loc[t,'object']
    out.loc[t,'color'] = trialInfo.loc[t,'color']
    out.loc[t,'face'] = trialInfo.loc[t,'face']
    out.loc[t,'sceneFace'] = trialInfo.loc[t,'sceneFace']
    out.loc[t,'trial'] = t + 1
    
    # do nothing while isi is still occuring
    while trialClock.getTime() < isiDur:
        core.wait(.001)

    # then flip your window
    win.flip()
    stimClock.reset()
    # record when stimulus was prsented 
    out.loc[t, 'trialStart'] = expClock.getTime()

    
    myScale.reset()  #reset rating scale right before drawing for RT
    while myScale.noResponse and stimClock.getTime()<stimDur:
            faceRight.draw()
            objectLeft.draw()
            myScale.draw()
            myText.draw()
            win.flip()
    
     # record when stimulus removed
    if myScale.noResponse == False: 
        out.loc[t,'trialEnd'] = expClock.getTime()
     
    
    trialResp = myScale.getRating()
    trialRT = myScale.getRT()
    
        # show feedback
    if trialResp < 4:
        smallFeedback.draw()
        out.loc[t,'val'] = 'notVivid'
    elif trialResp > 4:
        bigFeedback.draw()
        out.loc[t,'val'] = 'Vivid'
    else:
        neutFeedback.draw()
        out.loc[t,'val'] = 'Neutral'
    win.flip()
    fbClock.reset()
    while fbClock.getTime() < fbDur:
        core.wait(.001)
    
    
    # save responses       
    if myScale.noResponse == False: #if response was made
         out.loc[t, 'rating'] = trialResp
         out.loc[t, 'rt'] = trialRT
         out.loc[[t]].to_csv(outputFileName, mode = 'a', header = False, index = False)
      

# finish experiment
win.flip() 
core.wait(1)
 
goodby = visual.TextStim(win, text="""Thank you for participating
                         
Please get the experimenter""", height=.05, color = 'black')  
goodby.draw()
win.flip()

#%% Required clean up
# this cell will make sure that your window displays for a while and then 
# closes properly

# manage output    
#out['subj'] = subjID
#out.to_csv(outputFileName, index = False)


core.wait(4)
win.close()
core.quit()
