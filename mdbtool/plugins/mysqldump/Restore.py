'''
Created on 25 oct. 2016

@author: lym
'''

import argparse
import sys, os
import logging
from . import printHeader, checkAndGetEnv, checkBin, DEST_DIR
from datetime import datetime
import re
import subprocess
import tools

BIN = 'mysql'

logger = logging.getLogger(__name__)

class Restorer:

    def __init__(self, args):
        self.args = args

    def parseBackups(self):
        self.backups = []
        for file in os.listdir(DEST_DIR):
            if not file.lower().endswith(('.sql', '.sql.7z')):
                continue
            fullpath = os.path.join(DEST_DIR, file)
            infos = {
                'file' : file,
                'fullpath' : fullpath,
                'size' : tools.FileSize(os.path.getsize(fullpath)),
            }
            infos['date'] = self.extractDateFromName(file)
            infos['md5'] = self.checkMd5(file)
            self.backups.append(infos)

    def extractDateFromName(self, name):
        m = re.search('(\d{4}(?:-\d{2}){5})', name)
        date = None
        if m:
            date = datetime.strptime(m.group(1),'%Y-%m-%d-%H-%M-%S')
        return date

    def checkMd5(self,file):
        status = 'ABS'
        md5file = file + '.md5'
        if ( os.path.exists(os.path.join(DEST_DIR, md5file)) ):
            command = 'md5sum -c {}'.format(md5file)
            try:
                subprocess.check_call(command, shell=True, cwd=DEST_DIR,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                status = 'OK'
            except subprocess.CalledProcessError:
                status = 'KO'
        return status

    def colorMd5(self, status):
        final = status
        if (status == 'OK'):
            final = tools.TermColor.okgreen(status)
        elif (status == 'KO'):
            final = tools.TermColor.fail(status)
        else:
            final = tools.TermColor.warn(status)
        return final

    def listBackups(self):
        print('   {:19} {:10} {}'.format('date', 'size', 'md5'))
        for n, bck in enumerate(self.backups):
            print('{n:2} {b[date]:%F-%T} {b[size]!s:10} {md5}'
                  .format(n=n,b=bck,md5=self.colorMd5(bck['md5'])))

    def exec(self):
        self.parseBackups()
        if (self.args.latest):
            self.restoreData(0)
        else:
            self.launchCli()
        return

    def launchCli(self):
        print('Choose backup to restore')
        self.listBackups()
        print('q - quit')
        correct_choice = False
        choice = 0
        for attempt in list(range(6)):
            choice = input('Which one do you want to restore ? [0]:')
            if not choice:
                choice = 0
            if (choice == 'q'):
                exit(0)
            choice = int(choice)
            if ( choice < 0 and choice >= len(self.backups)):
                print('Please choose a correct number or a letter')
                continue
            if ( self.backups[choice]['md5'] != 'OK' ):
                force = input("This backup seems to have a wrong or missing md5sum\n" +
                    'are you sure to continue ? [yN]:')
                if not force:
                    force = 'N'
                if force == 'y':
                    correct_choice = True
            else:
                correct_choice = True
            if correct_choice:
                break
        if not correct_choice:
            print('Maximum attemp reached, quitting')
            exit(1)
        self.restoreData(choice)    

    def restoreData(self,idx=0):
        checkBin(BIN)
        cmd = [BIN]
        if not (self.args.skip_mysql_env):
            # Host
            cmd.append('-h{}'.format(checkAndGetEnv('MYSQL_HOST')))
            
            # User 
            cmd.append('-u{}'.format(checkAndGetEnv('MYSQL_USER')))
            
            # Password
            if ( os.environ['MYSQL_PASSWORD'] ) :
                cmd.append('-p{}'.format(os.environ['MYSQL_PASSWORD']))
        
#         cmd.extend(self.args.args)

        if os.environ['MYSQL_DATABASE']:
            cmd.append(os.environ['MYSQL_DATABASE'])
        
        fullpath = self.backups[idx]['fullpath']
        begining = []
        if fullpath.endswith('.7z'):
            begining.extend([
                '7zr e -so',
                fullpath,
                '2>/dev/null'
                '|'
            ])
        else:
            begining.extend([
                'cat',
                fullpath,
                '|'
            ])
        
        begining.extend(cmd)
        final_cmd = ' '.join(begining)
        logger.debug('Running command : {}'.format(final_cmd))
        if self.args.simule:
            print('Should be running cmd : {}'.format(final_cmd))
        else:
            subprocess.check_call(final_cmd, shell=True)

def main(args):
    parser = argparse.ArgumentParser(
        prog='%s %s %s' % (sys.argv[0], sys.argv[1], 'mysqldump'),
        description='Restore data from mysqldump backups'
    )
    parser.add_argument('--skip-mysql-env', help='Ignore all MYSQL env', action='store_true')
    parser.add_argument('--latest', help='Restore latest and quit', action='store_true')
    parser.add_argument('--simule', help='No sending data to database', action='store_true')
#     parser.add_argument('+', help='Put this to ensure following args passed to mysqldump', nargs='?')
#     parser.add_argument('args', help='Arguments to pass to mysqldump', nargs=argparse.REMAINDER)
    args = parser.parse_args(args)
    logger.debug('Parsed args : {}'.format(args))
    
    obj=Restorer(args)
    obj.exec()        

