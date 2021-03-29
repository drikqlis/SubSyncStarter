# SubSyncStarter
Simple post-processing script for Bazarr to start SubSync. 
## Description and warnings
This script is written in Python and requires Python 3.6 or greater.
It runs after subtitle download and starts SubSync with configured parameters for downloaded subs.
If sync fails script will add subtitles to Bazarr blacklist automatically.
It can work alongside build-in Bazarr synchronization which is using diffrent synchronizer (worse for foreign subtitles from my expirence).

# Installation
Tested on Ubuntu 18.04.03 LTS with Python 3.6.9.
  - Install GIT with `apt-get install git-core python3-pip`
  - Upgrade Python to version 3.6 or greater.
  - Install requests: `pip install requests`
  - Install Bazarr: https://github.com/morpheus65535/bazarr
  - Install SubSync: https://github.com/sc0ty/subsync
  - Make folder `sudo mkdir /opt/SubSyncStarter`
  - Change ownership to your user (must have access to sub files) `sudo chown -R user:user /opt/SubSyncStarter`
  - Go to folder `cd /opt`
  - Clone repository `git clone https://github.com/drikqlis/SubSyncStarter.git`

# Configuration
Create config.ini file based on config.ini.sample:
## General
  - LoggingLevel - Logging level of the script, can be DEBUG, INFO, WARNING, ERROR.
  - Logfile - Where to save log file of the script. Default if installed to /opt/SubSyncStarter
  - BazarrApiKey - API key for Bazarr for blacklisting wrong subtitles.
  - BazarrUrl - URL to your Bazarr instance with protocol and port and without slash at the end (e.g. http://192.168.1.10:6767).
## SubSync
  - Location - Where SubSync is installed. Default should work.
  - LoggingLevel - Logging level of SubSync.
  - Logfile - Where to save log file of the SubSync subprocess. Default if installed to /opt/SubSyncStarter
  - Effort - How hard to try, between 0.0 and 1.0.
  - WindowSize - Maximum correction (in seconds).
  - MaxPointDistance - Maximum acceptable synchronization error (in seconds).
  
# Adding to Bazarr
  - Go to Bazarr -> Settings -> General
  - Find Post-processing and turn on option "Use post processing".
  - In post-processing command input: 
    ```
    python3 /opt/SubSyncStarter/SubSyncStarter.py "{{episode}}" "{{subtitles}}" "{{subtitles_language_code2}}" "{{subtitles_language_code3}}" "{{episode_language_code3}}" "{{subtitle_id}}" "{{provider}}" "{{series_id}}" "{{episode_id}}" 0
    ```
  - Save settings and restart Bazarr.
  - Now after downloading subtitles you should see entry in Bazarr logs about post-processing script and its result (Sync successful/failed). If sync fails script will add subtitles to Bazarr blacklist automatically.
