import os
import configuration

VV_APP_ROOT = os.path.dirname(os.path.abspath(__file__))
os.environ['VV_APP_ROOT'] = VV_APP_ROOT

# Config Section Mapping function
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1


# Configure the environmental variables
from configparser import ConfigParser
CONF_ROOT = os.environ.get('CONF_ROOT')
Config = ConfigParser()
Config.read(os.path.join(CONF_ROOT, 'config.ini'))
HGVS_SEQREPO_DIR = ConfigSectionMap("SeqRepo")['seqrepo_dir']
os.environ['HGVS_SEQREPO_DIR'] = HGVS_SEQREPO_DIR
UTA_DB_URL = ConfigSectionMap("UTA")['uta_url']
os.environ['UTA_DB_URL'] = UTA_DB_URL
VALIDATOR_DATA = ConfigSectionMap("validatorDB")['validator_databases']
os.environ['VALIDATOR_DATA'] = VALIDATOR_DATA
PYLIFTOVER_DIR = ConfigSectionMap("pyLiftover")['pyliftover_dir']
os.environ['PYLIFTOVER_DIR'] = PYLIFTOVER_DIR
