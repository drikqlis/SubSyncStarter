import os
import sys
import logging
import subprocess
import configparser
import requests

reference_file = sys.argv[1]
sub_file = sys.argv[2]
sub_code2 = sys.argv[3]
sub_code3 = sys.argv[4]
audio_code3 = sys.argv[5]
subtitle_id = sys.argv[6]
provider = sys.argv[7]
series_id = sys.argv[8]
episode_id = sys.argv[9]
subsyncstarter_path = os.path.dirname(sys.argv[0])

config = configparser.ConfigParser()
config.read(os.path.join(subsyncstarter_path,'config.ini'))
loglevel_starter = config['General']['LoggingLevel']
logfile_starter = config['General']['Logfile']
apikey = config['General']['BazarrApiKey']
bazarr_url = config['General']['BazarrUrl']
location_subsync = config['SubSync']['Location']
loglevel_subsync = config['SubSync']['LoggingLevel']
logfile_subsync = config['SubSync']['Logfile']
effort = config['SubSync']['Effort']
window_size = config['SubSync']['WindowSize']
max_point_dist = config['SubSync']['MaxPointDistance']

command = location_subsync + ' --cli --verbose ' + loglevel_subsync + ' --logfile ' + '"' + logfile_subsync + '"' + ' --window-size ' + window_size + ' --max-point-dist ' + max_point_dist + ' sync --sub ' + '"' + sub_file + '"' + ' --ref ' + '"' + reference_file + '"' + ' --ref-lang ' + audio_code3 + ' --out ' + '"' + sub_file + '"' + ' --effort ' + effort + ' --overwrite'

logging.root.handlers = []
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG, handlers=[logging.FileHandler(logfile_starter, encoding="utf-8"),logging.StreamHandler()])
log = logging.getLogger()

log.debug('Reference file: %s' % reference_file)
log.debug('Subtitles file: %s' % sub_file)
log.debug('Subtitles code (2): %s' % sub_code2)
log.debug('Subtitles code (3): %s' % sub_code3)
log.debug('Audio code (3): %s' % audio_code3)
log.debug('Subtitles id: %s' % subtitle_id)
log.debug('Provider: %s' % provider)
log.debug('Series id: %s' % series_id)
log.debug('Episode id: %s' % episode_id)


log.info('Starting synchronization of subtitles file: %s' % sub_file)
log.debug('Running command: %s' % command)

try:
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    p_status = p.wait()

    output = output.decode('utf-8')
    output_list = output.splitlines()
    for outputs in output_list:
        log.debug('Output: %s' % outputs)
    log.debug('Error: %s' % err)
    log.debug('Exit code: %s' % p_status)
    if any("[+] done" in s for s in output_list):
        log.info('Sync succesful. Lang: ' + sub_code2 + ', Provider: ' + provider + ', Sub id: ' + subtitle_id)
        print('Sync succesful. Lang: ' + sub_code2 + ', Provider: ' + provider + ', Sub id: ' + subtitle_id)
    else:
        if series_id == "":
            url = bazarr_url + f'/api/movies/blacklist?radarrid={episode_id}'
            headers = {
                'X-API-KEY': apikey
            }
            payload = {
                'provider': provider,
                'subs_id': subtitle_id,
                'language': sub_code2,
                'subtitles_path': sub_file
            }
        else:
            url = bazarr_url + f'/api/episodes/blacklist?seriesid={series_id}&episodeid={episode_id}'
            headers = {
                'X-API-KEY': apikey
            }
            payload = {
                'provider': provider,
                'subs_id': subtitle_id,
                'language': sub_code2,
                'subtitles_path': sub_file
            }
        try:
            requests.request('POST', url, data=payload, headers=headers, timeout=10)
        except requests.exceptions.ReadTimeout:
            pass

        #if os.path.isfile(sub_file):
        #    os.remove(sub_file)
        log.warning('Sync failed - wrong subs. Lang: ' + sub_code2 + ', Provider: ' + provider + ', Sub id: ' + subtitle_id)
        print('Sync failed - wrong subs. Lang: ' + sub_code2 + ', Provider: ' + provider + ', Sub id: ' + subtitle_id)
except:
    os.remove(sub_file)
    log.exception('Sync failed - exception')
    print('Sync failed - exception')
