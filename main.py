import os
import struct
import wave
import pvporcupine
import pvrhino
from threading import Thread
from datetime import datetime

from pvrecorder import PvRecorder
from dotenv import load_dotenv, find_dotenv

from RhinoEngine import RhinoEngine
from PorcupineEngine import WakeUpEngine


def main():
    """Creates the two engines and runs the wakeup engine

    The rhino engine is passed into the wakeup engine and is called when
    a wake up word is detected.
    """
    # Load environment variables
    load_dotenv(find_dotenv())

    # For both
    access_key = os.getenv("access_key")
    audio_device_index = int(os.getenv("audio_device_index"))

    # For WakeUpEngine
    keyword_paths = [os.getenv("keyword_paths")]

    # For RhinoEngine
    context_path = os.getenv("context_path")

    rhino_engine = RhinoEngine(
        access_key=access_key,
        library_path=pvrhino.LIBRARY_PATH,
        model_path=pvrhino.MODEL_PATH,
        context_path=context_path,
        require_endpoint=True,
        audio_device_index=audio_device_index,
        output_path=None,
    )

    WakeUpEngine(
        access_key=access_key,
        library_path=pvporcupine.LIBRARY_PATH,
        model_path=pvporcupine.MODEL_PATH,
        keyword_paths=keyword_paths,
        sensitivities=[0.5] * len(keyword_paths),
        output_path=None,
        input_device_index=audio_device_index,
        rhino_engine=rhino_engine,
    ).run()


if __name__ == "__main__":
    main()
