import csv
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from Pycharm_Python import Data_Collection_Spectrogram


def plot_but_record():
    axes_record = plt.axes([0.1, 0.02, 0.1, 0.075])
    record_spec = Button(axes_record, 'Record')
    record_spec.on_clicked(ButtonFunctions().recording_funcs)
    axes_record.button = record_spec


def plot_but_save():
    axes_save = plt.axes([0.3, 0.02, 0.1, 0.075])
    save_spec = Button(axes_save, 'Save')
    save_spec.on_clicked(ButtonFunctions().saving_funcs)
    axes_save.button = save_spec


def plot_but_close():
    axes_close = plt.axes([0.81, 0.02, 0.1, 0.075])
    exit_spec = Button(axes_close, 'Close')
    exit_spec.on_clicked(ButtonFunctions().closing_funcs)
    axes_close.button = exit_spec


def closing_funcs():
    plt.ioff()
    plt.clf()
    plt.cla()
    plt.close()


class ButtonFunctions(object):
    def __init__(self):
        self.x, self.y, self.z = Data_Collection_Spectrogram.AudioInput().process_block()
        self.escape = False
        self.trial_count = 0

    def plot_but_close_rts(self):
        axes_close = plt.axes([0.81, 0.02, 0.1, 0.075])
        exit_spec = Button(axes_close, 'Close')
        exit_spec.on_clicked(self.closing_funcs_rts)
        axes_close.button = exit_spec
        return self.escape

    def closing_funcs_rts(self):
        self.escape = True
        plt.ioff()
        plt.clf()
        plt.cla()
        plt.close()
        return self.escape

    def recording_funcs(self):
        plt.clf()
        Data_Collection_Spectrogram.plot_spec(self.x, self.y, self.z)

        plot_but_record()
        plot_but_save()
        plot_but_close()
        print('Done')

    def saving_funcs(self):
        print('Saving...')
        count = 1
        size = len(self.x) * len(self.y)
        new_row = np.zeros(size+1)
        new_row[0] = 0
        for i in range(len(self.y)):
            for j in range(len(self.x)):
                    new_row[count] = self.z[i][j]
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
        self.trial_count += 1
        print('Saved')
        print("Trial number: ", self.trial_count)
