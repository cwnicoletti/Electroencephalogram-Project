import time
import struct
import pyaudio
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from Pycharm_Python import Plot_Buttons
from Pycharm_Python import Low_Pass_Filter
from Pycharm_Python import High_Pass_Filter
from Pycharm_Python import Instructions_Page

# Variables for the filters
first_low_cutoff = 60.0  # first low-pass cutoff frequency
second_low_cutoff = 31.0  # second low-pass cutoff frequency
first_high_cutoff = 4.0  # first high-pass cutoff frequency
fs = 44100.0  # sampling frequency
order = 1  # order of filter
alpha_low = 8
alpha_high = 15
beta_low = 16
beta_high = 31

# Variables for the PyAudio stream (see: get_mic_stream)
FORMAT = pyaudio.paInt16  # 16-bit depth
NUM_CHANNELS = 1  # Number of channels (we're just using one)
RATE = 44100  # Sample rate
INPUT_BLOCK_TIME = 0.5  # 500ms blocks
BUFFER_RATE = int(RATE * INPUT_BLOCK_TIME)


def get_rms(block):
    return np.sqrt(np.mean(np.square(block)))


def plot_spec(x, y, z):
    print('Plotting Spectrogram...')
    plt.pcolormesh(x, y, z, cmap='inferno')  # Plots x, y, z as a spectrogram in the color 'inferno'
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    print('Finished Plotting')


'''
shows instructions page
'''
def show_instructions():
    Instructions_Page.plot_but_instructions()
    Instructions_Page.plot_but_next()
    fig = plt.figure(1)
    fig.canvas.set_window_title('Instructions')
    plt.show()
    fig.canvas.set_window_title('Brain-Wave Spectrogram')


'''
This is the first function called in the program
It simply opens a window with two buttons plotted
'''
def listen():
    try:
        show_instructions()
        plt.clf()
        Plot_Buttons.plot_but_record()
        Plot_Buttons.plot_but_close()
        plt.show()

    except Exception as e:
        print('Error recording: {}'.format(e))
        return


'''
AudioInput is a class that holds the object "AudioInput"
It's here to share a local variable between the functions self.pa
This allows the program to only open PyAudio once (instead of every time it's called)
'''
class AudioInput(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()

    # Function simply finds the default audio device to use
    def find_input_device(self):
        device_index = None
        for i in range(self.pa.get_device_count()):
            device_info = self.pa.get_device_info_by_index(i)
            print('Device {}: {}'.format(i, device_info['name']))

            for keyword in ['mic']:
                if keyword in device_info['name'].lower():
                    print('Found an input: device {} - {}'.format(i, device_info['name']))
                    device_index = i
                    return device_index

        if device_index is None:
            print('No preferred input found. Using default input device.')

        return device_index

    def get_mic_stream(self):
        device_index = self.find_input_device()
        print("THINK")
        stream = self.pa.open(format=FORMAT,
                              channels=NUM_CHANNELS,
                              rate=RATE,
                              input=True,
                              input_device_index=device_index,
                              frames_per_buffer=BUFFER_RATE)

        return stream

    def process_block(self):
        print('Starting Recording in...')
        time.sleep(.5)
        print('3...')
        time.sleep(.5)
        print('2...')
        time.sleep(.5)
        print('1...')
        time.sleep(.5)

        stream = self.get_mic_stream()
        raw_block = stream.read(BUFFER_RATE, exception_on_overflow=False)  # Reads in 500ms of audio
        print('End Recording')
        time.sleep(.5)
        stream.stop_stream()
        stream.close()
        self.pa.terminate()

        count = len(raw_block) / 2
        block_format = '%dh' % count
        snd_block = np.array(struct.unpack(block_format, raw_block))
        snd_block = Low_Pass_Filter.butter_low_pass_filter(snd_block, second_low_cutoff, fs, order)
        snd_block = High_Pass_Filter.butter_high_pass_filter(snd_block, first_high_cutoff, fs, order)

        # nperg=178, noverlap=8: gives 129 x 129 x 129
        # nperg=64, noverlap=60: gives 5197 x 129 x 129
        # nperg=64, noverlap=50: gives 1571 x 129 x 129 -- middle-point, will use
        print('Creating Spectrogram')
        f, t, sxx = signal.spectrogram(snd_block, RATE, nperseg=64, noverlap=50, nfft=256)
        print(len(f))
        print(len(t))
        print(len(sxx))
        print('Finished Creating')

        # We'll be working with decibels since this program functions similarly to voice recognition
        # Hint: Human hearing works logarithmically (Reason for: np.log10)
        with np.errstate(divide='raise'):
            try:
                decibels = 10 * np.log10(sxx)
            except FloatingPointError as e:
                print('Error processing decibels: {}'.format(e))
                print('Retrying...')
                return AudioInput().process_block()

        f = Low_Pass_Filter.butter_low_pass_filter(f, second_low_cutoff, fs, order)
        f = High_Pass_Filter.butter_high_pass_filter(f, first_high_cutoff, fs, order)

        print("Frequency[1]: ", f[1])
        return t, f, decibels

    # Deletes AudioInput object manually, since program only terminates once "Close"d
    def __del__(self):
        print("Deleting AudioInput Object")
