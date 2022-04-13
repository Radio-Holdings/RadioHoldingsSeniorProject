import os
import struct
import wave
import pvporcupine
from threading import Thread
from datetime import datetime

from pvrecorder import PvRecorder
from dotenv import load_dotenv, find_dotenv


class WakeUpEngine(Thread):
    def __init__(
        self,
        access_key,
        library_path,
        model_path,
        keyword_paths,
        sensitivities,
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
    # Load environment variables
    load_dotenv(find_dotenv())
    access_key = os.getenv("access_key")
    model_path = pvporcupine.MODEL_PATH
    keyword_paths = [os.getenv("keyword_paths")]
    # keyword_paths = ["hey-pico_en_windows_v2_1_0.ppn"]
    sensitivities = [0.5] * len(keyword_paths)
    library_path = pvporcupine.LIBRARY_PATH
    output_path = None
    audio_device_index = 1

    # Try to make a porcupine instance

    WakeUpEngine(
        access_key=access_key,
        library_path=library_path,
        model_path=model_path,
        keyword_paths=keyword_paths,
        sensitivities=sensitivities,
        output_path=output_path,
        input_device_index=audio_device_index,
    ).run()


if __name__ == "__main__":
    main()
