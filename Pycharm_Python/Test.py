import matplotlib.pyplot as plt
import numpy as np

def butter_lowpass(cutoff, fs, order =1):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=1):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y


#plt.plot(4, 6)
plt.plot([1,2,3,4])
plt.ylabel('some numbers')

plt.show()
