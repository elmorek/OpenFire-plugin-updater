#!/usr/local/bin/env python

import os, sys, time
from optparse import OptionParser
import subprocess
from datetime import date

config = {
    'OPENFIRE_PLUGINS_DIRECTORY' : '/usr/share/openfire/plugins/',
    'AVAYA_PLUGIN_NAME' : 'avaya.jar',
    'OPENFIRE_USER' : 'openfire'
}

parser = OptionParser()
parser.add_option('-f', dest='filename')
parser.add_option('--rollback', action='store_true', dest='rollback')
(options, args) = parser.parse_args()

if options.filename and not options.rollback:
    newPlugin = options.filename
else:
    print 'No plugin name was provided. Please use <python upgrader.py -f [filename]>'
    sys.exit()

if options.rollback:
    rollback = options.rollback
else:
    rollback = False


today = date.today().isoformat()

def renamePlugin(newPlugin):
    if os.path.exists(newPlugin):
        os.system('mv '+newPlugin+' /tmp/'+config['AVAYA_PLUGIN_NAME'])
        if os.path.exists('/tmp/'+config['AVAYA_PLUGIN_NAME']):
            print "New plugin renamed to "+config['AVAYA_PLUGIN_NAME']
            serviceOps('java', 'off')
        else:
            print "New plugin could not be renamed, exiting..."
            sys.exit()
    else:
        print "New plugin has not been found, exiting..."
        sys.exit()


def serviceOps(processName, operation):
    if operation == 'off':
            proc = subprocess.Popen(["ps -ef | grep "+processName+" | grep -v grep | awk '{print $2}'"], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            if out:
                os.system('service openfire stop')
                print 'Stopping OpenFire service...'
                time.sleep(5)
            else:
                print 'OpenFire service is not running'
            proc = subprocess.Popen(["ps -ef | grep "+processName+" | grep -v grep | awk '{print $2}'"], stdout=subprocess.PIPE, shell=True)
            (out, err) = proc.communicate()
            if out:
                print 'OpenFire service is not stopped'
                sys.exit()
            else:
                print 'Openfire service stopped'
                deletePlugin()

    if operation == 'on':
        os.system('service openfire start')
        print 'Starting OpenFire service...'
        time.sleep(5)
        proc = subprocess.Popen(["ps -ef | grep "+processName+" | grep -v grep | awk '{print $2}'"], stdout=subprocess.PIPE, shell=True)
        (out, err) = proc.communicate()
        if out:
            print 'OpenFire service is started'
        else:
            print 'Openfire service cannot be started'
            sys.exit()

def deletePlugin():
    if os.path.exists(config['OPENFIRE_PLUGINS_DIRECTORY']+'avaya.jar'):
        if rollback == False:
            os.system('mv '+config['OPENFIRE_PLUGINS_DIRECTORY']+config['AVAYA_PLUGIN_NAME']+' '+config['OPENFIRE_PLUGINS_DIRECTORY']+'avaya.OLD.'+today)
            print 'Old plugin version stored as: '+config['OPENFIRE_PLUGINS_DIRECTORY']+'avaya.OLD.'+today
            installPlugin()
        else:
            os.system('mv '+config['OPENFIRE_PLUGINS_DIRECTORY']+config['AVAYA_PLUGIN_NAME']+' '+config['OPENFIRE_PLUGINS_DIRECTORY']+'avaya.NEW.'+today)
            print 'New plugin version stored as: '+config['OPENFIRE_PLUGINS_DIRECTORY']+'avaya.NEW.'+today
            installPlugin()
    else:
        print 'Plugin does not exist in '+config['OPENFIRE_PLUGINS_DIRECTORY']
        print 'New instalation will be executed'
        installNewPlugin()

def installPlugin():
    if rollback == False:
        os.system('cp  '+config['OPENFIRE_PLUGINS_DIRECTORY'])
        if os.path.exists(config['OPENFIRE_PLUGINS_DIRECTORY']+config['AVAYA_PLUGIN_NAME']):
            print 'New Avaya plugin copied to plugins directory'
            os.system('chown '+config['OPENFIRE_USER']+' '+config['OPENFIRE_PLUGINS_DIRECTORY']+config['AVAYA_PLUGIN_NAME'])
            print 'New Avaya plugin owned by user '+config['OPENFIRE_USER']
            serviceOps('openfire', 'on')
        else:
            print 'Plugin could not be copied, exiting...'
            serviceOps('openfire', 'on')
            sys.exit()
    else:
        os.system('mv '+config['OPENFIRE_PLUGINS_DIRECTORY']+'avaya.OLD.'+today+' '+config['OPENFIRE_PLUGINS_DIRECTORY']+config['AVAYA_PLUGIN_NAME'])
        print 'Previos plugin restored'
        os.system('chown '+config['OPENFIRE_USER']+' '+config['OPENFIRE_PLUGINS_DIRECTORY']+config['AVAYA_PLUGIN_NAME'])
        serviceOps('openfire', 'on')

if __name__ == "__main__":
    os.system('clear')
    print 'OpenFire Plugins directory: '+config['OPENFIRE_PLUGINS_DIRECTORY']
    print 'Avaya plugin name: '+config['AVAYA_PLUGIN_NAME']+'\n\n'
    if rollback == False:
        renamePlugin(newPlugin)
    else:
        serviceOps('openfire', 'off')
