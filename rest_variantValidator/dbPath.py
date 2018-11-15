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
