import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
from multiprocessing import Process
from Pycharm_Python import Data_Collection_Spectrogram
from Pycharm_Python import Write_Files

escape = False
trial_count = 0

'''
Here we have a list of button plotting functions for the different buttons
When adding new buttons, it should be as easy as copy-pasting and manipulating some values
'''

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


def plot_but_close_rts():
    global escape
    axes_close = plt.axes([0.81, 0.02, 0.1, 0.075])
    close_rts_spec = Button(axes_close, 'Close')
    close_rts_spec.on_clicked(closing_funcs_rts)
    axes_close.button = close_rts_spec
    return escape

# End button plotting


'''
Here we have the button functions, which is basically the scripts that activate on-click
Note: There are two different closing functions: 
    One for Data_Collection_Spectrogram and one for Real_Time_Spectrogram (rts)
'''


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
    del trial_count
    return escape


def recording_funcs(self):
    plt.clf()  # Quick clear function just in case
    global x, y, z

    '''
    Once "Record" is hit, this starts the processing pipeline
    Data_collection_Spectrogram -> process_block -> get_mic_stream -> find_input_device /
    -> continue process_block to return f, t, decibels (or x, y, z)
    '''
    x, y, z = Data_Collection_Spectrogram.AudioInput().process_block()

    # Simply calling plotting function in Data_Collection_Spectrogram
    Data_Collection_Spectrogram.plot_spec(x, y, z)

    # Re-plot buttons each trial
    plot_but_record()
    plot_but_save()
    plot_but_close()
    print('Done')


def saving_funcs(self):
    global trial_count

    print('Saving...')

    count = 1  # Start at index [1] since [0] is label column
    size = len(x) * len(y)
    csv_spec = np.zeros(size+1)

    ''' 
    These are the different labels of spectrogram types
    0 - nothing; random thoughts
    1 - thinking the word "hello"
    2 - thinking the word "world"
    '''

    csv_spec[0] = 0  # First column - label
    for i in range(len(y)):
        for j in range(len(x)):
            csv_spec[count] = z[i][j]  # Populating csv rows by concatenating spectrogram pixel rows
            count += 1
    
    # Start multiprocessing to utilize multiple cores for faster (parallel) writing
    p1 = Process(target=Write_Files.write_train, args=(csv_spec,))
    print('...')
    p2 = Process(target=Write_Files.write_test, args=(csv_spec,))
    print('...')

    p1.start()
    p2.start()

    p1.join()
    p2.join()
    
    # End multiprocessing
    
    trial_count += 1
    print('Saved')
    print("Trial number: ", trial_count)
