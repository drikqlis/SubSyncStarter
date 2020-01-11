import os
import sys
import logging
import subprocess
from subprocess import Popen, PIPE

logging.basicConfig(format='%(asctime)s - %(levelname)s: %(message)s', filename='SubSyncStarter.log', level=logging.DEBUG)

reference_file = sys.argv[1]
sub_file = sys.argv[2]
sub_code2 = '.%s.srt' % sys.argv[3]
sub_code3 = '.%s.srt' % sys.argv[4]
sub_new = sub_file.replace(sub_code3, sub_code2)

logging.debug('Reference file: %s' % reference_file)
logging.debug('Subtitles file: %s' % sub_file)
logging.debug('Subtitles code (2): %s' % sub_code2)
logging.debug('Subtitles code (3): %s' % sub_code3)

logging.info('Starting conversion of subtitles file: %s' % sub_file)
process = Popen("/snap/bin/subsync --cli --verbose 2 sync --sub %s --ref %s --out %s --effort 1 --loglevel 2 --logfile /var/log/subsync/subsync.log" % sub_file, reference_file, sub_new, stdout=PIPE)
(output, err) = process.communicate()
exit_code = process.wait()

logging.debug('Output: %s' % output)
logging.debug('Error: %s' % err)
logging.debug('Exit code: %s' % exit_code)