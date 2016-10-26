
import os, sys, subprocess
import argparse
import logging
from datetime import datetime
from . import printHeader, checkAndGetEnv, checkBin, DEST_DIR

BIN = 'mysqldump'
OUTFILE_FORMAT = 'mysqldump_{}_{:%F-%H-%M-%S}.sql'
COMPRESS_METHODS = ['zip', 'tar', 'tarball', 'bzip2']

DESCRIPTION = 'Backup mariaDB with mysqldump'
EPILOG = '''
Environment:
    mysqldump method use these environment variable for default command line argument.
    You can skip this comportement with swith --skip-mysql-env

    MYSQL_HOST        [required] mysql database host
    MYSQL_USER        [required] mysql database user
    MYSQL_PASSWORD    [optional] user password
    MYSQL_DATABASE    [optional] database to backup

Example
    Backup in single transaction
    mdbtool backup mysqldump + --single-transaction
'''

logger = logging.getLogger(__name__)

def backup(args):
    printHeader('BackUp')
    print('Backing up data')
    cmd = [BIN]
    if not (args.skip_mysql_env):
        # Host
        cmd.append('-h{}'.format(checkAndGetEnv('MYSQL_HOST')))
        
        # User 
        cmd.append('-u{}'.format(checkAndGetEnv('MYSQL_USER')))
        
        # Password
        if ( os.environ['MYSQL_PASSWORD'] ) :
            cmd.append('-p{}'.format(os.environ['MYSQL_PASSWORD']))
    
    cmd.extend(args.args)
    
    cmd.append('--result-file {}'.format(os.path.join(DEST_DIR, args.outfile)))
    cmd.append(args.database)
    
    final_cmd = ' '.join(cmd)
    logger.debug('Running command : {}'.format(final_cmd))
    subprocess.check_call(final_cmd, shell=True)
    print('Backing successfull')
    return

def generateMd5(file):
    if not ( file ):
        raise ValueError('unable to generate md5, file required')
    printHeader('md5')
    print('generating md5 files')
    outfile = file + '.md5'
    command = ' '.join(['md5sum -b', file, " > ",outfile])
    subprocess.check_call(command, shell=True, cwd=DEST_DIR)
    return

def compress(file=None):
    if not ( file ):
        raise ValueError('unable to compress, file required')
    printHeader('Compression')
    outfile = file + '.7z'
    cmd = ['7zr', 'a', outfile]
    cmd.append(file)
    try:
        command = ' '.join(cmd)
        logger.debug('Running command : {}'.format(command))
        subprocess.check_call(command, shell=True, cwd=DEST_DIR)
        os.remove(os.path.join(DEST_DIR,file))
        generateMd5(outfile)
    except subprocess.CalledProcessError:
        print('Error while compressing')
        exit()
    return

def main(args):
    parser = argparse.ArgumentParser(
        prog='%s %s %s' % (sys.argv[0], sys.argv[1], 'mysqldump'),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=DESCRIPTION,
        epilog=EPILOG
    )
    parser.add_argument('--skip-mysql-env', help='Ignore all MYSQL env', action='store_true')
    parser.add_argument('--no-compress', help='Do not compress', dest='compress', action='store_false')
    parser.add_argument('+', help='Put this to ensure following args passed to mysqldump', nargs='?')
    parser.add_argument('args', help='Arguments to pass to mysqldump', nargs=argparse.REMAINDER)
    args = parser.parse_args(args)
    logger.debug('Parsed args : {}'.format(args))
    
    database=''
    if not (args.skip_mysql_env):
        # Database
        database = os.environ['MYSQL_DATABASE']
    
    args.database = database
    args.outfile = OUTFILE_FORMAT.format(database, datetime.now())
    
    checkBin(BIN)
    backup(args)
    if (args.compress):
        compress(file=args.outfile)
    else:
        generateMd5(args.outfile)
    
