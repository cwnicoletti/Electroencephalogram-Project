from scipy.signal import butter, lfilter


def butter_high_pass(cutoff, fs, order):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='high', analog=False)
    return b, a


def butter_high_pass_filter(data, cutoff, fs, order):
    b, a = butter_high_pass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y