import os,subprocess

DEST_DIR = '/backup'

def checkBin(binary):
    try:
        subprocess.check_call(['which',binary],stdout=subprocess.DEVNULL)
    except subprocess.CalledProcessError:
        print('%s binary is required, please install it and run again' % binary)
        exit(1)

def checkAndGetEnv(name):
    val = os.environ[name]
    if not (val):
        print('Env Var {} is not set, please set and retry'.format(name))
        exit(1)
    return val

def printHeader(title):
    print('#### {} ####'.format(title))
