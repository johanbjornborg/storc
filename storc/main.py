#!/usr/bin/env python

# Modules from the Python standard library.
import sys
import ConfigParser
import logging
import traceback
import optparse
from os import path
from numpy import array

# Local package imports
import listener
# Output logger format
log = logging.getLogger('main')
log_formatter = logging.Formatter('%(levelname)s: %(message)s')
console = logging.StreamHandler()
console.setFormatter(log_formatter)
log.addHandler(console)

#===============================================================================
# TODO: Allow the app to take in payload size
# TODO: Calculate the seize of the balloon we will need for launch.
#===============================================================================
            
class Main:
    def __init__(self, iniFile):
        self.iniFile=iniFile
        self.cfg=ConfigParser.ConfigParser()
        self.cfg.read(self.iniFile)

        params = {}
        
        for pluginName in self.cfg.sections():
            if pluginName =='main': continue
            
            for name, value in self.cfg.items(pluginName):
                params[name] = value


        lstnr = listener.listener(params)
        lstnr.start()    
        

if __name__ == '__main__':
    try:
        ini = 'config.ini'
        main = Main(ini)
    except SystemExit as e:
        log.debug("Exit: " + repr(e))
        raise
    except Exception as e:
        log.exception("Uncaught exception")
        (exc_type, exc_value, discard_tb) = sys.exc_info()
        exc_tb = traceback.format_exception_only(exc_type, exc_value)
        info = exc_tb[-1].strip()
        raise
