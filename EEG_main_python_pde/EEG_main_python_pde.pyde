# Imports
add_library('minim')
add_library('serial')

# Important constants that may need to be changed.
timeScale = 50 # scales the amplitude of time-domain data, can be changed
normalScale = 50
alphaScale = 100
freqAvgScale = 50 # does same for averages of frequency data
alphaCenter = 12
alphaBandwidth = 2 # really bandwidth divided by 2
betaCenter = 24
betaBandwidth = 2
NUM_CHANNELS = 2
seconds = 2 # how many seconds of data to display / analyze at once
fRate = 60
inBuffer = 4 # how many data points to take in at once, this*60 = sampling rate
displayBuffer = [[0 for i in range(fRate*inBuffer*seconds)] for j in range(NUM_CHANNELS)]
timeLength = len(displayBuffer[0]) # number of samples/sec in time 

# Variables used to store data functions/effects.
minim = Minim
in2 = AudioInput
myPort = Serial
timeSignal = [0 for i in range(240)]
fft = FFT
notch = NotchFilter
lpSP = LowPassSP
lpFS = LowPassFS
betaFilter = BandPass
alphaFilter = BandPass

# Spectrogram variables
colmax = 840
rowmax = 100
col = 0 
leftedge = 0
R = 0
G = 0
B = 0

# Constants mainly used for scaling the data to readable sizes.
windowLength = 1440
windowHeight = 900
scaling = {.00202,.002449/2,.0075502/2,.00589,.008864,.01777}
FFTrectWidth = 18
scaleFreq = 1.33
timeDomainAverage = 0

# Variables used to handle bad data
cutoffHeight = 200 # frequency height to throw out "bad data" for averaging after
absoluteCutoff = 1.5

# absoluteBadDataFlag: Data that is bad because it's way too far out of our desired range --
# ex: shaking your head for a second

# averageBadDataFlag: Data that's bad because it spikes too far outside of the average for 
# that second -- 
# ex: blinking your eyes for a split second
                             
# Constants used to create a running average of the data.
averageLength = 200 # averages about the last 5 seconds worth of data
averageBins = 6 # we have 6 types of brain waves
counter = 0

def setup():
    # Initialize array of averages for running average calculation
    averages = [[0 for i in range(averageLength)] for j in range(averageBins)]
    
    # Set some drawing parameters
    FFTheight = windowHeight - 200
    size(windowLength, windowHeight)
    
    # Initialize minim, as well as some filters
    minim = Minim(this)
    minim.debugOn()
    notch = NotchFilter(60, 10, 44100)
    lpSP = LowPassSP(40, 44100)
    lpFS = LowPassFS(60, 44100)
    betaFilter = BandPass(betaCenter / scaleFreq, betaBandwidth / scaleFreq, 44100)
    alphaFilter = BandPass(alphaCenter / scaleFreq, alphaBandwidth / scaleFreq, 44100)
    in2 = minim.getLineIn(Minim.MONO, 32768, 44100, 16)
    
    # Initialize values in array that will be used for input
    for x in range(240):
        timeSignal[x] = 0
        
    # Initialize FFT
    fft = FFT(in2.bufferSize(), in2.sampleRate())
    fft.window(FFT.HAMMING)
    rectMode(CORNERS)
    
def draw():
    """
    badDataFlag handles any "artifacts" we may pick up while recording the data.
    Artifacts are essentially imperfections in the data recording -- they can come
    from muscle movements, blinking, anything that disturbs the electrodes. If the 
    program encounters a set of data that spikes out of a reasonable window 
    (controlled by the variable cutoffHeight), it won't consider that data
    when computing the running average.
    """
    absoluteBadDataFlag = False
    averageBadDataFlag = False
    
    background(0) # make sure the background color is black
    stroke(255) # and that time data is drawn in white
    
    line(0,100,windowLength,100) # line separating time and frequency data
    
    drawSignalData()
    
    # check for spikes relative to other data
    for i in range(windowLength - 1):
        if abs(in2.left.get((i+1)*round(in2.bufferSize()/windowLength))) > timeDomainAverage*4:
            averageBadDataFlag = True
    
    displayText()
    
    displayFreqAverages()
    
    counter += 1
    
def keyPressed():
    if key == 'w':
        fft.window(FFT.HAMMING)
    if key == 'e':
        fft.window(FFT.NONE)

def serialEvent(): 
    while (Serial.available() > 0):  # While bytes available
        shiftNtimes(timeSignal, 1)

# Shifts all elements in myArray numShifts times left, resulting in the 
# [0-numShift] elements being pushed off, and the last numShift elements
# becoming zero. Does this for all data channels.
def shiftNtimes(myArray, numShifts):
    timesShifted = 0
    while timesShifted < numShifts:
        for j in range(len(timeLength) - 1):
            myArray[j] = myArray[j + 1]
        myArray[timeLength - 1] = 0
        timesShifted += 1
    
# Draw the signal in time and frequency.
def drawSignalData():
    # Performing forward FFT on samples from the left buffer
    fft.forward(in2.left);
    
    # Defining spectral values
    for i in range(rowmax):
        sgram[i][col] = round(max(0,2*20*(log(1000*fft.getBand(i)/log(10)))))
    col = col + 1 # Next column on next loop
    
    if (col == colmax): 
        col = 0 # Once this wraps around, reset columns to 0
    
    # Drawing the spectrogram points
    for i in range(len(colmax-leftedge)):
      for j in range(rowmax):
        clr = sgram[j][i+leftedge]
        hex_clr = Integer.toHexString(clr)
        hex.append(hex_clr);
        if (hex.length() != 6):
            while (hex.length() < 6):
                hex.append(000000)
        R = Integer.valueOf(hex.substring(0, 2), 16)
        G = Integer.valueOf(hex.substring(2, 4), 16)
        B = Integer.valueOf(hex.substring(4, 6), 16)
        stroke(R, G, B)
        point(i, j)
        hex.setLength(0)
    
    # Drawing the rest of the image as the beginning of the array
    for i in range(leftedge):
        for j in range(rowmax):
            clr = sgram[j][i]
            hex_clr = Integer.toHexString(clr)
            hex.append(hex_clr)
            if (hex.length() != 6):
                while (hex.length() < 6):
                    hex.append(000000)
            R = Integer.valueOf(hex.substring(0, 2), 16)
            G = Integer.valueOf(hex.substring(2, 4), 16)
            B = Integer.valueOf(hex.substring(4, 6), 16)
            stroke(R, G, B)
            point(i + colmax - leftedge, j)
            hex.setLength(0)
    leftedge = leftedge + 1 # Move left by one, moving the spectrogram to the left
    if (leftedge == colmax):
        leftedge = 0 # Wraps around in a circular array
    
    timeDomainAverage = 0
    for i in range(windowLength - 1):
        # data that fills our window is normalized to +-1, so we want to throw out
        # sets that have data that exceed this by the factor absoluteCutoff
        if abs(in2.left.get(i*round(in2.bufferSize()/windowLength)))*timeScale/normalScale > .95:
            absoluteBadDataFlag = True
            fill(250,250,250)
            stroke(150,150,150)

    timeDomainAverage += abs(in2.left.get(i*round(in2.bufferSize()/windowLength)))
      
    # Draw un-averaged frequency bands of signal.
    if i < (windowLength - 1)/2:
        # set colors for each type of brain wave
        if i <= round(3/scaleFreq):          
            fill(0,0,250)      # delta
            stroke(25,0,225)
            
        if i >= round(4/scaleFreq) and i <= round((alphaCenter - alphaBandwidth)/scaleFreq) - 1:
            fill(50,0,200)      # theta
            stroke(75,0,175)
            
        if i >= round((alphaCenter - alphaBandwidth)/scaleFreq) and i <= round((alphaCenter + alphaBandwidth)/scaleFreq):
            fill(100,0,150)      # alpha
            stroke(125,0,125)
    
        if i >= round((alphaCenter + alphaBandwidth)/scaleFreq)+1 and i <= round((betaCenter-betaBandwidth)/scaleFreq) - 1: 
            fill(150,0,100)      # low beta
            stroke(175,0,75)
        
        if i >= round((betaCenter - betaBandwidth)/scaleFreq) and i <= round((betaCenter + betaBandwidth)/scaleFreq): 
            fill(200,0,50)       # midrange beta
            stroke(225,0,25)
    
        if i >= round((betaCenter + betaBandwidth)/scaleFreq)+1 and i <= round(30/scaleFreq):
            fill(250,0,0)        # high beta
            stroke(255,0,10)
    
        if i >= round(32/scaleFreq):
            fill(240,240,240)    # rest of stuff, mainly noise
            stroke(200,200,200)
    
        if i == round(60/scaleFreq):
            fill(200,200,200)    # color 60 Hz a different tone of grey,
            stroke(150,150,150)  # to see how much noise is in data

    # draw the actual frequency bars
    rect(FFTrectWidth*i, FFTheight, FFTrectWidth*(i+1), FFTheight - fft.getBand(i)/10)
        
    # divide the average by how many time points we have
    timeDomainAverage = timeDomainAverage / (windowLength - 1)
  
# Give user textual information on data being thrown out and filters we have active.
def displayText():
    # show user when data is being thrown out
    text("absoluteBadDataFlag = " + absoluteBadDataFlag, windowLength - 200, 120)
    if absoluteBadDataFlag == True:
        print ("absoluteBadDataFlag = " + absoluteBadDataFlag)
        print (counter)
    
    text("averageBadDataFlag = " + averageBadDataFlag, windowLength - 200, 140)
    if averageBadDataFlag == True:
        print ("averageBadDataFlag = " + averageBadDataFlag)
        print (counter)
        
    # and when a filter is being applied to the data
    text("alpha filter is " + in2.hasEffect(alphaFilter), windowLength - 200, 160)
    text("beta filter is " + in2.hasEffect(betaFilter), windowLength - 200, 180)

# Compute and display averages for each brain wave for the past ~5 seconds.
def displayFreqAverages():
    # Show averages of alpha, beta, etc. waves
    for i in range(6):
        avg = 0 # raw data for amplitude of section of frequency
        lowFreq = 0
        hiFreq = 0
    
        # Set custom frequency ranges to be averaged. 
        if i == 0:
            lowFreq = 0
            hiFreq = 3
            fill(0,0,250)
            stroke(25,0,225)
    
        if i == 1:
            lowFreq = 3
            hiFreq = 7
            fill(50,0,200)
            stroke(75,0,175)
    
        if i == 2:
            lowFreq = alphaCenter - alphaBandwidth
            hiFreq = alphaCenter + alphaBandwidth
            fill(100,0,150)
            stroke(125,0,125)
    
        if i == 3:
            lowFreq = 12
            hiFreq = 15
            fill(150,0,100)
            stroke(175,0,75)
    
        if i == 4:
            lowFreq = betaCenter - betaBandwidth
            hiFreq = betaCenter + betaBandwidth
            fill(200,0,50)
            stroke(225,0,25)
    
        if i == 5:
            lowFreq = 20
            hiFreq = 30
            fill(250,0,0)
            stroke(255,0,10)
        
        # Convert frequencies we want to the actual FFT bands. Because of our
        # FFT parameters, these happen to be equal (each band has a 1 Hz width).
        lowBound = fft.freqToIndex(lowFreq)
        hiBound = fft.freqToIndex(hiFreq)
        
        # Scale the band number, because of the issue outlined at very beginning of
        # program.
        lowBound = round(lowBound/scaleFreq)
        hiBound = round(hiBound/scaleFreq)
        
        # get average for frequencies in range
        j = lowBound
        while j <= hiBound:
            avg += fft.getBand(j)
            j += 1
    
        avg /= (hiBound - lowBound + 1)
        
        # Scale the bars so that it fits our window a little better.
        for k in range(6):
            if i == k:
                avg *= scaling[i]*freqAvgScale
        
        # Update our array for the moving average (only if our data is "good")
        if absoluteBadDataFlag == False and averageBadDataFlag == False:
            averages[i][counter%averageLength] = avg
        
        # Calculate the running average for each frequency range
        sum = 0
        for k in range(len(averageLength)):
            sum += averages[i][k]
        sum = sum / averageLength
        
        # draw averaged/smoothed frequency ranges
        rect(i*width/6, height, (i+1)*width/6, height - sum)

# always close Minim audio classes when you are done with them
def stop():
  in2.close()
  minim.stop()
  super.stop()
