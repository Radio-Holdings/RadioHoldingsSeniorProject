from pvrecorder import PvRecorder


def show_audio_devices():
    """Lists all audio devices with their assosiated index"""
    devices = PvRecorder.get_audio_devices()

    for i in range(len(devices)):
        print(f"index: {i}, device name: {devices[i]}")


if __name__ == "__main__":
    show_audio_devices()
