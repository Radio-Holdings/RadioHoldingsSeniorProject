import os
import struct
import wave
import pvporcupine
import pvrhino
from threading import Thread
from datetime import datetime

from pvrecorder import PvRecorder
from dotenv import load_dotenv, find_dotenv


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

            print(rhino.context_info)
            print()

            print(f"Using device: {recorder.selected_device}")
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
                        # Happy path
                        print("{")
                        print("  intent : '%s'" % inference.intent)
                        print("  slots : {")
                        for slot, value in inference.slots.items():
                            print("    %s : '%s'" % (slot, value))
                        print("  }")
                        print("}\n")
                        break
                    else:
                        # Sad path
                        print("Didn't understand the command.\n")
                        break
        except pvrhino.RhinoInvalidArgumentError as e:
            print(
                "One or more arguments provided to Rhino is invalid: {\n"
                + f"\t{self._access_key=}\n"
                + f"\t{self._library_path=}\n"
                + f"\t{self._model_path=}\n"
                + f"\t{self._context_path=}\n"
                + f"\t{self._require_endpoint=}\n"
                + "}"
            )
            print(
                f"If all other arguments seem valid, ensure that '{self._access_key}' is a valid AccessKey"
            )
            raise e
        except pvrhino.RhinoActivationError as e:
            print("AccessKey activation error")
            raise e
        except pvrhino.RhinoActivationLimitError as e:
            print(
                f"AccessKey '{self._access_key}' has reached it's temporary device limit"
            )
            raise e
        except pvrhino.RhinoActivationRefusedError as e:
            print(f"AccessKey '{self._access_key}' refused")
            raise e
        except pvrhino.RhinoActivationThrottledError as e:
            print(f"AccessKey '{self._access_key}' has been throttled")
            raise e
        except pvrhino.RhinoError as e:
            print(f"Failed to initialize Rhino")
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


class WakeUpEngine(Thread):
    """Wake up engine, calls rhino engine run when wake up word detected"""

    def __init__(
        self,
        access_key,
        library_path,
        model_path,
        keyword_paths,
        sensitivities,
        rhino_engine,
        input_device_index=None,
        output_path=None,
    ):
        super(WakeUpEngine, self).__init__()

        self._access_key = access_key
        self._library_path = library_path
        self._model_path = model_path
        self._keyword_paths = keyword_paths
        self._sensitivities = sensitivities
        self._input_device_index = input_device_index

        self._output_path = output_path
        self._rhino_engine = rhino_engine

    def run(self):
        print(self._keyword_paths)
        keywords = list()
        for x in self._keyword_paths:
            keyword_phrase_part = os.path.basename(x).replace(".ppn", "").split("_")
            if len(keyword_phrase_part) > 6:
                keywords.append(" ".join(keyword_phrase_part[0:-6]))
            else:
                keywords.append(keyword_phrase_part[0])

        porcupine = None
        recorder = None
        wav_file = None
        try:
            porcupine = pvporcupine.create(
                access_key=self._access_key,
                library_path=self._library_path,
                model_path=self._model_path,
                keyword_paths=self._keyword_paths,
                sensitivities=self._sensitivities,
            )

            recorder = PvRecorder(
                device_index=self._input_device_index,
                frame_length=porcupine.frame_length,
            )
            recorder.start()

            if self._output_path is not None:
                wav_file = wave.open(self._output_path, "w")
                wav_file.setparams((1, 2, 16000, 512, "NONE", "NONE"))

            print(f"Using device: {recorder.selected_device}")

            print("Listening {")
            for keyword, sensitivity in zip(keywords, self._sensitivities):
                print("  %s (%.2f)" % (keyword, sensitivity))
            print("}")

            while True:
                pcm = recorder.read()

                if wav_file is not None:
                    wav_file.writeframes(struct.pack("h" * len(pcm), *pcm))

                result = porcupine.process(pcm)
                if result >= 0:
                    print("[%s] Detected %s" % (str(datetime.now()), keywords[result]))
                    recorder.stop()
                    self._rhino_engine.run()
                    recorder.start()
                    print("Exited rhino, waiting for wakeup call")

        except pvporcupine.PorcupineInvalidArgumentError as e:
            print(
                "One or more arguments provided to Porcupine is invalid: {\n"
                + f"\t{self._access_key=}\n"
                + f"\t{self._library_path=}\n"
                + f"\t{self._model_path=}\n"
                + f"\t{self._keyword_paths=}\n"
                + f"\t{self._sensitivities=}\n"
                + "}"
            )
            print(
                f"If all other arguments seem valid, ensure that '{self._access_key}' is a valid AccessKey"
            )
            raise e
        except pvporcupine.PorcupineActivationError as e:
            print("AccessKey activation error")
            raise e
        except pvporcupine.PorcupineActivationLimitError as e:
            print(
                f"AccessKey '{self._access_key}' has reached it's temporary device limit"
            )
            raise e
        except pvporcupine.PorcupineActivationRefusedError as e:
            print(f"AccessKey '{self._access_key}' refused")
            raise e
        except pvporcupine.PorcupineActivationThrottledError as e:
            print(f"AccessKey '{self._access_key}' has been throttled")
            raise e
        except pvporcupine.PorcupineError as e:
            print(f"Failed to initialize Porcupine")
            raise e
        except KeyboardInterrupt:
            print("Stopping ...")
        finally:
            if porcupine is not None:
                porcupine.delete()

            if recorder is not None:
                recorder.delete()

            if wav_file is not None:
                wav_file.close()


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
