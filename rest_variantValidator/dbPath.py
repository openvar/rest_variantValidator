import os
def locate_dbs():
	HGVS_SEQREPO_DIR = os.environ.get('HGVS_SEQREPO_DIR')
	UTA_DB_URL = os.environ.get('UTA_DB_URL')
	VALIDATOR_DB_URL = os.environ.get('VALIDATOR_DB_URL')
	
	locate = {
			'HGVS_SEQREPO_DIR' : HGVS_SEQREPO_DIR,
			'UTA_DB_URL' : UTA_DB_URL,
			'VALIDATOR_DB_URL' : VALIDATOR_DB_URL
			}
	
	return locate

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
