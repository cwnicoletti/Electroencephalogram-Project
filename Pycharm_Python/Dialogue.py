import matplotlib.pyplot as plt


def plot_instructions():
    words =  'Instructions: \n\n' 'Electrodes: Electrodes should remain placed on the scalp as instructed by our '\
        'assistants.\n  If the electrodes fall off, simply raise your hand and an assistant will come to\n help you' \
        'put them back on.\n Circuit board: Please do not touch the circuit board! Touching or pulling out' \
             ' components ' \
        '\ncan lead to shorting the circuit, and/or may cause harm. \n\n Recording: \n'\
        '   Words will be displayed above the spectrogram as well as how many words are left to record. This will be ' \
             'the word you will be “saying” in your head.  \n'\
        'The best method for “saying” the word in your head is by consciously not moving your vocal cords when' \
             ' “saying” it. \n' \
        'There is an audio/speaker button next to the word, please press this speaker for every word to clarify ' \
             'how the ' \
        'word is said and with what accent (i.e. different ways of saying “the” or “caramel”)  \n'\
        'Once you have listened to the word, you will then press the “Record” button. Watch the count down, and ' \
             'once it\n hits 1 (i.e. 3.. 2… 1), it will record 500 milliseconds of audio.  '\
        '\n\n'\
        '   This is a small window and there are plenty of ways to miss it. You may always press the “Record”' \
             ' button\n again to get a new reading for any reason.   '\
        '\n\n'\
        'Once you get this reading, make sure to press save. Once you press save, you are brought to the next word, ' \
             'and\n steps 1-5 repeat again.  '\
        '\n\n'\
        'If you feel as though you did not record the word correctly, missed it, or for any reason are not happy ' \
             'with it, you may always press the “Delete last save” button'\
        '\n\n'\
        'There is an option to speed up/slow down the countdown, feel free to adjust this to your comfort.\n' \
        'Any questions/concerns raise your hand, and an assistant will be more than happy to help <[:~)  '
    plot_words = plt.text(.02, .01, words, fontsize=9, wrap=True)
    plot_words.axes.get_xaxis().set_visible(False)
    plot_words.axes.get_yaxis().set_visible(False)
