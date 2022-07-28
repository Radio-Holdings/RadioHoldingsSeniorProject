# RadioHoldings Voice Recognition Dialer

The Voice Recognition Dialer is software that enables voice dialing (of a number
or a name via directory look up) to an All Star Link active node.

## Setup & Usage

1. Install the required python libnraries by running the following command:  
`pip install -r requirements.txt`

2. Create a .env file with the following format, filling in the API keys and
   and changing the files to the appropriate operating system.

```
access_key=
audio_device_index=0
keyword_paths=wake_up_word_windows.ppn
context_path=intent_windows.rhn
```

3. Run the main.py file.

## Available Commands

- disconnect from all nodes
- connect to node x
- disconnect from node x
- announce system time
- announce connection status
- Reconnect to all previous nodes
