from scipy.fftpack import fftn
from scipy import signal
import pyaudio

timeScale = 50  # Scales the amplitude of time-domain data
normalScale = 50
alphaScale = 100
freqAvgScale = 50  # Scales the amplitude for averages of frequency data
alphaCenter = 10
alphaBandwidth = 2
betaCenter = 25
betaBandwidth = 2
NUM_CHANNELS = 1
seconds = 2  # How many seconds of data to display / analyze at once
fRate = 60
inBuffer = 4  # How many data points to take in at once, this*60 = sampling rate
displayBuffer = [[0 for i in range(fRate * inBuffer * seconds)] for j in range(NUM_CHANNELS)]
timeLength = len(displayBuffer[0])  # Number of samples/sec in time

# Spectrogram variables
colmax = 840
rowmax = 100
col = 0
leftedge = 0
R = 0
G = 0
B = 0

# Window interface & variables scaling data to readable sizes
windowWidth = 840
windowHeight = 500
scaling = {.00202, .002449 / 2, .0075502 / 2, .00589, .008864, .01777}
FFTrectWidth = 18
scaleFreq = 1.33
timeDomainAverage = 0

# Handling bad data variables
cutoffHeight = 200  # Frequency height to throw out "bad data" for averaging after
absoluteCutoff = 1.5

# Constants used to create a running average of the data.
averageLength = 200  # averages about the last 5 seconds worth of data
averageBins = 6  # we have 6 types of brain waves
counter = 0


# --------------------------Functions------------------------------------------------------
def setup():
    # Initialize 2D array of averages for running average calculation
    averages = [[0 for i in range(averageLength)] for j in range(averageBins)]

    # Set drawing parameters
    FFTheight = windowHeight - 200

    # Set size of window interface
    size(windowWidth, windowHeight)

    # Initialize minim and filter objects
    # NotchFilter: Frame size of 4,096 samples gives us 2048 frequency bands or bins
    # This gives a bin width of ~21 Hz (giving worse resolution at low freq and better at high freq)
    # bin width = frequency / number of bins
    lpfr = LowPassSP(30, 44100)
    hpfr = HighPassSP(7, 44100)
    notch = signal.iirnotch(60, 30)
    betaFilter = BandPass(betaCenter / scaleFreq, betaBandwidth / scaleFreq, 44100)
    alphaFilter = BandPass(alphaCenter / scaleFreq, alphaBandwidth / scaleFreq, 44100)




def draw():
    """
    badDataFlag handles any "artifacts" we may pick up while recording the data.
    Artifacts are essentially imperfections in the data recording -- they can come
    from muscle movements, blinking, anything that disturbs the electrodes. If the
    program encounters a set of data that spikes out of a reasonable window
    (controlled by the variable cutoffHeight), it won't consider that data
    when computing the running average.
    """
    absoluteBadDataFlag = False  # absoluteBadDataFlag: Data that is bad because it's way too far out of our desired range --
    # ex: shaking your head for a second

    averageBadDataFlag = False  # averageBadDataFlag: Data that's bad because it spikes too far outside of the average for
    # that second --
    # ex: blinking your eyes for a split second

    background(0)  # Make sure the background color is black
    stroke(255)  # Time data is drawn in white

    line(0, 100, windowWidth, 100)  # Line separating time and frequency data

    drawSignalData()

    # check for spikes relative to other data
    for i in range(windowWidth - 1):
        if abs(in2.left.get((i + 1) * round(in2.bufferSize() / windowWidth))) > timeDomainAverage * 4:
            averageBadDataFlag = True

    displayText()

    displayFreqAverages()

    counter += 1


# Draw the signal in time and frequency.
def drawSignalData():
    # Performing forward FFT on samples from the left buffer
    fftn(in2.left)

    # Defining spectral values
    for i in range(rowmax):
        sgram[i][col] = round(max(0, 2 * 20 * (log(1000 * fft.getBand(i) / log(10)))))
    col = col + 1  # Next column on next loop

    if (col == colmax):
        col = 0  # Once this wraps around, reset columns to 0

    # Drawing the spectrogram points
    for i in range(len(colmax - leftedge)):
        for j in range(rowmax):
            clr = sgram[j][i + leftedge]
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
    leftedge = leftedge + 1  # Move left by one, moving the spectrogram to the left
    if (leftedge == colmax):
        leftedge = 0  # Wraps around in a circular array

    timeDomainAverage = 0
    for i in range(windowWidth - 1):

        # Data that fills our window is normalized to +-1, so we want to throw out
        # sets that have data that exceed this by the factor absoluteCutoff
        if abs(in2.left.get(i * round(in2.bufferSize() / windowWidth))) * timeScale / normalScale > .95:
            absoluteBadDataFlag = True
            fill(250, 250, 250)
            stroke(150, 150, 150)

    timeDomainAverage += abs(in2.left.get(i * round(in2.bufferSize() / windowWidth)))

    # Draw un-averaged frequency bands of signal.
    if i < (windowWidth - 1) / 2:
        # Set colors for each type of brain wave
        if i <= round(3 / scaleFreq):
            fill(0, 0, 250)  # Delta (Red) (~1-4 Hz)
            stroke(25, 0, 225)

        if i >= round(4 / scaleFreq) and i <= round((alphaCenter - alphaBandwidth) / scaleFreq) - 1:
            fill(50, 0, 200)  # Theta (Red) (~4-7 Hz)
            stroke(75, 0, 175)

        if i >= round((alphaCenter - alphaBandwidth) / scaleFreq) and i <= round(
                (alphaCenter + alphaBandwidth) / scaleFreq):
            fill(100, 0, 150)  # Alpha (Red - Light Purple) (~7-12 Hz)
            stroke(125, 0, 125)

        if i >= round((alphaCenter + alphaBandwidth) / scaleFreq) + 1 and i <= round(
                (betaCenter - betaBandwidth) / scaleFreq) - 1:
            fill(150, 0, 100)  # Low Beta (Light Purple - Purple)) (~12-16 Hz)
            stroke(175, 0, 75)

        if i >= round((betaCenter - betaBandwidth) / scaleFreq) and i <= round(
                (betaCenter + betaBandwidth) / scaleFreq):
            fill(200, 0, 50)  # Midrange Beta (Purple) (~16-20 Hz)
            stroke(225, 0, 25)

        if i >= round((betaCenter + betaBandwidth) / scaleFreq) + 1 and i <= round(30 / scaleFreq):
            fill(250, 0, 0)  # High Beta (Purple - Light Blue) (~20-30 Hz)
            stroke(255, 0, 10)

        if i >= round(32 / scaleFreq):
            fill(240, 240, 240)  # Noise (30-60 Hz)
            stroke(200, 200, 200)

        if i == round(60 / scaleFreq):
            fill(200, 200, 200)  # Color 60 Hz a different tone of grey,
            stroke(150, 150, 150)  # to see how much noise is in data

    # draw the actual frequency bars
    rect(FFTrectWidth * i, FFTheight, FFTrectWidth * (i + 1), FFTheight - fft.getBand(i) * 20)

    # divide the average by how many time points we have
    timeDomainAverage = timeDomainAverage / (windowWidth - 1)


# Give user textual information on data being thrown out and filters we have active.
def displayText():
    # show user when data is being thrown out
    text("absoluteBadDataFlag = " + absoluteBadDataFlag, windowWidth - 200, 120)
    if absoluteBadDataFlag == True:
        print("absoluteBadDataFlag = " + absoluteBadDataFlag)
        print(counter)

    text("averageBadDataFlag = " + averageBadDataFlag, windowWidth - 200, 140)
    if averageBadDataFlag == True:
        print("averageBadDataFlag = " + averageBadDataFlag)
        print(counter)

    # and when a filter is being applied to the data
    text("alpha filter is " + in2.hasEffect(alphaFilter), windowWidth - 200, 160)
    text("beta filter is " + in2.hasEffect(betaFilter), windowWidth - 200, 180)


# Compute and display averages for each brain wave for the past ~5 seconds.
def displayFreqAverages():
    # Show averages of alpha, beta, etc. waves
    for i in range(6):
        avg = 0  # Raw data for amplitude of section of frequency
        lowFreq = 0
        hiFreq = 0

        # Set custom frequency ranges to be averaged
        if i == 0:
            lowFreq = 0
            hiFreq = 3
            fill(0, 0, 250)
            stroke(25, 0, 225)

        if i == 1:
            lowFreq = 3
            hiFreq = 7
            fill(50, 0, 200)
            stroke(75, 0, 175)

        if i == 2:
            lowFreq = alphaCenter - alphaBandwidth
            hiFreq = alphaCenter + alphaBandwidth
            fill(100, 0, 150)
            stroke(125, 0, 125)

        if i == 3:
            lowFreq = 12
            hiFreq = 15
            fill(150, 0, 100)
            stroke(175, 0, 75)

        if i == 4:
            lowFreq = betaCenter - betaBandwidth
            hiFreq = betaCenter + betaBandwidth
            fill(200, 0, 50)
            stroke(225, 0, 25)

        if i == 5:
            lowFreq = 20
            hiFreq = 30
            fill(250, 0, 0)
            stroke(255, 0, 10)

        # Convert frequencies to FFT bands. Because of our FFT parameters(256, 256),
        # these are equal (each band has a 1 Hz width).
        lowBound = fft.freqToIndex(lowFreq)
        hiBound = fft.freqToIndex(hiFreq)

        # Scale the band number, issue outlined in ACCREDITATION file
        lowBound = round(lowBound / scaleFreq)
        hiBound = round(hiBound / scaleFreq)

        # Get average for frequencies in range
        j = lowBound
        while j <= hiBound:
            avg += fft.getBand(j)
            j += 1

        avg /= (hiBound - lowBound + 1)

        # Scale the bars so that it fits our window better
        for k in range(6):
            if i == k:
                avg *= scaling[i] * freqAvgScale

        # Update array for the moving average (only if our data is "good")
        if absoluteBadDataFlag == False and averageBadDataFlag == False:
            averages[i][counter % averageLength] = avg

        # Calculate the running average for each frequency range
        sum = 0
        for k in range(len(averageLength)):
            sum += averages[i][k]  # Adding to sum from 2D averages array

        sum = sum / averageLength  # Averaging sum

        # Draw averaged/smoothed frequency ranges
        rect(i * width / 6, height, (i + 1) * width / 6, height - sum * 20)


# Always close Minim audio classes when you are done with them
def stop():
    in2.close()
    minim.stop()
    super.stop()
