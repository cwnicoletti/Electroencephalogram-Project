import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from Pycharm_Python import Data_Collection_Spectrogram

trial_count = 0
escape = False


def plot_but_record():
    axrecord = plt.axes([0.1, 0.02, 0.1, 0.075])
    record_spec = Button(axrecord, 'Record')
    record_spec.on_clicked(recording_funcs)
    axrecord.button = record_spec


def plot_but_save():
    axsave = plt.axes([0.3, 0.02, 0.1, 0.075])
    save_spec = Button(axsave, 'Save')
    save_spec.on_clicked(saving_funcs)
    axsave.button = save_spec


def plot_but_close():
    axclose = plt.axes([0.81, 0.02, 0.1, 0.075])
    exit_spec = Button(axclose, 'Close')
    exit_spec.on_clicked(closing_funcs)
    axclose.button = exit_spec


def plot_but_close_rts():
    global escape
    axclose = plt.axes([0.81, 0.02, 0.1, 0.075])
    exit_spec = Button(axclose, 'Close')
    exit_spec.on_clicked(closing_funcs_rts)
    axclose.button = exit_spec
    return escape


def closing_funcs(self):
    plt.ioff()
    plt.clf()
    plt.cla()
    plt.close()


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
    new_row = np.zeros(size+1)
    new_row[0] = 2
    for i in range(len(y)):
        for j in range(len(x)):
                new_row[count] = z[i][j]
                count += 1
    # 0 - nothing, 1 - hello, 2 - world
    with open('data/training.csv', 'a+') as brain_data:
        brain_csv = csv.writer(brain_data, delimiter=',', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        brain_csv.writerow(new_row)
    print('...')
    with open('data/test.csv', 'a+') as brain_data:
        brain_csv = csv.writer(brain_data, delimiter=',', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        brain_csv.writerow(new_row)
    print('...')
    trial_count += 1
    print('Saved')
    print("Trial number: ", trial_count)
