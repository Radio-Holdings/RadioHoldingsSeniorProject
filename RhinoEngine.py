import os
import struct
import wave
import pvporcupine
import pvrhino
from threading import Thread
from datetime import datetime

from pvrecorder import PvRecorder
from dotenv import load_dotenv, find_dotenv

from commands import *


class RhinoEngine(Thread):
    """Intent Engine"""

    def __init__(
        self,
        access_key,
        library_path,
        model_path,
        context_path,
        require_endpoint,
        audio_device_index=None,
        output_path=None,
    ):

        super(RhinoEngine, self).__init__()

        self._access_key = access_key
        self._library_path = library_path
        self._model_path = model_path
        self._context_path = context_path
        self._require_endpoint = require_endpoint
        self._audio_device_index = audio_device_index

        self._output_path = output_path

    def run(self):

        rhino = None
        recorder = None
        wav_file = None

        try:
            rhino = pvrhino.create(
                access_key=self._access_key,
                library_path=self._library_path,
                model_path=self._model_path,
                context_path=self._context_path,
                require_endpoint=self._require_endpoint,
            )

            recorder = PvRecorder(
                device_index=self._audio_device_index, frame_length=rhino.frame_length
            )
            recorder.start()

            if self._output_path is not None:
                wav_file = wave.open(self._output_path, "w")
                wav_file.setparams((1, 2, 16000, 512, "NONE", "NONE"))

            # print(rhino.context_info)
            # print()

            print("Using device: {}".format(recorder.selected_device))
            print("Listening...")
            print()

            while True:
                pcm = recorder.read()

                if wav_file is not None:
                    wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))

                is_finalized = rhino.process(pcm)
                if is_finalized:
                    inference = rhino.get_inference()
                    if inference.is_understood:
                        if inference.intent == "disconnectFromAll":
                            disconnect_from_all_nodes()
                        elif inference.intent == "connectToNode":
                            connect_to_node(
                                int("".join(x for x in inference.slots.values()))
                            )
                        elif inference.intent == "disconnectFromNode":
                            disconnect_from_node(
                                int("".join(x for x in inference.slots.values()))
                            )
                        break
                    else:
                        # Sad path
                        print("Didn't understand the command.\n")
                        break
        except pvrhino.RhinoInvalidArgumentError as e:
            print(
                "One or more arguments provided to Rhino is invalid: {\n"
                + "\t{}\n".format(self._access_key)
                + "\t{}\n".format(self._library_path)
                + "\t{}\n".format(self._model_path)
                + "\t{}\n".format(self._context_path)
                + "\t{}\n".format(self._require_endpoint)
                + "}"
            )
            print(
                "If all other arguments seem valid, ensure that '{}' is a valid AccessKey".format(
                    self._access_key
                )
            )
            raise e
        except pvrhino.RhinoActivationError as e:
            print("AccessKey activation error")
            raise e
        except pvrhino.RhinoActivationLimitError as e:
            print(
                "AccessKey '{}' has reached it's temporary device limit".format(
                    self._access_key
                )
            )
            raise e
        except pvrhino.RhinoActivationRefusedError as e:
            print("AccessKey '{}' refused".format(self._access_key))
            raise e
        except pvrhino.RhinoActivationThrottledError as e:
            print("AccessKey '{}' has been throttled".format(self._access_key))
            raise e
        except pvrhino.RhinoError as e:
            print("Failed to initialize Rhino")
            raise e
        except KeyboardInterrupt:
            print("Stopping ...")

        finally:
            if recorder is not None:
                recorder.delete()

            if rhino is not None:
                rhino.delete()

            if wav_file is not None:
                wav_file.close()
