'''
Created on 25 oct. 2016

@author: lym
'''

class FileSize:
    
    def __init__(self, value):
        self.value = value
    
    def getValue(self):
        return self.value
    
    def __str__(self):
        return sizeof_fmt(self.value)
    
    def __repr__(self):
        return str(self)

class TermColor:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
   
    @staticmethod 
    def header(text):
        return TermColor.HEADER + text + TermColor.ENDC

    @staticmethod
    def okgreen(text):
        return TermColor.OKGREEN + text + TermColor.ENDC
    
    @staticmethod
    def warn(text):
        return TermColor.WARNING + text + TermColor.ENDC
    
    @staticmethod
    def fail(text):
        return TermColor.FAIL + text + TermColor.ENDC

def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)
