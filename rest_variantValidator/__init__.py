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
SERVER_NAME = ConfigSectionMap("Server")['server_url']
os.environ['SERVER_NAME'] = SERVER_NAME

# <LICENSE>
# Copyright (C) 2019  Peter Causey-Freeman, University of Manchester
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# </LICENSE>
