# This application uses the flask restful API framework
import os
from os import listdir
import re
import sys
from dns import resolver, reversename
from datetime import date, datetime, timedelta

# IMPORT FLASK MODULES
from flask import Flask ,request, jsonify, abort, url_for, g, send_file #, session, g, redirect, , abort, render_template, flash, make_response, abort
from flask_restful import Resource, Api, reqparse
from flask_log import Logging
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_mail import Mail
from flask_mail import Message

# Import auth modules
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (JSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

# Set version
__version__ = '0.1.0'

# Set up os paths data and log folders 
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# Import variant validator code
import variantValidator
from variantValidator import variantValidator, variantanalyser

# CREATE APP 
app = Flask(__name__)
# configure
app.config.from_object(__name__)
app.config['SECRET_KEY'] = '_24-11-79-21-11-80-21-09-14-19-20'
app.config['PROPAGATE_EXCEPTIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://vvadmin:var1ant@127.0.0.1/apiAccess'
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

# Create database
db = SQLAlchemy(app)
auth = HTTPBasicAuth()

# Create API 
api = Api(app)

# Create Logging instance
flask_log = Logging(app)

# Create Mail instance
mail = Mail(app)

# Database models
# Reference
# https://blog.miguelgrinberg.com/post/restful-authentication-with-flask
class User(db.Model):
    # Database model, currently very simple
    __tablename__ = 'authUsers'
    id = db.Column(db.Integer, primary_key = True)
    domain = db.Column(db.String(50), index = True)
    password_hash = db.Column(db.String(1000))
    email = db.Column(db.String(50))
    added = db.Column(db.Date)
    expires = db.Column(db.Date)
    termination = db.Column(db.Integer)	
 
    # Code for password hashing
    # The hash_password method takes a plain password as argument and stores a hash of it with the user. 
    # This method is called when a new user is registering with the server, or when the user changes the password.
    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)
    # The verify_password() method takes a plain password as argument and returns True if the password is correct or False if not. 
    # This method is called whenever the user provides credentials and they need to be validated.
    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    # Method to generate token
    def generate_auth_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user

# Password verification decorator
@auth.verify_password
def verify_password(username_or_token, password):
	# first try to authenticate by token
	user = User.verify_auth_token(username_or_token)
	if not user:
		# try to authenticate with username/password
		user = User.query.filter_by(domain=username_or_token).first()
		if not user or not user.verify_password(password):
			return False
	# Get domain name from request environ
	origin = ''
	g.user = user
	domain = g.user.domain
	try:
		ip = str(request.environ['HTTP_X_FORWARDED_FOR'])
		addr = reversename.from_address(ip)
		origin = str(resolver.query(addr,"PTR")[0])
	except:
		return False
	if re.search('@', domain):
# 		if str(domain.split('@')[1]) != 'le.ac.uk':
# 			return False
# 		else:
# 			domain = str(domain.split('@')[1])
		domain = str(domain.split('@')[1])
	if not re.search(domain, origin):	
		return False
	else:
		now = datetime.now().date()
		if now > g.user.expires:
			return False
		else:
			return True	

# Resources
############
class hellOworlD(Resource):
	def get(self):	
		return jsonify({
		'Genome builds' : 'Supported builds are GRCh37 or GRCH38 e.g. https://rest.variantvalidator.org/GRCh37',
 		'Accepted variant desctiptions' : 	{'HGVS compliant descriptions e.g.' : 'NM_000548.3:c.138+821del, NC_000016.9:g.2099575del',
 												'VCF format' : '16-2099572-TC-T, 16:2099572TC>T or chr16:2099572TC>T (chr is not case sensitive)',
 												'Merged formats e.g. ' : 'NC_000016.9:g.2099572TC>T'},
 		'Specify Transcripts' : {'GENOMIC variants (HGVS :g. or VCF)' :  'specify a single transcript ID e.g /NM_000548.3 several transcripts e.g./NM_000548.3|NM_000548.4 or /all for all relevant transcripts',
 																		'TRANSCRIPT variants' : ' the final value should always be set to /all'},
 		'Examples' : {'GENOMIC' : 'https://rest.variantvalidator.org/GRCh37/Chr16:2099572TC>T/NM_000548.3; https://rest.variantvalidator.org/GRCh37/Chr16:2099572TC>T/all',
 					'TRANSCRIPT' : 'https://rest.variantvalidator.org/GRCh37/NM_000088.3:c.589G>T/all'}											
		})
		
class modules(Resource):
	@auth.login_required
	def get(self):	
		modules = {}
		import sqlite3
		import platform			
		modules['sqlite3'] = sqlite3.sqlite_version	
		modules['python_version'] = platform.python_version()	
		return jsonify(modules)

class resource(Resource):
	@auth.login_required
	def get(self):	
		modules = {}
		import sqlite3
		import platform			
		try:
			origin = str(request.environ['HTTP_X_FORWARDED_FOR'])
			addr = reversename.from_address(origin)
			domain = str(resolver.query(addr,"PTR")[0])
		except:
			domain = str(request.environ['HTTP_X_FORWARDED_FOR'])	
		now = str(datetime.now().date())	
		modules['now'] = now
		modules['request_from'] = domain
		modules['sqlite3'] = sqlite3.sqlite_version	
		modules['python_version'] = platform.python_version()	
		# db = variantvalidator.locate_dbs()
		#import dbPath
		#db = dbPath.locate_dbs()
		#modules['db'] = str(db)
		return jsonify(modules)	
		
class token(Resource):
	@auth.login_required
	def get(self):
		token = g.user.generate_auth_token()
		return jsonify({'your token': token.decode('ascii')})

class new_password(Resource):
	@auth.login_required
	def post(self):
		username = request.json.get('username')
		new_password = request.json.get('new_password')
		if username is None or new_password is None:
			abort(400) # missing arguments	
		g.user.password_hash = pwd_context.encrypt(new_password)
		db.session.commit()
		token = g.user.generate_auth_token()
		return jsonify({'your new token': token.decode('ascii')})		

class add_user(Resource):
	@auth.login_required
	def post(self):
		admin_username = request.json.get('admin_username')
		admin_password = request.json.get('admin_password')
		new_username = request.json.get('new_username')
		user_password = request.json.get('user_password')		
		email = request.json.get('email')
		duration = request.json.get('duration')
		if admin_username is None or admin_password is None or new_username is None or user_password is None or duration is None or email is None:
			abort(400) # missing arguments	
		# Import access control module and create access control object
		from controlModule import apiAccess as apiAccess
		from controlModule import apiAccessException
		acc = apiAccess()
		try:
			acc.add_user(admin_username, admin_password, new_username, user_password, email, duration)
		except apiAccessException as e:
			error = str(e)
			return jsonify({'Failed to add new user' : error})
		else:
			return jsonify({'New user added' : new_username})


class variantValidator38(Resource):
	@auth.login_required
	def get(self, variant_id, transcript_ids):	
		# Collect queries'
		batch_variant = str(variant_id)
		select_transcripts = str(transcript_ids)
		# Assign assembly
		selected_assembly = 'GRCh38'
		# Submit to batch
		try:
			validation = variantValidator.validator(batch_variant, selected_assembly, select_transcripts)
		except:
			import traceback
			import time
			variant = batch_variant
			exc_type, exc_value, last_traceback = sys.exc_info()
			te = traceback.format_exc()
			tbk = str(exc_type) + str(exc_value) + '\n\n' + str(te) + '\n\nVariant = ' + variant + ' and selected_assembly = GRCh38'
			error = str(tbk)
			# Email admin
			msg = Message(recipients=["variantvalidator@gmail.com"],
				sender='apiValidator',
				body=error + '\n\n' + time.ctime(),
				subject='Major error recorded')
			# Send the email
			mail.send(msg)			
			error = [{'validation_warnings': 'Validation error: Admin have been made aware of the issue'}]
			return jsonify(validation=error)
		# Look for warnings
		for val in validation:
			if val['validation_warnings'] == 'Validation error':
				import time
				variant = batch_variant
				error = 'Variant = ' + variant + ' and selected_assembly = GRCh38' + '/n' + str(val)
				# Email admin
				msg = Message(recipients=["variantvalidator@gmail.com"],
					sender='apiValidator',
					body=error + '\n\n' + time.ctime(),
					subject='Validation server error recorded')
				# Send the email
				mail.send(msg)			
		return jsonify(validation=validation)
		
class variantValidatorHg38(Resource):
	@auth.login_required
	def get(self, variant_id, transcript_ids):	
		# Collect queries'
		batch_variant = str(variant_id)
		select_transcripts = str(transcript_ids)
		# Assign assembly
		selected_assembly = 'GRCh38'
		# Submit to batch
		try:
			validation = variantValidator.validator(batch_variant, selected_assembly, select_transcripts)
		except:
			import traceback
			import time
			variant = batch_variant
			exc_type, exc_value, last_traceback = sys.exc_info()
			te = traceback.format_exc()
			tbk = str(exc_type) + str(exc_value) + '\n\n' + str(te) + '\n\nVariant = ' + variant + ' and selected_assembly = GRCh38'
			error = str(tbk)
			# Email admin
			msg = Message(recipients=["variantvalidator@gmail.com"],
				sender='apiValidator',
				body=error + '\n\n' + time.ctime(),
				subject='Major error recorded')
			# Send the email
			mail.send(msg)			
			error = [{'validation_warnings': 'Validation error: Admin have been made aware of the issue'}]
			return jsonify(validation=error)
		# Look for warnings
		for val in validation:
			if val['validation_warnings'] == 'Validation error':
				import time
				variant = batch_variant
				error = 'Variant = ' + variant + ' and selected_assembly = hg38' + '/n' + str(val)
				# Email admin
				msg = Message(recipients=["variantvalidator@gmail.com"],
					sender='apiValidator',
					body=error + '\n\n' + time.ctime(),
					subject='Validation server error recorded')
				# Send the email
				mail.send(msg)			
		return jsonify(validation=validation)

class variantValidator37(Resource):
	@auth.login_required
	def get(self, variant_id, transcript_ids):	
		# Collect queries'
		batch_variant = str(variant_id)
		select_transcripts = str(transcript_ids)
		# Assign assembly
		selected_assembly = 'GRCh37'
		# Submit to batch
		try:
			validation = variantValidator.validator(batch_variant, selected_assembly, select_transcripts)
		except:
			import traceback
			import time
			variant = batch_variant
			exc_type, exc_value, last_traceback = sys.exc_info()
			te = traceback.format_exc()
			tbk = str(exc_type) + str(exc_value) + '\n\n' + str(te) + '\n\nVariant = ' + variant + ' and selected_assembly = GRCh37'
			error = str(tbk)
			# Email admin
			msg = Message(recipients=["variantvalidator@gmail.com"],
				sender='apiValidator',
				body=error + '\n\n' + time.ctime(),
				subject='Major error recorded')
			# Send the email
			mail.send(msg)			
			error = [{'validation_warnings': 'Validation error: Admin have been made aware of the issue'}]
			return jsonify(validation=error)
		# Look for warnings
		for val in validation:
			import time
			if val['validation_warnings'] == 'Validation error':
				variant = batch_variant
				error = 'Variant = ' + variant + ' and selected_assembly = GRCh37' + '/n' + str(val)
				# Email admin
				msg = Message(recipients=["variantvalidator@gmail.com"],
					sender='apiValidator',
					body=error + '\n\n' + time.ctime(),
					subject='Validation server error recorded')
				# Send the email
				mail.send(msg)			
		return jsonify(validation=validation)
		
class variantValidatorHg19(Resource):
	@auth.login_required
	def get(self, variant_id, transcript_ids):	
		# Collect queries'
		batch_variant = str(variant_id)
		select_transcripts = str(transcript_ids)
		# Assign assembly
		selected_assembly = 'GRCh37'
		# Submit to batch
		try:
			validation = variantValidator.validator(batch_variant, selected_assembly, select_transcripts)
		except:
			import traceback
			import time
			variant = batch_variant
			exc_type, exc_value, last_traceback = sys.exc_info()
			te = traceback.format_exc()
			tbk = str(exc_type) + str(exc_value) + '\n\n' + str(te) + '\n\nVariant = ' + variant + ' and selected_assembly = hg19' + '/n' + str(val)
			error = str(tbk)
			# Email admin
			msg = Message(recipients=["variantvalidator@gmail.com"],
				sender='apiValidator',
				body=error + '\n\n' + time.ctime(),
				subject='Major error recorded')
			# Send the email
			mail.send(msg)			
			error = [{'validation_warnings': 'Validation error: Admin have been made aware of the issue'}]
			return jsonify(validation=error)
		# Look for warnings
		for val in validation:
			import time
			if val['validation_warnings'] == 'Validation error':
				variant = batch_variant
				error = 'Variant = ' + variant + ' and selected_assembly = GRCh37'
				# Email admin
				msg = Message(recipients=["variantvalidator@gmail.com"],
					sender='apiValidator',
					body=error + '\n\n' + time.ctime(),
					subject='Validation server error recorded')
				# Send the email
				mail.send(msg)			
		return jsonify(validation=validation)		

class gene2transcripts(Resource):
	@auth.login_required
	def get(self, query):
		g2t = variantValidator.gene2transcripts(query)
		return jsonify(g2t)

class hgvs2reference(Resource):
	@auth.login_required
	def get(self, query):
		h2r = variantValidator.hgvs2ref(query)
		return jsonify(h2r)		

class myAccount(Resource):
	@auth.login_required
	def get(self):
		account_details = {'contact_email' : g.user.email,
		'account_id' : g.user.domain,
		'expiry' : g.user.expires,
		'status' : 'LIVE'
		}
		return jsonify(account_details)	

class validator_data(Resource):
	@auth.login_required
	def get(self):
		directory_path = os.environ.get('VALIDATOR_DATA')
		versions = os.listdir(directory_path)
		databases = {'available_database_versions' : versions}
		return jsonify(databases)

class download_database(Resource):
	@auth.login_required
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
api.add_resource(hellOworlD, '/')
api.add_resource(modules, '/modules')
api.add_resource(resource, '/api/resource')
api.add_resource(token, '/api/mytoken')
api.add_resource(new_password, '/api/newpassword')
api.add_resource(add_user, '/api/add_user')
api.add_resource(myAccount, '/api/myaccount')
api.add_resource(validator_data, '/api/validatordata')
api.add_resource(download_database, '/api/download_database/<string:query>')
api.add_resource(variantValidator37, '/GRCh37/<string:variant_id>/<string:transcript_ids>')
api.add_resource(variantValidatorHg19, '/hg19/<string:variant_id>/<string:transcript_ids>')
api.add_resource(variantValidator38, '/GRCh38/<string:variant_id>/<string:transcript_ids>')
api.add_resource(variantValidatorHg38, '/hg38/<string:variant_id>/<string:transcript_ids>')
api.add_resource(gene2transcripts, '/gene2transcripts/<string:query>')
api.add_resource(hgvs2reference, '/hgvs2reference/<string:query>')

# Run the server (if file is called directly by python, server is internal dev server)
if __name__ == '__main__':
    app.debug=True
    os.environ['VALIDATOR_DEBUG'] = 'TRUE'
    app.run()
else:
	app.debug=False		
