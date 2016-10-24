
import os, sys, subprocess
import argparse
import logging
from datetime import datetime

BIN = 'mysqldump'
DEST_DIR = '/backup'
OUTFILE_FORMAT = 'mysqldump_{}_{:%F-%T}.sql'

def checkBin():
#     subprocess.Popen
    try:
        subprocess.run(['which',BIN], check=True)
    except subprocess.CalledProcessError:
        print('%s binary is required, please install it and run again' % BIN)
        exit(1)

def checkAndGetEnv(name):
    val = os.environ(name)
    if not (val):
        print('Env Var {} is not set, please set and retry'.format(name))
        exit(1)
    return val

def main(args):
    logger = logging.getLogger(__name__)
    parser = argparse.ArgumentParser(
        prog='%s %s %s' % (sys.argv[0], sys.argv[1], 'mysqldump'),
        description='Backup mariaDB with mysqldump'
    )
    parser.add_argument('--skip-mysql-env', help='Ignore all MYSQL env', action='store_true')
    parser.add_argument('--compress-with', help='Compress dump with binary', choices=['zip', 'tar', 'tarball', 'bzip2'])
    parser.add_argument('+', help='Put this to ensure following args passed to mysqldump', nargs='?')
    parser.add_argument('args', help='Arguments to pass to mysqldump', nargs=argparse.REMAINDER)
    args = parser.parse_args(args)
    logger.debug('Parsed args :' + str(args))
    
    checkBin()
    
    cmd = [BIN]
    if not (args.skip_mysql_env):
        # Host
        cmd.extend(['-h', checkAndGetEnv('MYSQL_HOST')])
        
        # User 
        cmd.extend(['-u', checkAndGetEnv('MYSQL_USER')])
        
        # Password
        if ( os.environ['MYSQL_PASS'] ) :
            cmd.extend(['-p', os.environ['MYSQL_PASS']])
    
    cmd.extend(args.args)
    
    database=''
    if not (args.skip_mysql_env):
        # Database
        database = os.environ['MYSQL_DATABASE']
        cmd.extend(database)
    
    cmd.append('>')
    
    cmd.append(os.path.join(DEST_DIR, OUTFILE_FORMAT.format(database, datetime.now())))
    
    try:
        subprocess.run(cmd,check=True)
    except subprocess.CalledProcessError:
        print('Error while backing up')
        exit(1)
