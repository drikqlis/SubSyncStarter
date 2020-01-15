import os
import sys
import logging
import subprocess
import configparser

reference_file = sys.argv[1]
sub_file = sys.argv[2]
sub_code2 = '.%s.srt' % sys.argv[3]
sub_code3 = '.%s.srt' % sys.argv[4]
sub_new = sub_file.replace(sub_code3, sub_code2)

config = configparser.ConfigParser()
config.read('config.ini')
loglevel_starter = config['General']['LoggingLevel']
logfile_starter = config['General']['Logfile']
location_subsync = config['SubSync']['Location']
loglevel_subsync = config['SubSync']['LoggingLevel']
logfile_subsync = config['SubSync']['Logfile']
effort = config['SubSync']['Effort']
window_size = config['SubSync']['WindowSize']

logging.root.handlers = []
logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG, handlers=[logging.FileHandler(logfile_starter, encoding="utf-8"),logging.StreamHandler()])
log = logging.getLogger()

command = "/snap/bin/subsync --cli --verbose " + loglevel_subsync + " --logfile '" + logfile_subsync + "' --window-size " + window_size + " sync --sub '" + sub_file + "' --ref '" + reference_file + "' --out '" + sub_new + "' --effort " + effort +" --overwrite"

log.debug('Reference file: %s' % reference_file)
log.debug('Subtitles file: %s' % sub_file)
log.debug('Subtitles code (2): %s' % sub_code2)
log.debug('Subtitles code (3): %s' % sub_code3)

log.info('Starting conversion of subtitles file: %s' % sub_file)
log.debug('Running command: %s' % command)

try:
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()
    ## Wait for date to terminate. Get return returncode ##
    p_status = p.wait()

    output = output.decode('utf-8')
    output_list = output.splitlines()
    for outputs in output_list:
        log.debug('Output: %s' % outputs)
    log.debug('Error: %s' % err)
    log.debug('Exit code: %s' % p_status)
    if "[+] done" in output_list[-1]:
        log.info('Conversion succesfull')
        print('Conversion succesfull')
    else:
        os.remove(sub_file)
        log.warning('Conversion failed')
        print('Conversion failed')
except:
    os.remove(sub_file)
    log.exception('Conversion failed')
    print('Conversion failed')
