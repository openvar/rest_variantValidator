# This application uses the flask restful API framework
import os
from os import listdir
import re
import sys
# from dns import resolver, reversename
from datetime import date, datetime, timedelta
import warnings

# IMPORT FLASK MODULES
from flask import Flask ,request, jsonify, abort, url_for, g, send_file, redirect #, session, g, redirect, , abort, render_template, flash, make_response, abort
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_restful_swagger import swagger
from flask_log import Logging
# from flask_httpauth import HTTPBasicAuth
from flask_mail import Mail, Message

# Set up os paths data and log folders 
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_STATIC = os.path.join(APP_ROOT, 'static')

# Import variant validator code
import VariantValidator
from VariantValidator import variantValidator

# Extract API related metadata
config_dict =  VariantValidator.variantValidator.my_config()
api_version = config_dict['variantvalidator_version']

# CREATE APP 
app = Flask(__name__, static_folder=APP_STATIC)
# app = Flask(__name__, static_url_path=APP_STATIC)

# configure
app.config.from_object(__name__)
app.config['PROPAGATE_EXCEPTIONS'] = False

# Wrap the Api with swagger.docs. 
api = swagger.docs(Api(app), apiVersion=str(api_version),
				   basePath='https://rest.variantvalidator.org',
				   resourcePath='/',
				   produces=["application/json"],
				   api_spec_url='/webservices/variantvalidator',
				   description='VariantValidator web API'
				   )

# Create Logging instance
flask_log = Logging(app)

# Create Mail instance
mail = Mail(app)
			
# Resources
############
"""
Essentially web pages that display json data
"""

"""
Home
"""
class home(Resource):
	def get(self):
		return redirect('https://rest.variantvalidator.org/webservices/variantvalidator.html')


"""
VariantValidator
"""
class variantValidator(Resource):
	@swagger.operation(
		notes='Submit a sequence variation to VariantValidator',
		nickname='VariantValidator',
		parameters=[
		  {
			"name": "genome_build",
			"description": "Possible values: GRCh37, GRCh38, hg19, hg38",
			"required": True,
			"allowMultiple": False,
			"dataType": 'string',
			"paramType": "path"
			  },
		  {
			"name": "variant_description",
			"description": "Supported variant types: HGVS e.g. NM_000088.3:c.589G>T, NC_000017.10:g.48275363C>A, NG_007400.1:g.8638G>T, LRG_1:g.8638G>T, LRG_1t1:c.589G>T; pseudo-VCF e.g. 17-50198002-C-A, 17:50198002:C:A, GRCh3817-50198002-C-A, GRCh38:17:50198002:C:A; hybrid e.g. chr17:50198002C>A, chr17:50198002C>A(GRCh38), chr17:g.50198002C>A, chr17:g.50198002C>A(GRCh38)",
			"required": True,
			"allowMultiple": False,
			"dataType": 'string',
			"paramType": "path"
			  },
		  {
			"name": "select_transcripts",
			"description": "Possible values: all = return data for all relevant transcripts; single transcript id e.g. NM_000093.4; multiple transcript ids e.g. NM_000093.4|NM_001278074.1|NM_000093.3",
			"required": True,
			"allowMultiple": False,
			"dataType": 'string',
			"paramType": "path"
			  }			  			  			  
		])

	def get(self, genome_build, variant_description, select_transcripts):	
		try:
			validation = VariantValidator.variantValidator.validator(variant_description, genome_build, select_transcripts)
		except:
			import traceback
			import time
			exc_type, exc_value, last_traceback = sys.exc_info()
			te = traceback.format_exc()
			tbk = str(exc_type) + str(exc_value) + '\n\n' + str(te) + '\n\nVariant = ' + str(variant_description) + ' and selected_assembly = ' + str(genome_build) + '/n'
			error = str(tbk)
			# Email admin
			msg = Message(recipients=["variantvalidator@gmail.com"],
				sender='apiValidator',
				body=error + '\n\n' + time.ctime(),
				subject='Major error recorded')
			# Send the email
			mail.send(msg)			
			error = {'flag' : ' Major error', 
					'validation_error': 'A major validation error has occurred. Admin have been made aware of the issue'}
			return error, 200, {'Access-Control-Allow-Origin': '*'}
				
		# Look for warnings
		for key, val in validation.iteritems():
			if key == 'flag' or key == 'metadata':
				if key == 'flag' and str(val) == 'None':					
					import time
					variant = variant_description
					error = 'Variant = ' + str(variant_description) + ' and selected_assembly = ' + str(genome_build) + '\n'
					# Email admin
					msg = Message(recipients=["variantvalidator@gmail.com"],
						sender='apiValidator',
						body=error + '\n\n' + time.ctime(),
						subject='Validation server error recorded')
					# Send the email
					mail.send(msg)
				else:
					continue					
			try:
				if val['validation_warnings'] == 'Validation error':
					import time
					variant = variant_description
					error = 'Variant = ' + str(variant_description) + ' and selected_assembly = ' + str(genome_build) + '\n'
					# Email admin
					msg = Message(recipients=["variantvalidator@gmail.com"],
						sender='apiValidator',
						body=error + '\n\n' + time.ctime(),
						subject='Validation server error recorded')
					# Send the email
					mail.send(msg)
			except TypeError:
				pass
		return validation, 200, {'Access-Control-Allow-Origin': '*'}


"""
Return the transcripts for a gene 
"""
class gene2transcripts(Resource):
	@swagger.operation(
		notes='Get a list of available transcripts for a gene by providing a valid HGNC gene symbol or transcript ID',
		nickname='get genes2transcripts',
		parameters=[
		  {
			"name": "gene_symbol",
			"description": "HGNC gene symbol or transcript ID (Supported transcript types: RefSeq; LRG_t) (Note, work needed on LRG_t types)",
			"required": True,
			"allowMultiple": False,
			"dataType": 'string',
			"paramType": "path"
			  }
		])
	def get(self, gene_symbol):
		g2t = VariantValidator.variantValidator.gene2transcripts(gene_symbol)
		return g2t, 200, {'Access-Control-Allow-Origin': '*'}


"""
Simple function that returns the reference bases for a hgvs description
"""
class hgvs2reference(Resource):
	@swagger.operation(
		notes='Get the reference bases for a HGVS variant description',
		nickname='get reference bases',
		parameters=[
		  {
			"name": "hgvs_description",
			"description": "Sequence variation description in the HGVS format. Intronic descriptions must be in the format Genomic_id(transcript_id):type.PositionVariation, e.g. NC_000017.11(NM_000088.3):c.589-1del (Work needed on intronic types!)",
			"required": True,
			"allowMultiple": False,
			"dataType": 'string',
			"paramType": "path"
			  }
		])
	def get(self, hgvs_description):
		h2r = VariantValidator.variantValidator.hgvs2ref(hgvs_description)
		return jsonify(h2r)		


"""
Functions that will provide downloadable versions of the vv database once made
"""
class validator_data(Resource):
	def get(self):
		directory_path = os.environ.get('VALIDATOR_DATA')
		versions = os.listdir(directory_path)
		databases = {'available_database_versions' : versions}
		return jsonify(databases)

class download_database(Resource):
	def get(self, query):
		directory_path = os.environ.get('VALIDATOR_DATA')
		file = query
		full_path = directory_path + '/' + file
		try:
			return send_file(full_path,
						as_attachment=True,
						attachment_filename=file)		
		except IOError as e:
			return jsonify({'error' : 'No such file: ' + file})
			

# ADD API resources to API handler
api.add_resource(home, '/')
api.add_resource(validator_data, '/data/validatordata')
api.add_resource(download_database, '/data/download_database/<string:schema>')
api.add_resource(variantValidator, '/variantvalidator/<string:genome_build>/<string:variant_description>/<string:select_transcripts>')
api.add_resource(gene2transcripts, '/tools/gene2transcripts/<string:gene_symbol>')
api.add_resource(hgvs2reference, '/tools/hgvs2reference/<string:hgvs_description>')


# Run the server (if file is called directly by python, server is internal dev server)
if __name__ == '__main__':
	app.debug=True
	os.environ['VALIDATOR_DEBUG'] = 'TRUE'
	app.run()
else:
	app.debug=False		
