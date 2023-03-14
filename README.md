# OBS Auto Cam

![GitHub release (latest by date)](https://img.shields.io/github/v/release/Wiibleyde/obsAutoCam) ![GitHub last commit](https://img.shields.io/github/last-commit/Wiibleyde/obsAutoCam) ![GitHub issues](https://img.shields.io/github/issues-raw/Wiibleyde/obsAutoCam) ![GitHub pull requests](https://img.shields.io/github/issues-pr-raw/Wiibleyde/obsAutoCam) ![GitHub All Releases](https://img.shields.io/github/downloads/Wiibleyde/obsAutoCam/total)

This is a simple script to automatically switch between scenes in OBS Studio.

## How to use

1. Start OBS Studio

2. Start the script

3. Fill the config file with the ip, port and password of your OBS Studio

4. Start the script again

And that's it. The script will now automatically switch between the scenes with specific names.

You can control the script with the following link: 
- [http://localhost:5000](http://localhost:5000), if you want to control the script on the same computer.



## Cam names

The script will only switch between scenes with the following names:
- Scene scenes : name contains "SCE"
- Public scenes : name contains "PUB"
- Piano scenes : name contains "PIA"

## Config file

The config file is a simple json file with the following structure:

```json
{
    "minTime": 5, 
    "maxTime": 10, 
    "ip": "127.0.0.1", 
    "port": 4455, 
    "password": "password"
}
```

- minTime : minimum time in seconds between two scene switches
- maxTime : maximum time in seconds between two scene switches
- ip : ip of the computer running OBS Studio websocket
- port : port of the OBS Studio websocket
- password : password of the OBS Studio websocket

## How to install

