import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from Pycharm_Python import Data_Collection_Spectrogram

escape = False
trial_count = 0


def plot_but_record():
    axes_record = plt.axes([0.1, 0.02, 0.1, 0.075])
    record_spec = Button(axes_record, 'Record')
    record_spec.on_clicked(recording_funcs)
    axes_record.button = record_spec


def plot_but_save():
    axes_save = plt.axes([0.3, 0.02, 0.1, 0.075])
    save_spec = Button(axes_save, 'Save')
    save_spec.on_clicked(saving_funcs)
    axes_save.button = save_spec


def plot_but_close():
    axes_close = plt.axes([0.81, 0.02, 0.1, 0.075])
    close_spec = Button(axes_close, 'Close')
    close_spec.on_clicked(closing_funcs)
    axes_close.button = close_spec


def closing_funcs(self):
    plt.ioff()
    plt.clf()
    plt.cla()
    plt.close()


def plot_but_close_rts():
    global escape
    axes_close = plt.axes([0.81, 0.02, 0.1, 0.075])
    close_rts_spec = Button(axes_close, 'Close')
    close_rts_spec.on_clicked(closing_funcs_rts)
    axes_close.button = close_rts_spec
    return escape


def closing_funcs_rts(self):
    global escape
    escape = True
    plt.ioff()
    plt.clf()
    plt.cla()
    plt.close()
    return escape


def recording_funcs(self):
    plt.clf()
    global x, y, z
    x, y, z = Data_Collection_Spectrogram.AudioInput().process_block()
    Data_Collection_Spectrogram.plot_spec(x, y, z)

    plot_but_record()
    plot_but_save()
    plot_but_close()
    print('Done')


def saving_funcs(self):
    global trial_count
    print('Saving...')
    count = 1
    size = len(x) * len(y)
    csv_spec = np.zeros(size+1)
    csv_spec[0] = 0
    for i in range(len(y)):
        for j in range(len(x)):
                csv_spec[count] = z[i][j]
                count += 1
    # 0 - nothing, 1 - hello, 2 - world
    with open('data/train.csv', 'a+') as brain_data_train:
        brain_csv = csv.writer(brain_data_train, delimiter=',', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        brain_csv.writerow(csv_spec)
    print('...')
    with open('data/test.csv', 'a+') as brain_data_test:
        brain_csv = csv.writer(brain_data_test, delimiter=',', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        brain_csv.writerow(csv_spec)
    print('...')
    trial_count += 1
    print('Saved')
    print("Trial number: ", trial_count)
