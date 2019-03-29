import csv
import struct
import pyaudio
import numpy as np
from scipy import signal
import matplotlib.pyplot as plt
from Pycharm_Python import Plot_Buttons
from Pycharm_Python import Low_Pass_Filter

cutoff = 200  # cutoff frequency
fs = 44100  # sampling frequency
order = 2  # order of filter

FORMAT = pyaudio.paInt16
NUM_CHANNELS = 1
RATE = 44100
INPUT_BLOCK_TIME = 0.5
BUFFER_RATE = int(RATE * INPUT_BLOCK_TIME)

escape = False


def get_rms(block):
    return np.sqrt(np.mean(np.square(block)))


def process_block():
    raw_block = get_mic_stream().read(BUFFER_RATE, exception_on_overflow=False)
    stream.close()
    pa.terminate()
    count = len(raw_block) / 2
    format = '%dh' % count
    snd_block = np.array(struct.unpack(format, raw_block))

    # nperg=178, noverlap=8: gives 129 x 129 x 129
    # nperg=64, noverlap=60: gives 5197 x 129 x 129
    # nperg=64, noverlap=50: gives 1571 x 129 x 129 -- middle-point, will use
    f, t, sxx = signal.spectrogram(snd_block, RATE, nperseg=64, nfft=256, noverlap=50)

    if escape is True:
        return
    with np.errstate(divide='raise'):
        try:
            decibels = 10 * np.log10(sxx)
        except FloatingPointError as e:
            print('Error processing decibels: {}'.format(e))
            print('Retrying...')
            return process_block()

    f = Low_Pass_Filter.butter_low_pass_filter(f, cutoff, fs, order)
    return t, f, decibels


def listen():
    while True:
        if escape is True:
            stream.close()
            AudioInput().pa.terminate()
            return

        time, frequency, intensity = process_block()
        plot_spec(time, frequency, intensity)


def plot_spec(x, y, z):
    global escape
    plt.pcolormesh(x, y, z, cmap='inferno')
    escape = Plot_Buttons.plot_but_close()
    plt.pause(0.02)
    plt.clf()


def get_pyaudio():
    global pa
    pa = pyaudio.PyAudio()
    return pa


def find_input_device():
    device_index = None
    for i in range(get_pyaudio().get_device_count()):
        device_info = pa.get_device_info_by_index(i)
        print('Device {}: {}'.format(i, device_info['name']))

        for keyword in ['mic']:
            if keyword in device_info['name'].lower():
                print('Found an input: device {} - {}'.format(i, device_info['name']))
                device_index = i
                return device_index

    if device_index is None:
        print('No preferred input found. Using default input device.')

    return device_index


def get_mic_stream():
    device_index = find_input_device()
    global stream
    stream = pa.open(format=FORMAT,
                     channels=NUM_CHANNELS,
                     rate=RATE,
                     input=True,
                     input_device_index=device_index,
                     frames_per_buffer=BUFFER_RATE)

    print("THINK")
    return stream
