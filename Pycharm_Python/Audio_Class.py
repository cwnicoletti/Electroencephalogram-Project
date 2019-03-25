import pyaudio
import struct
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

FORMAT = pyaudio.paInt16
NUM_CHANNELS = 1
RATE = 44100
INPUT_BLOCK_TIME = 0.15
BUFFER_RATE = int(RATE * INPUT_BLOCK_TIME)


def get_rms(block):
    return np.sqrt(np.mean(np.square(block)))


def process_block(snd_block):
    f, t, sxx = signal.spectrogram(snd_block, RATE, nperseg=64, nfft=256, noverlap=60)
    decibels = 10 * np.log10(sxx)
    return t, f, decibels


def plot_spec(x, y, z):
    plt.pcolormesh(x, y, z, cmap='inferno')
    plt.show()
    plt.pause(0.05)
    plt.clf()
    plt.cla()


class AudioInput(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.get_mic_stream()

    def stop(self):
        self.stream.close()

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

        stream = self.pa.open(format=FORMAT,
                              channels=NUM_CHANNELS,
                              rate=RATE,
                              input=True,
                              input_device_index=device_index,
                              frames_per_buffer=BUFFER_RATE)

        return stream

    def listen(self):
        try:
            plt.ion()
            while True:
                raw_block = self.stream.read(BUFFER_RATE, exception_on_overflow=False)
                count = len(raw_block) / 2
                format = '%dh' % count
                snd_block = np.array(struct.unpack(format, raw_block))
                time, frequency, intensity = process_block(snd_block)
                plot_spec(time, frequency, intensity)

        except Exception as e:
            print('Error recording: {}'.format(e))
            return
