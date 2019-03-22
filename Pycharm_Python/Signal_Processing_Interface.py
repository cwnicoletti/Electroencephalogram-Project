from Pycharm_Python import Audio_Class


def call_audio():
    return Audio_Class.AudioInput().listen()


def stop():
    return Audio_Class.AudioInput().stop()


def repeat():
    try:
        call_audio()
    except KeyboardInterrupt:
        stop()
        return


if __name__ == '__main__':
    repeat()
