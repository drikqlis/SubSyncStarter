import os
import sys
import logging
import subprocess

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', level=logging.DEBUG, handlers=[logging.FileHandler("/home/mateusz/subsync/SubSyncStarter.log"),logging.StreamHandler()])
log = logging.getLogger()

reference_file = sys.argv[1]
sub_file = sys.argv[2]
sub_code2 = '.%s.srt' % sys.argv[3]
sub_code3 = '.%s.srt' % sys.argv[4]
sub_new = sub_file.replace(sub_code3, sub_code2)
command = "/snap/bin/subsync --cli --verbose 1 --loglevel 1 --logfile '/home/mateusz/subsync/subsync.log' sync --sub '%s' --ref '%s' --out '%s' --effort 0 --overwrite" % (sub_file, reference_file, sub_new)

log.debug('Reference file: %s' % reference_file)
log.debug('Subtitles file: %s' % sub_file)
log.debug('Subtitles code (2): %s' % sub_code2)
log.debug('Subtitles code (3): %s' % sub_code3)

log.info('Starting conversion of subtitles file: %s' % sub_file)
log.debug('Running command: %s' % command)
p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
(output, err) = p.communicate()
## Wait for date to terminate. Get return returncode ##
p_status = p.wait()

print("Command output : ", output)
print("Command exit status/return code : ", p_status)

log.debug('Output: %s' % output)
log.debug('Error: %s' % err)
log.debug('Exit code: %s' % p_status)