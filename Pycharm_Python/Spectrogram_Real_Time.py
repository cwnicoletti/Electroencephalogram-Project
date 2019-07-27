import csv
import time
import struct
import pyaudio
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from Pycharm_Python import Plot_Buttons
from Pycharm_Python.Filters import Low_Pass_Filter, High_Pass_Filter

# Variables for the filters
first_low_cutoff = 30.0  # first low-pass cutoff frequency
first_high_cutoff = 4.0  # first high-pass cutoff frequency
fs = 1000.0  # sampling frequency
order = 1  # order of filter

# Variables for the PyAudio stream (see: get_mic_stream)
FORMAT = pyaudio.paInt16  # 16-bit depth
NUM_CHANNELS = 1  # Number of channels (we're just using one)
RATE = 1000  # Sample rate
INPUT_BLOCK_TIME = 0.5  # 500ms blocks
BUFFER_RATE = int(RATE * INPUT_BLOCK_TIME)

trial_count = 0


def get_rms(block):
    return np.sqrt(np.mean(np.square(block)))


def listen():
    global trial_count
    while True:
        x, y, z = AudioInput().process_block()
        escape_bool = plot_spec(x, y, z)
        if escape_bool is True:
            del x, y, z
            del trial_count
            plt.ioff()
            plt.clf()
            plt.cla()
            plt.close()
            return

        print('Saving...')

        column_count = 1  # Start at index [1] since [0] is label column
        size = len(x) * len(y)
        csv_spec = np.zeros(size + 1)

        ''' 
        These are the different labels of spectrogram types
        0 - nothing; random thoughts
        1 - thinking the word "hello"
        2 - thinking the word "world"
        '''

        csv_spec[0] = 1  # First column - label
        for row in range(len(y)):
            for column in range(len(x)):
                csv_spec[column_count] = z[row][column]  # Populating csv rows by concatenating spectrogram pixel rows
                column_count += 1

        with open('data/train.csv', 'a+') as brain_data_train:
            brain_csv = csv.writer(brain_data_train, delimiter=',', quotechar='"', lineterminator='\n',
                                   quoting=csv.QUOTE_MINIMAL)
            brain_csv.writerow(csv_spec)
        print('...')
        with open('data/test.csv', 'a+') as brain_data_test:
            brain_csv = csv.writer(brain_data_test, delimiter=',', quotechar='"', lineterminator='\n',
                                   quoting=csv.QUOTE_MINIMAL)
            brain_csv.writerow(csv_spec)

        trial_count += 1
        print('Saved')
        print("Trial number: ", trial_count)


def plot_spec(x, y, z):
    escape = Plot_Buttons.plot_but_close_rts()
    if escape is True:
        return escape
    plt.pause(0.01)
    plt.clf()


class AudioInput(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()

    def find_input_device(self):
        device_index = None
        for i in range(self.pa.get_device_count()):
            device_info = self.pa.get_device_info_by_index(i)

            for keyword in ['mic']:
                if keyword in device_info['name'].lower():
                    device_index = i
                    return device_index

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
        time.sleep(.2)
        print('3...')
        time.sleep(.3)
        print('2...')
        time.sleep(.3)
        print('1...')
        time.sleep(.3)

        stream = self.get_mic_stream()
        raw_block = stream.read(BUFFER_RATE, exception_on_overflow=False)
        stream.stop_stream()
        stream.close()
        self.pa.terminate()
        count = len(raw_block) / 2
        block_format = '%dh' % count
        snd_block = np.array(struct.unpack(block_format, raw_block))
        snd_block = Low_Pass_Filter.butter_low_pass_filter(snd_block, first_low_cutoff, fs, order=4)
        snd_block = High_Pass_Filter.butter_high_pass_filter(snd_block, first_high_cutoff, fs, order=4)

        f, t, sxx = signal.spectrogram(snd_block, RATE,
                                       window='hamming',
                                       nperseg=int((RATE * (INPUT_BLOCK_TIME / 2))) + 151,
                                       noverlap=int((RATE * (INPUT_BLOCK_TIME / 2))) + 150,
                                       nfft=2 ** 14)

        fmin = 4  # Hz
        fmax = 30  # Hz
        freq_slice = np.where((f >= fmin) & (f <= fmax))
        f = f[freq_slice]
        sxx = sxx[freq_slice, :][0]

        return t, f, sxx
