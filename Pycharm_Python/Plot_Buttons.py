

import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from Pycharm_Python import Data_Collection_Spectrogram


def plot_but_record():
    axrecord = plt.axes([0.1, 0.02, 0.1, 0.075])
    record_spec = Button(axrecord, "Record")
    record_spec.on_clicked(recording_funcs)
    axrecord.button = record_spec


def plot_but_save():
    axsave = plt.axes([0.3, 0.02, 0.1, 0.075])
    save_spec = Button(axsave, "Save")
    save_spec.on_clicked(saving_funcs)
    axsave.button = save_spec


def plot_but_close():
    axclose = plt.axes([0.81, 0.02, 0.1, 0.075])
    exit_spec = Button(axclose, "Close")
    exit_spec.on_clicked(closing_funcs)
    axclose.button = exit_spec


def closing_funcs(self):
    global escape
    plt.ioff()
    plt.clf()
    plt.cla()
    plt.close()
    Data_Collection_Spectrogram.AudioInput().stop()
    escape = True
    return


def recording_funcs(self):
    global x, y, z
    x, y, z = Data_Collection_Spectrogram.process_block()
    Data_Collection_Spectrogram.plot_spec(x, y, z)
    plt.show()

    plot_but_record()
    plot_but_save()
    plot_but_close()


def saving_funcs(self):
    count = 0
    size = len(x) * len(y)
    new_row = np.zeros(size)
    for i in range(len(x)):
            for j in range(len(y)):
                new_row[count] = z[j][i]
                count += 1
    with open('brain_data.csv', 'a+') as brain_data:
        brain_csv = csv.writer(brain_data, delimiter=',', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        brain_csv.writerow(new_row)

    plot_but_record()
    plot_but_close()
