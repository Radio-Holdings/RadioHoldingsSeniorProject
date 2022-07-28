# RadioHoldings Voice Recognition Dialer

The Voice Recognition Dialer is software that enables voice dialing (of a number
or a name via directory look up) to an All Star Link active node.

## Setup & Usage

1. Install the required python libraries by running the following command:  
`pip install -r requirements.txt`

2. Run the following command to get the number/index of the input audio
   device:  
`python list_audio_devices.py`

3. Create a .env file with the following format, filling in the API keys,
   changing the files to the appropriate operating system, and updating the 
   audio device index aquired from the previous step.

```
access_key=
audio_device_index=0
keyword_paths=wake_up_word_windows.ppn
context_path=intent_windows.rhn
```

4. Run the main.py file with the following command  
`python main.py`

## Available Commands

- Disconnect from all nodes
- Connect to node x
- Disconnect from node x
- Announce system time
- Announce connection status
- Reconnect to all previous nodes
