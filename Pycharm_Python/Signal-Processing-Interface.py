# Minim branch
from scipy.fftpack import fftn
from scipy import signal
import pyaudio

time_scale = 50  # Scales the amplitude of time-domain data
normal_scale = 50
alpha_scale = 100
freq_avg_scale = 50  # Scales the amplitude for averages of frequency data
alpha_center = 10
alpha_bandwidth = 2
beta_center = 25
beta_bandwidth = 2
num_channels = 1
sample_rate = 44100
buffer_size = 32768
seconds = 2  # How many seconds of data to display / analyze at once
frame_rate = 60
in_buffer = 4  # How many data points to take in at once, this*60 = sampling rate
display_buffer = [[0 for i in range(frame_rate * in_buffer * seconds)] for j in range(num_channels)]
time_length = len(display_buffer[0])  # Number of samples/sec in time


# Spectrogram variables
col_max = 840
row_max = 100
col = 0
left_edge = 0
R = 0
G = 0
B = 0

# Window interface & variables scaling data to readable sizes
window_width = 840
window_height = 500
scaling = {.00202, .002449 / 2, .0075502 / 2, .00589, .008864, .01777}
fft_rect_width = 18
scale_freq = 1.33
time_domain_average = 0

# Handling bad data variables
cut_off_height = 200  # Frequency height to throw out "bad data" for averaging after
absolute_cutoff = 1.5
absolute_bad_data_flag = False  # absoluteBadDataFlag: Data that is bad because it's way too far out of our desired range --
                                # ex: shaking your head for a second

average_bad_data_flag = False  # averageBadDataFlag: Data that's bad because it spikes too far outside of the average for that second --
                                # ex: blinking your eyes for a split second

# Constants used to create a running average of the data.
average_length = 200  # averages about the last 5 seconds worth of data
average_bins = 6  # we have 6 types of brain waves
counter = 0

# Initialize 2D array of averages for running average calculation
averages = [[0 for i in range(average_length)] for j in range(average_bins)]

p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16,
                channels=num_channels,
                rate=sample_rate,
                input=True,
                frames_per_buffer=buffer_size)


def setup():
    # Set drawing parameters
    fft_height = window_height - 200

    # Set size of window interface
    size(window_width, window_height)

    # Initialize minim and filter objects
    # NotchFilter: Frame size of 4,096 samples gives us 2048 frequency bands or bins
    # This gives a bin width of ~21 Hz (giving worse resolution at low freq and better at high freq)
    # bin width = frequency / number of bins
    lpfr = LowPassSP(30, 44100)
    hpfr = HighPassSP(7, 44100)
    notch = signal.iirnotch(60, 30)
    betaFilter = BandPass(beta_center / scale_freq, beta_bandwidth / scale_freq, 44100)
    alphaFilter = BandPass(alpha_center / scale_freq, alpha_bandwidth / scale_freq, 44100)


def draw():
    """
    badDataFlag handles any "artifacts" we may pick up while recording the data.
    Artifacts are essentially imperfections in the data recording -- they can come
    from muscle movements, blinking, anything that disturbs the electrodes. If the
    program encounters a set of data that spikes out of a reasonable window
    (controlled by the variable cutoffHeight), it won't consider that data
    when computing the running average.
    """
    global counter, average_bad_data_flag

    background(0)  # Make sure the background color is black
    stroke(255)  # Time data is drawn in white

    line(0, 100, window_width, 100)  # Line separating time and frequency data

    draw_signal_data()

    # check for spikes relative to other data
    for i in range(window_width - 1):
        if abs(in2.left.get((i + 1) * round(in2.bufferSize() / window_width))) > time_domain_average * 4:
            average_bad_data_flag = True

    display_text()

    display_freq_averages()

    counter += 1


# Draw the signal in time and frequency.
def draw_signal_data():
    global col, left_edge, sgram, averages, time_domain_average
    # Performing forward FFT on samples from the left buffer
    fftn(in2.left)

    # Defining spectral values
    for i in range(row_max):
        sgram[i][col] = round(max(0, 2 * 20 * (log(1000 * fft.getBand(i) / log(10)))))
    col = col + 1  # Next column on next loop

    if col == col_max:
        col = 0  # Once this wraps around, reset columns to 0

    # Drawing the spectrogram points
    for i in range(len(col_max - left_edge)):
        for j in range(row_max):
            clr = sgram[j][i + left_edge]
            hex_clr = Integer.toHexString(clr)
            hex.append(hex_clr)
            if hex.length() != 6:
                while hex.length() < 6:
                    hex.append(000000)
            R = Integer.valueOf(hex.substring(0, 2), 16)
            G = Integer.valueOf(hex.substring(2, 4), 16)
            B = Integer.valueOf(hex.substring(4, 6), 16)
            stroke(R, G, B)
            point(i, j)
            hex.setLength(0)

    # Drawing the rest of the image as the beginning of the array
    for i in range(left_edge):
        for j in range(row_max):
            clr = sgram[j][i]
            hex_clr = Integer.toHexString(clr)
            hex.append(hex_clr)
            if hex.length() != 6:
                while hex.length() < 6:
                    hex.append(000000)
            R = Integer.valueOf(hex.substring(0, 2), 16)
            G = Integer.valueOf(hex.substring(2, 4), 16)
            B = Integer.valueOf(hex.substring(4, 6), 16)
            stroke(R, G, B)
            point(i + col_max - left_edge, j)
            hex.setLength(0)
    left_edge = left_edge + 1  # Move left by one, moving the spectrogram to the left
    if left_edge == col_max:
        left_edge = 0  # Wraps around in a circular array

    time_domain_average = 0
    for i in range(window_width - 1):

        # Data that fills our window is normalized to +-1, so we want to throw out
        # sets that have data that exceed this by the factor absoluteCutoff
        if abs(in2.left.get(i * round(in2.bufferSize() / window_width))) * time_scale / normal_scale > .95:
            absoluteBadDataFlag = True
            fill(250, 250, 250)
            stroke(150, 150, 150)

    time_domain_average += abs(in2.left.get(i * round(in2.bufferSize() / window_width)))

    # Draw un-averaged frequency bands of signal.
    if i < (window_width - 1) / 2:
        # Set colors for each type of brain wave
        if i <= round(3 / scale_freq):
            fill(0, 0, 250)  # Delta (Red) (~1-4 Hz)
            stroke(25, 0, 225)

        if i >= round(4 / scale_freq) and i <= round((alpha_center - alpha_bandwidth) / scale_freq) - 1:
            fill(50, 0, 200)  # Theta (Red) (~4-7 Hz)
            stroke(75, 0, 175)

        if i >= round((alpha_center - alpha_bandwidth) / scale_freq) and i <= round(
                (alpha_center + alpha_bandwidth) / scale_freq):
            fill(100, 0, 150)  # Alpha (Red - Light Purple) (~7-12 Hz)
            stroke(125, 0, 125)

        if i >= round((alpha_center + alpha_bandwidth) / scale_freq) + 1 and i <= round(
                (beta_center - beta_bandwidth) / scale_freq) - 1:
            fill(150, 0, 100)  # Low Beta (Light Purple - Purple)) (~12-16 Hz)
            stroke(175, 0, 75)

        if i >= round((beta_center - beta_bandwidth) / scale_freq) and i <= round(
                (beta_center + beta_bandwidth) / scale_freq):
            fill(200, 0, 50)  # Midrange Beta (Purple) (~16-20 Hz)
            stroke(225, 0, 25)

        if i >= round((beta_center + beta_bandwidth) / scale_freq) + 1 and i <= round(30 / scale_freq):
            fill(250, 0, 0)  # High Beta (Purple - Light Blue) (~20-30 Hz)
            stroke(255, 0, 10)

        if i >= round(32 / scale_freq):
            fill(240, 240, 240)  # Noise (30-60 Hz)
            stroke(200, 200, 200)

        if i == round(60 / scale_freq):
            fill(200, 200, 200)  # Color 60 Hz a different tone of grey,
            stroke(150, 150, 150)  # to see how much noise is in data

    # draw the actual frequency bars
    rect(fft_rect_width * i, FFTheight, fft_rect_width * (i + 1), FFTheight - fft.getBand(i) * 20)

    # divide the average by how many time points we have
    time_domain_average = time_domain_average / (window_width - 1)


# Give user textual information on data being thrown out and filters we have active.
def display_text():
    # show user when data is being thrown out
    text("absoluteBadDataFlag = " + absolute_bad_data_flag, window_width - 200, 120)
    if absolute_bad_data_flag:
        print("absoluteBadDataFlag = " + absolute_bad_data_flag)
        print(counter)

    text("averageBadDataFlag = " + average_bad_data_flag, window_width - 200, 140)
    if average_bad_data_flag:
        print("averageBadDataFlag = " + average_bad_data_flag)
        print(counter)

    # and when a filter is being applied to the data
    text("alpha filter is " + in2.hasEffect(alphaFilter), window_width - 200, 160)
    text("beta filter is " + in2.hasEffect(betaFilter), window_width - 200, 180)


# Compute and display averages for each brain wave for the past ~5 seconds.
def display_freq_averages():
    # Show averages of alpha, beta, etc. waves
    for i in range(6):
        avg = 0  # Raw data for amplitude of section of frequency
        low_freq = 0
        hi_freq = 0

        # Set custom frequency ranges to be averaged
        if i == 0:
            low_freq = 0
            hi_freq = 3
            fill(0, 0, 250)
            stroke(25, 0, 225)

        if i == 1:
            low_freq = 3
            hi_freq = 7
            fill(50, 0, 200)
            stroke(75, 0, 175)

        if i == 2:
            low_freq = alpha_center - alpha_bandwidth
            hi_freq = alpha_center + alpha_bandwidth
            fill(100, 0, 150)
            stroke(125, 0, 125)

        if i == 3:
            low_freq = 12
            hi_freq = 15
            fill(150, 0, 100)
            stroke(175, 0, 75)

        if i == 4:
            low_freq = beta_center - beta_bandwidth
            hi_freq = beta_center + beta_bandwidth
            fill(200, 0, 50)
            stroke(225, 0, 25)

        if i == 5:
            low_freq = 20
            hi_freq = 30
            fill(250, 0, 0)
            stroke(255, 0, 10)

        # Convert frequencies to FFT bands. Because of our FFT parameters(256, 256),
        # these are equal (each band has a 1 Hz width).
        low_bound = fft.freqToIndex(low_freq)
        hi_bound = fft.freqToIndex(hi_freq)

        # Scale the band number, issue outlined in ACCREDITATION file
        low_bound = round(low_bound / scale_freq)
        hi_bound = round(hi_bound / scale_freq)

        # Get average for frequencies in range
        j = low_bound
        while j <= hi_bound:
            avg += fft.getBand(j)
            j += 1

        avg /= (hi_bound - low_bound + 1)

        # Scale the bars so that it fits our window better
        for k in range(6):
            if i == k:
                avg *= scaling[i] * freq_avg_scale

        # Update array for the moving average (only if our data is "good")
        if absolute_bad_data_flag is False and average_bad_data_flag is False:
            averages[i][counter % average_length] = avg

        # Calculate the running average for each frequency range
        sum_avg = 0
        for k in range(len(average_length)):
            sum_avg += averages[i][k]  # Adding to sum_avg from 2D averages array

        sum_avg = sum_avg / average_length  # Averaging sum_avg

        # Draw averaged/smoothed frequency ranges
        rect(i * width / 6, height, (i + 1) * width / 6, height - sum_avg * 20)


# Always close PyAudio classes when you are done with them
def stop():
    stream.stop_stream()
    stream.close()
    super.stop()
