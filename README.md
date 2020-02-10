# SubSyncStarter
Simple post-processing script for Bazarr to start SubSync. 
## Description and warnings
This script is written in Python and requires Python 3.6 or greater.
It runs after subtitle download and starts SubSync with configured parameters for downloaded subs. 
If it fails the subs are deleted so be warned that Bazarr will try to download them again until other subs are downloaded manually.
It can be prevented but requires modifying Bazarr code. 
I know this approach is not perfect but I am not a programmer and it works for me.

# Installation
Tested on Ubuntu 18.04.03 LTS with Python 3.6.9.
  - Install GIT with `apt-get install git-core python3-pip`
  - Upgrade Python to version 3.6 or greater.
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
    python3 /opt/SubSyncStarter/SubSyncStarter.py "{{episode}}" "{{subtitles}}" "{{subtitles_language_code2}}" "{{subtitles_language_code3}}" 0
    ```
  - Save settings and restart Bazarr.
  - Now after downloading subtitles you should see entry in Bazarr logs about post-processing script and its result (Sync successful/failed).
  
# Modifying Bazarr code
Bazarr can be made to ignore files which SubSync failed to sync and try with next best one again, but it requires blacklist which at the time I am writing this is not implemented. 
I am using my fork of Bazarr for this but it has other changes specific to my setup so I advise against using it. 
You can however edit your Bazarr files (unless you are using docker). 
This code creates file with the same name as video and .bad extension and puts id of subs and provider there.
If sync is successful the .bad file is deleted, if not Bazarr checks it and skips subs which previously failed.
Assuming your Bazarr is installed in /opt/bazarr:
  
In /opt/bazarr/bazarr/get_subtitle.py find:
``` python
        if providers:
            if forced_minimum_score:
                min_score = int(forced_minimum_score) + 1
            downloaded_subtitles = download_best_subtitles({video}, language_set, int(min_score), hi,
                                                           providers=providers,
                                                           provider_configs=providers_auth,
                                                           pool_class=provider_pool(),
                                                           compute_score=compute_score,
                                                           throttle_time=None,  # fixme
                                                           blacklist=None,  # fixme
                                                           throttle_callback=provider_throttle,
                                                           pre_download_hook=None,  # fixme
                                                           post_download_hook=None,  # fixme
                                                           language_hook=None)  # fixme
        else:
            downloaded_subtitles = None
            logging.info("BAZARR All providers are throttled")
            return None
```
And replace it with:
``` python
        if providers:
            if forced_minimum_score:
                min_score = int(forced_minimum_score) + 1
            bad_file = os.path.splitext(path)[0] + '.bad'
            blacklist_new = []
            if os.path.isfile(bad_file):
                f2_open = open(bad_file, "r")
                bad_hashes = f2_open.read()
                bad_hashes_list = bad_hashes.splitlines()
                blacklist_new = [line2 for line2 in bad_hashes_list if line2.strip() != '']
                f2_open.close()
            downloaded_subtitles = download_best_subtitles({video}, language_set, int(min_score), hi,
                                                           providers=providers,
                                                           provider_configs=providers_auth,
                                                           pool_class=provider_pool(),
                                                           compute_score=compute_score,
                                                           throttle_time=None,  # fixme
                                                           blacklist=blacklist_new,  # fixme
                                                           throttle_callback=provider_throttle,
                                                           pre_download_hook=None,  # fixme
                                                           post_download_hook=None,  # fixme
                                                           language_hook=None)  # fixme
        else:
            downloaded_subtitles = None
            logging.info("BAZARR All providers are throttled")
            return None
```
Also find:
``` python
                try:
                    fld = get_target_folder(path)
                    chmod = int(settings.general.chmod, 8) if not sys.platform.startswith(
                        'win') and settings.general.getboolean('chmod_enabled') else None
                    saved_subtitles = save_subtitles(video.original_path, subtitles, single=single,
                                                     tags=None,  # fixme
                                                     directory=fld,
                                                     chmod=chmod,
                                                     # formats=("srt", "vtt")
                                                     path_decoder=force_unicode
                                                     )
                except Exception as e:
                    logging.exception('BAZARR Error saving Subtitles file to disk for this file:' + path)
                    pass
```
And replace it with:
``` python
                try:
                    for subb in subtitles:
                        subid = subb.id
                        prov = subb.provider_name
                        f_open = open(os.path.splitext(path)[0] + '.bad', "a+")
                        f_open.write(prov + ';' + subid + '\n')
                        f_open.close()
                    fld = get_target_folder(path)
                    chmod = int(settings.general.chmod, 8) if not sys.platform.startswith(
                        'win') and settings.general.getboolean('chmod_enabled') else None
                    saved_subtitles = save_subtitles(video.original_path, subtitles, single=single,
                                                     tags=None,  # fixme
                                                     directory=fld,
                                                     chmod=chmod,
                                                     # formats=("srt", "vtt")
                                                     path_decoder=force_unicode
                                                     )
                except Exception as e:
                    logging.exception('BAZARR Error saving Subtitles file to disk for this file:' + path)
                    pass
```

In /opt/bazarr/libs/subliminal_patch/core.py find:
``` python
            seen = []
            out = []
            for s in results:
                if (str(provider), str(s.id)) in self.blacklist:
                    logger.info("Skipping blacklisted subtitle: %s", s)
                    continue
                if s.id in seen:
                    continue
                s.plex_media_fps = float(video.fps) if video.fps else None
                out.append(s)
                seen.append(s.id)
```
And replace it with:
``` python
            seen = []
            out = []
            for s in results:
                if (str(provider) + ';' + str(s.id)) in self.blacklist:
                    logger.info("Skipping blacklisted subtitle: %s", s)
                    continue
                if s.id in seen:
                    continue
                s.plex_media_fps = float(video.fps) if video.fps else None
                out.append(s)
                seen.append(s.id)
```
Remember that indent is important in Python so make sure it is the same.
Turn off auto update because this edits will be wiped after Bazarr update and must be manually applied again.